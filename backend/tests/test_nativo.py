"""El motor C++ debe dar exactamente los mismos grupos que la referencia en Python."""

import random
from datetime import UTC, datetime, timedelta

import pytest

from app.modules.transito import agrupacion
from app.modules.transito.domain import ReporteTransito, TipoIncidente
from app.shared.geo import Punto

nativo = pytest.importorskip("naangareko_nativo", reason="motor C++ no compilado en este entorno")


def reportes_al_azar(n: int, semilla: int) -> list[ReporteTransito]:
    rnd = random.Random(semilla)
    t0 = datetime(2026, 10, 16, tzinfo=UTC)
    # Concentrados en pocos focos para que haya muchos grupos y muchos casos borde cerca de 50 m.
    focos = [(-25.51 + rnd.uniform(-0.05, 0.05), -54.64 + rnd.uniform(-0.05, 0.05)) for _ in range(30)]
    out = []
    for i in range(n):
        lat, lon = rnd.choice(focos)
        out.append(ReporteTransito(
            Punto(lat + rnd.gauss(0, 0.0004), lon + rnd.gauss(0, 0.0004)),
            rnd.choice(list(TipoIncidente)), f"dev-{rnd.randrange(200):04d}", t0 + timedelta(seconds=i),
        ))
    return out


@pytest.mark.parametrize("semilla", [1, 2, 3])
def test_paridad_con_python(semilla):
    reportes = reportes_al_azar(3000, semilla)
    assert agrupacion.asignar_grupos(reportes) == agrupacion.asignar_grupos_py(reportes)


def test_motor_activo():
    assert agrupacion.MOTOR == "c++"


def test_entrada_invalida():
    with pytest.raises(ValueError):
        nativo.asignar_grupos([1.0], [], [0], 50)
    assert nativo.asignar_grupos([], [], [], 50) == []
