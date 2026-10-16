from datetime import UTC, datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.transito import use_cases
from app.modules.transito.domain import TipoIncidente
from app.modules.transito.infra.repo_pg import ReporteTransitoPg
from app.modules.transito.ports import ReporteTransitoRepo
from app.shared.db import get_session
from app.shared.geo import Punto
from app.shared.http import device_id

router = APIRouter(prefix="/transito", tags=["Tape Ysyry"])


def get_repo(session: AsyncSession = Depends(get_session)) -> ReporteTransitoRepo:
    return ReporteTransitoPg(session)


class ReporteIn(BaseModel):
    tipo: TipoIncidente
    lat: float
    lon: float


class ReporteOut(BaseModel):
    id: str | None
    tipo: TipoIncidente


class ZonaRojaOut(BaseModel):
    tipo: TipoIncidente
    lat: float
    lon: float
    reportes: int
    dispositivos: int
    ultimo: datetime


@router.post("/reportes", response_model=ReporteOut, status_code=201)
async def reportar(body: ReporteIn, device: str = Depends(device_id), repo: ReporteTransitoRepo = Depends(get_repo)):
    r = await use_cases.reportar(Punto(body.lat, body.lon), body.tipo, device, datetime.now(UTC), repo)
    return ReporteOut(id=r.id, tipo=r.tipo)


@router.get("/zonas-rojas", response_model=list[ZonaRojaOut])
async def zonas_rojas(repo: ReporteTransitoRepo = Depends(get_repo)):
    return [
        ZonaRojaOut(tipo=z.tipo, lat=z.centro.lat, lon=z.centro.lon, reportes=z.reportes,
                    dispositivos=z.dispositivos, ultimo=z.ultimo)
        for z in await use_cases.zonas_rojas(repo, datetime.now(UTC))
    ]
