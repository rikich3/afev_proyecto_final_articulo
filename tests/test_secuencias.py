from software.adaptador import PlantaDeterminista
from software.controlador import step
from software.estado import Estado, Fase, Orden


def test_retiro_ajeno_se_rechaza_y_conserva_bloqueo():
    planta = PlantaDeterminista(seccionador_abierto=True, bloqueos={1, 2})
    orden = Orden(command_id="ret-1", tipo="retirar_bloqueo", operario_id=1, solicitante_id=2)
    resultado = step(Estado(fase=Fase.LIBERACION, bloqueos=frozenset({1, 2})), planta.snapshot(), [orden])
    assert resultado.estado.bloqueos == frozenset({1, 2})
    assert resultado.salidas.acciones_bloqueo == ()


def test_contacto_pegado_no_se_interpreta_como_apertura():
    planta = PlantaDeterminista(contacto_cerrado=True, contacto_pegado=True, velocidad_m_s=0.5)
    resultado = step(Estado(fase=Fase.PARADA_SOLICITADA), planta.snapshot(), [])
    assert resultado.estado.fase is Fase.PARADA_SOLICITADA
    assert resultado.salidas.orden_contactor is False
