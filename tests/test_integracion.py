from software.adaptador import PlantaDeterminista
from software.main import ejecutar_ciclo
from software.monitores import evaluar
from software.estado import Estado, Fase, Orden


def test_integracion_reset_start_activa_planta_sin_ocupar_zona():
    planta = PlantaDeterminista()
    estado = Estado()
    reset, _, _ = ejecutar_ciclo(estado, planta, [Orden("reset-1", "reset")])
    start, _, verdad = ejecutar_ciclo(reset.estado, planta, [Orden("start-1", "start")])
    assert start.estado.fase is Fase.MARCHA
    assert verdad["potencia_real"] is True
    assert evaluar(verdad) == []


def test_integracion_watchdog_lleva_a_fallo_y_corte():
    planta = PlantaDeterminista(fallo_watchdog=True, contacto_cerrado=True, velocidad_m_s=0.5)
    resultado, _, verdad = ejecutar_ciclo(Estado(fase=Fase.MARCHA), planta, [])
    assert resultado.estado.fase is Fase.FALLO
    assert verdad["potencia_real"] is False


def test_integracion_contacto_pegado_conserva_fallo_fisico_observable():
    planta = PlantaDeterminista(contacto_cerrado=True, contacto_pegado=True, velocidad_m_s=0.5)
    resultado, _, verdad = ejecutar_ciclo(Estado(fase=Fase.PARADA_SOLICITADA), planta, [])
    assert resultado.estado.fase is Fase.PARADA_SOLICITADA
    assert verdad["potencia_real"] is True
