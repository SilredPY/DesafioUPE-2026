from datetime import UTC, datetime, timedelta

from app.modules.transito.agrupacion import agrupar
from app.modules.transito.domain import ReporteTransito
from app.modules.transito.domain import TipoIncidente as T
from app.shared.geo import Punto

T0 = datetime(2026, 10, 16, 18, 0, tzinfo=UTC)
KM4 = Punto(-25.5170, -54.6400)  # Ruta PY02 Km 4 (aprox.)
# ~0.0001° de latitud ≈ 11 m
CERCA = [Punto(KM4.lat + i * 0.0001, KM4.lon) for i in range(4)]


def rep(p, tipo=T.RAUDAL, device="dev-0001", minutos=0):
    return ReporteTransito(p, tipo, device, T0 + timedelta(minutes=minutos))


def test_tres_dispositivos_cerca_forman_zona_roja():
    zonas = agrupar([rep(CERCA[i], device=f"dev-000{i}", minutos=i) for i in range(3)])
    assert len(zonas) == 1
    z = zonas[0]
    assert (z.tipo, z.reportes, z.dispositivos) == (T.RAUDAL, 3, 3)
    assert z.ultimo == T0 + timedelta(minutes=2)


def test_un_mismo_dispositivo_no_valida_spam():
    assert agrupar([rep(CERCA[i], device="spammer-01", minutos=i) for i in range(4)]) == []


def test_reportes_lejanos_no_se_agrupan():
    lejos = Punto(KM4.lat + 0.001, KM4.lon)  # ~110 m
    assert agrupar([rep(KM4, device="dev-0001"), rep(KM4, device="dev-0002"), rep(lejos, device="dev-0003")]) == []


def test_tipos_distintos_no_se_mezclan():
    reportes = [rep(KM4, T.RAUDAL, "dev-0001"), rep(KM4, T.BACHE, "dev-0002"), rep(KM4, T.SEMAFORO_CABLE, "dev-0003")]
    assert agrupar(reportes) == []
