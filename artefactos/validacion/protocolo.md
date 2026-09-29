# A08 — Protocolo experimental previo

## Preguntas y variables

P1: ¿Los modelos preservan exclusión presencia–potencia y orden de rearme bajo sus supuestos? Evidencia: Rodin y ProB. P2: ¿El controlador conserva el comportamiento especificado en la planta simulada? Evidencia: monitores físicos y trazabilidad. P3: ¿Qué límites exhibe frente a retardo, fallos e intrusión fuera de supuestos? Evidencia: latencias, contraejemplos y condiciones de fallo.

Unidad experimental: una corrida con escena restablecida, estado inicial conocido, escenario y semilla. Factores: escenario, número de operarios (1/2), retardo de señal (0/1/3 ticks) y paso (10/20 ms para sensibilidad). Mantener versión, geometría, motor y duración constantes dentro de cada comparación. Piloto de tres corridas antes de congelar el protocolo. Plan principal pequeño: una ejecución por caso determinista y 30 semillas (0–29) por escenario con jitter/retardo variable, inicialmente SC-06/07/09. Son 90 corridas estocásticas, no 90 evidencias independientes por tick. No tratar repeticiones idénticas deterministas como muestras independientes. Si falta tiempo, declarar el número real, sin rellenarlo.

Parámetros de laboratorio propuestos: paso nominal 20 ms; caducidad sensor 60 ms; heartbeat 20 ms y timeout 100 ms; presupuesto detección→orden 40 ms; apertura nominal contacto 20 ms. Parámetros sujetos al piloto, con justificación geométrica y temporal en el manifiesto; no son límites legales ni certifican seguridad. La parada mecánica se mide por separado hasta velocidad menor o igual al umbral epsilon predefinido; no se confunde con apertura de contacto. Para contacto pegado no hay latencia de corte finita: marcar no respondido, no eliminar la corrida.

## Escenarios obligatorios

| ID | Estímulo | Oráculo esperado | Requisitos |
|---|---|---|---|
| SC-01 | Arranque nominal, zona libre, sensores válidos. | Sólo reset seguido de start nuevo permite marcha. | RF-01/04 |
| SC-02 | Solicitud de mantenimiento con potencia activa. | Parada, aislamiento, bloqueo, energía cero y acceso en ese orden. | RF-01/02 |
| SC-03 | Dos operarios; uno sale y retira su bloqueo. | El bloqueo restante impide rearme. | RF-03/04 |
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

Agregar pruebas de frontera inmediatamente antes/después de timeout y umbral de parada. Introducir una violación conocida en una copia de prueba para comprobar que el monitor falla; no generar todos los oráculos llamando al propio controlador. No introducir un controlador inseguro en operación real: cualquier ablación es exclusivamente simulada y secundaria.

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
| Latencia extremo a extremo | t(contacto abierto) − t(peligro físico). | ms de simulación; informar detección→orden y tiempo hasta parada aparte. |
| Fallos de respuesta | Incidentes sin apertura antes del límite / incidentes evaluables. | Reportar junto a latencias de los que sí respondieron. |
| Disponibilidad nominal | Ciclos nominales completados / ciclos nominales pedidos. | No penalizar denegación correcta en escenarios de fallo. |
| Falsos cortes | Cortes sin peligro/fallo según oráculo / oportunidades nominales. | Definir ventana y denominador antes de medir. |

Calcular mediana, p95 y máximo por escenario, con n explícito. p95: método de rango más próximo, posición ceil(0.95*n) en observaciones ordenadas. No interpretar máximos empíricos como cotas demostradas. Intervalos de confianza por remuestreo de corridas (p. ej., 2000 remuestreos y semilla fija), nunca de ticks correlacionados. Ausencias = null/N/A; cero sólo si se midió cero. Datos crudos inmutables; todo CSV/figura se regenera desde ellos. Ningún resultado experimental está ejecutado todavía.
