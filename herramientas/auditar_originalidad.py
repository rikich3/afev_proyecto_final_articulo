"""Coteja la prosa del artículo con PDF/TXT aportados por el equipo.

Mide coincidencia literal consecutiva. No sustituye la revisión de citas,
paráfrasis traducidas ni el informe de similitud de una institución.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
import csv
import hashlib
from pathlib import Path
import re
import subprocess
import unicodedata


ROOT = Path(__file__).resolve().parents[1]
VENTANA = 3


def palabras(texto: str) -> list[str]:
    texto = unicodedata.normalize("NFKD", texto.lower())
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return re.findall(r"[a-z0-9]+", texto)


def leer_fuente(ruta: Path) -> str:
    if ruta.suffix.lower() == ".pdf":
        return subprocess.run(
            ["pdftotext", "-layout", str(ruta), "-"],
            capture_output=True,
            check=True,
            text=True,
        ).stdout
    if ruta.suffix.lower() == ".txt":
        return ruta.read_text(encoding="utf-8", errors="replace")
    raise ValueError(f"Formato no admitido: {ruta}")


def oraciones():
    for ruta in sorted((ROOT / "secciones").glob("*.typ")):
        if ruta.name.startswith("09-"):
            continue
        for linea, texto in enumerate(ruta.read_text(encoding="utf-8").splitlines(), 1):
            if texto.startswith(("=", "#")) or len(texto) < 60:
                continue
            texto = re.sub(r"@[\w-]+", "", texto)
            for oracion in re.split(r"(?<=[.!?])\s+", texto):
                if len(palabras(oracion)) >= 10:
                    yield ruta.name, linea, oracion.strip()


def cotejar(fuentes: list[Path]):
    corpus = {}
    indices = defaultdict(list)
    vistos = set()
    for ruta in fuentes:
        contenido = leer_fuente(ruta)
        huella = hashlib.sha256(contenido.encode()).hexdigest()
        if huella in vistos:
            continue
        vistos.add(huella)
        vocabulario = palabras(contenido)
        corpus[ruta.name] = vocabulario
        for pos in range(len(vocabulario) - VENTANA + 1):
            indices[tuple(vocabulario[pos:pos + VENTANA])].append((ruta.name, pos))

    filas = []
    for seccion, linea, oracion in oraciones():
        texto = palabras(oracion)
        mejor = (0, "", "")
        for pos in range(len(texto) - VENTANA + 1):
            for nombre, inicio in indices.get(tuple(texto[pos:pos + VENTANA]), ()):
                fuente = corpus[nombre]
                longitud = VENTANA
                while (pos + longitud < len(texto) and inicio + longitud < len(fuente)
                       and texto[pos + longitud] == fuente[inicio + longitud]):
                    longitud += 1
                if longitud > mejor[0]:
                    mejor = (longitud, nombre, " ".join(texto[pos:pos + longitud]))
        filas.append((seccion, linea, oracion, *mejor))
    return corpus, filas


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("fuentes", nargs="+", type=Path, help="PDF o TXT originales")
    parser.add_argument("--salida", type=Path, required=True, help="CSV de cotejo")
    parser.add_argument("--umbral", type=int, default=5, help="Palabras consecutivas (5 por defecto)")
    args = parser.parse_args()
    corpus, filas = cotejar(args.fuentes)
    args.salida.parent.mkdir(parents=True, exist_ok=True)
    with args.salida.open("w", newline="", encoding="utf-8") as salida:
        escritor = csv.writer(salida, lineterminator="\n")
        escritor.writerow(("seccion", "linea", "oracion", "max_palabras_consecutivas",
                           "fuente", "fragmento_coincidente"))
        escritor.writerows(filas)
    alertas = sum(fila[3] >= args.umbral for fila in filas)
    print(f"{len(filas)} oraciones; {len(corpus)} fuentes únicas; "
          f"{alertas} coincidencias de {args.umbral}+ palabras consecutivas")


if __name__ == "__main__":
    main()
