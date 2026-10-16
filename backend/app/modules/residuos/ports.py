from datetime import datetime
from typing import Protocol

from app.modules.residuos.domain import Clasificacion, ReporteResiduo
from app.shared.geo import Punto


class ClasificadorImagen(Protocol):
    async def clasificar(self, foto: bytes, media_type: str) -> Clasificacion: ...


class ReporteResiduoRepo(Protocol):
    async def guardar(self, reporte: ReporteResiduo) -> ReporteResiduo: ...

    async def desde(self, desde: datetime) -> list[ReporteResiduo]: ...

    async def contar_de_dispositivo(self, device_id: str, desde: datetime) -> int: ...

    async def contar_criticos_cerca(self, punto: Punto, radio_m: int, desde: datetime) -> int: ...
