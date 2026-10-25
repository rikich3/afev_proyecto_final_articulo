from software.adaptador import PlantaDeterminista
from software.controlador import step
from software.estado import Estado, Fase, Orden


def orden(i, tipo):
    return Orden(command_id=f"c-{i}", tipo=tipo)


def test_reset_y_start_requieren_dos_flancos():
    planta = PlantaDeterminista()
    estado = Estado()
    primero = step(estado, planta.snapshot(), [orden(1, "reset")])
    assert primero.estado.fase is Fase.LISTO
    segundo = step(primero.estado, planta.snapshot(), [orden(2, "start")])
    assert segundo.estado.fase is Fase.MARCHA
    assert segundo.salidas.orden_contactor is True


def test_presencia_con_potencia_enclava_fallo():
    planta = PlantaDeterminista(contacto_cerrado=True, ocupantes={1}, velocidad_m_s=0.5)
    resultado = step(Estado(fase=Fase.MARCHA), planta.snapshot(), [])
    assert resultado.estado.fase is Fase.FALLO
    assert resultado.salidas.orden_contactor is False


def test_un_bloqueo_no_autoriza_mantenimiento():
    planta = PlantaDeterminista(seccionador_abierto=True, bloqueos={1})
    resultado = step(Estado(fase=Fase.BLOQUEO, bloqueos=frozenset({1})), planta.snapshot(), [])
    assert resultado.estado.fase is Fase.BLOQUEO
    assert resultado.salidas.permiso_acceso is False


def test_reset_no_ignora_presencia_fisica_sin_evento_rfid():
    planta = PlantaDeterminista(ocupantes={1})
    resultado = step(Estado(), planta.snapshot(), [orden(3, "reset")])
    assert resultado.estado.fase is Fase.INICIO_SEGURO
    assert resultado.salidas.orden_contactor is False
