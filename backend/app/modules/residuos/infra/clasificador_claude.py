import base64
from typing import Literal

from anthropic import AsyncAnthropic
from pydantic import BaseModel

from app.modules.residuos.domain import Categoria, Clasificacion
from app.shared.ia.claude_client import FALLBACK

INSTRUCCION = """Clasificá esta foto de un reporte ciudadano de Alto Paraná, Paraguay, en UNA categoría:
- VERTEDERO_CLANDESTINO: basura acumulada en un terreno baldío o en la vía pública.
- SUMIDERO_BLOQUEADO: residuos tapando una boca de tormenta, rejilla o desagüe pluvial.
- OBSTRUCCION_VIAL: restos, escombros o ramas bloqueando la calle.
- NO_RELACIONADA: la foto no muestra ninguna de las anteriores.
confianza: número entre 0 y 1.
descripcion: una oración en español de lo que se ve. No describas personas, rostros ni patentes."""


class _Salida(BaseModel):
    categoria: Literal["VERTEDERO_CLANDESTINO", "SUMIDERO_BLOQUEADO", "OBSTRUCCION_VIAL", "NO_RELACIONADA"]
    confianza: float
    descripcion: str


class ClasificadorClaude:
    def __init__(self, client: AsyncAnthropic, modelo: str):
        self._client = client
        self._modelo = modelo

    async def clasificar(self, foto: bytes, media_type: str) -> Clasificacion:
        resp = await self._client.beta.messages.parse(
            model=self._modelo,
            max_tokens=4000,
            output_config={"effort": "low"},
            messages=[{
                "role": "user",
                "content": [
                    {"type": "image", "source": {
                        "type": "base64", "media_type": media_type,
                        "data": base64.standard_b64encode(foto).decode(),
                    }},
                    {"type": "text", "text": INSTRUCCION},
                ],
            }],
            output_format=_Salida,
            **FALLBACK,
        )
        salida = resp.parsed_output
        if resp.stop_reason == "refusal" or salida is None:
            raise RuntimeError(f"Clasificación no disponible (stop_reason={resp.stop_reason})")

        categoria = Categoria.PENDIENTE if salida.categoria == "NO_RELACIONADA" else Categoria(salida.categoria)
        return Clasificacion(categoria, min(max(salida.confianza, 0.0), 1.0), salida.descripcion[:300])
