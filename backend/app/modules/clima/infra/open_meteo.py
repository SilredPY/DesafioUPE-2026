from functools import lru_cache

import httpx

from app.modules.clima.domain import Boletin
from app.shared.geo import Punto

# shortcut: Open-Meteo (gratis, sin clave) porque la DMH de Paraguay no expone una API pública estable;
# sumar un adaptador DMH con este mismo puerto cuando exista.
URL = "https://api.open-meteo.com/v1/forecast"


@lru_cache
def _cliente() -> httpx.AsyncClient:
    # Un solo cliente para toda la API: reutiliza la conexión TLS en vez de abrir una por consulta.
    return httpx.AsyncClient(timeout=8.0)


class OpenMeteo:
    async def obtener(self, punto: Punto) -> Boletin:
        params = {
            "latitude": punto.lat,
            "longitude": punto.lon,
            "hourly": "precipitation,precipitation_probability,weather_code,wind_gusts_10m",
            "daily": "temperature_2m_max,uv_index_max",
            "forecast_hours": 6,
            "forecast_days": 1,
            "timezone": "America/Asuncion",
        }
        r = await _cliente().get(URL, params=params)
        r.raise_for_status()
        data = r.json()

        h, d = data["hourly"], data["daily"]
        return Boletin(
            precipitacion_mm=sum(v or 0 for v in h["precipitation"]),
            prob_lluvia=max((v or 0 for v in h["precipitation_probability"]), default=0),
            codigo_tiempo=max((v or 0 for v in h["weather_code"]), default=0),
            rafagas_kmh=max((v or 0 for v in h["wind_gusts_10m"]), default=0),
            temp_max=d["temperature_2m_max"][0] or 0,
            indice_uv=d["uv_index_max"][0] or 0,
        )
