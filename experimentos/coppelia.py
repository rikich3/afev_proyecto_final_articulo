"""Ejecuta el catálogo en CoppeliaSim y verifica los oráculos de cada caso."""

from __future__ import annotations

import argparse
from collections import deque
from dataclasses import asdict, replace
import json
from math import ceil
from pathlib import Path
import platform
import random
from time import monotonic, monotonic_ns, sleep
from uuid import uuid4

from software.controlador import reiniciar, step
from software.coppelia import ESCENA_BASE, RAIZ, SCRIPTS, PlantaCoppelia, conectar
from software.estado import Estado, Fase, Motivo, Orden
from software.monitores import evaluar
from software.telemetria import EscritorJsonl, actualizar_indice_manifiestos, escribir_manifiesto, hash_archivo

CATALOGO = RAIZ / "experimentos/escenarios.json"
FUENTES = (CATALOGO, ESCENA_BASE, *SCRIPTS, RAIZ / "requirements.txt", Path(__file__),
           *(RAIZ / "software" / nombre for nombre in
             ("estado.py", "controlador.py", "monitores.py", "coppelia.py")))
POTENCIA_FORZADA = {"SC-12-a", "SC-12-b"}
TOL = 1e-8


def normalizar(verdad):
    for campo in ("ocupantes_reales", "bloqueos_reales"):
        verdad[campo] = list(verdad[campo])
    return verdad


class Caso:
    def __init__(self, planta, config, escritor, run_id, caso, semilla):
        self.planta, self.config, self.escritor = planta, config, escritor
        self.run_id, self.caso, self.semilla = run_id, caso, semilla
        self.estado = Estado()
        self.serie = 0
        self.ultima_orden = self.ultimo_rfid = self.repetir_rfid = None
        self.fallos = {}
        self.muestras = deque(maxlen=20)
        self.congelado = None
        self.filas = []
        self.etapa = "preparacion"
        self.resultado = None
        self.observaciones = {}
        self.capturas = {}
        self.verdad = normalizar(self.planta.llamar("verdad"))

    def guardar(self, verdad, *, antes=None, muestra=None, ordenes=(), resultado=None, evento=None):
        verdad = normalizar(verdad)
        fila = {
            "esquema_version": 1, "run_id": self.run_id, "scenario_id": self.caso,
            "seed": self.semilla, "tick": verdad["tick"], "t_sim_s": verdad["t_sim_s"],
            "t_wall_ns": monotonic_ns(), "etapa": self.etapa,
            "inputs": asdict(muestra) if muestra else None, "physical_truth": verdad,
            "state_before": asdict(antes) if antes else None,
            "state_after": asdict(resultado.estado) if resultado else None,
            "outputs": asdict(resultado.salidas) if resultado else None,
            "diagnostico": resultado.motivo if resultado else None,
            "eventos": resultado.eventos if resultado else (),
            "ordenes": [asdict(o) for o in ordenes], "event": evento,
            "violated_properties": evaluar(verdad),
        }
        self.verdad = verdad
        self.filas.append(fila)
        self.escritor.escribir(fila)
        return fila

    def orden(self, tipo, operario_id=None, solicitante_id=None):
        self.serie += 1
        return Orden(f"cmd-{self.serie}", tipo, operario_id, solicitante_id)

    def muestra(self):
        cruda = self.planta.snapshot()
        self.muestras.append(cruda)
        eventos = tuple(e for e in cruda.rfid_eventos if not (
            e.accion == "salida" and e.operario_id == self.fallos.get("perder_evento_rfid_salida")
        ))
        if self.repetir_rfid is not None:
            eventos += (self.repetir_rfid,)
            self.repetir_rfid = None
        if cruda.rfid_eventos:
            self.ultimo_rfid = cruda.rfid_eventos[-1]
        cambios = {"rfid_eventos": eventos}
        retardo = self.fallos.get("retardo_senal", 0)
        if retardo:
            origen = self.muestras[max(0, len(self.muestras) - 1 - retardo)]
            cambios.update(laser_ocupado=origen.laser_ocupado,
                           sensor_age_s=cruda.t_sim_s - origen.t_sim_s)
        if "sensor_congelado" in self.fallos:
            if self.congelado is None:
                self.congelado = cruda
            cambios.update(laser_ocupado=self.congelado.laser_ocupado,
                           sensor_age_s=cruda.t_sim_s - self.congelado.t_sim_s)
        if "sensor_invalido" in self.fallos:
            cambios.update(sensor_valid=False, laser_ocupado=None)
        if "presencia_falsa_libre" in self.fallos:
            cambios["laser_ocupado"] = False
        if "todos_canales_ocultando_presencia" in self.fallos:
            cambios.update(laser_ocupado=False, barrera_libre=True, rfid_eventos=())
        if "feedback_contacto_incorrecto" in self.fallos:
            cambios["contacto_cerrado"] = self.fallos["feedback_contacto_incorrecto"]
        if "bloqueos_desconocidos" in self.fallos:
            cambios["bloqueos_confirmados"] = None
        return replace(cruda, **cambios)

    def ciclo(self, *ordenes):
        self.planta.latido()
        muestra = self.muestra()
        c = self.config
        antes = self.estado
        self.resultado = step(
            antes, muestra, ordenes, sensor_timeout_s=c["sensor_timeout_s"],
            contact_open_timeout_s=c["contact_open_timeout_s"],
            epsilon=c["epsilon_parada_m_s"], parada_max_s=c["parada_max_s"],
        )
        self.estado = self.resultado.estado
        if ordenes:
            self.ultima_orden = ordenes[-1]
        verdad = self.planta.avanzar(self.resultado.salidas)
        self.guardar(verdad, antes=antes, muestra=muestra, ordenes=ordenes, resultado=self.resultado)
        if verdad["t_sim_s"] > self.config["scenario_timeout_s"]:
            raise AssertionError("Se agotó el horizonte del caso")
        return self.resultado

    def enviar(self, tipo, id_=None, solicitante=None):
        return self.ciclo(self.orden(tipo, id_, solicitante))

    def esperar(self, condicion, limite=2.0):
        for _ in range(ceil(limite / self.config["step_s"]) + 1):
            if self.confirmacion(condicion):
                return
            self.ciclo()
        raise AssertionError(f"Confirmación ausente: {condicion}")

    def confirmacion(self, condicion):
        v = self.verdad
        if condicion in Fase.__members__:
            return self.estado.fase is Fase[condicion]
        condiciones = {
            "contacto_abierto": not v["contacto_real_cerrado"],
            "parada": abs(v["velocidad_real_m_s"]) <= self.config["epsilon_parada_m_s"],
            "seccionador_abierto": v["seccionador_real_abierto"],
            "permiso": v["permiso_efectivo"] and not v["puerta_real_cerrada"],
            "bloqueo_1_confirmado": 1 in v["bloqueos_reales"],
            "bloqueo_2_confirmado_y_parada": 2 in v["bloqueos_reales"] and
            abs(v["velocidad_real_m_s"]) <= self.config["epsilon_parada_m_s"],
            "bloqueos_confirmados=[2]": v["bloqueos_reales"] == [2],
            "equipo_restituido": v["puerta_real_cerrada"] and not v["seccionador_real_abierto"],
        }
        return condiciones[condicion]

    def mover(self, id_, entrada, forzar=False, avanzar=True):
        aceptado = self.planta.llamar("moverOperario", id_, entrada, forzar)
        self.guardar(self.planta.llamar("verdad"), evento={
            "tipo": "cruce", "id": id_, "entrada": entrada, "forzado": forzar,
            "aceptado": aceptado,
        })
        if avanzar:
            self.ciclo()
        return aceptado

    def aislar(self):
        self.enviar("solicitar_mantenimiento")
        self.esperar("AISLAMIENTO")
        self.enviar("abrir_seccionador")
        self.esperar("BLOQUEO")

    def preparar(self, fixture, esperado):
        fases = ("inicio_seguro", "listo", "marcha", "aislado",
                 "mantenimiento_ambos", "liberacion", "restablecimiento")
        nivel = fases.index(fixture)
        if nivel >= 1:
            self.enviar("reset")
        if nivel >= 2:
            self.enviar("start")
        if nivel >= 3:
            self.aislar()
        if nivel >= 4:
            for id_ in (1, 2):
                self.enviar("aplicar_bloqueo", id_, id_)
            self.esperar("permiso")
            for id_ in (1, 2):
                self.enviar("solicitar_ingreso", id_, id_)
                assert self.mover(id_, True), f"Ingreso de preparación rechazado: {id_}"
        if nivel >= 5:
            for id_ in (1, 2):
                assert self.mover(id_, False), f"Salida de preparación rechazada: {id_}"
            self.enviar("cerrar_acceso")
        if nivel >= 6:
            for id_ in (1, 2):
                self.enviar("retirar_bloqueo", id_, id_)
            self.esperar("equipo_restituido")
        observado = {
            "fase": self.estado.fase.value, "ocupantes": self.verdad["ocupantes_reales"],
            "bloqueos": self.verdad["bloqueos_reales"],
            "contacto_cerrado": self.verdad["contacto_real_cerrado"],
            "seccionador_abierto": self.verdad["seccionador_real_abierto"],
            "puerta_cerrada": self.verdad["puerta_real_cerrada"],
            "velocidad_m_s": self.verdad["velocidad_real_m_s"],
        }
        assert observado == esperado, f"Fixture {fixture}: {observado}"
        self.observaciones["fixture"] = observado
        self.etapa = "ensayo"

    def inyectar(self, paso, factores):
        tipo = paso["tipo"]
        valor = True
        if tipo in ("emergencia", "contacto_pegado"):
            valor = paso.get("activa", True)
            self.planta.llamar("forzarCondicion", tipo, valor)
        elif tipo == "reiniciar_controlador":
            anterior = self.planta.sesion
            self.planta.nueva_sesion()
            self.observaciones["sesion_anterior_rechazada"] = not self.planta.llamar("latido", anterior, 500)
            self.estado = reiniciar(self.estado)
            if paso.get("conservar_bloqueos") is False:
                self.fallos["bloqueos_desconocidos"] = True
        elif tipo in ("terminar_cliente", "repetir_heartbeat"):
            self.autonomo(tipo)
        else:
            valor = {
                "retardo_senal": factores.get("factor_retardo", 0) + factores.get("jitter_ticks", 0),
                "perder_evento_rfid_salida": paso.get("operario_id"),
                "feedback_contacto_incorrecto": paso.get("reportar_cerrado"),
            }.get(tipo, True)
            self.fallos[tipo] = valor
        if tipo not in ("terminar_cliente", "repetir_heartbeat"):
            self.guardar(self.planta.llamar("verdad"), evento={"tipo": tipo, "valor": valor})

    def autonomo(self, tipo):
        p = self.planta
        reloj_antes = p.llamar("verdad")
        ultimo = reloj_antes["ultimo_heartbeat_s"]
        if tipo == "repetir_heartbeat":
            self.observaciones["repeticion_rechazada"] = not p.llamar("latido", p.sesion, p.secuencia)
            assert abs(p.llamar("verdad")["ultimo_heartbeat_s"] - ultimo) < TOL
        congelado = self.caso == "SC-09-c"
        if not congelado:
            p.sim.setStepping(False)
        # Un cliente dedicado reanuda sin enviar latidos, pasos ni órdenes de actuadores.
        # El observador sólo consulta la escena y mantiene abierto su propio socket.
        p.cliente.socket.close(linger=0)
        observador, sim = conectar(p.puerto)
        self.observador = observador
        self.sim_observador = sim
        if congelado:
            sleep(0.18)
        else:
            fin = monotonic() + 5
            while sim.callScriptFunction("verdad", p.script)["t_sim_s"] < ultimo + 0.60 - TOL:
                if monotonic() > fin:
                    raise AssertionError("El reloj de la escena no alcanzó el horizonte autónomo")
        despues = sim.callScriptFunction("verdad", p.script)
        historia = sim.callScriptFunction("leerHistorial", p.script, reloj_antes["tick"])
        for fila in historia:
            self.guardar(fila, evento={"tipo": "observacion_autonoma"})
        self.guardar(despues, evento={"tipo": tipo})
        self.observaciones.update(reloj_avanza=despues["tick"] > reloj_antes["tick"],
                                  ultimo_heartbeat_s=ultimo,
                                  fallo_watchdog_s=despues.get("fallo_watchdog_s"),
                                  apertura_s=despues.get("apertura_s"),
                                  parada_s=despues.get("parada_s"))
        self.observaciones["entrada_denegada"] = despues["permiso_efectivo"] is False

    def ejecutar_paso(self, paso, factores):
        accion = paso["accion"]
        if accion == "orden":
            self.enviar(paso["tipo"], paso["operario_id"], paso["solicitante_id"])
        elif accion == "ordenes_simultaneas":
            tipos = paso["tipos"]
            if factores.get("orden_lista") == "inverso":
                tipos = tipos[::-1]
            self.ciclo(*(self.orden(tipo) for tipo in tipos))
        elif accion == "esperar_confirmacion":
            self.esperar(paso["condicion"], paso["limite_s"])
            if paso["condicion"] == "seccionador_abierto":
                self.esperar("BLOQUEO", paso["limite_s"])
            if paso["condicion"] == "bloqueo_2_confirmado_y_parada":
                self.esperar("permiso", paso["limite_s"])
        elif accion == "inyectar_fallo":
            self.inyectar(paso, factores)
        elif accion == "planta":
            tipo, id_ = paso["tipo"], paso.get("operario_id")
            if tipo in ("ingreso_normal", "salida_normal", "forzar_ingreso", "intrusion_con_rfid"):
                aceptado = self.mover(id_, tipo != "salida_normal",
                                     tipo in ("forzar_ingreso", "intrusion_con_rfid"),
                                     avanzar=tipo != "intrusion_con_rfid")
                assert aceptado, f"El estímulo físico {tipo} fue rechazado"
            elif tipo == "aproximacion_al_acceso":
                self.observaciones["entrada_denegada"] = not self.planta.llamar("aproximar", id_)
                self.ciclo()
            elif tipo == "mantener_boton_start":
                start = next(o for fila in self.filas for o in fila["ordenes"] if o["tipo"] == "start")
                for _ in range(paso["ticks"]):
                    self.ciclo(Orden(**start))
            elif tipo == "repetir_ultimo_command_id":
                self.ciclo(self.ultima_orden)
            elif tipo == "repetir_ultimo_event_id_rfid":
                self.repetir_rfid = self.ultimo_rfid
                self.ciclo()
            elif tipo == "mantener_movimiento_residual":
                self.planta.llamar("forzarCondicion", "movimiento_residual", paso["velocidad_m_s"])
                self.guardar(self.planta.llamar("verdad"), evento=paso)
                self.ciclo()
            else:
                raise ValueError(f"Estímulo desconocido: {tipo}")
        else:
            raise ValueError(f"Acción desconocida: {accion}")

    def cerrar(self):
        if hasattr(self, "sim_observador"):
            self.sim_observador.stopSimulation()
            fin = monotonic() + 2
            while self.sim_observador.getSimulationState() != self.sim_observador.simulation_stopped:
                if monotonic() >= fin:
                    raise RuntimeError("La escena no se detuvo después del ensayo autónomo")
                sleep(0.02)
            self.observador.socket.close(linger=0)
        else:
            self.planta.detener()
        self.planta.cliente.socket.close(linger=0)

    def comprobar(self, factores, capturar):
        id_ = self.caso
        filas = [f for f in self.filas if f["etapa"] == "ensayo"]
        v = self.verdad
        potencias = [f["physical_truth"]["potencia_real"] for f in filas]
        fallos = [f for f in filas if f["state_after"] and f["state_after"]["fase"] is Fase.FALLO]
        motivos = {f["diagnostico"] for f in filas}
        fisica = any(f["violated_properties"] for f in filas)
        c = self.config
        if id_ not in POTENCIA_FORZADA:
            assert not fisica, "Incumplimiento de exclusión presencia–potencia"
        assert all(not f["physical_truth"]["permiso_efectivo"] or (
            not f["physical_truth"]["contacto_real_cerrado"]
            and f["physical_truth"]["seccionador_real_abierto"]
            and abs(f["physical_truth"]["velocidad_real_m_s"]) <= c["epsilon_parada_m_s"]
            and f["physical_truth"]["bloqueos_reales"] == [1, 2]
        ) for f in filas), "Permiso de acceso sin protecciones confirmadas"

        if id_ == "SC-01-a":
            assert self.estado.fase is Fase.MARCHA and potencias == [False, True]
        elif id_ == "SC-01-b":
            assert self.estado.fase is Fase.LISTO and not any(potencias)
            assert any("ORDEN_REPETIDA_O_SIN_ID" in f["eventos"] for f in filas)
        elif id_ == "SC-02-a":
            assert self.estado.fase is Fase.MANTENIMIENTO and v["ocupantes_reales"] == [1, 2]
            assert not v["potencia_real"] and v["permiso_efectivo"]
            assert v["apertura_s"] < v["parada_s"]
            self.observaciones["apertura_desde_orden_ms"] = round(1000 * (
                v["apertura_s"] - filas[0]["inputs"]["t_sim_s"]), 6)
            self.observaciones["parada_desde_apertura_ms"] = round(1000 * (
                v["parada_s"] - v["apertura_s"]), 6)
            if capturar:
                self.captura("mantenimiento_ambos", capturar)
        elif id_ == "SC-03-a":
            assert v["ocupantes_reales"] == [2] and v["bloqueos_reales"] == [1, 2]
            assert Motivo.FASE_INCORRECTA in motivos and not any(potencias)
            if capturar:
                self.captura("rearme_inhibido", capturar)
        elif id_ == "SC-03-b":
            assert v["bloqueos_reales"] == [2] and v["seccionador_real_abierto"]
            assert not any(potencias)
        elif id_ in ("SC-02-b", "SC-04-b"):
            assert v["seccionador_real_abierto"] and v["puerta_real_cerrada"] and not any(potencias)
            assert not self.mover(1, True)
        elif id_ == "SC-04-a":
            assert v["ocupantes_reales"] == v["bloqueos_reales"] == [1, 2]
            assert Motivo.OPERARIO_DENTRO in motivos and not any(potencias)
        elif id_.startswith("SC-05"):
            assert not any(potencias)
            assert all(not f["outputs"]["orden_contactor"] for f in filas if f["outputs"])
            if id_ == "SC-05-a":
                assert Motivo.START_NO_NUEVO in motivos
            if id_ == "SC-05-b":
                assert self.estado.fase is Fase.PARADA_SOLICITADA
            if id_ in ("SC-05-c", "SC-05-d"):
                assert fallos and not v["permiso_efectivo"]
            if id_ == "SC-05-e":
                assert v["ocupantes_reales"] == [1] and self.estado.fase is not Fase.MARCHA
        elif id_ == "SC-06-a":
            edad = (factores.get("factor_retardo", 0) + factores.get("jitter_ticks", 0)) * c["step_s"]
            esperado = edad + TOL >= c["sensor_timeout_s"]
            assert self.observaciones["entrada_denegada"]
            inicio_retardo = next(i for i, f in enumerate(filas)
                                  if f["event"] and f["event"]["tipo"] == "retardo_senal")
            muestras = [f["inputs"] for f in filas[inicio_retardo:] if f["inputs"]]
            assert all(abs(s["sensor_age_s"] - edad) < TOL for s in muestras)
            assert (Motivo.DATO_CADUCADO in motivos) == esperado
            self.observaciones["edad_senal_ms"] = round(1000 * edad, 6)
            if esperado:
                orden_corte = next(f for f in filas if f["diagnostico"] is Motivo.DATO_CADUCADO)
                latencia = v["apertura_s"] - orden_corte["inputs"]["t_sim_s"]
                assert 0 <= latencia <= c["incident_cut_budget_s"] + TOL
                assert not v["potencia_real"]
                self.observaciones["corte_desde_caducidad_ms"] = round(1000 * latencia, 6)
        elif id_ == "SC-07-a":
            assert Motivo.DATO_INVALIDO in motivos and fallos and not v["potencia_real"]
            assert not self.mover(1, True)
        elif id_ == "SC-07-b":
            edades = [f["inputs"]["sensor_age_s"] for f in filas if f["inputs"]]
            assert edades[0] == 0 and all(a < b for a, b in zip(edades, edades[1:]))
            edad_fallo = fallos[0]["inputs"]["sensor_age_s"]
            assert abs(edad_fallo - c["sensor_timeout_s"]) < TOL
            assert not v["potencia_real"] and Motivo.DATO_CADUCADO in motivos
            self.observaciones["edad_diagnostico_ms"] = round(1000 * edad_fallo, 6)
        elif id_ == "SC-07-c":
            assert v["ocupantes_reales"] == [] and self.estado.ocupantes == {1}
            assert fallos and not any(potencias)
        elif id_ == "SC-07-d":
            assert Motivo.DISCREPANCIA in motivos and fallos and not any(potencias)
        elif id_ in ("SC-08-a", "SC-08-b"):
            assert fallos and Motivo.CONTACTO_NO_ABRE in motivos
            assert all(not f["outputs"]["orden_contactor"] for f in filas if f["outputs"])
            assert not self.mover(1, True)
            pegado = id_ == "SC-08-a"
            assert (v.get("apertura_s") is None) == pegado
            assert v["potencia_real"] == pegado
            self.observaciones.update(
                estado_respuesta="no_respondido" if pegado else "respondido",
                apertura_s=v.get("apertura_s"),
            )
        elif id_.startswith("SC-09"):
            o = self.observaciones
            if id_ == "SC-09-c":
                assert not o["reloj_avanza"] and not v["fallo_watchdog"] and v["potencia_real"]
                return "no_evaluable"
            assert o["reloj_avanza"] and v["fallo_watchdog"] and not v["potencia_real"]
            assert o["entrada_denegada"] and o["parada_s"] is not None
            edad = o["fallo_watchdog_s"] - o["ultimo_heartbeat_s"]
            latencia = o["apertura_s"] - o["ultimo_heartbeat_s"]
            assert abs(edad - c["heartbeat_timeout_s"]) < TOL
            for desplazamiento, estado in ((-1, False), (0, True), (1, True)):
                frontera = o["fallo_watchdog_s"] + desplazamiento * c["step_s"]
                assert any(abs(f["t_sim_s"] - frontera) < TOL
                           and f["physical_truth"]["fallo_watchdog"] is estado for f in filas)
            assert edad <= latencia + TOL and latencia <= c["watchdog_cut_budget_s"] + TOL
            if id_ == "SC-09-b":
                assert o["repeticion_rechazada"]
            o.update(caducidad_ms=round(1000 * edad, 6),
                     corte_desde_latido_ms=round(1000 * latencia, 6),
                     parada_desde_apertura_ms=round(1000 * (o["parada_s"] - o["apertura_s"]), 6))
        elif id_ in ("SC-10-a", "SC-10-b"):
            assert v["bloqueos_reales"] == [1, 2]
            assert (Motivo.ID_DESCONOCIDA if id_ == "SC-10-a" else Motivo.TITULAR_DISTINTO) in motivos
        elif id_ == "SC-10-c":
            assert v["bloqueos_reales"] == [2]
            assert any("ORDEN_REPETIDA_O_SIN_ID" in f["eventos"] for f in filas)
        elif id_ == "SC-10-d":
            assert self.estado.ocupantes == {1, 2} and v["bloqueos_reales"] == [1, 2]
            assert any(e.startswith("RFID_REPETIDO:") for f in filas for e in f["eventos"])
        elif id_.startswith("SC-11"):
            assert self.observaciones["sesion_anterior_rechazada"] and fallos
            assert not fallos[0]["outputs"]["orden_contactor"] and not v["potencia_real"]
            assert not v["permiso_efectivo"] and not self.estado.reset_pendiente
            if id_ in ("SC-11-b", "SC-11-c"):
                assert v["bloqueos_reales"] == [1, 2] and self.estado.ocupantes == {1, 2}
                if id_ == "SC-11-c":
                    assert fallos[-1]["inputs"]["bloqueos_confirmados"] is None
                assert self.mover(1, False) and self.verdad["ocupantes_reales"] == [2]
        elif id_ in POTENCIA_FORZADA:
            assert fisica and v["ocupantes_reales"] == [1]
            assert any(f["physical_truth"]["potencia_real"] for f in filas)
            if id_ == "SC-12-b":
                assert any(f["inputs"] and not f["inputs"]["laser_ocupado"] and
                           f["violated_properties"] for f in filas)
        elif id_ == "SC-13-a":
            assert fallos and not fallos[-1]["state_after"]["reset_pendiente"]
            assert not any(potencias)
            self.planta.llamar("forzarCondicion", "emergencia", False)
            self.enviar("start")
            assert not self.verdad["potencia_real"]
            self.enviar("reset")
            self.enviar("start")
            assert self.verdad["potencia_real"]
        elif id_ == "SC-13-b":
            assert self.estado.fase is Fase.FALLO and Motivo.ENERGIA_RESIDUAL in motivos
            assert v["velocidad_real_m_s"] > c["epsilon_parada_m_s"]
            assert not v["seccionador_real_abierto"] and not v["permiso_efectivo"]
            assert not self.mover(1, True)
        else:
            raise ValueError(f"Oráculo ausente para {id_}")
        return "cumple_oraculo"

    def captura(self, nombre, carpeta):
        archivo = carpeta / (nombre + ".png")
        self.planta.capturar(archivo)
        self.capturas[nombre] = {
            "archivo": archivo.name, "sha256": hash_archivo(archivo),
            "tick": self.verdad["tick"], "t_sim_s": self.verdad["t_sim_s"],
        }


def ejecutar(puerto, destino, catalogo, caso, factores, grupo, semilla, escena=None, capturar=None):
    config = catalogo["parametros"] | {"step_s": factores.get("step_s", catalogo["parametros"]["step_s"])}
    run_id = f"{grupo}-{caso['id'].lower()}-{semilla if semilla is not None else 'fijo'}-{uuid4().hex[:8]}"
    traza = destino / "crudos" / (run_id + ".jsonl")
    planta = PlantaCoppelia(puerto)
    version = planta.sim.getStringProperty(planta.sim.handle_app, "productVersion")
    ensayo = None
    error = None
    clasificacion = "fallo_preparacion"
    try:
        planta.preparar(config, escena)
        ensayo = Caso(planta, config, EscritorJsonl(traza), run_id, caso["id"], semilla)
        ensayo.guardar(ensayo.verdad, evento={"tipo": "inicio"})
        ensayo.preparar(caso["fixture"], catalogo["fixtures"][caso["fixture"]])
        profundidad = (factores.get("factor_retardo", 0) + factores.get("jitter_ticks", 0)
                       if caso["id"] == "SC-06-a" else 0)
        ensayo.etapa = "preparacion"
        for _ in range(profundidad + factores.get("jitter_ticks", 0)):
            ensayo.ciclo()
        ensayo.etapa = "ensayo"
        for paso in caso["pasos"]:
            if caso["id"] == "SC-02-a" and paso.get("tipo") == "abrir_seccionador":
                ensayo.esperar("AISLAMIENTO")
            ensayo.ejecutar_paso(paso, factores)
        if not hasattr(ensayo, "sim_observador"):
            espera = 1
            if caso["id"] in ("SC-06-a", "SC-07-a", "SC-07-b", "SC-08-a", "SC-08-b", "SC-11-a", "SC-12-a", "SC-12-b"):
                espera = ceil(0.20 / config["step_s"])
            if caso["id"] == "SC-13-b":
                espera = ceil(config["parada_max_s"] / config["step_s"])
            for _ in range(espera):
                # SC-01-a conserva el par explícito reset/start como único estímulo.
                if caso["id"] != "SC-01-a":
                    ensayo.ciclo()
        clasificacion = ensayo.comprobar(factores, capturar)
    except (AssertionError, KeyError, IndexError) as exc:
        error = str(exc) or "Un criterio del oráculo falló"
        if ensayo is not None and ensayo.etapa == "ensayo":
            clasificacion = "no_cumple_oraculo"
    finally:
        if ensayo is not None:
            ensayo.cerrar()
        else:
            planta.detener()

    if ensayo is None:
        raise RuntimeError(error or "No se pudo crear la traza")
    manifiesto = escribir_manifiesto(destino / "manifiestos" / (run_id + ".json"), {
        "run_id": run_id, "scenario_id": caso["id"], "seed": semilla, "campana": grupo,
        "tipo_ejecucion": "coppeliasim_zeromq", "resultados_experimentales": True,
        "coppeliasim": version, "python": platform.python_version(), "so": platform.platform(),
        "fuentes_sha256": {str(p.relative_to(RAIZ)): hash_archivo(p) for p in FUENTES},
        "parametros": config, "factores": factores, "oraculo_catalogo": caso["esperado"],
        "clasificacion": clasificacion, "error": error, "registros": len(ensayo.filas),
        "observaciones": ensayo.observaciones, "capturas": ensayo.capturas,
    }, traza)
    actualizar_indice_manifiestos(destino / "manifest.csv", manifiesto)
    print(run_id, clasificacion, error or "", flush=True)
    return clasificacion


def plan(catalogo, grupo, seleccion):
    escenarios = {s["id"]: s for s in catalogo["escenarios"]}
    casos = {c["id"]: c for s in escenarios.values() for c in s["casos"]}
    if seleccion:
        for id_ in seleccion:
            yield casos[id_], {}, None, "piloto"
        return
    if grupo in ("piloto", "todo"):
        for id_ in catalogo["piloto"]["casos"]:
            yield casos[id_], {}, None, "piloto"
    if grupo in ("determinista", "todo"):
        for s in escenarios.values():
            for caso in s["casos"]:
                for factores in (
                    [{"orden_lista": x} for x in ("original", "inverso")] if s["id"] == "SC-05"
                    else [{"factor_retardo": x} for x in (0, 1, 3)] if s["id"] == "SC-06"
                    else [{}]
                ):
                    yield caso, factores, None, "determinista"
    if grupo in ("estocastica", "todo"):
        reglas = catalogo["campana"]["estocastica"]
        for id_ in reglas["escenarios"]:
            s = escenarios[id_]
            elegibles = [c for c in s["casos"] if c["id"] in s.get("casos_estocasticos", casos)]
            for seed in reglas["semillas"]:
                rng = random.Random(seed)
                caso = rng.choice(elegibles)
                factores = {"factor_retardo": rng.choice((0, 1, 3))} if id_ == "SC-06" else {}
                factores["jitter_ticks"] = rng.choice(reglas["jitter_ticks"])
                yield caso, factores, seed, "estocastica"
    if grupo in ("sensibilidad", "todo"):
        for id_ in ("SC-06-a", "SC-09-a"):
            for dt in catalogo["campana"]["sensibilidad"]["step_s"]:
                factores = {"step_s": dt}
                if id_ == "SC-06-a":
                    factores["factor_retardo"] = round(0.06 / dt)
                yield casos[id_], factores, None, "sensibilidad"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--puerto", required=True, type=int)
    parser.add_argument("--output", type=Path, default=RAIZ / "buffer/coppelia")
    parser.add_argument("--grupo", choices=("piloto", "determinista", "estocastica", "sensibilidad", "todo"), default="piloto")
    parser.add_argument("--caso", action="append", help="Ejecuta un caso concreto")
    parser.add_argument("--guardar-escena", type=Path)
    parser.add_argument("--capturas", type=Path)
    args = parser.parse_args()
    catalogo = json.loads(CATALOGO.read_text(encoding="utf-8"))
    resultados = [
        ejecutar(args.puerto, args.output, catalogo, caso, factores, grupo, semilla,
                 escena=args.guardar_escena if i == 0 else None,
                 capturar=args.capturas if grupo == "determinista" or args.caso else None)
        for i, (caso, factores, semilla, grupo) in enumerate(plan(catalogo, args.grupo, args.caso))
    ]
    print(dict((e, resultados.count(e)) for e in sorted(set(resultados))), flush=True)
    return int(any(r not in ("cumple_oraculo", "no_evaluable") for r in resultados))


if __name__ == "__main__":
    raise SystemExit(main())
