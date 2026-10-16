from dataclasses import dataclass
from enum import StrEnum

from app.shared.geo import Punto
from app.shared.severidad import Severidad


class Temporada(StrEnum):
    EL_NINO = "EL_NINO"  # exceso de lluvia
    LA_NINA = "LA_NINA"  # calor y sequía
    NEUTRAL = "NEUTRAL"


class TipoAlerta(StrEnum):
    TORMENTA = "TORMENTA"
    LLUVIA_INTENSA = "LLUVIA_INTENSA"
    INCENDIO = "INCENDIO"
    CALOR = "CALOR"
    UV = "UV"


CIUDADES: dict[str, tuple[str, Punto]] = {
    "ciudad-del-este": ("Ciudad del Este", Punto(-25.5097, -54.6111)),
    "presidente-franco": ("Presidente Franco", Punto(-25.5622, -54.6111)),
    "hernandarias": ("Hernandarias", Punto(-25.4058, -54.6386)),
    "minga-guazu": ("Minga Guazú", Punto(-25.4833, -54.8000)),
}


@dataclass(frozen=True)
class Boletin:
    """Pronóstico de las próximas 6 horas para un punto."""

    precipitacion_mm: float  # acumulada
    prob_lluvia: int  # % máximo
    codigo_tiempo: int  # código WMO más severo
    rafagas_kmh: float
    temp_max: float
    indice_uv: float


@dataclass(frozen=True)
class Alerta:
    tipo: TipoAlerta
    severidad: Severidad
    mensaje_tecnico: str
    consejos: tuple[str, ...]
    mensaje_ciudadano: str = ""


@dataclass(frozen=True)
class ResumenClima:
    ciudad: str
    temporada: Temporada
    lluvia_activa: bool
    alertas: list[Alerta]
