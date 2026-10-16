"""Recorre la API completa con adaptadores falsos: sin red, sin Claude, sin base de datos."""

from dataclasses import replace

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.modules.campus import api as campus_api
from app.modules.campus.domain import Institucion
from app.modules.clima import api as clima_api
from app.modules.clima.domain import Boletin
from app.modules.residuos import api as residuos_api
from app.modules.residuos.domain import Categoria, Clasificacion
from app.modules.transito import api as transito_api
from app.shared import cache
from app.shared.geo import Punto, distancia_m

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

    async def contar_criticos_cerca(self, punto, radio_m, desde):
        return sum(r.severidad == "CRITICO" and r.creado >= desde and distancia_m(r.punto, punto) <= radio_m
                   for r in self.items)


UPE = Institucion("upe-presidente-franco", "UPE Sede Presidente Franco", "Presidente Franco", Punto(-25.5560, -54.6110))


class CampusMem:
    def __init__(self):
        self.inst = {UPE.slug: UPE}
        self.avisos = []

    async def instituciones(self):
        return list(self.inst.values())

    async def institucion(self, slug):
        return self.inst.get(slug)

    async def crear_institucion(self, i):
        self.inst[i.slug] = i
        return i

    async def avisos_vigentes(self, slug, ahora):
        return [a for a in self.avisos if a.institucion == slug and a.vigente_hasta > ahora]

    async def crear_aviso(self, a):
        a = replace(a, id=str(len(self.avisos) + 1))
        self.avisos.append(a)
        return a


TOKEN = "token-de-prueba-123"


@pytest.fixture
def client(monkeypatch):
    cache.limpiar()
    monkeypatch.setattr(campus_api.settings, "admin_token", TOKEN)
    repo_residuos, repo_transito, repo_campus = RepoMem(), RepoMem(), CampusMem()
    app.dependency_overrides = {
        clima_api.get_fuente: FuenteFake,
        clima_api.get_traductor: TraductorFake,
        residuos_api.get_clasificador: ClasificadorFake,
        residuos_api.get_repo: lambda: repo_residuos,
        transito_api.get_repo: lambda: repo_transito,
        campus_api.get_repo: lambda: repo_campus,
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


def test_modo_demo_tormenta_sin_red(client, monkeypatch):
    monkeypatch.setattr(clima_api.settings, "clima_demo", "tormenta")
    del app.dependency_overrides[clima_api.get_fuente]  # usar la fuente real configurada
    body = client.get("/api/clima/alertas", params={"ciudad": "minga-guazu"}).json()
    assert body["lluvia_activa"] and {"TORMENTA", "LLUVIA_INTENSA"} <= {a["tipo"] for a in body["alertas"]}


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


def admin_h():
    return {"X-Admin-Token": TOKEN}


def test_campus_upe_incluida_y_estado_con_tormenta(client):
    assert [i["slug"] for i in client.get("/api/campus/instituciones").json()] == ["upe-presidente-franco"]
    e = client.get("/api/campus/upe-presidente-franco/estado").json()
    assert e["recomendacion"]["nivel"] == "PRECAUCION"  # la fuente falsa trae tormenta de nivel ALTO
    assert e["alertas"][0]["mensaje_ciudadano"].startswith("Oĩ la peligro")


def test_campus_zona_roja_cercana_y_lejana(client):
    for i in range(3):  # raudal a ~100 m del campus
        client.post("/api/transito/reportes", json={"tipo": "RAUDAL", "lat": -25.5551, "lon": -54.6110},
                    headers=h(f"vecino-00{i}"))
    for i in range(3):  # raudal en Hernandarias, lejos
        client.post("/api/transito/reportes", json={"tipo": "RAUDAL", "lat": -25.4058, "lon": -54.6386},
                    headers=h(f"vecino-10{i}"))
    e = client.get("/api/campus/upe-presidente-franco/estado").json()
    assert len(e["zonas_rojas"]) == 1


def test_publicar_aviso_requiere_token(client):
    aviso = {"tipo": "CLASES_SUSPENDIDAS", "titulo": "Sin clases", "mensaje": "Suspendidas por tormenta"}
    assert client.post("/api/campus/upe-presidente-franco/avisos", json=aviso).status_code == 401
    assert client.post("/api/campus/upe-presidente-franco/avisos", json=aviso,
                       headers={"X-Admin-Token": "otro"}).status_code == 401
    assert client.post("/api/campus/upe-presidente-franco/avisos", json=aviso, headers=admin_h()).status_code == 201
    e = client.get("/api/campus/upe-presidente-franco/estado").json()
    assert e["recomendacion"]["nivel"] == "SIN_CLASES" and e["avisos"][0]["titulo"] == "Sin clases"


def test_admin_deshabilitado_sin_token_configurado(client, monkeypatch):
    monkeypatch.setattr(campus_api.settings, "admin_token", "")
    nueva = {"nombre": "Facultad Politécnica UNE", "ciudad": "Ciudad del Este", "lat": -25.50, "lon": -54.62}
    assert client.post("/api/campus/instituciones", json=nueva, headers=admin_h()).status_code == 403


def test_agregar_institucion(client):
    nueva = {"nombre": "Facultad Politécnica UNE", "ciudad": "Ciudad del Este", "lat": -25.50, "lon": -54.62}
    r = client.post("/api/campus/instituciones", json=nueva, headers=admin_h())
    assert r.status_code == 201 and r.json()["slug"] == "facultad-politecnica-une"
    assert client.post("/api/campus/instituciones", json=nueva, headers=admin_h()).status_code == 409
    assert client.get("/api/campus/facultad-politecnica-une/estado").status_code == 200
    fuera = {**nueva, "nombre": "Colegio en Asunción", "lat": -25.26, "lon": -57.57}
    assert client.post("/api/campus/instituciones", json=fuera, headers=admin_h()).status_code == 422


def test_institucion_inexistente(client):
    assert client.get("/api/campus/no-existe/estado").status_code == 404


def test_salud_informa_motor(client):
    assert client.get("/api/salud").json()["motor_agrupacion"] in ("c++", "python")


def test_campus_cuenta_residuos_criticos_solo_cerca(client):
    foto = {"foto": ("f.jpg", JPEG, "image/jpeg")}
    cerca = {"lat": -25.5570, "lon": -54.6115}  # ~120 m de la UPE
    client.post("/api/residuos/reportes", data=cerca, files=foto, headers=h("vecino-0001"))
    client.post("/api/residuos/reportes", data=CDE, files=foto, headers=h("vecino-0002"))  # ~5 km
    assert client.get("/api/campus/upe-presidente-franco/estado").json()["residuos_criticos"] == 1
