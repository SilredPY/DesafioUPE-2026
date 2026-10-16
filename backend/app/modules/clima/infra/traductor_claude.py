from anthropic import AsyncAnthropic

from app.modules.clima.domain import Alerta
from app.shared.ia.claude_client import FALLBACK

SISTEMA = """Sos el asistente de alertas de Ñangarekó IA para el área metropolitana de Alto Paraná, Paraguay \
(Ciudad del Este, Presidente Franco, Hernandarias, Minga Guazú).
Convertís un aviso meteorológico técnico en un mensaje preventivo para la gente:
- Máximo 2 oraciones y 280 caracteres.
- Español paraguayo cercano, con voseo y alguna expresión guaraní o jopara común \
(por ejemplo "Oĩ la peligro", "Ñañangarekó"). Nada de portugués.
- Nombrá la ciudad y la acción más importante que la persona tiene que hacer ahora.
- No inventes datos que no estén en el aviso.
Respondé solo con el mensaje, sin comillas ni encabezados."""


class TraductorClaude:
    def __init__(self, client: AsyncAnthropic, modelo: str):
        self._client = client
        self._modelo = modelo

    async def traducir(self, alerta: Alerta, ciudad: str) -> str:
        aviso = (
            f"Ciudad: {ciudad}\nTipo: {alerta.tipo}\nSeveridad: {alerta.severidad}\n"
            f"Aviso técnico: {alerta.mensaje_tecnico}\nConsejos: {' '.join(alerta.consejos)}"
        )
        resp = await self._client.beta.messages.create(
            model=self._modelo,
            max_tokens=4000,
            output_config={"effort": "low"},
            system=SISTEMA,
            messages=[{"role": "user", "content": aviso}],
            **FALLBACK,
        )
        if resp.stop_reason == "refusal":
            raise RuntimeError("El modelo rechazó la traducción")
        texto = "".join(b.text for b in resp.content if b.type == "text").strip()
        if not texto:
            raise RuntimeError("Respuesta vacía del modelo")
        return texto
