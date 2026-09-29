"""Verificación editorial; no verifica el controlador ni las pruebas Event-B."""
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
registro = (ROOT / 'artefactos/artefactos.md').read_text()
filas = {}
for line in registro.splitlines():
    if re.match(r'\| [AG]\d{2} \|', line):
        fields = [x.strip() for x in line.strip('|').split('|')]
        code = fields[0]
        assert code not in filas, f'Código repetido: {code}'
        filas[code] = fields
assert len([c for c in filas if c.startswith('A')]) == 28
for integrante in range(1, 5):
    paquetes = [f for c, f in filas.items() if c.startswith('A') and f[5] == f'I{integrante}']
    assert len(paquetes) == 7, f'Carga desigual I{integrante}'
    assert sorted(int(f[6]) for f in paquetes) == list(range(1, 8))

rutas = {p for f in filas.values() for p in re.findall(r'`([^`]+)`', f[2])}
def registrado(rel):
    for patron in rutas:
        if patron.endswith('/') and rel.startswith(patron):
            return True
        expresion = re.escape(patron)
        expresion = re.sub(r'<[^>]+>', r'[^/]+', expresion)
        if re.fullmatch(expresion, rel):
            return True
    return False

for path in ROOT.rglob('*'):
    if path.is_file() and not any(x.startswith('.') or x == '__pycache__' for x in path.relative_to(ROOT).parts):
        rel = path.relative_to(ROOT).as_posix()
        assert registrado(rel), f'Archivo sin registrar: {rel}'

fuentes = [ROOT / 'main.typ', ROOT / 'estilo.typ', *sorted((ROOT / 'secciones').glob('*.typ'))]
assert len(list((ROOT / 'secciones').glob('*.typ'))) == 10
refs = 0
for file in fuentes:
    text = file.read_text()
    for code, path in re.findall(r'#recurso\("([AG]\d{2})",\s*"([^"]+)"\)', text):
        assert code in filas, f'Código no registrado: {code}'
        assert path in re.findall(r'`([^`]+)`', filas[code][2]), f'Ruta no canónica: {code}: {path}'
        refs += 1
    for image in re.findall(r'image\("(/img/[^\"]+)"', text):
        assert (ROOT / image.lstrip('/')).exists(), f'Falta figura conceptual: {image}'
    for inc in re.findall(r'#include "([^"]+)"', text):
        assert (file.parent / inc).is_file(), f'Include ausente: {inc}'

resumen = json.loads((ROOT / 'artefactos/resultados/resumen.json').read_text())
if resumen['estado'] == 'pendiente':
    assert all(resumen[k] is None for k in ('corridas', 'violaciones_fisicas', 'po_total', 'po_descargadas', 'latencia_p95_ms'))
assert (ROOT / 'articulo.pdf').stat().st_size > 1000, 'Compilar primero el PDF'
print(f'OK: {len(filas)} artefactos, 28 paquetes equilibrados, 10 secciones, {refs} referencias a rutas canónicas.')
print('Alcance: estructura y consistencia editorial; no prueba formal ni validación experimental.')
