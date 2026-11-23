"""Reproduce el modelo nominal y un control de sensibilidad con NuSMV."""
import argparse
import hashlib
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]


def ejecutar(binario, modelo):
    proceso = subprocess.run([binario, '-r', str(modelo)], capture_output=True, text=True)
    if proceso.returncode:
        raise RuntimeError(proceso.stdout + proceso.stderr)
    return proceso.stdout + proceso.stderr


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bin', default=shutil.which('NuSMV'))
    args = parser.parse_args()
    if not args.bin:
        parser.error('Indique --bin con la ruta del ejecutable NuSMV.')
    binario = str(Path(args.bin).resolve())
    modelo = RAIZ / 'modelo/nusmv/enclavamiento.smv'
    destino = RAIZ / 'artefactos/verificacion/nusmv'
    destino.mkdir(parents=True, exist_ok=True)
    salida = ejecutar(binario, modelo)
    (destino / 'ejecucion.log').write_text(salida)
    resultados = [line for line in salida.splitlines() if line.startswith('-- specification')]
    if len(resultados) != 6 or sum(line.endswith('is true') for line in resultados) != 5:
        raise RuntimeError('Se esperaban cinco propiedades verdaderas y un control negativo falso.')
    if not any('G !potencia' in line and line.endswith('is false') for line in resultados):
        raise RuntimeError('El control negativo de energizacion no produjo el resultado esperado.')
    # Retirar solamente la guarda de ingreso permite intrusiones durante marcha.
    # La copia temporal comprueba que MC01 detecta ese cambio en el entorno.
    original = 'evento = ingresar1 & permiso_acceso & !dentro1'
    fuente = modelo.read_text()
    if fuente.count(original) != 1:
        raise RuntimeError('No se encontro una unica guarda para la prueba de sensibilidad.')
    mutante = fuente.replace(original, 'evento = ingresar1 & !dentro1')
    with tempfile.TemporaryDirectory(prefix='afev-nusmv-') as carpeta:
        ruta = Path(carpeta) / 'intrusion.smv'
        ruta.write_text(mutante)
        sensibilidad = ejecutar(binario, ruta)
    (destino / 'intrusion.log').write_text(sensibilidad)
    if '-- specification  G !(ocupada & potencia)  is false' not in sensibilidad:
        raise RuntimeError('La intrusión no genero el contraejemplo esperado de MC01.')
    manifiesto = {
        'modelo': str(modelo.relative_to(RAIZ)),
        'sha256_modelo': hashlib.sha256(modelo.read_bytes()).hexdigest(),
        'sha256_binario': hashlib.sha256(Path(binario).read_bytes()).hexdigest(),
        'comando': ['NuSMV', '-r', str(modelo.relative_to(RAIZ))],
        'version': next(line for line in salida.splitlines() if 'This is NuSMV' in line),
        'resultados': resultados,
        'sensibilidad': 'MC01 falsa al permitir ingreso sin permiso',
        'sha256_logs': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in destino.glob('*.log')},
    }
    (destino / 'manifiesto.json').write_text(json.dumps(manifiesto, indent=2, ensure_ascii=False) + '\n')
    print('NuSMV: 5 propiedades satisfechas; control negativo y prueba de intrusión detectados.')


if __name__ == '__main__':
    main()
