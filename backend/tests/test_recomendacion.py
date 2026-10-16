from datetime import UTC, datetime

from app.modules.campus.domain import Aviso, Nivel, TipoAviso
from app.modules.campus.recomendacion import recomendar
from app.modules.campus.use_cases import slugificar
from app.shared.severidad import Severidad as S

AHORA = datetime(2026, 10, 16, tzinfo=UTC)


def aviso(tipo):
    return Aviso("upe", tipo, "t", "m", AHORA, AHORA)


def test_sin_novedades_es_normal():
    assert recomendar([], 0, []).nivel == Nivel.NORMAL


def test_aviso_de_suspension_gana_sobre_todo():
    r = recomendar([S.CRITICO], 3, [aviso(TipoAviso.GENERAL), aviso(TipoAviso.CLASES_SUSPENDIDAS)])
    assert r.nivel == Nivel.SIN_CLASES and "suspend" in r.titulo.lower()


def test_clases_virtuales():
    assert recomendar([S.CRITICO], 0, [aviso(TipoAviso.CLASES_VIRTUALES)]).titulo == "Clases virtuales"


def test_clima_critico_recomienda_no_salir():
    assert recomendar([S.ALTO, S.CRITICO], 0, []).nivel == Nivel.NO_SALIR


def test_zona_roja_cerca_pide_precaucion():
    r = recomendar([], 2, [])
    assert r.nivel == Nivel.PRECAUCION and "2 zona(s) roja(s)" in r.texto


def test_aviso_informativo_no_cambia_el_nivel():
    assert recomendar([], 0, [aviso(TipoAviso.CLIMA)]).nivel == Nivel.NORMAL


def test_slugificar():
    assert slugificar("Universidad Nacional del Este — Facultad Politécnica") == \
        "universidad-nacional-del-este-facultad-politecnica"
    assert slugificar("¡¡!!") == ""
