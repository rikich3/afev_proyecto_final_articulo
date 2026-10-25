"""Ejecutor mínimo para comprobar el formato de telemetría.

La opción por defecto usa PlantaDeterminista y produce una traza etiquetada como
prueba. No sustituye las corridas finales en CoppeliaSim.
"""

from __future__ import annotations

import argparse
import json
import platform
import sys
import time
import uuid
from dataclasses import asdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from software.adaptador import PlantaDeterminista
from software.controlador import step
from software.estado import Estado, Orden
from software.monitores import evaluar
from software.telemetria import ESQUEMA_VERSION, EscritorJsonl, actualizar_indice_manifiestos, escribir_manifiesto


def _plano(valor):
    if hasattr(valor, "value"):
        return valor.value
    if isinstance(valor, (set, frozenset)):
        return sorted(valor)
    if isinstance(valor, tuple):
        return [_plano(x) for x in valor]
    if isinstance(valor, list):
        return [_plano(x) for x in valor]
    if isinstance(valor, dict):
        return {k: _plano(v) for k, v in valor.items()}
    return valor


def _estado_plano(estado: Estado) -> dict:
    return _plano(asdict(estado))


def ejecutar_piloto_determinista(destino: Path, seed: int = 0) -> tuple[Path, Path]:
    """Ejecuta reset/start; es una prueba del flujo y no un resultado experimental."""
    run_id = f"fixture-{uuid.uuid4().hex[:12]}"
    ruta_jsonl = destino / "crudos" / f"{run_id}.jsonl"
    ruta_manifiesto = destino / "manifiestos" / f"{run_id}.json"
    escritor = EscritorJsonl(ruta_jsonl)
    planta = PlantaDeterminista()
    estado = Estado()
    ordenes = [
        Orden(command_id="fixture-reset", tipo="reset"),
        Orden(command_id="fixture-start", tipo="start"),
    ]
    for orden in ordenes:
        snapshot = planta.snapshot()
        antes = estado
        resultado = step(estado, snapshot, [orden])
        verdad = planta.avanzar(resultado.salidas)
        violaciones = evaluar(verdad)
        escritor.escribir({
            "esquema_version": ESQUEMA_VERSION, "run_id": run_id,
            "scenario_id": "FIXTURE-RESET-START", "seed": seed,
            "tick": snapshot.tick, "t_sim_s": snapshot.t_sim_s,
            "t_wall_ns": time.monotonic_ns(), "inputs": _plano(asdict(snapshot)),
            "physical_truth": verdad, "state_before": _estado_plano(antes),
            "event": {"command_id": orden.command_id, "tipo": orden.tipo},
            "state_after": _estado_plano(resultado.estado),
            "outputs": _plano(asdict(resultado.salidas)),
            "violated_properties": violaciones,
        })
        estado = resultado.estado
    manifiesto = escribir_manifiesto(ruta_manifiesto, {
        "run_id": run_id, "scenario_id": "FIXTURE-RESET-START", "seed": seed,
        "tipo_ejecucion": "fixture_de_prueba_con_planta_determinista",
        "resultados_experimentales": False, "python": platform.python_version(),
    }, ruta_jsonl)
    actualizar_indice_manifiestos(destino / "manifest.csv", manifiesto)
    return ruta_jsonl, ruta_manifiesto


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=RAIZ / "buffer" / "ejecucion_prueba")
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()
    traza, manifiesto = ejecutar_piloto_determinista(args.output, args.seed)
    print(json.dumps({"traza": str(traza), "manifiesto": str(manifiesto), "tipo": "fixture_de_prueba"}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
