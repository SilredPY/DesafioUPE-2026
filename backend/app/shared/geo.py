from dataclasses import dataclass
from math import asin, cos, radians, sin, sqrt

# Área metropolitana de Alto Paraná: Hernandarias (N), Pdte. Franco (S), Minga Guazú (O), río Paraná (E).
# shortcut: rectángulo aproximado (incluye un borde de Foz do Iguaçu); usar polígono real si molesta.
LAT_MIN, LAT_MAX = -25.80, -25.20
LON_MIN, LON_MAX = -55.00, -54.55


class FueraDeZona(ValueError):
    pass


@dataclass(frozen=True)
class Punto:
    lat: float
    lon: float

    def __post_init__(self) -> None:
        if not (LAT_MIN <= self.lat <= LAT_MAX and LON_MIN <= self.lon <= LON_MAX):
            raise FueraDeZona("La ubicación está fuera del área metropolitana de Alto Paraná.")


def distancia_m(a: Punto, b: Punto) -> float:
    """Distancia haversine en metros."""
    dlat, dlon = radians(b.lat - a.lat), radians(b.lon - a.lon)
    h = sin(dlat / 2) ** 2 + cos(radians(a.lat)) * cos(radians(b.lat)) * sin(dlon / 2) ** 2
    return 2 * 6_371_000 * asin(sqrt(h))
