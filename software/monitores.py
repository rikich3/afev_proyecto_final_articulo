"""Oráculo independiente basado en la observación física posterior al paso."""

from __future__ import annotations

from typing import Any, Mapping


CAMPOS_FISICOS = {
    "tick", "t_sim_s", "ocupantes_reales", "potencia_real", "velocidad_real_m_s",
    "puerta_real_cerrada", "seccionador_real_abierto",
}


def evaluar(verdad_fisica: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Devuelve propiedades incumplidas sin mirar fase, órdenes ni RFID."""
    faltantes = sorted(CAMPOS_FISICOS.difference(verdad_fisica))
    if faltantes:
        return [{"propiedad": "OBSERVACION_INCOMPLETA", "faltantes": faltantes}]
    violaciones: list[dict[str, Any]] = []
    if verdad_fisica["ocupantes_reales"] and verdad_fisica["potencia_real"] is True:
        violaciones.append({
            "propiedad": "RF-01", "detalle": "ocupante físico con potencia física activa",
            "tick": verdad_fisica["tick"], "t_sim_s": verdad_fisica["t_sim_s"],
        })
    return violaciones
