from software.monitores import evaluar


def verdad(**cambios):
    base = {
        "tick": 4, "t_sim_s": 0.08, "ocupantes_reales": [], "potencia_real": False,
        "velocidad_real_m_s": 0.0, "puerta_real_cerrada": True,
        "seccionador_real_abierto": False,
    }
    base.update(cambios)
    return base


def test_monitor_detecta_violacion_fisica_conocida():
    violaciones = evaluar(verdad(ocupantes_reales=[1], potencia_real=True))
    assert violaciones[0]["propiedad"] == "RF-01"


def test_monitor_no_confunde_orden_con_potencia_fisica():
    assert evaluar(verdad(ocupantes_reales=[1], potencia_real=False)) == []


def test_monitor_rechaza_observacion_incompleta():
    incompleta = verdad()
    del incompleta["potencia_real"]
    assert evaluar(incompleta)[0]["propiedad"] == "OBSERVACION_INCOMPLETA"
