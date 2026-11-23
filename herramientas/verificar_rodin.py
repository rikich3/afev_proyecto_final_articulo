"""Construye y demuestra los refinamientos M1/M2 en una copia temporal de Rodin y del proyecto."""
import argparse
import csv
import hashlib
import json
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]


def sha256(ruta):
    return hashlib.sha256(ruta.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rodin', type=Path, required=True, help='Carpeta con plugins y configuration de Rodin 3.10.')
    parser.add_argument('--java-home', type=Path, required=True, help='JDK 21 con java, javac y jar.')
    parser.add_argument('--modelo', choices=['M1', 'M2'], default='M1')
    parser.add_argument('--replay', action='store_true', help='Reproduce los árboles guardados sin buscar una estrategia alternativa.')
    args = parser.parse_args()
    origen = args.rodin.resolve()
    objetivo = args.modelo
    contexto = 'C2' if objetivo == 'M2' else 'C1'
    destino = RAIZ / 'artefactos/verificacion/rodin'
    if objetivo == 'M2':
        destino = destino / 'm2'
    destino.mkdir(parents=True, exist_ok=True)
    nombre_base = ('reproduccion_' if args.replay else 'verificacion_') + objetivo.lower()
    nombre_log = nombre_base + '.log'
    jdk = args.java_home.resolve() / 'bin'
    with tempfile.TemporaryDirectory(prefix='afev-rodin-') as carpeta:
        temporal = Path(carpeta)
        instalacion = temporal / 'rodin'
        shutil.copytree(origen, instalacion, symlinks=True)
        plugins = instalacion / 'plugins'
        clases = temporal / 'classes'
        clases.mkdir()
        soporte = RAIZ / 'herramientas/rodin'
        subprocess.run([str(jdk/'javac'), '-cp', str(plugins/'*'), '-d', str(clases), str(soporte/'VerificarM1.java')], check=True)
        nombre_bundle = 'org.afev.proofs_1.0.0.jar'
        subprocess.run([str(jdk/'jar'), 'cfm', str(plugins/nombre_bundle), str(soporte/'MANIFEST.MF'), '-C', str(clases), '.', '-C', str(soporte), 'plugin.xml'], check=True)
        bundles = instalacion / 'configuration/org.eclipse.equinox.simpleconfigurator/bundles.info'
        lineas = [line for line in bundles.read_text().splitlines() if not line.startswith('org.afev.proofs,')]
        lineas.append(f'org.afev.proofs,1.0.0,plugins/{nombre_bundle},4,false')
        bundles.write_text('\n'.join(lineas)+'\n')
        launcher = next(plugins.glob('org.eclipse.equinox.launcher_*.jar'))
        comando = [str(jdk/'java'), '-jar', str(launcher), '-nosplash', '-consoleLog', '-application', 'org.afev.proofs.run', '-data', str(temporal/'workspace'), str(RAIZ/'modelo/rodin/Enclavamiento'), str(destino), objetivo]
        if args.replay:
            comando.append('--replay')
        with (destino/nombre_log).open('w') as log:
            proceso = subprocess.run(comando, stdout=log, stderr=subprocess.STDOUT)
        if proceso.returncode:
            raise SystemExit(f'Rodin terminó con código {proceso.returncode}. Consulte {destino/nombre_log}.')
    with (destino/'estados.csv').open() as archivo:
        estados = list(csv.DictReader(archivo))
    obligaciones = [r for r in estados if r['modelo'] == objetivo]
    if not obligaciones or any(int(r['confianza']) < 1000 or r['rota'] != 'false' for r in estados):
        raise SystemExit('Existen obligaciones pendientes o pruebas rotas.')
    if not args.replay:
        for nombre in [contexto+'.bcc', contexto+'.bpr', objetivo+'.bcm', objetivo+'.bpr']:
            shutil.copy2(destino/nombre, RAIZ/'modelo/rodin/Enclavamiento'/nombre)
    nombres_fuente = ['C0.buc','M0.bum','C1.buc','M1.bum']
    if objetivo == 'M2':
        nombres_fuente += ['M0.bpr', 'M1.bpr', 'C2.buc', 'M2.bum']
    nombres_fuente += [objetivo+'.bpr']
    fuentes = [RAIZ/'modelo/rodin/Enclavamiento'/nombre for nombre in nombres_fuente]
    manifiesto = {
        'fecha_utc': datetime.now(timezone.utc).isoformat(),
        'modo': 'reproduccion' if args.replay else 'demostracion',
        'rodin': next((origen/'plugins').glob('org.rodinp.platform_*.jar')).name.removeprefix('org.rodinp.platform_').removesuffix('.jar'),
        'jdk': subprocess.check_output([str(jdk/'java'), '-version'], stderr=subprocess.STDOUT, text=True).splitlines()[0],
        'chequeo_estatico': 'sin_errores',
        objetivo+'_generadas': len(obligaciones),
        objetivo+'_demostradas': len(obligaciones),
        'total_comprobadas': len(estados),
        'sha256_fuentes': {str(p.relative_to(RAIZ)): sha256(p) for p in fuentes},
        'sha256_log': sha256(destino/nombre_log),
        'sha256_estados': sha256(destino/'estados.csv'),
    }
    if objetivo == 'M2':
        manifiesto['sha256_complementos_smt'] = {
            p.name: sha256(p) for p in sorted((origen/'plugins').glob('org.eventb.smt.*.jar'))
        }
    nombre_json = nombre_base+'.json'
    (destino/nombre_json).write_text(json.dumps(manifiesto, ensure_ascii=False, indent=2)+'\n')
    print(f'Rodin {objetivo}: {len(obligaciones)}/{len(obligaciones)} obligaciones demostradas; {len(estados)} comprobadas en total ({manifiesto["modo"]}).')


if __name__ == '__main__':
    main()
