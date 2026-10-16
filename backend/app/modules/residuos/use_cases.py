import asyncio
import logging
from collections.abc import Awaitable, Callable
from datetime import datetime, timedelta

from app.modules.residuos.domain import Categoria, Clasificacion, ReporteResiduo
from app.modules.residuos.ports import ClasificadorImagen, ReporteResiduoRepo
from app.modules.residuos.scoring import calcular_severidad
from app.shared.geo import Punto
from app.shared.http import LimiteExcedido

log = logging.getLogger(__name__)

LIMITE_POR_HORA = 10
DIAS_EN_MAPA = 30
SIN_CLASIFICAR = Clasificacion(Categoria.PENDIENTE, 0.0, "Pendiente de revisión: no se pudo clasificar la foto.")


async def crear_reporte(
    foto: bytes,
    media_type: str,
    punto: Punto,
    device_id: str,
    ahora: datetime,
    clasificador: ClasificadorImagen,
    repo: ReporteResiduoRepo,
    lluvia_activa: Callable[[Punto], Awaitable[bool]],
) -> ReporteResiduo:
    if await repo.contar_de_dispositivo(device_id, ahora - timedelta(hours=1)) >= LIMITE_POR_HORA:
        raise LimiteExcedido

    clasificacion, lluvia = await asyncio.gather(
        _clasificar(clasificador, foto, media_type), _lluvia(lluvia_activa, punto)
    )
    reporte = ReporteResiduo(
        punto=punto,
        device_id=device_id,
        categoria=clasificacion.categoria,
        confianza=clasificacion.confianza,
        descripcion=clasificacion.descripcion,
        severidad=calcular_severidad(clasificacion.categoria, clasificacion.confianza, lluvia),
        creado=ahora,
    )
    return await repo.guardar(reporte)


async def mapa(repo: ReporteResiduoRepo, ahora: datetime) -> list[ReporteResiduo]:
    return await repo.desde(ahora - timedelta(days=DIAS_EN_MAPA))


async def _clasificar(clasificador: ClasificadorImagen, foto: bytes, media_type: str) -> Clasificacion:
    # Si la IA falla, el reporte se guarda igual como PENDIENTE: nunca se pierde.
    try:
        return await clasificador.clasificar(foto, media_type)
    except Exception:
        log.exception("Fallo la clasificación de imagen")
        return SIN_CLASIFICAR


async def _lluvia(lluvia_activa: Callable[[Punto], Awaitable[bool]], punto: Punto) -> bool:
    try:
        return await lluvia_activa(punto)
    except Exception:
        log.exception("No se pudo consultar el pronóstico; se asume sin lluvia")
        return False
