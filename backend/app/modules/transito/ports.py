from datetime import datetime
from typing import Protocol

from app.modules.transito.domain import ReporteTransito


class ReporteTransitoRepo(Protocol):
    async def guardar(self, reporte: ReporteTransito) -> ReporteTransito: ...

    async def desde(self, desde: datetime) -> list[ReporteTransito]: ...

    async def contar_de_dispositivo(self, device_id: str, desde: datetime) -> int: ...
