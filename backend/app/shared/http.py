import re

from fastapi import Header, HTTPException

_DEVICE_ID = re.compile(r"^[A-Za-z0-9-]{8,64}$")


def device_id(x_device_id: str = Header(..., description="Identificador anónimo del dispositivo")) -> str:
    if not _DEVICE_ID.match(x_device_id):
        raise HTTPException(400, "X-Device-Id inválido")
    return x_device_id


class LimiteExcedido(Exception):
    """El dispositivo superó la cantidad de reportes permitidos por hora."""
