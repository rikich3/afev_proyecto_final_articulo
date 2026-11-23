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


def test_fronteras_del_sensor_y_contacto():
    from dataclasses import replace
    from software.estado import Motivo

    muestra = PlantaDeterminista(contacto_cerrado=True, velocidad_m_s=0.5).snapshot()
    for edad, caducado in ((0.04, False), (0.06, True), (0.08, True)):
        r = step(Estado(fase=Fase.MARCHA), replace(muestra, sensor_age_s=edad), [])
        assert (r.motivo is Motivo.DATO_CADUCADO) == caducado
        assert r.salidas.orden_contactor is not caducado
    for edad, vencido in ((0.04, False), (0.06, True), (0.08, True)):
        estado = Estado(fase=Fase.PARADA_SOLICITADA, corte_desde_s=0.0)
        r = step(estado, replace(muestra, t_sim_s=edad), [])
        assert (r.motivo is Motivo.CONTACTO_NO_ABRE) == vencido
        assert not r.salidas.orden_contactor


def test_fronteras_de_velocidad_y_prioridad_de_mantenimiento():
    for v, parada in ((0.0, True), (0.001, True), (0.002, False), (-0.002, False)):
        s = PlantaDeterminista(velocidad_m_s=v).snapshot()
        r = step(Estado(fase=Fase.PARADA_SOLICITADA, intervencion_activa=True), s, [])
        assert (r.estado.fase is Fase.AISLAMIENTO) == parada
    s = PlantaDeterminista().snapshot()
    for acciones in (("start", "solicitar_mantenimiento"), ("solicitar_mantenimiento", "start")):
        r = step(Estado(fase=Fase.LISTO, reset_pendiente=True), s,
                 [orden(i, tipo) for i, tipo in enumerate(acciones)])
        assert r.estado.fase is Fase.PARADA_SOLICITADA
        assert not r.salidas.orden_contactor
