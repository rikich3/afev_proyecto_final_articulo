"""Agrega la evidencia CoppeliaSim validada por hashes, conservando su clasificación."""

import argparse
from collections import Counter, defaultdict
import csv
import json
from pathlib import Path
from statistics import median

from analisis.metricas import _viola_rf01, cargar_corridas, episodios_rf01, percentil_95
from software.telemetria import hash_archivo


def leer_json(ruta):
    return json.loads(ruta.read_text(encoding="utf-8"))


def guardar_csv(ruta, filas):
    ruta.parent.mkdir(parents=True, exist_ok=True)
    with ruta.open("w", encoding="utf-8", newline="") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=list(filas[0]))
        escritor.writeheader()
        escritor.writerows(filas)


def duracion_rf01(filas):
    segundos = sum(max(0.0, despues["t_sim_s"] - antes["t_sim_s"])
                   for antes, despues in zip(filas, filas[1:]) if _viola_rf01(antes))
    return round(1000 * segundos, 6), bool(filas and _viola_rf01(filas[-1]))


def estadistica(valores):
    return {"n": len(valores), "mediana_ms": median(valores) if valores else None,
            "p95_ms": percentil_95(valores), "max_ms": max(valores) if valores else None}


def resumir(datos):
    corridas = cargar_corridas(datos / "crudos")
    manifiestos = [leer_json(p) for p in sorted((datos / "manifiestos").glob("*.json"))]
    if not manifiestos or set(corridas) != {m["run_id"] for m in manifiestos}:
        raise ValueError("Trazas y manifiestos desalineados")
    latencias = defaultdict(list)
    por_caso = defaultdict(Counter)
    por_grupo = defaultdict(Counter)
    por_corrida = []
    for m in manifiestos:
        id_, caso = m["run_id"], m["scenario_id"]
        traza = datos / "crudos" / m["traza"]
        if (m["tipo_ejecucion"] != "coppeliasim_zeromq"
                or hash_archivo(traza) != m["sha256_traza"] or len(corridas[id_]) != m["registros"]):
            raise ValueError(f"Integridad de la corrida: {id_}")
        for captura in m["capturas"].values():
            if hash_archivo(datos / "evidencias" / captura["archivo"]) != captura["sha256"]:
                raise ValueError(f"Integridad de captura: {captura['archivo']}")
        clase = m["clasificacion"]
        k = (m["campana"], caso)
        por_grupo[m["campana"]][clase] += 1
        por_caso[k][clase] += 1
        filas = corridas[id_]
        episodios = episodios_rf01(filas)
        duracion, censurado = duracion_rf01(filas)
        forzado = caso.startswith("SC-12")
        por_caso[k]["episodios_forzados" if forzado else "episodios_nominales"] += episodios
        obs = m["observaciones"]
        if clase == "cumple_oraculo":
            for campo, valor in obs.items():
                if campo.endswith("_ms"):
                    latencias[(m["campana"], caso, m["parametros"]["step_s"], campo)].append(valor)
        por_corrida.append({
            "run_id": id_, "grupo": m["campana"], "scenario_id": caso, "seed": m["seed"],
            "paso_s": m["parametros"]["step_s"], "clasificacion": clase,
            "episodios_rf01": episodios, "intrusion_forzada": forzado,
            "duracion_rf01_ms": duracion, "duracion_censurada": censurado,
            "latido_a_corte_ms": obs.get("corte_desde_latido_ms"),
            "orden_a_corte_ms": obs.get("apertura_desde_orden_ms"),
            "caducidad_a_corte_ms": obs.get("corte_desde_caducidad_ms"),
            "apertura_a_parada_ms": obs.get("parada_desde_apertura_ms"),
            "respuesta_fisica": obs.get("estado_respuesta"),
        })

    campos = ("cumple_oraculo", "no_cumple_oraculo", "fallo_preparacion",
              "no_evaluable", "episodios_nominales", "episodios_forzados")
    filas_casos = [{"grupo": grupo, "scenario_id": caso, **{c: n[c] for c in campos}}
                   for (grupo, caso), n in sorted(por_caso.items())]
    filas_latencias = [{"grupo": grupo, "scenario_id": caso, "paso_s": paso, "medida": medida,
                       **estadistica(valores)}
                      for (grupo, caso, paso, medida), valores in sorted(latencias.items())]
    finales = [r for r in por_corrida if r["grupo"] != "piloto"]
    watchdog = [r["latido_a_corte_ms"] for r in finales if r["grupo"] != "sensibilidad"
                and r["scenario_id"] == "SC-09-a" and r["latido_a_corte_ms"] is not None]
    por_paso = {str(dt): estadistica([r["latido_a_corte_ms"] for r in finales
                if r["grupo"] == "sensibilidad" and r["scenario_id"] == "SC-09-a"
                and r["paso_s"] == dt and r["latido_a_corte_ms"] is not None])["mediana_ms"]
                for dt in (0.01, 0.02)}
    resumen = {
        "estado": "calculado", "corridas": len(por_corrida), "campana": len(finales),
        "oraculos_cumplidos": sum(r["clasificacion"] == "cumple_oraculo" for r in finales),
        "por_grupo": {g: dict(n) for g, n in sorted(por_grupo.items())},
        "violaciones_fisicas": sum(r["episodios_rf01"] for r in finales if not r["intrusion_forzada"]),
        "intrusiones_detectadas": sum(r["episodios_rf01"] for r in finales if r["intrusion_forzada"]),
        "contactos_sin_apertura": sum(r["respuesta_fisica"] == "no_respondido" for r in finales),
        "corte_watchdog_sc09a": estadistica(watchdog),
        "sensibilidad_watchdog_ms": por_paso,
        "fuente": "datos/procesados/resumen.csv",
    }
    return resumen, por_corrida, filas_casos, filas_latencias


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--datos", type=Path, default=Path("datos"))
    parser.add_argument("--resumen-articulo", type=Path, default=Path("artefactos/resultados/resumen.json"))
    args = parser.parse_args()
    resumen, corridas, casos, latencias = resumir(args.datos)
    salida = args.datos / "procesados"
    guardar_csv(salida / "corridas.csv", corridas)
    guardar_csv(salida / "resumen.csv", casos)
    if latencias:
        guardar_csv(salida / "latencias.csv", latencias)
    args.resumen_articulo.write_text(json.dumps(resumen, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(resumen, ensure_ascii=False))


if __name__ == "__main__":
    main()
