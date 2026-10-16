"""Regla pura: ¿conviene ir a clase hoy?"""

from app.modules.campus.domain import Aviso, Nivel, Recomendacion, TipoAviso
from app.shared.severidad import Severidad


def recomendar(severidades_clima: list[Severidad], zonas_rojas_cerca: int, avisos: list[Aviso]) -> Recomendacion:
    tipos = {a.tipo for a in avisos}
    if TipoAviso.CLASES_SUSPENDIDAS in tipos:
        return Recomendacion(Nivel.SIN_CLASES, "Clases suspendidas",
                             "La institución suspendió las clases. Quedate en casa y seguí los avisos oficiales.")
    if TipoAviso.CLASES_VIRTUALES in tipos:
        return Recomendacion(Nivel.SIN_CLASES, "Clases virtuales",
                             "Hoy las clases son a distancia. No hace falta trasladarte.")
    if Severidad.CRITICO in severidades_clima:
        return Recomendacion(Nivel.NO_SALIR, "Evitá trasladarte",
                             "Hay alertas climáticas críticas en la zona del campus. Si podés, esperá a que pase "
                             "y avisá a tus profesores.")
    if Severidad.ALTO in severidades_clima or zonas_rojas_cerca:
        detalle = []
        if Severidad.ALTO in severidades_clima:
            detalle.append("hay alertas climáticas")
        if zonas_rojas_cerca:
            detalle.append(f"{zonas_rojas_cerca} zona(s) roja(s) de tránsito cerca del campus")
        return Recomendacion(Nivel.PRECAUCION, "Salí con precaución",
                             f"Ojo: {' y '.join(detalle)}. Salí con tiempo y buscá rutas alternativas.")
    return Recomendacion(Nivel.NORMAL, "Todo en orden", "Sin alertas ni incidentes cerca del campus. ¡Buena clase!")
