"""Compara el motor C++ con Python. Uso: python nativo/bench.py [cantidad_de_reportes]"""

import sys
import time

sys.path.insert(0, ".")
from app.modules.transito import agrupacion  # noqa: E402
from tests.test_nativo import reportes_al_azar  # noqa: E402

n = int(sys.argv[1]) if len(sys.argv) > 1 else 20_000
reportes = reportes_al_azar(n, 42)

t = time.perf_counter()
py = agrupacion.asignar_grupos_py(reportes)
t_py = time.perf_counter() - t

t = time.perf_counter()
cpp = agrupacion.asignar_grupos(reportes)
t_cpp = time.perf_counter() - t

print(f"{n} reportes, {max(py) + 1} grupos")
print(f"python: {t_py * 1000:8.1f} ms")
print(f"{agrupacion.MOTOR:>6}: {t_cpp * 1000:8.1f} ms  ({t_py / t_cpp:.0f}x)  iguales={py == cpp}")
