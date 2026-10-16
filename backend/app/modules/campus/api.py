import secrets
from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.modules.campus import use_cases
from app.modules.campus.domain import Aviso, Institucion, TipoAviso
from app.modules.campus.infra.repo_pg import CampusPg
from app.modules.campus.ports import CampusRepo
from app.modules.clima.api import AlertaOut, get_fuente, get_traductor
from app.modules.clima.ports import FuenteClima, TraductorCiudadano
from app.modules.residuos.api import get_repo as get_repo_residuos
from app.modules.residuos.ports import ReporteResiduoRepo
from app.modules.transito.api import ZonaRojaOut
from app.modules.transito.api import get_repo as get_repo_transito
from app.modules.transito.ports import ReporteTransitoRepo
from app.shared.db import get_session
from app.shared.geo import Punto

router = APIRouter(prefix="/campus", tags=["Modo Campus (estudiantes)"])


def get_repo(session: AsyncSession = Depends(get_session)) -> CampusRepo:
    return CampusPg(session)


def admin(x_admin_token: str = Header("", description="Token de administración (ADMIN_TOKEN)")) -> None:
    if not settings.admin_token:
        raise HTTPException(403, "Administración deshabilitada: configurá ADMIN_TOKEN en el servidor")
    if not secrets.compare_digest(x_admin_token, settings.admin_token):
        raise HTTPException(401, "Token de administración inválido")


async def _institucion(slug: str, repo: CampusRepo) -> Institucion:
    inst = await repo.institucion(slug)
    if not inst:
        raise HTTPException(404, "Institución no encontrada")
    return inst


class InstitucionIn(BaseModel):
    nombre: str = Field(min_length=3, max_length=120)
    ciudad: str = Field(min_length=2, max_length=60)
    lat: float
    lon: float
    radio_m: int = Field(1500, ge=200, le=10_000)


class InstitucionOut(BaseModel):
    slug: str
    nombre: str
    ciudad: str
    lat: float
    lon: float
    radio_m: int


class AvisoIn(BaseModel):
    tipo: TipoAviso
    titulo: str = Field(min_length=3, max_length=120)
    mensaje: str = Field(min_length=3, max_length=1000)
    horas_vigencia: int = Field(24, ge=1, le=24 * 30)


class AvisoOut(BaseModel):
    id: str | None
    tipo: TipoAviso
    titulo: str
    mensaje: str
    vigente_hasta: datetime
    creado: datetime


class RecomendacionOut(BaseModel):
    nivel: str
    titulo: str
    texto: str


class EstadoOut(BaseModel):
    institucion: InstitucionOut
    recomendacion: RecomendacionOut
    lluvia_activa: bool
    alertas: list[AlertaOut]
    zonas_rojas: list[ZonaRojaOut]
    residuos_criticos: int
    avisos: list[AvisoOut]


def _inst_out(i: Institucion) -> InstitucionOut:
    return InstitucionOut(slug=i.slug, nombre=i.nombre, ciudad=i.ciudad, lat=i.punto.lat, lon=i.punto.lon,
                          radio_m=i.radio_m)


def _aviso_out(a: Aviso) -> AvisoOut:
    return AvisoOut(id=a.id, tipo=a.tipo, titulo=a.titulo, mensaje=a.mensaje, vigente_hasta=a.vigente_hasta,
                    creado=a.creado)


@router.get("/instituciones", response_model=list[InstitucionOut])
async def instituciones(repo: CampusRepo = Depends(get_repo)):
    return [_inst_out(i) for i in await repo.instituciones()]


@router.post("/instituciones", response_model=InstitucionOut, status_code=201, dependencies=[Depends(admin)])
async def crear_institucion(body: InstitucionIn, repo: CampusRepo = Depends(get_repo)):
    slug = use_cases.slugificar(body.nombre)
    if not slug:
        raise HTTPException(422, "Nombre inválido")
    inst = Institucion(slug, body.nombre, body.ciudad, Punto(body.lat, body.lon), body.radio_m)
    try:
        return _inst_out(await use_cases.crear_institucion(inst, repo))
    except use_cases.InstitucionDuplicada:
        raise HTTPException(409, "Ya existe una institución con ese nombre") from None


@router.get("/{slug}/estado", response_model=EstadoOut)
async def estado(
    slug: str,
    repo: CampusRepo = Depends(get_repo),
    fuente: FuenteClima = Depends(get_fuente),
    traductor: TraductorCiudadano = Depends(get_traductor),
    transito: ReporteTransitoRepo = Depends(get_repo_transito),
    residuos: ReporteResiduoRepo = Depends(get_repo_residuos),
):
    inst = await _institucion(slug, repo)
    try:
        e = await use_cases.estado(inst, datetime.now(UTC), repo, fuente, traductor, settings.temporada_enso,
                                   transito, residuos)
    except Exception as ex:
        raise HTTPException(503, "No se pudo armar el estado del campus. Probá de nuevo en unos minutos.") from ex
    return EstadoOut(
        institucion=_inst_out(inst),
        recomendacion=RecomendacionOut(nivel=e.recomendacion.nivel, titulo=e.recomendacion.titulo,
                                       texto=e.recomendacion.texto),
        lluvia_activa=e.clima.lluvia_activa,
        alertas=[AlertaOut(tipo=a.tipo, severidad=a.severidad, mensaje_ciudadano=a.mensaje_ciudadano,
                           mensaje_tecnico=a.mensaje_tecnico, consejos=list(a.consejos)) for a in e.clima.alertas],
        zonas_rojas=[ZonaRojaOut(tipo=z.tipo, lat=z.centro.lat, lon=z.centro.lon, reportes=z.reportes,
                                 dispositivos=z.dispositivos, ultimo=z.ultimo) for z in e.zonas_rojas],
        residuos_criticos=e.residuos_criticos,
        avisos=[_aviso_out(a) for a in e.avisos],
    )


@router.post("/{slug}/avisos", response_model=AvisoOut, status_code=201, dependencies=[Depends(admin)])
async def publicar_aviso(slug: str, body: AvisoIn, repo: CampusRepo = Depends(get_repo)):
    inst = await _institucion(slug, repo)
    ahora = datetime.now(UTC)
    aviso = Aviso(inst.slug, body.tipo, body.titulo, body.mensaje, ahora + timedelta(hours=body.horas_vigencia), ahora)
    return _aviso_out(await repo.crear_aviso(aviso))
