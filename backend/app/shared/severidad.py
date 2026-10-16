from enum import StrEnum


class Severidad(StrEnum):
    BAJO = "BAJO"
    MEDIO = "MEDIO"
    ALTO = "ALTO"
    CRITICO = "CRITICO"

    def mover(self, niveles: int) -> "Severidad":
        orden = list(Severidad)
        return orden[max(0, min(len(orden) - 1, orden.index(self) + niveles))]
