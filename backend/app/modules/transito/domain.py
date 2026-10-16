from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from app.shared.geo import Punto


class TipoIncidente(StrEnum):
    RAUDAL = "RAUDAL"  # raudal peligroso / calle intransitable
    SEMAFORO_CABLE = "SEMAFORO_CABLE"  # semáforo fuera de servicio / cable caído
    BACHE = "BACHE"  # bache ciego u obstrucción por agua


@dataclass(frozen=True)
class ReporteTransito:
    punto: Punto
    tipo: TipoIncidente
    device_id: str
    creado: datetime
    id: str | None = None


@dataclass(frozen=True)
class ZonaRoja:
    tipo: TipoIncidente
    centro: Punto
    reportes: int
    dispositivos: int
    ultimo: datetime
