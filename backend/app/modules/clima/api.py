from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.config import settings
from app.modules.clima import use_cases
from app.modules.clima.domain import CIUDADES
from app.modules.clima.infra.open_meteo import OpenMeteo
from app.modules.clima.infra.traductor_claude import TraductorClaude
from app.modules.clima.ports import FuenteClima, TraductorCiudadano
from app.shared.ia.claude_client import get_claude

router = APIRouter(prefix="/clima", tags=["Aratiri & Oky"])


def get_fuente() -> FuenteClima:
    return OpenMeteo()


def get_traductor() -> TraductorCiudadano:
    return TraductorClaude(get_claude(), settings.anthropic_model)


class CiudadOut(BaseModel):
    slug: str
    nombre: str


class AlertaOut(BaseModel):
    tipo: str
    severidad: str
    mensaje_ciudadano: str
    mensaje_tecnico: str
    consejos: list[str]


class ResumenOut(BaseModel):
    ciudad: str
    temporada: str
    lluvia_activa: bool
    alertas: list[AlertaOut]


@router.get("/ciudades", response_model=list[CiudadOut])
def ciudades():
    return [CiudadOut(slug=s, nombre=n) for s, (n, _) in CIUDADES.items()]


@router.get("/alertas", response_model=ResumenOut)
async def alertas(
    ciudad: str,
    fuente: FuenteClima = Depends(get_fuente),
    traductor: TraductorCiudadano = Depends(get_traductor),
):
    if ciudad not in CIUDADES:
        raise HTTPException(404, "Ciudad no soportada")
    try:
        r = await use_cases.obtener_resumen(ciudad, fuente, traductor, settings.temporada_enso)
    except Exception as e:
        raise HTTPException(503, "El servicio de pronóstico no responde. Probá de nuevo en unos minutos.") from e
    return ResumenOut(
        ciudad=r.ciudad,
        temporada=r.temporada,
        lluvia_activa=r.lluvia_activa,
        alertas=[AlertaOut(tipo=a.tipo, severidad=a.severidad, mensaje_ciudadano=a.mensaje_ciudadano,
                           mensaje_tecnico=a.mensaje_tecnico, consejos=list(a.consejos)) for a in r.alertas],
    )
