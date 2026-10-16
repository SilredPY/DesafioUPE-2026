from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from app.shared.geo import Punto
from app.shared.severidad import Severidad


class Categoria(StrEnum):
    VERTEDERO_CLANDESTINO = "VERTEDERO_CLANDESTINO"  # basura acumulada en terrenos o vía pública
    SUMIDERO_BLOQUEADO = "SUMIDERO_BLOQUEADO"  # residuos tapando desagües pluviales
    OBSTRUCCION_VIAL = "OBSTRUCCION_VIAL"  # restos o escombros bloqueando la calle
    PENDIENTE = "PENDIENTE"  # la IA no pudo clasificar o la foto no aplica: requiere revisión


@dataclass(frozen=True)
class Clasificacion:
    categoria: Categoria
    confianza: float
    descripcion: str


@dataclass(frozen=True)
class ReporteResiduo:
    punto: Punto
    device_id: str
    categoria: Categoria
    confianza: float
    descripcion: str
    severidad: Severidad
    creado: datetime
    id: str | None = None
