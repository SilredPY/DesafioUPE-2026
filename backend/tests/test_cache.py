import asyncio

import pytest

from app.shared import cache


@pytest.fixture(autouse=True)
def limpio():
    cache.limpiar()


def test_pedidos_simultaneos_calculan_una_sola_vez():
    llamadas = 0

    async def lento():
        nonlocal llamadas
        llamadas += 1
        await asyncio.sleep(0.05)
        return "ok"

    async def main():
        return await asyncio.gather(*(cache.cacheado("k", 60, lento) for _ in range(30)))

    assert asyncio.run(main()) == ["ok"] * 30
    assert llamadas == 1


def test_vencido_o_borrado_se_recalcula():
    llamadas = 0

    async def crear():
        nonlocal llamadas
        llamadas += 1
        return llamadas

    async def main():
        a = await cache.cacheado("k", 60, crear)
        b = await cache.cacheado("k", 0, crear)  # ttl 0: lo guardado ya está vencido
        c = await cache.cacheado("k", 60, crear)
        cache.borrar("k")
        d = await cache.cacheado("k", 60, crear)
        return a, b, c, d

    assert asyncio.run(main()) == (1, 2, 2, 3)


def test_un_error_no_queda_guardado():
    intentos = 0

    async def falla_una_vez():
        nonlocal intentos
        intentos += 1
        if intentos == 1:
            raise RuntimeError("sin red")
        return "ok"

    async def main():
        with pytest.raises(RuntimeError):
            await cache.cacheado("k", 60, falla_una_vez)
        return await cache.cacheado("k", 60, falla_una_vez)

    assert asyncio.run(main()) == "ok"
