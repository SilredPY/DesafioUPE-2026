from dataclasses import replace
from datetime import datetime

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.residuos.domain import Categoria, ReporteResiduo
from app.shared.geo import Punto
from app.shared.severidad import Severidad

LIMITE_MAPA = 2000


class ReporteResiduoPg:
    def __init__(self, session: AsyncSession):
        self._s = session

    async def guardar(self, r: ReporteResiduo) -> ReporteResiduo:
        res = await self._s.execute(
            text("""
                INSERT INTO reportes_residuos (ubicacion, device_id, categoria, confianza, descripcion, severidad, creado)
                VALUES (ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)::geography,
                        :device_id, :categoria, :confianza, :descripcion, :severidad, :creado)
                RETURNING id
            """),
            {"lon": r.punto.lon, "lat": r.punto.lat, "device_id": r.device_id, "categoria": r.categoria,
             "confianza": r.confianza, "descripcion": r.descripcion, "severidad": r.severidad, "creado": r.creado},
        )
        await self._s.commit()
        return replace(r, id=str(res.scalar_one()))

    async def desde(self, desde: datetime) -> list[ReporteResiduo]:
        res = await self._s.execute(
            text("""
                SELECT id, ST_Y(ubicacion::geometry) AS lat, ST_X(ubicacion::geometry) AS lon, device_id,
                       categoria, confianza, descripcion, severidad, creado
                FROM reportes_residuos WHERE creado >= :desde
                ORDER BY creado DESC LIMIT :limite
            """),
            {"desde": desde, "limite": LIMITE_MAPA},
        )
        return [
            ReporteResiduo(Punto(f.lat, f.lon), f.device_id, Categoria(f.categoria), f.confianza,
                           f.descripcion, Severidad(f.severidad), f.creado, str(f.id))
            for f in res
        ]

    async def contar_criticos_cerca(self, punto: Punto, radio_m: int, desde: datetime) -> int:
        # ST_DWithin sobre geography usa el índice GiST: no recorre toda la tabla.
        res = await self._s.execute(
            text("""
                SELECT count(*) FROM reportes_residuos
                WHERE severidad = 'CRITICO' AND creado >= :desde
                  AND ST_DWithin(ubicacion, ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)::geography, :radio)
            """),
            {"desde": desde, "lon": punto.lon, "lat": punto.lat, "radio": radio_m},
        )
        return res.scalar_one()

    async def contar_de_dispositivo(self, device_id: str, desde: datetime) -> int:
        res = await self._s.execute(
            text("SELECT count(*) FROM reportes_residuos WHERE device_id = :d AND creado >= :desde"),
            {"d": device_id, "desde": desde},
        )
        return res.scalar_one()
