from datetime import UTC, datetime

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.modules.clima.api import get_fuente
from app.modules.clima.ports import FuenteClima
from app.modules.clima.use_cases import hay_lluvia_activa
from app.modules.residuos import calendario, use_cases
from app.modules.residuos.domain import ReporteResiduo
from app.modules.residuos.infra.clasificador_claude import ClasificadorClaude
from app.modules.residuos.infra.repo_pg import ReporteResiduoPg
from app.modules.residuos.ports import ClasificadorImagen, ReporteResiduoRepo
from app.modules.residuos.scoring import PESO_MAPA
from app.shared.db import get_session
from app.shared.geo import Punto
from app.shared.http import device_id
from app.shared.ia.claude_client import get_claude

router = APIRouter(prefix="/residuos", tags=["Yty & Sumideros"])


def get_clasificador() -> ClasificadorImagen:
    return ClasificadorClaude(get_claude(), settings.anthropic_model)


def get_repo(session: AsyncSession = Depends(get_session)) -> ReporteResiduoRepo:
    return ReporteResiduoPg(session)


def get_lluvia(fuente: FuenteClima = Depends(get_fuente)):
    return lambda punto: hay_lluvia_activa(punto, fuente)


def tipo_imagen(data: bytes) -> str | None:
    """Detecta el formato por la firma del archivo; no confiamos en el Content-Type del cliente."""
    if data.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "image/webp"
    return None


class ReporteOut(BaseModel):
    id: str | None
    lat: float
    lon: float
    categoria: str
    confianza: float
    descripcion: str
    severidad: str
    peso: float
    creado: datetime


def _out(r: ReporteResiduo) -> ReporteOut:
    return ReporteOut(id=r.id, lat=r.punto.lat, lon=r.punto.lon, categoria=r.categoria, confianza=r.confianza,
                      descripcion=r.descripcion, severidad=r.severidad, peso=PESO_MAPA[r.severidad],
                      creado=r.creado)


@router.post("/reportes", response_model=ReporteOut, status_code=201)
async def reportar(
    foto: UploadFile = File(...),
    lat: float = Form(...),
    lon: float = Form(...),
    device: str = Depends(device_id),
    clasificador: ClasificadorImagen = Depends(get_clasificador),
    repo: ReporteResiduoRepo = Depends(get_repo),
    lluvia=Depends(get_lluvia),
):
    punto = Punto(lat, lon)
    data = await foto.read(settings.max_foto_bytes + 1)
    if len(data) > settings.max_foto_bytes:
        raise HTTPException(413, "La foto supera los 5 MB")
    media_type = tipo_imagen(data)
    if media_type is None:
        raise HTTPException(415, "Formato no soportado: usá JPG, PNG o WEBP")

    r = await use_cases.crear_reporte(data, media_type, punto, device, datetime.now(UTC), clasificador, repo, lluvia)
    return _out(r)


@router.get("/mapa", response_model=list[ReporteOut])
async def mapa(repo: ReporteResiduoRepo = Depends(get_repo)):
    return [_out(r) for r in await use_cases.mapa(repo, datetime.now(UTC))]


class RecorridoOut(BaseModel):
    barrio: str
    ciudad: str
    dias: list[str]
    hora: str
    proximo_paso: datetime


@router.get("/calendario", response_model=list[RecorridoOut])
def calendario_barrios():
    ahora = datetime.now(UTC)
    return [
        RecorridoOut(barrio=r.barrio, ciudad=r.ciudad, dias=[calendario.DIAS[d] for d in r.dias],
                     hora=r.hora.strftime("%H:%M"), proximo_paso=calendario.proximo_paso(r, ahora))
        for r in calendario.recorridos()
    ]
