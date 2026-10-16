"""Reglas puras que convierten un boletín en alertas según la temporada ENSO."""

from app.modules.clima.domain import Alerta, Boletin, Temporada, TipoAlerta
from app.shared.severidad import Severidad

CODIGO_TORMENTA = 95  # WMO 95-99: tormenta eléctrica (96+ con granizo)


def hay_lluvia(b: Boletin) -> bool:
    return b.precipitacion_mm >= 5 or b.prob_lluvia >= 70 or b.codigo_tiempo >= CODIGO_TORMENTA


def evaluar(b: Boletin, temporada: Temporada) -> list[Alerta]:
    alertas: list[Alerta] = []

    if b.codigo_tiempo >= CODIGO_TORMENTA or b.rafagas_kmh >= 60:
        critica = b.codigo_tiempo >= 96 or b.rafagas_kmh >= 90
        alertas.append(Alerta(
            TipoAlerta.TORMENTA,
            Severidad.CRITICO if critica else Severidad.ALTO,
            f"Tormenta prevista (código WMO {b.codigo_tiempo}) con ráfagas de hasta "
            f"{b.rafagas_kmh:.0f} km/h en las próximas 6 h.",
            ("Desenchufá tus aparatos eléctricos.",
             "Asegurá chapas, techos y objetos sueltos.",
             "No te refugies bajo árboles ni cerca de cables."),
        ))

    umbral_lluvia = 20 if temporada == Temporada.EL_NINO else 30
    if b.precipitacion_mm >= umbral_lluvia:
        consejos = ["No cruces calles inundadas: 30 cm de agua arrastran un auto.",
                    "Evitá zonas bajas y la orilla de los arroyos."]
        if temporada == Temporada.EL_NINO:
            consejos.append("Temporada El Niño: atención a crecidas de los arroyos Acaray y Monday "
                            "y a raudales sobre la Ruta PY02.")
        alertas.append(Alerta(
            TipoAlerta.LLUVIA_INTENSA,
            Severidad.CRITICO if b.precipitacion_mm >= 2 * umbral_lluvia else Severidad.ALTO,
            f"Lluvia acumulada estimada de {b.precipitacion_mm:.0f} mm en 6 h (umbral {umbral_lluvia} mm).",
            tuple(consejos),
        ))

    if temporada == Temporada.LA_NINA and b.temp_max >= 35 and b.prob_lluvia < 20:
        alertas.append(Alerta(
            TipoAlerta.INCENDIO,
            Severidad.CRITICO if b.temp_max >= 38 else Severidad.ALTO,
            f"Máxima de {b.temp_max:.0f} °C y {b.prob_lluvia}% de probabilidad de lluvia en temporada "
            "La Niña: riesgo de incendios periurbanos.",
            ("No quemes basura ni pastizales.",
             "Cuidá el agua: regá temprano o al atardecer y revisá pérdidas.",
             "Si ves humo o fuego, llamá a los Bomberos al 132."),
        ))
    elif b.temp_max >= 38:
        alertas.append(Alerta(
            TipoAlerta.CALOR,
            Severidad.ALTO,
            f"Temperatura máxima prevista de {b.temp_max:.0f} °C.",
            ("Tomá agua seguido aunque no tengas sed.",
             "Evitá el sol entre las 10 y las 16 h.",
             "Cuidá a niños, personas mayores y mascotas."),
        ))

    umbral_uv = 8 if temporada == Temporada.LA_NINA else 11
    if b.indice_uv >= umbral_uv:
        alertas.append(Alerta(
            TipoAlerta.UV,
            Severidad.CRITICO if b.indice_uv >= 11 else Severidad.ALTO,
            f"Índice UV máximo de {b.indice_uv:.0f}.",
            ("Usá protector solar, gorra y lentes.",
             "Buscá sombra entre las 10 y las 16 h."),
        ))

    return alertas
