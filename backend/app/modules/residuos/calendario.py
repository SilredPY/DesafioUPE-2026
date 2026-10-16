import json
from dataclasses import dataclass
from datetime import datetime, time, timedelta, timezone
from functools import lru_cache
from pathlib import Path

# Paraguay usa UTC-3 todo el año desde 2024 (horario de verano permanente).
HORA_PY = timezone(timedelta(hours=-3))
DIAS = ("lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo")


@dataclass(frozen=True)
class RecorridoBarrio:
    barrio: str
    ciudad: str
    dias: tuple[int, ...]  # 0 = lunes
    hora: time


@lru_cache
def recorridos() -> list[RecorridoBarrio]:
    data = json.loads((Path(__file__).parent / "data" / "calendario_barrios.json").read_text("utf-8"))
    return [
        RecorridoBarrio(r["barrio"], r["ciudad"], tuple(r["dias"]), time.fromisoformat(r["hora"]))
        for r in data["recorridos"]
    ]


def proximo_paso(r: RecorridoBarrio, ahora: datetime) -> datetime:
    ahora = ahora.astimezone(HORA_PY)
    for d in range(8):
        dia = ahora.date() + timedelta(days=d)
        if dia.weekday() in r.dias:
            paso = datetime.combine(dia, r.hora, tzinfo=HORA_PY)
            if paso > ahora:
                return paso
    raise ValueError(f"El recorrido de {r.barrio} no tiene días configurados")
