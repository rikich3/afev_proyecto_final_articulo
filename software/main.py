"""Bucle mínimo adquirir → decidir → actuar → observar."""

from __future__ import annotations

from .adaptador import PlantaDeterminista
from .controlador import step
from .estado import Estado, Orden


def ejecutar_ciclo(estado: Estado, planta: PlantaDeterminista, ordenes: list[Orden]):
    snapshot = planta.snapshot()
    resultado = step(estado, snapshot, ordenes)
    verdad_fisica = planta.avanzar(resultado.salidas)
    return resultado, snapshot, verdad_fisica
