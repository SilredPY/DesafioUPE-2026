"""Caché en memoria con vencimiento. Si muchos pedidos llegan juntos por la misma clave, se calcula una sola vez."""

import asyncio
from collections.abc import Awaitable, Callable
from time import monotonic

# shortcut: caché en memoria por proceso; pasar a Redis si se corre más de una réplica de la API.
_valores: dict[str, tuple[float, object]] = {}
_candados: dict[str, asyncio.Lock] = {}


def _vigente(clave: str, ttl_s: float) -> tuple[float, object] | None:
    hit = _valores.get(clave)
    return hit if hit and monotonic() - hit[0] < ttl_s else None


async def cacheado[T](clave: str, ttl_s: float, crear: Callable[[], Awaitable[T]]) -> T:
    """Devuelve el valor guardado o lo calcula con `crear`. Un error no se guarda: el próximo pedido reintenta."""
    if hit := _vigente(clave, ttl_s):
        return hit[1]
    async with _candados.setdefault(clave, asyncio.Lock()):
        if hit := _vigente(clave, ttl_s):  # otro pedido lo calculó mientras este esperaba
            return hit[1]
        valor = await crear()
        _valores[clave] = (monotonic(), valor)
        return valor


def borrar(clave: str) -> None:
    _valores.pop(clave, None)


def limpiar() -> None:
    _valores.clear()
    _candados.clear()
