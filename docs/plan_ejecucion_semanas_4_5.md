# Plan de ejecución — semanas 4 y 5

Este plan convierte A13–A20 en trabajo verificable. El proyecto es un
prototipo académico para una faja, una zona de peligro y dos operarios. La
propiedad central es que no haya un operario físicamente dentro de la zona con
potencia física activa. No se debe afirmar certificación industrial ni usar una
orden del controlador como si fuera confirmación física.

## 1. Estado real al comenzar

La revisión del repositorio encontró estas bases disponibles:

- A01, A02, A05 y A08: requisitos, riesgos, contrato de arquitectura y
  protocolo de pruebas documentados.
- A06: C0/M0 nativo de Rodin y cinco obligaciones de M0 demostradas.
- A07: escena geométrica de CoppeliaSim, sin comportamiento de seguridad.

No están presentes todavía `software/`, `tests/`, M1, M2, el adaptador, el
ejecutor ni las corridas. Por tanto, los paquetes A13–A20 no se pueden cerrar
como si la cadena ya funcionara. El primer objetivo operativo es disponer de
un corte vertical mínimo y reproducible:

```text
escena dinámica → snapshot → controlador → órdenes → planta → observación física
                                      ↘ registro y monitor independiente
```

Una maqueta, un archivo de prueba o una traza sintética puede probar una unidad
de software, pero no cuenta como resultado de CoppeliaSim. Debe llevar la
etiqueta `fixture_de_prueba` o `simulador_falso`.

## 2. Reglas de trabajo del equipo

1. Mantener el alcance: una zona y dos operarios. No añadir ROS, cámara,
   hardware, más máquinas ni interfaz gráfica.
2. Usar el contrato A05 como interfaz común. El adaptador es el único módulo
   Python que se conecta con CoppeliaSim; la lógica y los monitores reciben
   valores simples y no usan ZeroMQ.
3. En cada tick: adquirir el `snapshot`, decidir, emitir órdenes, avanzar un
   paso, y registrar la observación física posterior. No mezclar ambos lados
   del paso.
4. Si un sensor es desconocido, inválido o caducado, la decisión debe ser
   conservadora: contactor apagado, entrada denegada y fallo registrado.
5. Nunca usar `orden_contactor` o la fase interna para demostrar que la planta
   estaba segura. El monitor obtiene presencia y potencia de la escena.
6. Cada corrida usa una escena restablecida, `run_id`, `scenario_id`, semilla,
   versiones, parámetros, hashes y resultado final. El JSONL crudo no se edita
   después; los CSV, gráficas y resúmenes se regeneran desde él.
7. Todo hallazgo se conserva: PO pendiente, contraejemplo, fallo de preparación,
   corrida censurada y dato ausente. Un dato no medido se expresa como `null` o
   `N/A`, nunca como cero.

La revisión cruzada continúa siendo: I2 revisa I1, I3 revisa I2, I4 revisa I3
e I1 revisa I4. Una revisión verifica que los archivos abren, se regeneran y
coinciden con la versión indicada; no es sólo una lectura superficial.

## 3. Puerta de entrada: primera hora de la semana 4

Antes de repartir trabajo, ejecutar estas comprobaciones y registrar el
resultado en la bitácora del equipo:

1. Revisar A05, A08 y los supuestos A02; confirmar que no hubo cambios de
   contrato sin actualizar `experimentos/escenarios.json`.
2. Importar M0 en Rodin y comprobar sus cinco POs. Registrar la versión de
   Rodin, ProB, JRE, CoppeliaSim, Python y sistema operativo.
3. Validar `experimentos/escenarios.json` y ejecutar
   `python herramientas/verificar.py`.
4. Comprobar qué falta de semana 3: A09 controlador, A10 M1, A11 adaptador y
   A12 pruebas. En el estado actual del repositorio faltan los cuatro.

Si A09–A12 siguen ausentes, no iniciar una campaña de resultados en semana 5.
Usar el tiempo para construir interfaces, pruebas unitarias con dobles de
prueba y el primer corte vertical. Cuando se complete ese corte, ejecutar sólo
el piloto de A08 (SC-01-a, SC-02-a y SC-09-a); congelar parámetros únicamente
si el piloto funciona y el monitor detecta una violación introducida a propósito.

## 4. Orden de dependencia

| Orden | Resultado mínimo | Habilita |
|---:|---|---|
| 1 | A10: M1 con bloqueos, aislamiento y fases; A09: controlador puro | A13, A14, A16 y A18 |
| 2 | A11: adaptador y planta con señales, contacto, puerta, seccionador y watchdog | A15, A16 y A18 |
| 3 | A13, A14, A15 y A16 revisados | A17, piloto y A18 |
| 4 | Piloto aprobado y configuración congelada | A19 y A20 |

Los paquetes de los renglones 1 y 2 pertenecían a la semana 3. Si no se
entregaron, el equipo debe recuperarlos primero y registrar la desviación; no
es correcto marcar A13–A20 como terminados sólo por haber creado carpetas.

## 5. Semana 4 — construir evidencia, no resultados

Cada integrante tiene 8 h: 6 h de producción, 1 h de revisión y 1 h de
documentación/coordinación. Trabajar en ramas o commits pequeños por artefacto,
sin editar simultáneamente el contrato A05.

| Responsable | Paquete y pasos | Entregable y criterio de salida |
|---|---|---|
| I1 | **A13, M2 e interfaz.** Recuperar M1 si falta. Añadir a M2 señales observadas, órdenes, confirmaciones y fallo; conservar un invariante que conecte potencia/presencia abstracta con su representación concreta. Definir invariantes de enlace, refinar eventos existentes y clasificar eventos nuevos. Completar la matriz de correspondencia: variable Event-B, abstracción, función Python, precondición, postcondición y prueba. | `modelo/export/M2.txt` y `artefactos/diseno/correspondencia.csv`; M2 compila en Rodin y cada fila enlaza con código o queda claramente pendiente. |
| I2 | **A14, evidencia formal.** Recuperar M1/M2, ejecutar chequeo estático y generar POs. Por cada PO registrar identificador, modelo, versión/hash, tipo, estado, método (automático/interactivo) y ubicación de evidencia. Reproducir las POs de M0 antes de consolidar el registro. | `artefactos/verificacion/obligaciones.csv` y exportaciones/logs en `artefactos/verificacion/rodin/`; no hay conteos inventados y cada PO pendiente se ve. |
| I3 | **A15, instrumentación y ejecutor.** Definir el esquema de una línea JSONL y el manifiesto. Implementar primero escritura atómica por corrida, validación de campos y hashes. Después crear un ejecutor que cargue un caso A08, restablezca escena, haga ticks y entregue `command_id`/`event_id` nuevos. | `software/telemetria.py`, `experimentos/esquema.json`, `experimentos/ejecutar.py`; una corrida de prueba produce JSONL y manifiesto válidos, sin llamarla experimento final. |
| I4 | **A16, monitores y trazabilidad.** Implementar un monitor puro que reciba sólo verdad física postpaso: ocupantes reales, potencia real, velocidad, puerta y seccionador. Debe emitir una violación cuando `ocupantes_reales` y `potencia_real` coinciden. Preparar una prueba con violación conocida y una segura. Completar la matriz RF → invariante/evento → función → escenario → evidencia → sección, conservando `pendiente` donde aún no exista evidencia. | `software/monitores.py`, pruebas del monitor y `artefactos/validacion/trazabilidad.csv`; la prueba de violación falla de forma detectable y la matriz no contiene evidencia ficticia. |

### Secuencia recomendada para I4 (A16)

1. Acordar con I3 el objeto `physical_truth` del JSONL: debe contener tick,
   tiempo simulado, ocupantes por geometría, contacto/potencia real, velocidad,
   puerta y seccionador reales.
2. Escribir primero tres casos de prueba: zona vacía con potencia, ocupante con
   potencia apagada y ocupante con potencia activa. Sólo el último es una
   violación de RF-01.
3. Implementar funciones sin acceso a CoppeliaSim, por ejemplo una función que
   recibe el objeto físico y devuelve una lista de propiedades violadas. No
   puede leer la fase ni las salidas del controlador.
4. Añadir controles para datos físicos desconocidos: no declarar éxito; emitir
   `no_evaluable` o fallo de observación según lo defina el equipo.
5. Completar cada fila de trazabilidad cuando existe una función o caso. Para
   evidencia futura, dejar la celda como `pendiente`, no como `cumple`.
6. Pedir a I1 revisar la matriz y a I3 ejecutar el monitor sobre una traza de
   prueba. Guardar el resultado de esa revisión.

## 6. Semana 5 — validar, ejecutar y analizar

No comenzar la campaña de 90 corridas hasta terminar el piloto y congelar
escenarios, timeouts, versiones y semillas. Si el piloto falla, la salida de la
semana es el informe del fallo, su traza y la corrección; repetir campañas sin
registrar causa destruye la reproducibilidad.

| Responsable | Paquete y pasos | Entregable y criterio de salida |
|---|---|---|
| I1 | **A17, exploración ProB.** Cargar versión estable de M2, fijar dominios finitos, límites y preferencias antes de ejecutar. Buscar violaciones de invariantes y deadlocks; guardar configuración, fecha, versión, estados, transiciones, límite y si la exploración terminó o se truncó. Reproducir contraejemplos, si aparecen. | `modelo/prob/configuracion.json`, `artefactos/verificacion/prob/` y `prob.md`; “sin error hasta el límite” no se presenta como exploración exhaustiva. |
| I2 | **A18, integración y fallos.** Crear pruebas de punta a punta para el piloto y los fallos SC-07, SC-08, SC-09 y SC-11: dato caducado, contacto pegado, watchdog y reinicio. Cada prueba usa el adaptador, controlador, planta y monitor; separar pruebas con simulador falso de las que abren CoppeliaSim. | `tests/test_integracion.py` y `artefactos/validacion/integracion.md`; cada caso conserva precondición, estímulo, resultado esperado, resultado observado y ruta de traza. |
| I3 | **A19, datos y manifiestos.** Tras piloto aprobado, ejecutar primero todos los casos deterministas factibles; después las 30 semillas de SC-06/07/09. Crear una carpeta por `run_id`, un manifiesto inmutable y una fila de índice por corrida. Registrar fallos de preparación y `no_evaluable`. | `datos/crudos/`, `datos/manifiestos/` y `datos/manifest.csv`; cada corrida se puede localizar y relacionar con su versión y semilla. |
| I4 | **A20, análisis reproducible.** Leer sólo JSONL/manifiestos; validar esquema; agrupar por corrida y escenario; calcular los indicadores del protocolo. Generar CSV de resumen, informe metodológico y actualizar el JSON que consume el artículo. Probar el cálculo con fixtures etiquetados, sin copiar sus valores al artículo. | `analisis/metricas.py`, `datos/procesados/resumen.csv`, `artefactos/resultados/analisis.md` y `artefactos/resultados/resumen.json`; todo número tiene fuente, n y escenario. |

### Secuencia recomendada para I4 (A20)

1. Definir una función de carga que rechace JSONL o manifiestos incompletos y
   devuelva errores claros. Nunca intentar “arreglar” datos crudos durante el
   análisis.
2. Tratar una corrida como unidad estadística. Los ticks sirven para medir un
   episodio, pero no son réplicas independientes.
3. Por escenario, calcular: número de corridas, clasificación de corrida,
   episodios y duración de `ocupante ∧ potencia`, rearme indebido, cobertura de
   requisitos/eventos, y latencias de detección, orden, apertura y parada.
4. Una ausencia de apertura es `no_respondido`, tiene latencia `null` y sigue
   en el denominador de fallos de respuesta. No sustituirla por cero ni
   excluirla para mejorar percentiles.
5. Calcular mediana, p95 de rango más próximo y máximo sólo sobre respuestas
   observadas; publicar junto a `n`, cantidad de ausentes y escenario. Si se
   usan intervalos, remuestrear corridas con una semilla fija.
6. Crear `resumen.csv` desde el script y actualizar `resumen.json` desde ese
   CSV. Mientras no haya corridas reales, sus campos permanecen `null`.
7. Ejecutar el análisis dos veces sobre los mismos datos y comparar hashes de
   salida. Solicitar a I1 una revisión de que cada métrica responde a una
   pregunta o requisito del protocolo.

## 7. Buenas prácticas aplicadas

- El refinamiento Event-B requiere relacionar el estado concreto y abstracto
  mediante invariantes de enlace y POs; por eso A13 no es sólo añadir variables
  a M0. Referencia: [semántica y POs de Event-B](https://wiki.event-b.org/images/SM%26D-KAR.pdf).
- ProB sirve para animación y exploración finita, pero se debe registrar el
  límite y la completitud. Sus verificaciones encuentran deadlocks y
  violaciones de invariantes durante la exploración; una búsqueda interrumpida
  no demuestra el modelo completo. Referencia: [manual de validación de
  ProB](https://prob.hhu.de/w/index.php?title=Handbook%2FValidation).
- El modo *stepping* de CoppeliaSim permite sincronizar una aplicación externa
  con cada paso de simulación, que es la base para la secuencia adquirir →
  decidir → actuar → observar. Referencia: [API remota ZeroMQ de
  CoppeliaSim](https://manual.coppeliarobotics.com/en/zmqRemoteApiOverview.htm).
- Registrar configuración, versión, hash, semilla y dato crudo permite que
  otra persona reproduzca el cálculo. El artículo sólo mostrará mediciones
  derivadas de ese registro y distinguirá pruebas formales, exploración finita
  y simulación.

## 8. Riesgos y decisiones de contingencia

| Riesgo observado | Decisión |
|---|---|
| Faltan A09–A12 | Recuperar el corte vertical mínimo y limitar semana 5 al piloto. No ejecutar campaña ni completar tablas con valores simulados. |
| M2 produce POs pendientes | Registrar ID y causa; corregir el modelo o limitar la afirmación del artículo. No marcar descarga 100 %. |
| La escena no avanza cuando se pierde el cliente | SC-09 es `no_evaluable` para latencia de watchdog; documentar el reloj detenido y corregir la configuración. |
| El monitor no detecta la violación inyectada | Detener la campaña: no hay oráculo independiente confiable todavía. |
| Contacto pegado | La prueba puede cumplir el oráculo si detecta el fallo, pero la respuesta física se registra como `no_respondido`. |
| Falta tiempo | Reducir decoración, variantes de ruido y análisis opcionales; conservar M0/M1/M2, el monitor independiente, escenarios críticos y reproducción. |

## 9. Lista final de aceptación

Antes de decir que las semanas 4 y 5 están terminadas, comprobar:

- [ ] Cada archivo creado está registrado en `artefactos/artefactos.md`.
- [ ] Los modelos abren en Rodin y sus POs tienen registro por versión.
- [ ] Existe una traza de piloto reproducible y el monitor detecta la
      violación deliberada.
- [ ] Cada manifiesto identifica escenario, semilla, versiones, parámetros y
      hashes.
- [ ] El análisis se regenera desde JSONL y conserva fallos, ausencias y `n`.
- [ ] La trazabilidad enlaza cada RF aplicable con una evidencia o con el
      estado `pendiente` justificado.
- [ ] Un revisor distinto ejecutó las comprobaciones indicadas y registró el
      resultado.

