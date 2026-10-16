from app.modules.clima.domain import Boletin
from app.shared.geo import Punto

# Escenarios fijos para demostrar las alertas aunque el día real esté tranquilo.
ESCENARIOS = {
    "tormenta": Boletin(precipitacion_mm=48, prob_lluvia=95, codigo_tiempo=96, rafagas_kmh=85, temp_max=29, indice_uv=4),
    "sequia": Boletin(precipitacion_mm=0, prob_lluvia=5, codigo_tiempo=1, rafagas_kmh=20, temp_max=39, indice_uv=11),
}


class FuenteDemo:
    def __init__(self, escenario: str):
        self._boletin = ESCENARIOS[escenario]

    async def obtener(self, punto: Punto) -> Boletin:
        return self._boletin
