"""Registro JSONL y manifiestos reproducibles por corrida."""

from __future__ import annotations

import hashlib
import json
import os
import csv
from pathlib import Path
from typing import Any, Mapping


ESQUEMA_VERSION = 1


def hash_archivo(ruta: Path) -> str:
    digest = hashlib.sha256()
    with ruta.open("rb") as archivo:
        for bloque in iter(lambda: archivo.read(65536), b""):
            digest.update(bloque)
    return digest.hexdigest()


def _serializar(valor: Any) -> Any:
    if isinstance(valor, set) or isinstance(valor, frozenset):
        return sorted(valor)
    if hasattr(valor, "value"):
        return valor.value
    raise TypeError(f"Valor no serializable en telemetría: {type(valor).__name__}")


def validar_registro(registro: Mapping[str, Any]) -> None:
    requeridos = {
        "esquema_version", "run_id", "scenario_id", "seed", "tick", "t_sim_s",
        "inputs", "physical_truth", "state_before", "state_after", "outputs",
        "violated_properties",
    }
    faltantes = requeridos.difference(registro)
    if faltantes:
        raise ValueError(f"Registro incompleto: faltan {', '.join(sorted(faltantes))}")
    if registro["esquema_version"] != ESQUEMA_VERSION:
        raise ValueError("Versión de esquema no admitida")
    if not isinstance(registro["violated_properties"], list):
        raise ValueError("violated_properties debe ser lista")


class EscritorJsonl:
    def __init__(self, ruta: Path):
        self.ruta = ruta
        self.ruta.parent.mkdir(parents=True, exist_ok=True)

    def escribir(self, registro: Mapping[str, Any]) -> None:
        validar_registro(registro)
        with self.ruta.open("a", encoding="utf-8", newline="\n") as archivo:
            archivo.write(json.dumps(registro, ensure_ascii=False, default=_serializar, sort_keys=True))
            archivo.write("\n")
            archivo.flush()
            os.fsync(archivo.fileno())


def escribir_manifiesto(ruta: Path, contenido: Mapping[str, Any], ruta_jsonl: Path) -> dict[str, Any]:
    """Escribe el manifiesto de forma atómica tras calcular el hash de la traza."""
    if not ruta_jsonl.is_file():
        raise FileNotFoundError(ruta_jsonl)
    manifiesto = dict(contenido)
    manifiesto.update({
        "esquema_version": ESQUEMA_VERSION,
        "traza": ruta_jsonl.name,
        "sha256_traza": hash_archivo(ruta_jsonl),
    })
    ruta.parent.mkdir(parents=True, exist_ok=True)
    temporal = ruta.with_suffix(ruta.suffix + ".tmp")
    temporal.write_text(json.dumps(manifiesto, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporal, ruta)
    return manifiesto


def actualizar_indice_manifiestos(ruta: Path, manifiesto: Mapping[str, Any]) -> None:
    """Añade una corrida al índice sin modificar trazas ni manifiestos previos."""
    columnas = ["run_id", "scenario_id", "seed", "tipo_ejecucion", "resultados_experimentales", "traza", "sha256_traza"]
    ruta.parent.mkdir(parents=True, exist_ok=True)
    nuevo = not ruta.exists() or ruta.stat().st_size == 0
    with ruta.open("a", encoding="utf-8", newline="") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=columnas)
        if nuevo:
            escritor.writeheader()
        escritor.writerow({campo: manifiesto.get(campo) for campo in columnas})
