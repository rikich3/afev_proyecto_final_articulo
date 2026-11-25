# AFEV — Enclavamiento de seguridad para minería

Especificación formal, verificación y validación simulada de un enclavamiento de seguridad para el mantenimiento de una faja minera, con alcance de una faja, una zona y dos operarios. El proyecto integra tres niveles de evidencia: refinamiento en Event-B (`M0–M2`, 272 obligaciones demostradas), *model checking* en NuSMV (5 propiedades sobre 119 estados alcanzables) y evaluación de un controlador Python sobre CoppeliaSim mediante ZeroMQ y un monitor físico independiente (134 de 135 corridas conformes; SC-09-c no evaluable por reloj congelado).

## Guía rápida para el revisor

Esta tabla orienta la revisión directa de los entregables y del código de especificación formal sin requerir instalación previa de herramientas:

| Componente | Ubicación en el repositorio | Qué contiene |
| --- | --- | --- |
| **Artículo científico** | [articulo.pdf](articulo.pdf) · [main.typ](main.typ) · [secciones/](secciones/) | Manuscrito final (8 páginas, formato IEEE) y fuentes en Typst. |
| **Especificación Event-B (lectura rápida)** | [modelo/export/](modelo/export/) (`C0–C2.txt`, `M0–M2.txt`) | Exportación en texto plano de los contextos y las tres máquinas (`M0`, `M1`, `M2`) para lectura directa. |
| **Proyecto Event-B / Rodin** | [modelo/rodin/Enclavamiento/](modelo/rodin/Enclavamiento/) | Fuentes nativas (`.buc`, `.bum`), pruebas (`.bpr`) y evidencias de las 272 obligaciones demostradas ([M2](artefactos/verificacion/rodin/m2/README.md)). |
| **Model Checking (NuSMV)** | [modelo/nusmv/enclavamiento.smv](modelo/nusmv/enclavamiento.smv) · [README](modelo/nusmv/README.md) | Modelo finito de 11 fases, 5 propiedades LTL/CTL, controles negativos y logs de ejecución. |
| **Exploración de estados (ProB)** | [artefactos/verificacion/prob.md](artefactos/verificacion/prob.md) | Dos exploraciones de `M2` (10 000 y 20 000 estados) sin contraejemplos. |
| **Controlador y monitor Python** | [software/](software/) · [tests/](tests/) | Supervisor (`controlador.py`), monitor físico independiente (`monitores.py`), adaptador ZeroMQ (`adaptador.py`) y suite de pruebas. |
| **Planta simulada (CoppeliaSim)** | [simulacion/mina_integrada.ttt](simulacion/mina_integrada.ttt) · [scripts/](simulacion/scripts/) | Escena 3D de la faja y scripts Lua de planta (`planta.lua`) y watchdog local (`watchdog.lua`). |
| **Trazabilidad y resultados** | [trazabilidad.csv](artefactos/validacion/trazabilidad.csv) · [correspondencia.csv](artefactos/diseno/correspondencia.csv) · [resumen.json](artefactos/resultados/resumen.json) | Vínculo entre requisitos `RF-01–RF-10`, guardas Event-B, controlador Python, escenarios y resultados de las 135 corridas. |

### Ruta sugerida de revisión rápida

1. **Leer el modelo formal sin herramientas:** revisar en orden [C0.txt](modelo/export/C0.txt) y [M0.txt](modelo/export/M0.txt) (exclusión `INV-01`), [M1.txt](modelo/export/M1.txt) (bloqueos personales y rearme) y [M2.txt](modelo/export/M2.txt) (confirmación física, plazos y fallos).
2. **Revisar el model checking:** inspeccionar [enclavamiento.smv](modelo/nusmv/enclavamiento.smv) y los registros en [modelo/nusmv/README.md](modelo/nusmv/README.md).
3. **Contrastar requisitos, modelo y simulación:** consultar [correspondencia.csv](artefactos/diseno/correspondencia.csv), [trazabilidad.csv](artefactos/validacion/trazabilidad.csv) y [resultados de integración](artefactos/validacion/integracion.md).
4. **Documentación complementaria:** [registro de artefactos](artefactos/artefactos.md), [requisitos](artefactos/especificacion/requisitos.md), [supuestos y riesgos](artefactos/especificacion/riesgos.md), [arquitectura](artefactos/diseno/arquitectura.md), [protocolo](artefactos/validacion/protocolo.md) y [auditoría de originalidad](artefactos/entrega/originalidad.md).

## Verificación y pruebas

Rodin 3.10 comprobó 5 obligaciones de `M0`, 79 de `M1` y 188 de `M2` (272 en total). La [reproducción](artefactos/verificacion/rodin/m2/README.md) usa un segundo espacio de trabajo. [NuSMV](modelo/nusmv/README.md) conserva el modelo de estados, las propiedades, los controles negativos y los comandos. [ProB](artefactos/verificacion/prob.md) conserva dos exploraciones de `M2`.

```sh
python herramientas/verificar_rodin.py --rodin /ruta/a/rodin --java-home /ruta/al/jdk21 --replay
python herramientas/verificar_nusmv.py --bin /ruta/al/ejecutable/NuSMV
python -m pytest -q
```

La suite local pasó 18 pruebas. La parte 1 usa Event-B como lenguaje de especificación formal, con modelos y pruebas reproducibles en Rodin.

## Reproducir CoppeliaSim

Instalar CoppeliaSim EDU 4.10.0 rev0 y Python 3.12. Los comandos parten de la raíz del repositorio salvo el de arranque del simulador.

```sh
python -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
# En otra terminal, desde la instalación de CoppeliaSim
./coppeliaSim.sh -GzmqRemoteApi.rpcPort=23170
# Desde el repositorio, con el entorno Python activado
python -m experimentos.coppelia --puerto 23170 --grupo piloto --output buffer/piloto
python -m experimentos.coppelia --puerto 23170 --grupo todo --output buffer/reproduccion \
  --capturas buffer/reproduccion/evidencias
python -m analisis.campana --datos buffer/reproduccion --resumen-articulo buffer/resumen.json
```

En Linux, `-h` oculta la interfaz y permite renderizar en una sesión gráfica. `-Gpython=...` selecciona el intérprete si la instalación lo requiere. El ejecutor carga la geometría y monta los scripts Lua. `--guardar-escena` exporta la escena ensamblada del primer caso. Usar un directorio de salida nuevo para cada reproducción.

## Compilar y verificar el artículo

```sh
typst compile main.typ articulo.pdf
python herramientas/verificar.py
pdfinfo articulo.pdf
```

El artículo emplea tamaño carta, dos columnas y referencias IEEE. Los registros de NuSMV permanecen en el repositorio como evidencia técnica; no se añaden como anexo al PDF. Ver el [procedimiento de reproducción](artefactos/entrega/reproduccion.md). La carpeta `entregable_02/` conserva un avance histórico y no define el manuscrito vigente.

## Historial y versiones

Los cambios se registran por entregable, con el formato `tipo(alcance): descripción` de [Conventional Commits](docs/versionado.md). Las etiquetas `vMAJOR.MINOR.PATCH` identifican versiones reproducibles del artículo y sus artefactos. Las versiones `v0.x` son candidatas hasta la revisión cruzada del equipo.
