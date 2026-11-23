"""Función pura de transición del supervisor.

El módulo no conoce CoppeliaSim. Recibe una observación previa al paso y emite
órdenes que la planta confirmará, o no, en el siguiente snapshot.
"""

from __future__ import annotations

from dataclasses import replace
from math import isfinite
from typing import Iterable, Optional

from .estado import Estado, Fase, Motivo, OPERARIOS, Orden, ResultadoPaso, Salidas, Snapshot


EPSILON_PARADA_M_S = 0.001
TOLERANCIA_TIEMPO_S = 1e-9


def _seguro_para_listo(s: Snapshot, estado: Estado, epsilon: float) -> bool:
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
        and abs(s.velocidad_m_s) <= epsilon
    )


def _motivo_fallo(s: Snapshot, estado: Estado, timeout: float) -> Optional[Motivo]:
    if s.emergencia is True:
        return Motivo.EMERGENCIA_ACTIVA
    if s.fallo_watchdog is True or s.heartbeat_vigente is False:
        return Motivo.WATCHDOG_CADUCADO

    booleanos = (
        s.laser_ocupado, s.barrera_libre, s.puerta_cerrada, s.contacto_cerrado,
        s.seccionador_abierto, s.emergencia, s.fallo_watchdog, s.heartbeat_vigente,
    )
    if (
        not s.sensor_valid
        or any(type(valor) is not bool for valor in booleanos)
        or s.bloqueos_confirmados is None
        or not s.bloqueos_confirmados <= OPERARIOS
        or s.sensor_age_s is None or not isfinite(s.sensor_age_s) or s.sensor_age_s < 0
        or s.velocidad_m_s is None or not isfinite(s.velocidad_m_s)
    ):
        return Motivo.DATO_INVALIDO
    if s.sensor_age_s + TOLERANCIA_TIEMPO_S >= timeout:
        return Motivo.DATO_CADUCADO
    if (estado.ocupantes or s.laser_ocupado) and s.contacto_cerrado:
        return Motivo.PRESENCIA_PELIGROSA
    if estado.fase in (Fase.MARCHA, Fase.MANTENIMIENTO, Fase.LIBERACION):
        if bool(estado.ocupantes) != s.laser_ocupado:
            return Motivo.DISCREPANCIA
    if estado.fase is Fase.MARCHA and (
        not s.puerta_cerrada or s.seccionador_abierto or estado.bloqueos
    ):
        return Motivo.DISCREPANCIA
    return None


def reiniciar(estado: Estado) -> Estado:
    """Revoca mando y rearme mientras se reconcilia el estado de la planta."""
    return replace(estado, fase=Fase.FALLO, reset_pendiente=False)


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


def step(
    estado: Estado, snapshot: Snapshot, ordenes: Iterable[Orden], *,
    sensor_timeout_s: float = 0.06, contact_open_timeout_s: float = 0.06,
    epsilon: float = EPSILON_PARADA_M_S, parada_max_s: float = 2.0,
) -> ResultadoPaso:
    """Avanza como máximo una fase y prioriza fallo, parada y mantenimiento."""
    ordenes = tuple(ordenes)
    repetidos = [
        evento.event_id for evento in snapshot.rfid_eventos
        if evento.event_id in estado.eventos_vistos
    ]
    estado = estado.con_snapshot(snapshot)
    nuevas, estado = _ordenes_nuevas(estado, ordenes)
    tipos = {orden.tipo for orden in nuevas}
    eventos = [f"RFID_REPETIDO:{id_}" for id_ in repetidos]
    if len(nuevas) != len(ordenes):
        eventos.append("ORDEN_REPETIDA_O_SIN_ID")

    corte = estado.corte_desde_s
    if snapshot.contacto_cerrado is False:
        corte = None
    elif snapshot.contacto_cerrado is True and corte is None and estado.fase is not Fase.MARCHA:
        corte = snapshot.t_sim_s
    estado = replace(estado, corte_desde_s=corte)
    parada_desde = estado.parada_desde_s
    if estado.fase is Fase.PARADA_SOLICITADA and snapshot.contacto_cerrado is False:
        if parada_desde is None:
            parada_desde = snapshot.t_sim_s
    else:
        parada_desde = None
    estado = replace(estado, parada_desde_s=parada_desde)
    motivo = _motivo_fallo(snapshot, estado, sensor_timeout_s)
    if (motivo is None and parada_desde is not None
            and abs(snapshot.velocidad_m_s) > epsilon
            and snapshot.t_sim_s - parada_desde + TOLERANCIA_TIEMPO_S >= parada_max_s):
        motivo = Motivo.ENERGIA_RESIDUAL
    if (
        snapshot.contacto_cerrado is True and corte is not None
        and snapshot.t_sim_s - corte + TOLERANCIA_TIEMPO_S >= contact_open_timeout_s
    ):
        motivo = Motivo.CONTACTO_NO_ABRE
    if motivo is not None:
        if corte is None and snapshot.contacto_cerrado is True:
            corte = snapshot.t_sim_s
        salidas = _salida_segura()
        if (
            motivo is Motivo.WATCHDOG_CADUCADO and "reset" in tipos
            and snapshot.heartbeat_vigente is True and snapshot.fallo_watchdog is True
            and _motivo_fallo(replace(snapshot, fallo_watchdog=False), estado, sensor_timeout_s) is None
            and _seguro_para_listo(snapshot, estado, epsilon)
        ):
            salidas = replace(salidas, reset_watchdog=True)
        return ResultadoPaso(
            replace(estado, fase=Fase.FALLO, reset_pendiente=False, corte_desde_s=corte),
            salidas, tuple(eventos), motivo,
        )

    if "stop" in tipos:
        fase = Fase.PARADA_SOLICITADA if estado.fase in (Fase.MARCHA, Fase.LISTO) else estado.fase
        if fase not in (Fase.PARADA_SOLICITADA, Fase.INICIO_SEGURO):
            fase = Fase.FALLO
        return ResultadoPaso(
            replace(estado, fase=fase, reset_pendiente=False,
                    corte_desde_s=snapshot.t_sim_s if corte is None and snapshot.contacto_cerrado else corte),
            _salida_segura(), tuple(eventos), None,
        )

    # En fallo se exige un reset nuevo cuando la planta ya está en condición segura.
    if estado.fase is Fase.FALLO:
        if "reset" in tipos and _seguro_para_listo(snapshot, estado, epsilon):
            return ResultadoPaso(replace(estado, fase=Fase.LISTO, reset_pendiente=True, intervencion_activa=False), Salidas(alarma=False), tuple(eventos), None)
        return ResultadoPaso(estado, _salida_segura(), tuple(eventos), Motivo.FASE_INCORRECTA if tipos else None)

    if estado.fase is Fase.INICIO_SEGURO:
        if "reset" in tipos and _seguro_para_listo(snapshot, estado, epsilon):
            return ResultadoPaso(replace(estado, fase=Fase.LISTO, reset_pendiente=True, intervencion_activa=False), Salidas(alarma=False), tuple(eventos), None)
        return ResultadoPaso(estado, _salida_segura(), tuple(eventos), Motivo.FASE_INCORRECTA if tipos else None)

    if estado.fase in (Fase.LISTO, Fase.MARCHA) and "solicitar_mantenimiento" in tipos:
        return ResultadoPaso(
            replace(estado, fase=Fase.PARADA_SOLICITADA, intervencion_activa=True,
                    reset_pendiente=False,
                    corte_desde_s=snapshot.t_sim_s if snapshot.contacto_cerrado else None),
            _salida_segura(), tuple(eventos), None,
        )

    if estado.fase is Fase.LISTO:
        if "reset" in tipos and _seguro_para_listo(snapshot, estado, epsilon):
            motivo = Motivo.START_NO_NUEVO if "start" in tipos else None
            return ResultadoPaso(replace(estado, reset_pendiente=True), Salidas(alarma=False), tuple(eventos), motivo)
        if "start" in tipos and estado.reset_pendiente and _seguro_para_listo(snapshot, estado, epsilon):
            return ResultadoPaso(replace(estado, fase=Fase.MARCHA, reset_pendiente=False), Salidas(orden_contactor=True, alarma=False), tuple(eventos), None)
        motivo = Motivo.START_NO_NUEVO if "start" in tipos else (Motivo.FASE_INCORRECTA if tipos else None)
        return ResultadoPaso(estado, Salidas(alarma=False), tuple(eventos), motivo)

    if estado.fase is Fase.MARCHA:
        return ResultadoPaso(estado, Salidas(orden_contactor=True, alarma=False), tuple(eventos), Motivo.FASE_INCORRECTA if tipos else None)

    if estado.fase is Fase.PARADA_SOLICITADA:
        if snapshot.contacto_cerrado is False and abs(snapshot.velocidad_m_s) <= epsilon:
            if estado.intervencion_activa:
                return ResultadoPaso(replace(estado, fase=Fase.AISLAMIENTO), _salida_segura(), tuple(eventos), None)
            if "reset" in tipos and _seguro_para_listo(snapshot, estado, epsilon):
                return ResultadoPaso(replace(estado, fase=Fase.LISTO, reset_pendiente=True, intervencion_activa=False), Salidas(alarma=False), tuple(eventos), None)
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
                motivo = Motivo.ID_DESCONOCIDA if orden.operario_id not in OPERARIOS else Motivo.TITULAR_DISTINTO
                return ResultadoPaso(estado, _salida_segura(), tuple(eventos), motivo)
        if estado.bloqueos == OPERARIOS:
            return ResultadoPaso(replace(estado, fase=Fase.VERIFICACION_CERO), _salida_segura(), tuple(eventos), None)
        return ResultadoPaso(estado, Salidas(acciones_bloqueo=tuple(acciones)), tuple(eventos), Motivo.BLOQUEO_PENDIENTE if tipos and not acciones else None)

    if estado.fase is Fase.VERIFICACION_CERO:
        if (snapshot.contacto_cerrado is False and snapshot.seccionador_abierto is True
                and abs(snapshot.velocidad_m_s) <= epsilon and estado.bloqueos == OPERARIOS):
            return ResultadoPaso(replace(estado, fase=Fase.MANTENIMIENTO), Salidas(permiso_acceso=True, orden_puerta="ABRIR", alarma=False), tuple(eventos), None)
        return ResultadoPaso(estado, _salida_segura(), tuple(eventos), Motivo.ENERGIA_RESIDUAL)

    if estado.fase is Fase.MANTENIMIENTO:
        if snapshot.contacto_cerrado or not snapshot.seccionador_abierto or abs(snapshot.velocidad_m_s) > epsilon or estado.bloqueos != OPERARIOS:
            return ResultadoPaso(replace(estado, fase=Fase.FALLO, reset_pendiente=False), _salida_segura(), tuple(eventos), Motivo.DISCREPANCIA)
        if "retirar_bloqueo" in tipos:
            return ResultadoPaso(estado, Salidas(permiso_acceso=True, alarma=False), tuple(eventos), Motivo.FASE_INCORRECTA)
        if "cerrar_acceso" in tipos:
            if estado.ocupantes or snapshot.laser_ocupado:
                return ResultadoPaso(estado, Salidas(permiso_acceso=True, alarma=False), tuple(eventos), Motivo.OPERARIO_DENTRO)
            return ResultadoPaso(replace(estado, fase=Fase.LIBERACION), Salidas(alarma=False), tuple(eventos), None)
        return ResultadoPaso(estado, Salidas(permiso_acceso=True, orden_puerta="ABRIR", alarma=False), tuple(eventos), None)

    if estado.fase is Fase.LIBERACION:
        if estado.ocupantes or snapshot.laser_ocupado:
            return ResultadoPaso(replace(estado, fase=Fase.FALLO), _salida_segura(), tuple(eventos), Motivo.OPERARIO_DENTRO)
        acciones = []
        for orden in nuevas:
            if orden.tipo == "retirar_bloqueo" and _personal_valida(orden) and orden.operario_id in estado.bloqueos:
                acciones.append((orden.operario_id, "RETIRAR"))
            elif orden.tipo == "retirar_bloqueo":
                motivo = Motivo.ID_DESCONOCIDA if orden.operario_id not in OPERARIOS else Motivo.TITULAR_DISTINTO
                return ResultadoPaso(estado, _salida_segura(), tuple(eventos), motivo)
        if not estado.bloqueos:
            return ResultadoPaso(replace(estado, fase=Fase.RESTABLECIMIENTO), Salidas(orden_puerta="CERRAR", alarma=False), tuple(eventos), None)
        return ResultadoPaso(estado, Salidas(acciones_bloqueo=tuple(acciones), alarma=False), tuple(eventos), Motivo.BLOQUEO_PENDIENTE if tipos and not acciones else None)

    # RESTABLECIMIENTO
    if estado.fase is Fase.RESTABLECIMIENTO:
        if snapshot.puerta_cerrada is not True:
            return ResultadoPaso(estado, Salidas(orden_puerta="CERRAR", alarma=False), tuple(eventos), None)
        if snapshot.seccionador_abierto is True:
            return ResultadoPaso(estado, Salidas(orden_seccionador="CERRAR", alarma=False), tuple(eventos), None)
        if "reset" in tipos and _seguro_para_listo(snapshot, estado, epsilon):
            return ResultadoPaso(replace(estado, fase=Fase.LISTO, reset_pendiente=True, intervencion_activa=False), Salidas(alarma=False), tuple(eventos), None)
        return ResultadoPaso(estado, Salidas(alarma=False), tuple(eventos), Motivo.FASE_INCORRECTA if tipos else None)

    return ResultadoPaso(replace(estado, fase=Fase.FALLO), _salida_segura(), tuple(eventos), Motivo.DATO_INVALIDO)
