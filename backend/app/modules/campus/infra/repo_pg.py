from dataclasses import replace
from datetime import datetime

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.campus.domain import Aviso, Institucion, TipoAviso
from app.shared.geo import Punto

_SELECT_INST = """
    SELECT slug, nombre, ciudad, ST_Y(ubicacion::geometry) AS lat, ST_X(ubicacion::geometry) AS lon, radio_m
    FROM instituciones
"""


def _inst(f) -> Institucion:
    return Institucion(f.slug, f.nombre, f.ciudad, Punto(f.lat, f.lon), f.radio_m)


class CampusPg:
    def __init__(self, session: AsyncSession):
        self._s = session

    async def instituciones(self) -> list[Institucion]:
        return [_inst(f) for f in await self._s.execute(text(_SELECT_INST + " ORDER BY nombre"))]

    async def institucion(self, slug: str) -> Institucion | None:
        f = (await self._s.execute(text(_SELECT_INST + " WHERE slug = :s"), {"s": slug})).first()
        return _inst(f) if f else None

    async def crear_institucion(self, i: Institucion) -> Institucion:
        await self._s.execute(
            text("""
                INSERT INTO instituciones (slug, nombre, ciudad, ubicacion, radio_m)
                VALUES (:slug, :nombre, :ciudad, ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)::geography, :radio)
            """),
            {"slug": i.slug, "nombre": i.nombre, "ciudad": i.ciudad, "lon": i.punto.lon, "lat": i.punto.lat,
             "radio": i.radio_m},
        )
        await self._s.commit()
        return i

    async def avisos_vigentes(self, slug: str, ahora: datetime) -> list[Aviso]:
        res = await self._s.execute(
            text("""
                SELECT id, institucion, tipo, titulo, mensaje, vigente_hasta, creado FROM avisos
                WHERE institucion = :s AND vigente_hasta > :ahora ORDER BY creado DESC LIMIT 20
            """),
            {"s": slug, "ahora": ahora},
        )
        return [Aviso(f.institucion, TipoAviso(f.tipo), f.titulo, f.mensaje, f.vigente_hasta, f.creado, str(f.id))
                for f in res]

    async def crear_aviso(self, a: Aviso) -> Aviso:
        res = await self._s.execute(
            text("""
                INSERT INTO avisos (institucion, tipo, titulo, mensaje, vigente_hasta, creado)
                VALUES (:inst, :tipo, :titulo, :mensaje, :hasta, :creado) RETURNING id
            """),
            {"inst": a.institucion, "tipo": a.tipo, "titulo": a.titulo, "mensaje": a.mensaje,
             "hasta": a.vigente_hasta, "creado": a.creado},
        )
        await self._s.commit()
        return replace(a, id=str(res.scalar_one()))
