"""Adaptador intercambiable para la planta.

`PlantaDeterminista` es un doble de prueba local. No representa CoppeliaSim ni
se usa como evidencia experimental; permite probar la secuencia del controlador
mientras se implementa la conexión ZeroMQ real.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .estado import EventoRfid, Salidas, Snapshot


@dataclass
class PlantaDeterminista:
    tick: int = 0
    t_sim_s: float = 0.0
    contacto_cerrado: bool = False
    seccionador_abierto: bool = False
    puerta_cerrada: bool = True
    bloqueos: set[int] = field(default_factory=set)
    ocupantes: set[int] = field(default_factory=set)
    velocidad_m_s: float = 0.0
    emergencia: bool = False
    fallo_watchdog: bool = False
    heartbeat_vigente: bool = True
    contacto_pegado: bool = False
    eventos_rfid: list[EventoRfid] = field(default_factory=list)

    def snapshot(self) -> Snapshot:
        return Snapshot(
            tick=self.tick, t_sim_s=self.t_sim_s,
            laser_ocupado=bool(self.ocupantes), barrera_libre=True,
            puerta_cerrada=self.puerta_cerrada, contacto_cerrado=self.contacto_cerrado,
            seccionador_abierto=self.seccionador_abierto,
            bloqueos_confirmados=frozenset(self.bloqueos), velocidad_m_s=self.velocidad_m_s,
            emergencia=self.emergencia, fallo_watchdog=self.fallo_watchdog,
            heartbeat_vigente=self.heartbeat_vigente, sensor_valid=True,
            sensor_age_s=0.0, rfid_eventos=tuple(self.eventos_rfid),
        )

    def avanzar(self, salidas: Salidas, step_s: float = 0.02) -> dict:
        if not self.contacto_pegado:
            self.contacto_cerrado = salidas.orden_contactor
        self.seccionador_abierto = True if salidas.orden_seccionador == "ABRIR" else (False if salidas.orden_seccionador == "CERRAR" else self.seccionador_abierto)
        self.puerta_cerrada = False if salidas.orden_puerta == "ABRIR" else (True if salidas.orden_puerta == "CERRAR" else self.puerta_cerrada)
        for operario, accion in salidas.acciones_bloqueo:
            if accion == "APLICAR": self.bloqueos.add(operario)
            if accion == "RETIRAR": self.bloqueos.discard(operario)
        self.velocidad_m_s = 0.5 if self.contacto_cerrado else 0.0
        self.tick += 1
        self.t_sim_s += step_s
        self.eventos_rfid.clear()
        return self.verdad_fisica()

    def verdad_fisica(self) -> dict:
        return {
            "tick": self.tick, "t_sim_s": self.t_sim_s,
            "ocupantes_reales": sorted(self.ocupantes), "potencia_real": self.contacto_cerrado,
            "velocidad_real_m_s": self.velocidad_m_s, "puerta_real_cerrada": self.puerta_cerrada,
            "seccionador_real_abierto": self.seccionador_abierto,
        }
