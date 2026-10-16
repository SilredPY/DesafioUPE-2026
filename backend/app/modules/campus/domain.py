from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from app.shared.geo import Punto


class TipoAviso(StrEnum):
    CLASES_SUSPENDIDAS = "CLASES_SUSPENDIDAS"
    CLASES_VIRTUALES = "CLASES_VIRTUALES"
    CLIMA = "CLIMA"
    TRANSITO = "TRANSITO"
    GENERAL = "GENERAL"


class Nivel(StrEnum):
    NORMAL = "NORMAL"
    PRECAUCION = "PRECAUCION"
    NO_SALIR = "NO_SALIR"
    SIN_CLASES = "SIN_CLASES"


@dataclass(frozen=True)
class Institucion:
    slug: str
    nombre: str
    ciudad: str
    punto: Punto
    radio_m: int = 1500  # zona de influencia para tránsito y residuos cercanos


@dataclass(frozen=True)
class Aviso:
    institucion: str
    tipo: TipoAviso
    titulo: str
    mensaje: str
    vigente_hasta: datetime
    creado: datetime
    id: str | None = None


@dataclass(frozen=True)
class Recomendacion:
    nivel: Nivel
    titulo: str
    texto: str
