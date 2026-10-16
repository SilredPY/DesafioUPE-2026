"""Anti-spam: un incidente solo es Zona Roja si varios dispositivos distintos lo reportan en el mismo lugar."""

from datetime import timedelta
from statistics import fmean

from app.modules.transito.domain import ReporteTransito, ZonaRoja
from app.shared.geo import Punto, distancia_m

RADIO_M = 50
MIN_DISPOSITIVOS = 3
VENTANA = timedelta(hours=3)


def agrupar(reportes: list[ReporteTransito]) -> list[ZonaRoja]:
    # Cada grupo se ancla en su primer reporte. shortcut: O(n·grupos), sobra para los reportes de 3 h
    # de un área metropolitana; pasar a ST_ClusterDBSCAN en PostGIS si crece mucho.
    grupos: list[list[ReporteTransito]] = []
    for r in sorted(reportes, key=lambda r: r.creado):
        grupo = next(
            (g for g in grupos if g[0].tipo == r.tipo and distancia_m(g[0].punto, r.punto) <= RADIO_M), None
        )
        if grupo:
            grupo.append(r)
        else:
            grupos.append([r])

    zonas = []
    for g in grupos:
        dispositivos = len({r.device_id for r in g})
        if dispositivos >= MIN_DISPOSITIVOS:
            centro = Punto(fmean(r.punto.lat for r in g), fmean(r.punto.lon for r in g))
            zonas.append(ZonaRoja(g[0].tipo, centro, len(g), dispositivos, g[-1].creado))
    return zonas
