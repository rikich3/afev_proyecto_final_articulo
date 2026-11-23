"""Interfaz ZeroMQ entre el supervisor y la escena de CoppeliaSim."""

from dataclasses import asdict
from math import radians
from pathlib import Path

from .estado import EventoRfid, Salidas, Snapshot

RAIZ = Path(__file__).resolve().parents[1]
ESCENA_BASE = RAIZ / "simulacion/mina_modelada.ttt"
SCRIPTS = tuple(RAIZ / "simulacion/scripts" / f"{nombre}.lua" for nombre in ("watchdog", "planta"))


def conectar(puerto):
    import zmq
    from coppeliasim_zmqremoteapi_client import RemoteAPIClient

    cliente = RemoteAPIClient(host="127.0.0.1", port=puerto)
    for opcion, valor in ((zmq.RCVTIMEO, 5000), (zmq.SNDTIMEO, 5000), (zmq.LINGER, 0)):
        cliente.socket.setsockopt(opcion, valor)
    return cliente, cliente.require("sim")


class PlantaCoppelia:
    def __init__(self, puerto):
        self.puerto = puerto
        self.cliente, self.sim = conectar(puerto)
        self.sesion, self.secuencia = 0, 0

    def preparar(self, parametros, guardar_escena=None):
        sim = self.sim
        sim.loadScene(str(ESCENA_BASE))
        sim.setFloatParam(sim.floatparam_simulation_time_step, parametros["step_s"])
        dt = sim.getFloatParam(sim.floatparam_simulation_time_step)
        if abs(dt - parametros["step_s"]) > 1e-6:
            raise RuntimeError(f"Paso de simulación inesperado: {dt}")
        mina = sim.getObject("/mina")
        sim.writeCustomTableData(mina, "parametros_banco", parametros)
        fuente = "\n".join(archivo.read_text(encoding="utf-8") for archivo in SCRIPTS)
        self.script = sim.createScript(sim.scripttype_simulation, fuente, 0, "lua")
        sim.setObjectAlias(self.script, "PlantaAFEV")
        sim.setObjectParent(self.script, mina, True)
        sim.setBoolParam(sim.boolparam_realtime_simulation, False)
        if guardar_escena is not None:
            sim.saveScene(str(guardar_escena.resolve()))
        self.sesion, self.secuencia = 0, 0
        sim.setStepping(True)
        sim.startSimulation()
        sim.step()
        self.nueva_sesion()
        self.sim.step()

    def llamar(self, funcion, *args):
        return self.sim.callScriptFunction(funcion, self.script, *args)

    def nueva_sesion(self):
        self.sesion += 1
        self.secuencia = 0
        if not self.llamar("nuevaSesion", self.sesion):
            raise RuntimeError("Sesión rechazada")
        self.latido()

    def latido(self):
        self.secuencia += 1
        if not self.llamar("latido", self.sesion, self.secuencia):
            raise RuntimeError("Latido rechazado")

    def snapshot(self):
        muestra = self.llamar("tomarMuestra")
        muestra["bloqueos_confirmados"] = frozenset(muestra["bloqueos_confirmados"])
        muestra["rfid_eventos"] = tuple(EventoRfid(**e) for e in muestra["rfid_eventos"])
        return Snapshot(**muestra)

    def avanzar(self, salidas: Salidas):
        orden = asdict(salidas)
        orden["acciones_bloqueo"] = [list(par) for par in salidas.acciones_bloqueo]
        if not self.llamar("ordenar", self.sesion, orden):
            raise RuntimeError("Orden rechazada por el canal de actuación")
        self.sim.step()
        return self.llamar("verdad")

    def capturar(self, destino):
        sim = self.sim
        sensor = sim.createVisionSensor(
            1 | 2, [1280, 900, 0, 0],
            [0.05, 30.0, radians(49), 0.1, 0.1, 0.1, 0, 0, 0, 0, 0],
        )
        camara = sim.getObject("/DefaultCamera")
        sim.setObjectPose(sensor, sim.getObjectPose(camara, sim.handle_world), sim.handle_world)
        sim.handleVisionSensor(sensor)
        datos, resolucion = sim.getVisionSensorImg(sensor)
        destino.parent.mkdir(parents=True, exist_ok=True)
        sim.saveImage(datos, resolucion, 0, str(destino.resolve()), 30)
        sim.removeObjects([sensor])
        if not destino.is_file() or not destino.stat().st_size:
            raise RuntimeError("CoppeliaSim no guardó la captura")

    def detener(self):
        import time

        self.sim.stopSimulation()
        fin = time.monotonic() + 5
        while self.sim.getSimulationState() != self.sim.simulation_stopped:
            if time.monotonic() >= fin:
                raise RuntimeError("No se detuvo la simulación")
            time.sleep(0.02)
        self.sim.setStepping(False)
