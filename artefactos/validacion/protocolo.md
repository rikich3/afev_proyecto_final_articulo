# A08 — Protocolo experimental previo

Versión 1, 2026-10-07. Protocolo y catálogo preparados; revisión cruzada y
piloto pendientes. [Escenarios JSON](../../experimentos/escenarios.json) es
la configuración declarativa de referencia. No incluye un ejecutor ni
resultados de simulación.

## Preguntas y variables

P1: ¿Los modelos preservan exclusión presencia–potencia y orden de rearme bajo sus supuestos? Evidencia: Rodin y ProB. P2: ¿El controlador conserva el comportamiento especificado en la planta simulada? Evidencia: monitores físicos y trazabilidad. P3: ¿Qué límites exhibe frente a retardo, fallos e intrusión fuera de supuestos? Evidencia: latencias, contraejemplos y condiciones de fallo.

Unidad experimental: una corrida con escena restablecida, estado inicial conocido, escenario y semilla. Factores: escenario, retardo de señal (0/1/3 ticks) y paso (10/20 ms para sensibilidad). La intervención nominal requiere los dos titulares de A05; la participación de uno solo se ensaya como intento de acceso rechazado, no como intervención nominal alternativa. Mantener versión, geometría, motor y duración constantes dentro de cada comparación. Piloto de tres corridas antes de congelar el protocolo. Plan principal pequeño: una ejecución por caso determinista y 30 semillas (0–29) por escenario con jitter/retardo variable, inicialmente SC-06/07/09. Son 90 corridas estocásticas, no 90 evidencias independientes por tick. No tratar repeticiones idénticas deterministas como muestras independientes. Si falta tiempo, declarar el número real, sin rellenarlo.

Los parámetros siguientes fijan la versión del piloto; su congelación para
las corridas finales exige ejecutar el piloto y justificar cualquier cambio.
Son valores de laboratorio, sin significado normativo o certificación.
El JSON conserva sus nombres y unidades para el futuro ejecutor.

| Parámetro JSON | Valor | Justificación / uso |
|---|---:|---|
| `step_s` | 0.020 s | Paso nominal de adquisición y actuación. |
| `sensor_timeout_s` | 0.060 s | Tres pasos nominales; dato caducado cuando edad ≥ límite. |
| `heartbeat_period_s` | 0.020 s | Una secuencia nueva por ciclo. |
| `heartbeat_timeout_s` | 0.100 s | Cinco pasos sin renovación; repetir secuencia no renueva. |
| `contact_open_delay_s` | 0.020 s | Retardo nominal que deberá implementar la planta. |
| `contact_open_timeout_s` | 0.060 s | Tres pasos para confirmar apertura; fallo cuando no abre y edad ≥ límite. |
| `detect_order_budget_s` | 0.040 s | Dos pasos desde detección hasta orden de corte. |
| `incident_cut_budget_s` | 0.160 s | Presupuesto de ensayo: hasta 80 ms de retardo con jitter, 40 ms de decisión, 20 ms de apertura y 20 ms de discretización. |
| `watchdog_cut_budget_s` | 0.140 s | Desde último heartbeat aceptado: 100 ms de timeout, 20 ms de apertura y 20 ms de discretización. |
| `epsilon_parada_m_s` | 0.001 m/s | Umbral propuesto de parada; probar igualdad, valores a ambos lados y velocidad negativa. |
| `velocidad_nominal_m_s` | 0.5 m/s | Condición inicial de marcha para la planta simplificada. |
| `parada_max_s` | 2.0 s | Plazo propuesto para confirmar parada tras corte; calibrar con el modelo de movimiento residual. |
| `scenario_timeout_s` | 15.0 s | Duración máxima de caso; agotarla produce fallo/no evaluable, nunca éxito por ausencia de datos. |

Los timeouts permanecen en segundos en el ensayo de sensibilidad; no convertir
100 ms en cinco ticks de 10 ms. No confundir retardo nominal con plazo de fallo.
La parada mecánica se mide aparte hasta `abs(velocidad) <= epsilon_parada_m_s`.
Si el contacto está pegado, la latencia de apertura se registra como `null` y
el incidente como `no_respondido`, conservándola en el denominador.

## Escenarios obligatorios

| ID | Estímulo | Oráculo esperado | Requisitos |
|---|---|---|---|
| SC-01 | Arranque nominal, zona libre, sensores válidos. | Sólo reset seguido de start nuevo permite marcha. | RF-01/04 |
| SC-02 | Solicitud de mantenimiento con potencia activa. | Parada, aislamiento, bloqueo, energía cero y acceso en ese orden. | RF-01/02 |
| SC-03 | Retiro temprano con otro operario dentro; luego retiro parcial con ambos fuera. | El retiro temprano se rechaza según la fase; el bloqueo restante impide rearme. | RF-03/04 |
| SC-04 | Intentar saltar verificación, retirar bloqueo dentro o start antes de reset. | Rechazo con motivo; sin potencia. | RF-03/04 |
| SC-05 | Start/reset simultáneo a presencia, emergencia o fallo. | Predomina corte; ensayar orden inverso y mismo ciclo. | RF-04/06 |
| SC-06 | Señal de presencia retrasada 0/1/3 ticks. | Medir tiempo y exclusión física; acceso normal permanece cerrado. | RF-01/05 |
| SC-07 | Sensor inválido, congelado o discrepante; RFID ausente. | Revocar permiso, apagar y enclavar fallo. | RF-05 |
| SC-08 | Contacto pegado o realimentación incongruente. | No admitir mantenimiento ni rearme; registrar fallo de corte. | RF-02/10 |
| SC-09 | Pérdida de conexión y heartbeat. | Watchdog local actúa con reloj que avanza; documentar modo stepping. | RF-05/09 |
| SC-10 | ID desconocida, token repetido o intento de retirar bloqueo ajeno. | Ningún desbloqueo indebido. | RF-03 |
| SC-11 | Reinicio en marcha y durante mantenimiento. | Orden apagada; permisos revocados; bloqueo persistente/desconocido. | RF-07 |
| SC-12 | Intrusión forzada con energía o sensor que miente. | El monitor detecta la violación física; clasificar fuera de S1/S4, sin ocultar el fallo. | RF-01, límite |
| SC-13 | Emergencia durante rearme y energía residual tras corte. | Cancelar secuencia; no energizar con permiso antiguo; esperar parada. | RF-02/04/05 |

Agregar pruebas de frontera antes, exactamente en y después de cada timeout y umbral de parada; los valores están en `fronteras` del JSON. Introducir una violación conocida en una copia de prueba para comprobar que el monitor falla; no generar todos los oráculos llamando al propio controlador. No introducir un controlador inseguro en operación real: cualquier ablación es exclusivamente simulada y secundaria.

## Datos por tick y evento

JSONL: `run_id`, `scenario_id`, `seed`, `tick`, `t_sim_s`, `t_wall_ns`, `inputs`, `physical_truth`, `state_before`, `event`, `state_after`, `outputs`, `violated_properties`. Eventos emparejados por `incident_id`: peligro físico, detección, orden de corte, contacto abierto, parada mecánica. Guardar eventos rechazados y motivo. Manifiesto: versiones, commits, hashes, parámetros, SO/CPU, criterio de parada, resultado final y anomalías de registro.

## Métricas y aceptación

| Métrica | Definición | Evidencia / interpretación |
|---|---|---|
| Descarga PO | 100 × PO demostradas / PO generadas por modelo. | Separar automáticas, interactivas, pendientes y descartadas por cambio de versión. Meta: todas las vigentes. |
| Estados explorados | Estados y transiciones de ProB, límite, tiempo y estado de completitud. | Exhaustivo sólo en la instancia finita completamente explorada. |
| Violación física | Número de episodios y duración acumulada con presencia real AND potencia real. | Debe ser cero dentro de supuestos; fuera de ellos informar sin mezclar tasas. |
| Cobertura de requisitos | RF con evidencia aprobada / RF aplicables. | No equivale a cobertura de código o eventos. |
| Cobertura de eventos | Eventos alcanzados / eventos aplicables de M2. | Registrar los nunca habilitados; no inflar con un evento vacío. |
| Rearmes indebidos | Arranques que incumplen secuencia / intentos de arranque. | Cero esperado; con denominador cero usar N/A. |
| Latencia extremo a extremo | t(contacto abierto) − t(incidente de referencia). | ms de simulación; indicar origen (peligro físico, barrera, caducidad o heartbeat), sin mezclar orígenes; informar detección→orden y parada aparte. |
| Fallos de respuesta | Incidentes sin apertura antes del límite / incidentes evaluables. | Reportar junto a latencias de los que sí respondieron. |
| Disponibilidad nominal | Ciclos nominales completados / ciclos nominales pedidos. | No penalizar denegación correcta en escenarios de fallo. |
| Falsos cortes | Cortes no solicitados sin peligro/fallo según oráculo / oportunidades nominales de marcha. | Definir ventana y denominador antes de medir. |

Calcular mediana, p95 y máximo por escenario, con n explícito. p95: método de rango más próximo, posición ceil(0.95*n) en observaciones ordenadas. No interpretar máximos empíricos como cotas demostradas. Intervalos de confianza por remuestreo de corridas (p. ej., 2000 remuestreos y semilla fija), nunca de ticks correlacionados. Ausencias = null/N/A; cero sólo si se midió cero. Datos crudos inmutables; todo CSV/figura se regenera desde ellos. Ningún resultado experimental está ejecutado todavía.

## Preparación y ejecución del catálogo

El JSON contiene **13 escenarios y 34 casos base**. SC-05 se repite con la
lista de órdenes original e inversa, capturadas juntas; SC-06 usa retardos de
0/1/3 ticks. Esto produce **41 combinaciones deterministas planificadas**.
Las 13 comprobaciones escalares de frontera se reportan aparte; no se cuentan
como corridas independientes hasta que cada una tenga preparación y registro.

El catálogo es una especificación de pasos para A12/A15/A18, no un lenguaje
con intérprete ya implementado. `orden` usa los tipos de A05; el ejecutor debe
generar `command_id`/`event_id` nuevos salvo repetición deliberada. Las órdenes
personales incluyen titular y solicitante; el retiro ajeno de SC-10-b debe
rechazarse. Un evento de planta describe ingreso/salida física y su evento
RFID, salvo la pérdida explícita del canal. Los fallos persisten hasta su
retiro o restablecimiento del caso.

Cada caso comienza cargando la escena y reproduciendo un prefijo nominal que
alcance su fixture, con confirmaciones físicas y calidad de señales válida.
No basta escribir `fase=MANTENIMIENTO` para declarar lista una planta que
sigue energizada. Si una confirmación de preparación no llega, registrar
`fallo_preparacion`; no continuar con una precondición ficticia. Un paso de
espera tiene límite; una instrucción siguiente no fuerza la confirmación.

Para SC-13-b se mantiene movimiento residual antes de completar la verificación
de cero, de modo que los bloqueos no concedan permiso de entrada por sí solos.
SC-03-a verifica el retiro prematuro; SC-03-b parte de liberación con ambos
operarios fuera y comprueba que un solo bloqueo restante impide rearme.

### Piloto y congelación

El piloto tiene tres corridas: SC-01-a, SC-02-a y SC-09-a. Requiere controlador,
planta funcional, watchdog, monitor y registro, que se implementarán después
de esta semana. Comprobar transiciones, edades, latencias y recuperación de
estado; verificar además que SC-12 detecta una violación física conocida
antes de confiar en el monitor de las corridas finales.

Guardar cualquier modificación de parámetros como una nueva versión,
conservando configuración anterior, motivo, fecha y hashes. Congelar la versión
antes de la campaña definitiva; no ajustar límites después de observar sus
resultados para convertir fallos en éxitos.

La campaña estocástica agrega 30 corridas por escenario SC-06/07/09, semillas
0–29: **90 corridas planificadas**. Cada semilla selecciona un caso elegible;
SC-09 sólo admite SC-09-a. Usar `random.Random(seed)` con selección en orden:
caso, factor de retardo si aplica, jitter de 0/1 ticks. Registrar las elecciones
para reproducirlas. El jitter afecta al inicio del estímulo y, en SC-06, al
retardo de señal. Las variantes deterministas se ejecutan igualmente aunque
no sean elegidas por la campaña aleatoria.

### Oráculos y clasificación

- Dentro de supuestos: cero episodios presencia-potencia, cero rearme indebido
  y ninguna entrada normal antes de aislamiento/parada/bloqueos.
- SC-08-a: se espera detección del contacto que no abre; registrar fallo físico
  de respuesta y entrada denegada, no reclamar que el software cortó potencia.
- SC-09-c: con stepping congelado, resultado `no_evaluable`; tiempos ausentes
  y evidencia del reloj detenido, separado de los ensayos de watchdog activo.
- SC-12: se espera que el monitor detecte la violación, bajo ruptura de S1/S4.
  Su detección valida al monitor; no constituye éxito de la propiedad nominal.
- Cualquier reinicio conserva bloqueos o los trata como desconocidos; una
  ausencia de estado no se interpreta como permiso.

Clasificación de corrida: `cumple_oraculo`, `no_cumple_oraculo`,
`fallo_preparacion` o `no_evaluable`. Estado de respuesta física por incidente:
`respondido`, `no_respondido` o `no_aplicable`. Conservar ambos: detectar un
contacto pegado puede cumplir el oráculo de diagnóstico y aun así registrar
una respuesta física fallida. Las corridas censuradas y los datos faltantes
se reportan con sus motivos, sin eliminarlos de forma silenciosa.

Una oportunidad nominal de marcha es una solicitud válida con zona libre,
sin fallos y condiciones físicas de rearme satisfechas. Un corte pedido por
stop o mantenimiento no es un falso corte. La ventana de observación abarca
la corrida hasta su final/timeout; registrar el denominador real.

## Entrega de A08 y comprobaciones disponibles

A08 entrega este protocolo y `experimentos/escenarios.json`, con trazabilidad
RF→escenario, fixtures, pasos, criterios, parámetros, semillas y fronteras.
Los comandos del ejecutor/análisis permanecen planificados en A15/A20.
Los resultados físicos siguen sin ejecutar; las pruebas de M0 corresponden a
A06 y no se presentan como corridas de CoppeliaSim.

Comprobaciones de archivos disponibles:

```sh
python -m json.tool experimentos/escenarios.json > /dev/null
python herramientas/verificar.py
```

Estado: protocolo y catálogo definidos; revisión del equipo y piloto pendientes.
Revisor / fecha / observaciones: pendiente.
