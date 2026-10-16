from dataclasses import replace
from datetime import datetime

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.transito.domain import ReporteTransito, TipoIncidente
from app.shared.geo import Punto


class ReporteTransitoPg:
    def __init__(self, session: AsyncSession):
        self._s = session

    async def guardar(self, r: ReporteTransito) -> ReporteTransito:
        res = await self._s.execute(
            text("""
                INSERT INTO reportes_transito (ubicacion, tipo, device_id, creado)
                VALUES (ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)::geography, :tipo, :device_id, :creado)
                RETURNING id
            """),
            {"lon": r.punto.lon, "lat": r.punto.lat, "tipo": r.tipo, "device_id": r.device_id, "creado": r.creado},
        )
        await self._s.commit()
        return replace(r, id=str(res.scalar_one()))

    async def desde(self, desde: datetime) -> list[ReporteTransito]:
        res = await self._s.execute(
            text("""
                SELECT id, ST_Y(ubicacion::geometry) AS lat, ST_X(ubicacion::geometry) AS lon, tipo, device_id, creado
                FROM reportes_transito WHERE creado >= :desde
            """),
            {"desde": desde},
        )
        return [ReporteTransito(Punto(f.lat, f.lon), TipoIncidente(f.tipo), f.device_id, f.creado, str(f.id))
                for f in res]

    async def contar_de_dispositivo(self, device_id: str, desde: datetime) -> int:
        res = await self._s.execute(
            text("SELECT count(*) FROM reportes_transito WHERE device_id = :d AND creado >= :desde"),
            {"d": device_id, "desde": desde},
        )
        return res.scalar_one()
