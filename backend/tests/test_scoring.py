from app.modules.residuos.domain import Categoria as C
from app.modules.residuos.scoring import calcular_severidad
from app.shared.severidad import Severidad as S


def test_sumidero_tapado_con_lluvia_es_critico():
    assert calcular_severidad(C.SUMIDERO_BLOQUEADO, 0.9, lluvia_activa=True) == S.CRITICO


def test_sumidero_tapado_sin_lluvia_es_medio():
    assert calcular_severidad(C.SUMIDERO_BLOQUEADO, 0.9, lluvia_activa=False) == S.MEDIO


def test_sumidero_dudoso_con_lluvia_no_llega_a_critico():
    assert calcular_severidad(C.SUMIDERO_BLOQUEADO, 0.3, lluvia_activa=True) == S.MEDIO


def test_obstruccion_con_lluvia_sube_a_alto():
    assert calcular_severidad(C.OBSTRUCCION_VIAL, 0.8, lluvia_activa=True) == S.ALTO


def test_vertedero_no_depende_de_la_lluvia():
    assert calcular_severidad(C.VERTEDERO_CLANDESTINO, 0.8, True) == calcular_severidad(C.VERTEDERO_CLANDESTINO, 0.8, False)


def test_baja_confianza_baja_un_nivel():
    assert calcular_severidad(C.VERTEDERO_CLANDESTINO, 0.2, False) == S.BAJO


def test_pendiente_siempre_bajo():
    assert calcular_severidad(C.PENDIENTE, 0.0, True) == S.BAJO
