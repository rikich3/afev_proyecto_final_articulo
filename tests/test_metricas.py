import json

from analisis.metricas import cargar_corridas, escribir_resumen, resumir


def registro(run_id, tick, violacion=False, latencia=None):
    resultado = {
        "run_id": run_id, "scenario_id": "FIXTURE", "tick": tick, "t_sim_s": tick * 0.02,
        "violated_properties": [{"propiedad": "RF-01"}] if violacion else [],
    }
    if latencia is not None:
        resultado["latencia_ms"] = latencia
    return resultado


def test_analisis_cuenta_episodio_y_no_ticks(tmp_path):
    crudos = tmp_path / "crudos"
    crudos.mkdir()
    (crudos / "fixture.jsonl").write_text("\n".join(json.dumps(x) for x in [
        registro("r-1", 0), registro("r-1", 1, True, 10), registro("r-1", 2, True, 20), registro("r-1", 3),
    ]) + "\n", encoding="utf-8")
    filas = resumir(cargar_corridas(crudos))
    assert filas == [{"scenario_id": "FIXTURE", "corridas": 1, "violaciones_fisicas": 1, "latencia_p95_ms": 20}]


def test_analisis_escribe_nulos_si_no_hay_corridas(tmp_path):
    salida = tmp_path / "resumen.csv"
    articulo = tmp_path / "resumen.json"
    escribir_resumen([], salida, articulo)
    assert "scenario_id" in salida.read_text(encoding="utf-8")
    assert json.loads(articulo.read_text(encoding="utf-8"))["corridas"] is None
