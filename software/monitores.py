"""Oráculo independiente basado en la observación física posterior al paso."""

from __future__ import annotations

from math import isfinite
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
    invalidos = []
    for campo in ("potencia_real", "puerta_real_cerrada", "seccionador_real_abierto"):
        if type(verdad_fisica[campo]) is not bool:
            invalidos.append(campo)
    for campo in ("t_sim_s", "velocidad_real_m_s"):
        valor = verdad_fisica[campo]
        if type(valor) not in (int, float) or not isfinite(valor):
            invalidos.append(campo)
    if type(verdad_fisica["tick"]) is not int or verdad_fisica["tick"] < 0:
        invalidos.append("tick")
    ocupantes = verdad_fisica["ocupantes_reales"]
    if not isinstance(ocupantes, (list, tuple, set, frozenset)) or any(
        type(id_) is not int or id_ not in (1, 2) for id_ in ocupantes
    ):
        invalidos.append("ocupantes_reales")
    if invalidos:
        return [{"propiedad": "OBSERVACION_INVALIDA", "invalidos": invalidos}]
    violaciones: list[dict[str, Any]] = []
    if verdad_fisica["ocupantes_reales"] and verdad_fisica["potencia_real"] is True:
        violaciones.append({
            "propiedad": "RF-01", "detalle": "ocupante físico con potencia física activa",
            "tick": verdad_fisica["tick"], "t_sim_s": verdad_fisica["t_sim_s"],
        })
    return violaciones
