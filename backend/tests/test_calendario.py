from datetime import UTC, datetime, time

from app.modules.residuos.calendario import HORA_PY, RecorridoBarrio, proximo_paso, recorridos

LUN_MIE_VIE = RecorridoBarrio("Centro", "Presidente Franco", (0, 2, 4), time(6, 30))


def test_mismo_dia_antes_de_la_hora():
    lunes_5am = datetime(2026, 10, 12, 5, 0, tzinfo=HORA_PY)
    assert proximo_paso(LUN_MIE_VIE, lunes_5am) == datetime(2026, 10, 12, 6, 30, tzinfo=HORA_PY)


def test_despues_de_la_hora_salta_al_siguiente_dia_de_recorrido():
    lunes_7am = datetime(2026, 10, 12, 7, 0, tzinfo=HORA_PY)
    assert proximo_paso(LUN_MIE_VIE, lunes_7am) == datetime(2026, 10, 14, 6, 30, tzinfo=HORA_PY)


def test_viernes_tarde_pasa_al_lunes():
    viernes_noche = datetime(2026, 10, 16, 22, 0, tzinfo=HORA_PY)
    assert proximo_paso(LUN_MIE_VIE, viernes_noche) == datetime(2026, 10, 19, 6, 30, tzinfo=HORA_PY)


def test_convierte_utc_a_hora_paraguaya():
    # 09:00 UTC = 06:00 en Paraguay: todavía no pasó el camión de las 06:30
    assert proximo_paso(LUN_MIE_VIE, datetime(2026, 10, 12, 9, 0, tzinfo=UTC)).day == 12


def test_datos_de_ejemplo_cargan():
    assert recorridos()
