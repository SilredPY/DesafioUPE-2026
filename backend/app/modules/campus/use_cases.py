import asyncio
import re
import unicodedata
from dataclasses import dataclass
from datetime import datetime, timedelta

from app.modules.campus.domain import Aviso, Institucion, Recomendacion
from app.modules.campus.ports import CampusRepo
from app.modules.campus.recomendacion import recomendar
from app.modules.clima.domain import ResumenClima, Temporada
from app.modules.clima.ports import FuenteClima, TraductorCiudadano
from app.modules.clima.use_cases import resumen_en
from app.modules.residuos.ports import ReporteResiduoRepo
from app.modules.residuos.use_cases import DIAS_EN_MAPA
from app.modules.transito.domain import ZonaRoja
from app.modules.transito.ports import ReporteTransitoRepo
from app.modules.transito.use_cases import zonas_rojas
from app.shared.geo import distancia_m


class InstitucionDuplicada(Exception):
    pass


@dataclass(frozen=True)
class EstadoCampus:
    institucion: Institucion
    clima: ResumenClima
    zonas_rojas: list[ZonaRoja]
    residuos_criticos: int
    avisos: list[Aviso]
    recomendacion: Recomendacion


def slugificar(texto: str) -> str:
    ascii_ = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", ascii_.lower()).strip("-")[:60]


async def estado(
    inst: Institucion,
    ahora: datetime,
    repo: CampusRepo,
    fuente: FuenteClima,
    traductor: TraductorCiudadano,
    temporada: Temporada,
    transito: ReporteTransitoRepo,
    residuos: ReporteResiduoRepo,
) -> EstadoCampus:
    # El clima (red + IA) corre en paralelo con la base. Las consultas a la base van en serie:
    # comparten la misma AsyncSession, que no admite consultas concurrentes.
    clima_t = asyncio.create_task(
        resumen_en(f"campus:{inst.slug}", inst.nombre, inst.punto, fuente, traductor, temporada)
    )
    zonas = await zonas_rojas(transito, ahora)
    criticos = await residuos.contar_criticos_cerca(inst.punto, inst.radio_m, ahora - timedelta(days=DIAS_EN_MAPA))
    avisos = await repo.avisos_vigentes(inst.slug, ahora)
    clima = await clima_t
    cerca = [z for z in zonas if distancia_m(z.centro, inst.punto) <= inst.radio_m]
    return EstadoCampus(
        inst, clima, cerca, criticos, avisos,
        recomendar([a.severidad for a in clima.alertas], len(cerca), avisos),
    )


async def crear_institucion(i: Institucion, repo: CampusRepo) -> Institucion:
    if await repo.institucion(i.slug):
        raise InstitucionDuplicada
    return await repo.crear_institucion(i)
