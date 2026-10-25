"""Tipos sin efectos externos para el supervisor de enclavamiento."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from enum import Enum
from typing import FrozenSet, Optional, Sequence


OPERARIOS: FrozenSet[int] = frozenset({1, 2})


class Fase(str, Enum):
    INICIO_SEGURO = "INICIO_SEGURO"
    LISTO = "LISTO"
    MARCHA = "MARCHA"
    PARADA_SOLICITADA = "PARADA_SOLICITADA"
    AISLAMIENTO = "AISLAMIENTO"
    BLOQUEO = "BLOQUEO"
    VERIFICACION_CERO = "VERIFICACION_CERO"
    MANTENIMIENTO = "MANTENIMIENTO"
    LIBERACION = "LIBERACION"
    RESTABLECIMIENTO = "RESTABLECIMIENTO"
    FALLO = "FALLO"


class Motivo(str, Enum):
    DATO_INVALIDO = "DATO_INVALIDO"
    DATO_CADUCADO = "DATO_CADUCADO"
    EMERGENCIA_ACTIVA = "EMERGENCIA_ACTIVA"
    WATCHDOG_CADUCADO = "WATCHDOG_CADUCADO"
    PRESENCIA_PELIGROSA = "PRESENCIA_PELIGROSA"
    CONTACTO_NO_ABRE = "CONTACTO_NO_ABRE"
    AISLAMIENTO_NO_CONFIRMADO = "AISLAMIENTO_NO_CONFIRMADO"
    ENERGIA_RESIDUAL = "ENERGIA_RESIDUAL"
    BLOQUEO_PENDIENTE = "BLOQUEO_PENDIENTE"
    OPERARIO_DENTRO = "OPERARIO_DENTRO"
    TITULAR_DISTINTO = "TITULAR_DISTINTO"
    FASE_INCORRECTA = "FASE_INCORRECTA"
    START_NO_NUEVO = "START_NO_NUEVO"


@dataclass(frozen=True)
class EventoRfid:
    event_id: str
    operario_id: int
    accion: str  # ingreso o salida


@dataclass(frozen=True)
class Snapshot:
    tick: int
    t_sim_s: float
    laser_ocupado: Optional[bool]
    barrera_libre: Optional[bool]
    puerta_cerrada: Optional[bool]
    contacto_cerrado: Optional[bool]
    seccionador_abierto: Optional[bool]
    bloqueos_confirmados: Optional[FrozenSet[int]]
    velocidad_m_s: Optional[float]
    emergencia: Optional[bool]
    fallo_watchdog: Optional[bool]
    heartbeat_vigente: Optional[bool]
    sensor_valid: bool
    sensor_age_s: Optional[float]
    rfid_eventos: Sequence[EventoRfid] = field(default_factory=tuple)


@dataclass(frozen=True)
class Orden:
    command_id: str
    tipo: str
    operario_id: Optional[int] = None
    solicitante_id: Optional[int] = None


@dataclass(frozen=True)
class Estado:
    fase: Fase = Fase.INICIO_SEGURO
    ocupantes: FrozenSet[int] = field(default_factory=frozenset)
    bloqueos: FrozenSet[int] = field(default_factory=frozenset)
    reset_pendiente: bool = False
    intervencion_activa: bool = False
    comandos_vistos: FrozenSet[str] = field(default_factory=frozenset)
    eventos_vistos: FrozenSet[str] = field(default_factory=frozenset)

    def con_snapshot(self, snapshot: Snapshot) -> "Estado":
        """Incorpora únicamente eventos RFID válidos y confirmaciones físicas."""
        ocupantes = set(self.ocupantes)
        vistos = set(self.eventos_vistos)
        for evento in snapshot.rfid_eventos:
            if evento.event_id in vistos or evento.operario_id not in OPERARIOS:
                continue
            vistos.add(evento.event_id)
            if evento.accion == "ingreso":
                ocupantes.add(evento.operario_id)
            elif evento.accion == "salida":
                ocupantes.discard(evento.operario_id)
        bloqueos = self.bloqueos if snapshot.bloqueos_confirmados is None else snapshot.bloqueos_confirmados
        return replace(self, ocupantes=frozenset(ocupantes), bloqueos=frozenset(bloqueos), eventos_vistos=frozenset(vistos))


@dataclass(frozen=True)
class Salidas:
    orden_contactor: bool = False
    permiso_acceso: bool = False
    orden_puerta: str = "MANTENER"
    orden_seccionador: str = "MANTENER"
    acciones_bloqueo: tuple[tuple[int, str], ...] = ()
    reset_watchdog: bool = False
    alarma: bool = True


@dataclass(frozen=True)
class ResultadoPaso:
    estado: Estado
    salidas: Salidas
    eventos: tuple[str, ...]
    motivo: Optional[Motivo]
