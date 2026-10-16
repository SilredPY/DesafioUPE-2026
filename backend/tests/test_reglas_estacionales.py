from app.modules.clima.domain import Boletin
from app.modules.clima.domain import Temporada as Tp
from app.modules.clima.domain import TipoAlerta as A
from app.modules.clima.reglas_estacionales import evaluar, hay_lluvia
from app.shared.severidad import Severidad as S

CALMO = Boletin(precipitacion_mm=0, prob_lluvia=5, codigo_tiempo=1, rafagas_kmh=15, temp_max=28, indice_uv=6)


def b(**kw):
    return Boletin(**{**CALMO.__dict__, **kw})


def tipos(alertas):
    return {a.tipo: a for a in alertas}


def test_dia_calmo_sin_alertas():
    assert evaluar(CALMO, Tp.NEUTRAL) == []
    assert not hay_lluvia(CALMO)


def test_tormenta_con_granizo_es_critica():
    a = tipos(evaluar(b(codigo_tiempo=96, prob_lluvia=90), Tp.NEUTRAL))[A.TORMENTA]
    assert a.severidad == S.CRITICO
    assert "Desenchufá" in a.consejos[0]


def test_el_nino_baja_el_umbral_de_lluvia_y_menciona_arroyos():
    lluvia = b(precipitacion_mm=25, prob_lluvia=80)
    assert A.LLUVIA_INTENSA not in tipos(evaluar(lluvia, Tp.NEUTRAL))
    a = tipos(evaluar(lluvia, Tp.EL_NINO))[A.LLUVIA_INTENSA]
    assert any("Acaray" in c and "Monday" in c for c in a.consejos)


def test_la_nina_calor_seco_alerta_incendio():
    a = tipos(evaluar(b(temp_max=39, prob_lluvia=5), Tp.LA_NINA))
    assert a[A.INCENDIO].severidad == S.CRITICO
    assert A.CALOR not in a


def test_calor_extremo_fuera_de_la_nina_es_alerta_de_calor():
    assert A.CALOR in tipos(evaluar(b(temp_max=39), Tp.NEUTRAL))


def test_umbral_uv_mas_estricto_en_la_nina():
    uv9 = b(indice_uv=9)
    assert A.UV not in tipos(evaluar(uv9, Tp.NEUTRAL))
    assert tipos(evaluar(uv9, Tp.LA_NINA))[A.UV].severidad == S.ALTO
