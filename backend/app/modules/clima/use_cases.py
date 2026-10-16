import logging
from dataclasses import replace
from time import monotonic

from app.modules.clima.domain import CIUDADES, Alerta, ResumenClima, Temporada
from app.modules.clima.ports import FuenteClima, TraductorCiudadano
from app.modules.clima.reglas_estacionales import evaluar, hay_lluvia
from app.shared.geo import Punto

log = logging.getLogger(__name__)

# Evita llamar al pronóstico y a la IA en cada pedido de cada celular.
# shortcut: caché en memoria por proceso; pasar a Redis si se corre más de una réplica.
TTL_S = 600
_cache: dict[str, tuple[float, ResumenClima]] = {}


async def obtener_resumen(
    slug: str, fuente: FuenteClima, traductor: TraductorCiudadano, temporada: Temporada
) -> ResumenClima:
    hit = _cache.get(slug)
    if hit and monotonic() - hit[0] < TTL_S:
        return hit[1]

    nombre, punto = CIUDADES[slug]
    boletin = await fuente.obtener(punto)
    alertas = [await _traducir(a, nombre, traductor) for a in evaluar(boletin, temporada)]
    resumen = ResumenClima(nombre, temporada, hay_lluvia(boletin), alertas)
    _cache[slug] = (monotonic(), resumen)
    return resumen


async def _traducir(alerta: Alerta, ciudad: str, traductor: TraductorCiudadano) -> Alerta:
    try:
        mensaje = await traductor.traducir(alerta, ciudad)
    except Exception:
        # Sin IA la alerta igual tiene que llegar: usamos el texto técnico.
        log.exception("Fallo la traducción ciudadana de la alerta %s", alerta.tipo)
        mensaje = alerta.mensaje_tecnico
    return replace(alerta, mensaje_ciudadano=mensaje)


async def hay_lluvia_activa(punto: Punto, fuente: FuenteClima) -> bool:
    return hay_lluvia(await fuente.obtener(punto))
