from typing import Protocol

from app.modules.clima.domain import Alerta, Boletin
from app.shared.geo import Punto


class FuenteClima(Protocol):
    async def obtener(self, punto: Punto) -> Boletin: ...


class TraductorCiudadano(Protocol):
    async def traducir(self, alerta: Alerta, ciudad: str) -> str: ...
