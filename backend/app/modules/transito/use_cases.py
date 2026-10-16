from datetime import datetime, timedelta

from app.modules.transito.agrupacion import VENTANA, agrupar
from app.modules.transito.domain import ReporteTransito, TipoIncidente, ZonaRoja
from app.modules.transito.ports import ReporteTransitoRepo
from app.shared.geo import Punto
from app.shared.http import LimiteExcedido

LIMITE_POR_HORA = 20


async def reportar(
    punto: Punto, tipo: TipoIncidente, device_id: str, ahora: datetime, repo: ReporteTransitoRepo
) -> ReporteTransito:
    if await repo.contar_de_dispositivo(device_id, ahora - timedelta(hours=1)) >= LIMITE_POR_HORA:
        raise LimiteExcedido
    return await repo.guardar(ReporteTransito(punto, tipo, device_id, ahora))


async def zonas_rojas(repo: ReporteTransitoRepo, ahora: datetime) -> list[ZonaRoja]:
    return agrupar(await repo.desde(ahora - VENTANA))
