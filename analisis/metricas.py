"""Análisis reproducible de trazas JSONL por corrida, sin editar datos crudos."""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

RAIZ = Path(__file__).resolve().parents[1]


def cargar_corridas(ruta_crudos: Path) -> dict[str, list[dict[str, Any]]]:
    corridas: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for ruta in sorted(ruta_crudos.glob("*.jsonl")):
        with ruta.open(encoding="utf-8") as archivo:
            for numero, linea in enumerate(archivo, start=1):
                if not linea.strip():
                    continue
                registro = json.loads(linea)
                for campo in ("run_id", "scenario_id", "tick", "t_sim_s", "violated_properties"):
                    if campo not in registro:
                        raise ValueError(f"{ruta}:{numero}: falta {campo}")
                corridas[registro["run_id"]].append(registro)
    for registros in corridas.values():
        registros.sort(key=lambda r: (r["tick"], r["t_sim_s"]))
    return dict(corridas)


def _viola_rf01(registro: dict[str, Any]) -> bool:
    return any(item.get("propiedad") == "RF-01" for item in registro["violated_properties"])


def episodios_rf01(registros: Iterable[dict[str, Any]]) -> int:
    """Cuenta entradas en episodios, sin tratar cada tick como experimento."""
    activo = False
    episodios = 0
    for registro in registros:
        ahora = _viola_rf01(registro)
        if ahora and not activo:
            episodios += 1
        activo = ahora
    return episodios


def percentil_95(valores: list[float]) -> float | None:
    if not valores:
        return None
    ordenados = sorted(valores)
    return ordenados[math.ceil(0.95 * len(ordenados)) - 1]


def resumir(corridas: dict[str, list[dict[str, Any]]]) -> list[dict[str, Any]]:
    por_escenario: dict[str, list[list[dict[str, Any]]]] = defaultdict(list)
    for registros in corridas.values():
        if registros:
            por_escenario[registros[0]["scenario_id"]].append(registros)
    filas: list[dict[str, Any]] = []
    for escenario, grupo in sorted(por_escenario.items()):
        episodios = sum(episodios_rf01(registros) for registros in grupo)
        # El ejecutor puede añadir latencia_ms sólo cuando existe una respuesta física.
        latencias = [r["latencia_ms"] for registros in grupo for r in registros if isinstance(r.get("latencia_ms"), (int, float))]
        filas.append({
            "scenario_id": escenario,
            "corridas": len(grupo),
            "violaciones_fisicas": episodios,
            "latencia_p95_ms": percentil_95(latencias),
        })
    return filas


def escribir_resumen(filas: list[dict[str, Any]], ruta_csv: Path, ruta_json: Path) -> None:
    ruta_csv.parent.mkdir(parents=True, exist_ok=True)
    with ruta_csv.open("w", encoding="utf-8", newline="") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=["scenario_id", "corridas", "violaciones_fisicas", "latencia_p95_ms"])
        escritor.writeheader()
        escritor.writerows(filas)
    total_corridas = sum(fila["corridas"] for fila in filas)
    total_violaciones = sum(fila["violaciones_fisicas"] for fila in filas)
    latencias = [fila["latencia_p95_ms"] for fila in filas if fila["latencia_p95_ms"] is not None]
    ruta_json.write_text(json.dumps({
        "estado": "calculado" if filas else "pendiente",
        "corridas": total_corridas if filas else None,
        "violaciones_fisicas": total_violaciones if filas else None,
        "po_total": None, "po_descargadas": None,
        "latencia_p95_ms": max(latencias) if latencias else None,
        "fuente": "datos/procesados/resumen.csv",
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--crudos", type=Path, default=RAIZ / "datos" / "crudos")
    parser.add_argument("--salida", type=Path, default=RAIZ / "datos" / "procesados" / "resumen.csv")
    parser.add_argument("--resumen-articulo", type=Path, default=RAIZ / "artefactos" / "resultados" / "resumen.json")
    args = parser.parse_args()
    corridas = cargar_corridas(args.crudos) if args.crudos.exists() else {}
    escribir_resumen(resumir(corridas), args.salida, args.resumen_articulo)
    print(f"corridas={len(corridas)} salida={args.salida}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
