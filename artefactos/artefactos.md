# Registro de artefactos

Todas las rutas son relativas a la raíz del repositorio. Los códigos son estables. Las rutas con `<run_id>` describen familias de archivos, no archivos ya producidos. Un artefacto puede agrupar archivos inseparables de un entregable. **Base no significa verificado ni terminado**; los archivos planificados se crearán durante las siete semanas. Los resultados nunca se sustituyen por números ficticios. Los auxiliares G01–G05 se mantienen dentro de las horas de los paquetes asignados.

| Código | Nombre | Ubicación | Descripción breve | Estado inicial | Responsable | Semana de cierre |
|---|---|---|---|---|---|---|
| G01 | Registro de artefactos | `artefactos/artefactos.md` | Fuente de verdad de códigos, rutas y estados. | Documento base | I1 | 1 |
| G02 | Plan de siete semanas | `docs/plan_semanal.md`; `docs/plan_ejecucion_semanas_4_5.md` | Carga equitativa, dependencias, responsables, revisores y ejecución de A13–A20. | Documento base | I1 | 1 |
| G03 | Guía de implementación y artículo | `docs/guia_proyecto.md` | Ruta mínima, métricas, normas y criterios de redacción. | Documento base | I2 | 1 |
| G04 | Entrada y guía del repositorio | `README.md`; `img/README.md`; `img/enunciado.png`; `ejemplo_articulo.pdf` | Enunciado original, ejemplo de formato y uso del proyecto. | Disponible | I3 | 1 |
| G05 | Verificación editorial | `herramientas/verificar.py` | Comprueba secciones, referencias a artefactos y fuentes de imágenes. | Disponible | I4 | 7 |
| A01 | Alcance y requisitos | `artefactos/especificacion/requisitos.md` | Una zona, dos operarios; requisitos RF y criterios verificables. | Base | I1 | 1 |
| A02 | Peligros y supuestos | `artefactos/especificacion/riesgos.md` | Peligros, frontera física, fallos y condiciones de validez. | Base | I2 | 1 |
| A03 | Entorno reproducible | `docs/entorno.md`; `requirements.txt` | Versiones, licencias e instalación; dependencias congeladas tras piloto. | Guía; lock pendiente | I3 | 1 |
| A04 | Revisión bibliográfica | `artefactos/literatura/revision.md`; `referencias.bib` | Fuentes primarias, comparación y referencias IEEE. | Base | I4 | 1 |
| A05 | Arquitectura y contrato | `artefactos/diseno/arquitectura.md`; `img/arquitectura.svg` | Componentes, contratos tipados, fases, prioridades y canal físico independiente. | Contrato definido; revisión cruzada pendiente | I1 | 2 |
| A06 | Modelo abstracto M0 | `modelo/rodin/Enclavamiento/`; `modelo/export/M0.txt`; `modelo/export/C0.txt` | C0/M0 nativos, exportaciones y cinco obligaciones demostradas; presencia y potencia abstractas. | Modelo comprobado; revisión cruzada pendiente | I2 | 2 |
| A07 | Escena mínima | `simulacion/inicial.ttt`; `simulacion/mina.ttt`; `simulacion/mina_modelada.ttt`; `simulacion/scripts/crear_escena.lua`; `simulacion/scripts/watchdog.lua`; `simulacion/README.md` | Escena inicial, base y modelo mejorado con malla, operarios, sensores y articulaciones; comportamiento por integrar. | Generador y modelo geométrico comprobados; watchdog y comportamiento pendientes | I3 | 2 |
| A08 | Protocolo y escenarios | `artefactos/validacion/protocolo.md`; `experimentos/escenarios.json` | Protocolo, 13 escenarios/34 casos, parámetros, semillas, oráculos y fronteras. | Catálogo definido; revisión y piloto pendientes | I4 | 2 |
| A09 | Controlador discreto | `software/controlador.py`; `software/estado.py` | Transición pura, LOTO por operario y rearme manual. | Planificado | I1 | 3 |
| A10 | Refinamiento M1 LOTO | `modelo/export/M1.txt`; `modelo/export/C1.txt` | Bloqueos individuales, aislamiento y liberación ordenada; fuentes en A06. | Planificado | I2 | 3 |
| A11 | Adaptador CoppeliaSim | `software/adaptador.py`; `software/main.py` | Lectura, transición, actuación y pasos sincronizados. | Planificado | I3 | 3 |
| A12 | Pruebas del controlador | `tests/test_controlador.py`; `tests/test_secuencias.py` | Guardas, fronteras, concurrencia y secuencias inválidas. | Planificado | I4 | 3 |
| A13 | Refinamiento M2 e interfaz | `modelo/export/M2.txt`; `artefactos/diseno/correspondencia.csv` | Sensado, orden/realimentación, fallos y relación de abstracción. | Planificado | I1 | 4 |
| A14 | Evidencia de pruebas formales | `artefactos/verificacion/obligaciones.csv`; `artefactos/verificacion/rodin/` | PO por identificador, versión, estado, prueba automática o interactiva. | Planificado | I2 | 4 |
| A15 | Instrumentación y ejecutor | `software/telemetria.py`; `experimentos/ejecutar.py`; `experimentos/esquema.json` | Registro JSONL, metadatos, ejecución y manifiesto por corrida. | Planificado | I3 | 4 |
| A16 | Monitores y trazabilidad | `software/monitores.py`; `artefactos/validacion/trazabilidad.csv` | RF → INV/evento → función → escenario → evidencia → artículo. | Cabecera; monitor pendiente | I4 | 4 |
| A17 | Exploración ProB | `modelo/prob/configuracion.json`; `artefactos/verificacion/prob/`; `artefactos/verificacion/prob.md` | Estados/transiciones, límites, deadlocks y contraejemplos reproducibles. | Planificado | I1 | 5 |
| A18 | Integración y fallos | `tests/test_integracion.py`; `artefactos/validacion/integracion.md` | Watchdog, sensor, reinicio, contacto pegado y monitor independiente. | Planificado | I2 | 5 |
| A19 | Datos crudos y manifiestos | `datos/crudos/<run_id>.jsonl`; `datos/manifiestos/<run_id>.json`; `datos/manifest.csv` | Trazas inmutables con escenario, semilla, versión y hash. | Planificado | I3 | 5 |
| A20 | Análisis reproducible | `analisis/metricas.py`; `datos/procesados/resumen.csv`; `artefactos/resultados/analisis.md` | Cálculos por corrida, agregación, intervalos y ausencias. | Planificado | I4 | 5 |
| A21 | Problema y fundamentos del artículo | `secciones/00-resumen.typ`; `secciones/01-introduccion.typ`; `secciones/02-relacionados.typ`; `secciones/03-fundamentos.typ` | Motivación, preguntas, antecedentes y bases; edición con fuentes. | Base Typst | I1 | 6 |
| A22 | Propuesta y formalización del artículo | `secciones/04-propuesta.typ`; `secciones/05-formalizacion.typ` | Arquitectura, invariantes, eventos y alcance de refinamientos. | Base Typst | I2 | 6 |
| A23 | Figuras y evidencia visual | `analisis/figuras.py`; `img/rearme.svg`; `img/escena.png`; `img/latencia.svg`; `img/obligaciones.svg` | Diagramas propios y gráficos/capturas derivados de evidencias. | Rearme base; evidencia pendiente | I3 | 6 |
| A24 | Evaluación y discusión del artículo | `secciones/06-validacion.typ`; `secciones/07-resultados.typ`; `secciones/08-conclusiones.typ`; `artefactos/resultados/resumen.json` | Método, datos medidos, amenazas y conclusiones limitadas. | Base sin mediciones | I4 | 6 |
| A25 | Auditoría de requisitos y fuentes | `artefactos/entrega/auditoria.md` | Revisión cruzada de RF/INV, cifras, citas y enlaces. | Planificado | I1 | 7 |
| A26 | Reproducción independiente | `artefactos/entrega/reproduccion.md` | Un integrante reproduce modelos, pruebas, experimento y PDF de otro. | Planificado | I2 | 7 |
| A27 | Demostración y entrega técnica | `artefactos/entrega/guion.md`; `artefactos/entrega/demo.mp4`; `artefactos/entrega/manifest.sha256` | Guion corto, video y hashes de la versión entregada. | Planificado | I3 | 7 |
| A28 | Artículo final e integración editorial | `main.typ`; `estilo.typ`; `metadatos.typ`; `secciones/09-referencias.typ`; `articulo.pdf` | Compilación, autores, estilo basado en ejemplo y revisión final. | Base compilable | I4 | 7 |

## Convenciones y aceptación

- RF-xx: requisito; INV-xx: invariante; SC-xx: escenario; PO: obligación de prueba; I1–I4: integrantes, reemplazar por nombres.
- `modelo/rodin/Enclavamiento/` conserva TODOS los contextos, máquinas, refinamientos y pruebas nativos; los `.txt` son exportaciones legibles, no reemplazan el proyecto Rodin.
- `artefactos/verificacion/rodin/` contiene exportaciones y capturas de pruebas; `artefactos/verificacion/prob/` contiene comandos, logs y trazas.
- `img/` contiene todas las ilustraciones que consume Typst. No poner capturas en `secciones/`.
- Se considera terminado un paquete cuando su revisor puede abrirlo/reproducirlo, coincide con la versión registrada y está enlazado a la trazabilidad.
- Archivos temporales y cachés no son entregables. Todo nuevo entregable debe registrarse aquí antes de citarse en el artículo.
