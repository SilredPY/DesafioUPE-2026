"""Recorre la API completa con adaptadores falsos: sin red, sin Claude, sin base de datos."""

from dataclasses import replace

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.modules.clima import api as clima_api
from app.modules.clima import use_cases as clima_uc
from app.modules.clima.domain import Boletin
from app.modules.residuos import api as residuos_api
from app.modules.residuos.domain import Categoria, Clasificacion
from app.modules.transito import api as transito_api

TORMENTA = Boletin(precipitacion_mm=40, prob_lluvia=95, codigo_tiempo=95, rafagas_kmh=70, temp_max=27, indice_uv=3)
JPEG = b"\xff\xd8\xff\xe0" + b"\x00" * 64
CDE = {"lat": -25.5097, "lon": -54.6111}


class FuenteFake:
    async def obtener(self, punto):
        return TORMENTA


class TraductorFake:
    async def traducir(self, alerta, ciudad):
        return f"Oĩ la peligro en {ciudad}"


class TraductorRoto:
    async def traducir(self, alerta, ciudad):
        raise RuntimeError("sin IA")


class ClasificadorFake:
    async def clasificar(self, foto, media_type):
        return Clasificacion(Categoria.SUMIDERO_BLOQUEADO, 0.9, "Rejilla tapada con bolsas")


class RepoMem:
    def __init__(self):
        self.items = []

    async def guardar(self, r):
        r = replace(r, id=str(len(self.items) + 1))
        self.items.append(r)
        return r

    async def desde(self, desde):
        return [r for r in self.items if r.creado >= desde]

    async def contar_de_dispositivo(self, device_id, desde):
        return sum(r.device_id == device_id and r.creado >= desde for r in self.items)


@pytest.fixture
def client():
    clima_uc._cache.clear()
    repo_residuos, repo_transito = RepoMem(), RepoMem()
    app.dependency_overrides = {
        clima_api.get_fuente: FuenteFake,
        clima_api.get_traductor: TraductorFake,
        residuos_api.get_clasificador: ClasificadorFake,
        residuos_api.get_repo: lambda: repo_residuos,
        transito_api.get_repo: lambda: repo_transito,
    }
    yield TestClient(app)
    app.dependency_overrides = {}


def h(device="dev-0001"):
    return {"X-Device-Id": device}


def test_alertas_traducidas(client):
    r = client.get("/api/clima/alertas", params={"ciudad": "presidente-franco"})
    assert r.status_code == 200
    body = r.json()
    assert body["lluvia_activa"] is True
    tormenta = next(a for a in body["alertas"] if a["tipo"] == "TORMENTA")
    assert tormenta["mensaje_ciudadano"] == "Oĩ la peligro en Presidente Franco"


def test_alerta_llega_aunque_falle_la_ia(client):
    app.dependency_overrides[clima_api.get_traductor] = TraductorRoto
    a = client.get("/api/clima/alertas", params={"ciudad": "hernandarias"}).json()["alertas"][0]
    assert a["mensaje_ciudadano"] == a["mensaje_tecnico"]


def test_ciudad_desconocida(client):
    assert client.get("/api/clima/alertas", params={"ciudad": "asuncion"}).status_code == 404


def test_sumidero_con_tormenta_es_critico_y_aparece_en_mapa(client):
    r = client.post("/api/residuos/reportes", data=CDE, files={"foto": ("f.jpg", JPEG, "image/jpeg")}, headers=h())
    assert r.status_code == 201, r.text
    assert (r.json()["categoria"], r.json()["severidad"]) == ("SUMIDERO_BLOQUEADO", "CRITICO")
    mapa = client.get("/api/residuos/mapa").json()
    assert len(mapa) == 1 and "device_id" not in mapa[0]


def test_rechaza_archivo_que_no_es_imagen(client):
    r = client.post("/api/residuos/reportes", data=CDE, files={"foto": ("x.jpg", b"<script>", "image/jpeg")}, headers=h())
    assert r.status_code == 415


def test_rechaza_ubicacion_fuera_de_zona(client):
    asuncion = {"lat": -25.2637, "lon": -57.5759}
    r = client.post("/api/transito/reportes", json={"tipo": "RAUDAL", **asuncion}, headers=h())
    assert r.status_code == 422


def test_exige_device_id(client):
    assert client.post("/api/transito/reportes", json={"tipo": "RAUDAL", **CDE}).status_code == 422


def test_limite_de_reportes_por_hora(client):
    for _ in range(20):
        client.post("/api/transito/reportes", json={"tipo": "BACHE", **CDE}, headers=h())
    assert client.post("/api/transito/reportes", json={"tipo": "BACHE", **CDE}, headers=h()).status_code == 429


def test_tres_vecinos_marcan_zona_roja(client):
    for i in range(3):
        r = client.post("/api/transito/reportes", json={"tipo": "RAUDAL", **CDE}, headers=h(f"vecino-00{i}"))
        assert r.status_code == 201
    zonas = client.get("/api/transito/zonas-rojas").json()
    assert [(z["tipo"], z["dispositivos"]) for z in zonas] == [("RAUDAL", 3)]


def test_calendario(client):
    cal = client.get("/api/residuos/calendario").json()
    assert cal and {"barrio", "ciudad", "dias", "hora", "proximo_paso"} <= cal[0].keys()
