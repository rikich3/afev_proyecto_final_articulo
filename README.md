# AFEV — Enclavamiento de seguridad para minería

Artículo y código para una faja, una zona y dos operarios. Rodin reproduce
272 obligaciones de la cadena Event-B M0–M2 y NuSMV comprueba cinco
propiedades del ciclo nominal. Python controla la escena CoppeliaSim por
ZeroMQ. La campaña conserva trazas, manifiestos, capturas y resultados.

- [PDF de entrega con anexo NuSMV (8 páginas)](articulo_entrega.pdf),
  [manuscrito sin anexo (7 páginas)](articulo.pdf) y
  [escena integrada](simulacion/mina_integrada.ttt).
- [Registro de artefactos](artefactos/artefactos.md) y [plan semanal](docs/plan_semanal.md).
- [Requisitos](artefactos/especificacion/requisitos.md), [supuestos](artefactos/especificacion/riesgos.md),
  [arquitectura](artefactos/diseno/arquitectura.md) y [protocolo](artefactos/validacion/protocolo.md).
- [Resultados de integración](artefactos/validacion/integracion.md) y [trazabilidad](artefactos/validacion/trazabilidad.csv).
- [Auditoría de originalidad y atribución](artefactos/entrega/originalidad.md).
- [Anexo NuSMV incorporado al PDF de entrega](artefactos/verificacion/nusmv/evidencia.pdf),
  con [modelo y logs reproducibles](modelo/nusmv/README.md).

## Verificación y pruebas

Rodin 3.10 comprobó 5 obligaciones de M0, 79 de M1 y 188 de M2. La
[reproducción](artefactos/verificacion/rodin/m2/README.md) usa un segundo
espacio de trabajo. [NuSMV](modelo/nusmv/README.md) conserva el modelo de
estados, las propiedades, los controles negativos y los comandos.
[ProB](artefactos/verificacion/prob.md) conserva dos exploraciones de M2.

```sh
python herramientas/verificar_rodin.py --rodin /ruta/a/rodin --java-home /ruta/al/jdk21 --replay
python herramientas/verificar_nusmv.py --bin /ruta/al/ejecutable/NuSMV
python -m pytest -q
```

La suite local pasó 18 pruebas. La parte 1 usa Event-B como lenguaje de
especificación formal, con modelos y pruebas reproducibles en Rodin.

## Reproducir CoppeliaSim

Instalar CoppeliaSim EDU 4.10.0 rev0 y Python 3.12. Los comandos parten
de la raíz del repositorio salvo el de arranque del simulador.

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

En Linux, `-h` oculta la interfaz y permite renderizar en una sesión
gráfica. `-Gpython=...` selecciona el intérprete si la instalación lo
requiere. El ejecutor carga la geometría y monta los scripts Lua.
`--guardar-escena` exporta la escena ensamblada del primer caso. Usar un
directorio de salida nuevo para cada reproducción.

## Compilar y verificar

```sh
typst compile main.typ articulo.pdf
typst compile artefactos/verificacion/nusmv/evidencia.typ artefactos/verificacion/nusmv/evidencia.pdf
qpdf --empty --pages articulo.pdf artefactos/verificacion/nusmv/evidencia.pdf -- articulo_entrega.pdf
python herramientas/verificar.py
pdfinfo articulo_entrega.pdf
```

La compilación registrada usa Typst 0.14.2 y las fuentes Liberation Serif y
Liberation Mono. El manuscrito emplea tamaño carta, dos columnas y referencias
IEEE; el anexo ocupa la octava página en una columna.
Ver el [procedimiento de reproducción](artefactos/entrega/reproduccion.md).
La carpeta `entregable_02/` conserva un avance histórico y no define el
manuscrito vigente.

## Historial y versiones

Los cambios se registran por entregable, con el formato
`tipo(alcance): descripción` de [Conventional Commits](docs/versionado.md).
Las etiquetas `vMAJOR.MINOR.PATCH` identifican versiones reproducibles del
artículo y sus artefactos. Las versiones `v0.x` son candidatas hasta la
revisión cruzada del equipo.
