from app.modules.residuos.domain import Categoria
from app.shared.severidad import Severidad

CONFIANZA_MINIMA = 0.5


def calcular_severidad(categoria: Categoria, confianza: float, lluvia_activa: bool) -> Severidad:
    if categoria == Categoria.PENDIENTE:
        return Severidad.BAJO
    # Un sumidero tapado con lluvia en camino es inundación segura en la cuadra.
    if categoria == Categoria.SUMIDERO_BLOQUEADO and lluvia_activa and confianza >= CONFIANZA_MINIMA:
        return Severidad.CRITICO

    severidad = Severidad.MEDIO
    if lluvia_activa and categoria in (Categoria.SUMIDERO_BLOQUEADO, Categoria.OBSTRUCCION_VIAL):
        severidad = Severidad.ALTO
    if confianza < CONFIANZA_MINIMA:
        severidad = severidad.mover(-1)
    return severidad


PESO_MAPA = {Severidad.BAJO: 0.25, Severidad.MEDIO: 0.5, Severidad.ALTO: 0.75, Severidad.CRITICO: 1.0}
