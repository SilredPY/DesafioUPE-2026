from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.modules.clima.api import router as clima
from app.modules.residuos.api import router as residuos
from app.modules.transito.api import router as transito
from app.shared.geo import FueraDeZona
from app.shared.http import LimiteExcedido

app = FastAPI(title="Ñangarekó IA", description="Clima, residuos y tránsito preventivo para Alto Paraná")
app.add_middleware(GZipMiddleware, minimum_size=1000)  # el mapa con miles de reportes pesa menos en datos móviles
app.add_middleware(
    CORSMiddleware, allow_origins=settings.cors_origins, allow_methods=["GET", "POST"], allow_headers=["*"]
)

for router in (clima, residuos, transito):
    app.include_router(router, prefix="/api")


@app.exception_handler(FueraDeZona)
async def fuera_de_zona(_: Request, e: FueraDeZona):
    return JSONResponse({"detail": str(e)}, status_code=422)


@app.exception_handler(LimiteExcedido)
async def limite_excedido(_: Request, __: LimiteExcedido):
    return JSONResponse({"detail": "Demasiados reportes en la última hora. Probá más tarde."}, status_code=429)


@app.get("/api/salud")
def salud():
    return {"ok": True}
