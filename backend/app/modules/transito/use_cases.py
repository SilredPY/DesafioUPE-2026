from datetime import datetime, timedelta

from app.modules.transito.agrupacion import VENTANA, agrupar
from app.modules.transito.domain import ReporteTransito, TipoIncidente, ZonaRoja
from app.modules.transito.ports import ReporteTransitoRepo
from app.shared import cache
from app.shared.geo import Punto
from app.shared.http import LimiteExcedido

LIMITE_POR_HORA = 20
# Muchos celulares miran el mapa a la vez; agrupar una vez cada 30 s alcanza. Un reporte nuevo la invalida.
TTL_ZONAS_S = 30
_CLAVE_ZONAS = "transito:zonas-rojas"


async def reportar(
    punto: Punto, tipo: TipoIncidente, device_id: str, ahora: datetime, repo: ReporteTransitoRepo
) -> ReporteTransito:
    if await repo.contar_de_dispositivo(device_id, ahora - timedelta(hours=1)) >= LIMITE_POR_HORA:
        raise LimiteExcedido
    r = await repo.guardar(ReporteTransito(punto, tipo, device_id, ahora))
    cache.borrar(_CLAVE_ZONAS)
    return r


async def zonas_rojas(repo: ReporteTransitoRepo, ahora: datetime) -> list[ZonaRoja]:
    async def crear() -> list[ZonaRoja]:
        return agrupar(await repo.desde(ahora - VENTANA))

    return await cache.cacheado(_CLAVE_ZONAS, TTL_ZONAS_S, crear)
