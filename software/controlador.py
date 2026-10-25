"""Función pura de transición del supervisor.

El módulo no conoce CoppeliaSim. Recibe una observación previa al paso y emite
órdenes que la planta confirmará, o no, en el siguiente snapshot.
"""

from __future__ import annotations

from dataclasses import replace
from typing import Iterable, Optional

from .estado import Estado, Fase, Motivo, OPERARIOS, Orden, ResultadoPaso, Salidas, Snapshot


EPSILON_PARADA_M_S = 0.001


def _seguro_para_listo(s: Snapshot, estado: Estado) -> bool:
    return (
        s.sensor_valid
        and not estado.ocupantes
        and not estado.bloqueos
        and s.laser_ocupado is False
        and s.barrera_libre is True
        and s.puerta_cerrada is True
        and s.contacto_cerrado is False
        and s.seccionador_abierto is False
        and s.velocidad_m_s is not None
        and abs(s.velocidad_m_s) <= EPSILON_PARADA_M_S
    )


def _motivo_fallo(s: Snapshot, estado: Estado) -> Optional[Motivo]:
    if not s.sensor_valid or s.sensor_age_s is None:
        return Motivo.DATO_INVALIDO
    if s.emergencia is True:
        return Motivo.EMERGENCIA_ACTIVA
    if s.fallo_watchdog is True or s.heartbeat_vigente is False:
        return Motivo.WATCHDOG_CADUCADO
    # RFID identifica titulares, pero el sensor de presencia es una barrera de
    # seguridad adicional: su activación durante potencia obliga a fallo aunque
    # no haya llegado un evento RFID válido.
    if (estado.ocupantes or s.laser_ocupado is True) and s.contacto_cerrado is True:
        return Motivo.PRESENCIA_PELIGROSA
    return None


def _ordenes_nuevas(estado: Estado, ordenes: Iterable[Orden]) -> tuple[list[Orden], Estado]:
    nuevas: list[Orden] = []
    vistos = set(estado.comandos_vistos)
    for orden in ordenes:
        if orden.command_id and orden.command_id not in vistos:
            nuevas.append(orden)
            vistos.add(orden.command_id)
    return nuevas, replace(estado, comandos_vistos=frozenset(vistos))


def _personal_valida(orden: Orden) -> bool:
    return (
        orden.operario_id in OPERARIOS
        and orden.solicitante_id == orden.operario_id
    )


def _salida_segura() -> Salidas:
    return Salidas()


def step(estado: Estado, snapshot: Snapshot, ordenes: Iterable[Orden]) -> ResultadoPaso:
    """Avanza como máximo una fase y prioriza siempre la condición insegura."""
    estado = estado.con_snapshot(snapshot)
    nuevas, estado = _ordenes_nuevas(estado, ordenes)
    eventos: list[str] = []

    motivo = _motivo_fallo(snapshot, estado)
    if motivo is not None:
        return ResultadoPaso(replace(estado, fase=Fase.FALLO, reset_pendiente=False), _salida_segura(), tuple(eventos), motivo)

    tipos = {orden.tipo for orden in nuevas}
    if "stop" in tipos:
        return ResultadoPaso(
            replace(estado, fase=Fase.PARADA_SOLICITADA, reset_pendiente=False),
            _salida_segura(), tuple(eventos), None,
        )

    # En fallo se exige un reset nuevo cuando la planta ya está en condición segura.
    if estado.fase is Fase.FALLO:
        if "reset" in tipos and _seguro_para_listo(snapshot, estado):
            return ResultadoPaso(replace(estado, fase=Fase.LISTO, reset_pendiente=True), Salidas(alarma=False), tuple(eventos), None)
        return ResultadoPaso(estado, _salida_segura(), tuple(eventos), Motivo.FASE_INCORRECTA if tipos else None)

    if estado.fase is Fase.INICIO_SEGURO:
        if "reset" in tipos and _seguro_para_listo(snapshot, estado):
            return ResultadoPaso(replace(estado, fase=Fase.LISTO, reset_pendiente=True), Salidas(alarma=False), tuple(eventos), None)
        return ResultadoPaso(estado, _salida_segura(), tuple(eventos), Motivo.FASE_INCORRECTA if tipos else None)

    if estado.fase is Fase.LISTO:
        if "start" in tipos and estado.reset_pendiente and _seguro_para_listo(snapshot, estado):
            return ResultadoPaso(replace(estado, fase=Fase.MARCHA, reset_pendiente=False), Salidas(orden_contactor=True, alarma=False), tuple(eventos), None)
        if "solicitar_mantenimiento" in tipos:
            return ResultadoPaso(replace(estado, fase=Fase.PARADA_SOLICITADA, intervencion_activa=True), _salida_segura(), tuple(eventos), None)
        motivo = Motivo.START_NO_NUEVO if "start" in tipos else (Motivo.FASE_INCORRECTA if tipos else None)
        return ResultadoPaso(estado, Salidas(alarma=False), tuple(eventos), motivo)

    if estado.fase is Fase.MARCHA:
        if "solicitar_mantenimiento" in tipos:
            return ResultadoPaso(replace(estado, fase=Fase.PARADA_SOLICITADA, intervencion_activa=True), _salida_segura(), tuple(eventos), None)
        return ResultadoPaso(estado, Salidas(orden_contactor=True, alarma=False), tuple(eventos), Motivo.FASE_INCORRECTA if tipos else None)

    if estado.fase is Fase.PARADA_SOLICITADA:
        if snapshot.contacto_cerrado is False and snapshot.velocidad_m_s is not None and abs(snapshot.velocidad_m_s) <= EPSILON_PARADA_M_S:
            return ResultadoPaso(replace(estado, fase=Fase.AISLAMIENTO), _salida_segura(), tuple(eventos), None)
        return ResultadoPaso(estado, _salida_segura(), tuple(eventos), None)

    if estado.fase is Fase.AISLAMIENTO:
        if snapshot.seccionador_abierto is True:
            return ResultadoPaso(replace(estado, fase=Fase.BLOQUEO), _salida_segura(), tuple(eventos), None)
        if "abrir_seccionador" in tipos:
            return ResultadoPaso(estado, Salidas(orden_seccionador="ABRIR"), tuple(eventos), None)
        return ResultadoPaso(estado, _salida_segura(), tuple(eventos), Motivo.AISLAMIENTO_NO_CONFIRMADO if tipos else None)

    if estado.fase is Fase.BLOQUEO:
        acciones: list[tuple[int, str]] = []
        for orden in nuevas:
            if orden.tipo == "aplicar_bloqueo" and _personal_valida(orden):
                acciones.append((orden.operario_id, "APLICAR"))
            elif orden.tipo == "aplicar_bloqueo":
                return ResultadoPaso(estado, _salida_segura(), tuple(eventos), Motivo.TITULAR_DISTINTO)
        if estado.bloqueos == OPERARIOS:
            return ResultadoPaso(replace(estado, fase=Fase.VERIFICACION_CERO), _salida_segura(), tuple(eventos), None)
        return ResultadoPaso(estado, Salidas(acciones_bloqueo=tuple(acciones)), tuple(eventos), Motivo.BLOQUEO_PENDIENTE if tipos and not acciones else None)

    if estado.fase is Fase.VERIFICACION_CERO:
        if snapshot.contacto_cerrado is False and snapshot.seccionador_abierto is True and snapshot.velocidad_m_s is not None and abs(snapshot.velocidad_m_s) <= EPSILON_PARADA_M_S:
            return ResultadoPaso(replace(estado, fase=Fase.MANTENIMIENTO), Salidas(permiso_acceso=True, orden_puerta="ABRIR", alarma=False), tuple(eventos), None)
        return ResultadoPaso(estado, _salida_segura(), tuple(eventos), Motivo.ENERGIA_RESIDUAL)

    if estado.fase is Fase.MANTENIMIENTO:
        if "cerrar_acceso" in tipos:
            if estado.ocupantes:
                return ResultadoPaso(estado, Salidas(permiso_acceso=True, alarma=False), tuple(eventos), Motivo.OPERARIO_DENTRO)
            return ResultadoPaso(replace(estado, fase=Fase.LIBERACION), Salidas(alarma=False), tuple(eventos), None)
        return ResultadoPaso(estado, Salidas(permiso_acceso=True, orden_puerta="ABRIR", alarma=False), tuple(eventos), None)

    if estado.fase is Fase.LIBERACION:
        acciones = []
        for orden in nuevas:
            if orden.tipo == "retirar_bloqueo" and _personal_valida(orden) and orden.operario_id in estado.bloqueos:
                acciones.append((orden.operario_id, "RETIRAR"))
            elif orden.tipo == "retirar_bloqueo":
                return ResultadoPaso(estado, _salida_segura(), tuple(eventos), Motivo.TITULAR_DISTINTO)
        if not estado.bloqueos:
            return ResultadoPaso(replace(estado, fase=Fase.RESTABLECIMIENTO), Salidas(orden_puerta="CERRAR", alarma=False), tuple(eventos), None)
        return ResultadoPaso(estado, Salidas(acciones_bloqueo=tuple(acciones), alarma=False), tuple(eventos), Motivo.BLOQUEO_PENDIENTE if tipos and not acciones else None)

    # RESTABLECIMIENTO
    if estado.fase is Fase.RESTABLECIMIENTO:
        if snapshot.puerta_cerrada is not True:
            return ResultadoPaso(estado, Salidas(orden_puerta="CERRAR", alarma=False), tuple(eventos), None)
        if snapshot.seccionador_abierto is True:
            return ResultadoPaso(estado, Salidas(orden_seccionador="CERRAR", alarma=False), tuple(eventos), None)
        if "reset" in tipos and _seguro_para_listo(snapshot, estado):
            return ResultadoPaso(replace(estado, fase=Fase.LISTO, reset_pendiente=True), Salidas(alarma=False), tuple(eventos), None)
        return ResultadoPaso(estado, Salidas(alarma=False), tuple(eventos), Motivo.FASE_INCORRECTA if tipos else None)

    return ResultadoPaso(replace(estado, fase=Fase.FALLO), _salida_segura(), tuple(eventos), Motivo.DATO_INVALIDO)
