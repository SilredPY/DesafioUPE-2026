import asyncio
import logging
from dataclasses import replace

from app.modules.clima.domain import CIUDADES, Alerta, ResumenClima, Temporada
from app.modules.clima.ports import FuenteClima, TraductorCiudadano
from app.modules.clima.domain import Boletin
from app.modules.clima.reglas_estacionales import evaluar, hay_lluvia
from app.shared.cache import cacheado
from app.shared.geo import Punto

log = logging.getLogger(__name__)

# Evita llamar al pronóstico y a la IA en cada pedido de cada celular.
TTL_S = 600


async def obtener_resumen(
    slug: str, fuente: FuenteClima, traductor: TraductorCiudadano, temporada: Temporada
) -> ResumenClima:
    nombre, punto = CIUDADES[slug]
    return await resumen_en(slug, nombre, punto, fuente, traductor, temporada)


async def resumen_en(
    clave: str, nombre: str, punto: Punto, fuente: FuenteClima, traductor: TraductorCiudadano, temporada: Temporada
) -> ResumenClima:
    """Resumen para cualquier lugar (ciudad o campus); `clave` identifica la entrada en caché."""

    async def crear() -> ResumenClima:
        boletin = await _boletin(punto, fuente)
        alertas = list(await asyncio.gather(*(_traducir(a, nombre, traductor) for a in evaluar(boletin, temporada))))
        return ResumenClima(nombre, temporada, hay_lluvia(boletin), alertas)

    return await cacheado(f"resumen:{clave}", TTL_S, crear)


async def _boletin(punto: Punto, fuente: FuenteClima) -> Boletin:
    # Redondeado a ~1 km: los reportes de un mismo barrio comparten una sola consulta al pronóstico.
    return await cacheado(f"boletin:{punto.lat:.2f},{punto.lon:.2f}", TTL_S, lambda: fuente.obtener(punto))


async def _traducir(alerta: Alerta, ciudad: str, traductor: TraductorCiudadano) -> Alerta:
    try:
        mensaje = await traductor.traducir(alerta, ciudad)
    except Exception:
        # Sin IA la alerta igual tiene que llegar: usamos el texto técnico.
        log.exception("Fallo la traducción ciudadana de la alerta %s", alerta.tipo)
        mensaje = alerta.mensaje_tecnico
    return replace(alerta, mensaje_ciudadano=mensaje)


async def hay_lluvia_activa(punto: Punto, fuente: FuenteClima) -> bool:
    return hay_lluvia(await _boletin(punto, fuente))
