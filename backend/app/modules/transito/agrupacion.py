"""Anti-spam: un incidente solo es Zona Roja si varios dispositivos distintos lo reportan en el mismo lugar."""

from datetime import timedelta
from statistics import fmean

from app.modules.transito.domain import ReporteTransito, TipoIncidente, ZonaRoja
from app.shared.geo import Punto, distancia_m

try:  # Motor C++ (backend/nativo). Si no está compilado, se usa la versión Python con el mismo resultado.
    from naangareko_nativo import asignar_grupos as _asignar_nativo
except ImportError:
    _asignar_nativo = None

MOTOR = "c++" if _asignar_nativo else "python"
RADIO_M = 50
MIN_DISPOSITIVOS = 3
VENTANA = timedelta(hours=3)
_INDICE_TIPO = {t: i for i, t in enumerate(TipoIncidente)}


def asignar_grupos_py(reportes: list[ReporteTransito], radio_m: float = RADIO_M) -> list[int]:
    """Referencia en Python: cada reporte se une al grupo más antiguo del mismo tipo cuyo ancla esté a <= radio."""
    anclas: list[ReporteTransito] = []
    grupos = []
    for r in reportes:
        g = next((i for i, a in enumerate(anclas) if a.tipo == r.tipo and distancia_m(a.punto, r.punto) <= radio_m),
                 None)
        if g is None:
            g = len(anclas)
            anclas.append(r)
        grupos.append(g)
    return grupos


def asignar_grupos(reportes: list[ReporteTransito]) -> list[int]:
    if _asignar_nativo is None:
        return asignar_grupos_py(reportes)
    return _asignar_nativo([r.punto.lat for r in reportes], [r.punto.lon for r in reportes],
                           [_INDICE_TIPO[r.tipo] for r in reportes], RADIO_M)


def agrupar(reportes: list[ReporteTransito]) -> list[ZonaRoja]:
    ordenados = sorted(reportes, key=lambda r: r.creado)
    grupos: dict[int, list[ReporteTransito]] = {}
    for r, g in zip(ordenados, asignar_grupos(ordenados)):
        grupos.setdefault(g, []).append(r)

    zonas = []
    for g in grupos.values():
        dispositivos = len({r.device_id for r in g})
        if dispositivos >= MIN_DISPOSITIVOS:
            centro = Punto(fmean(r.punto.lat for r in g), fmean(r.punto.lon for r in g))
            zonas.append(ZonaRoja(g[0].tipo, centro, len(g), dispositivos, g[-1].creado))
    return zonas
