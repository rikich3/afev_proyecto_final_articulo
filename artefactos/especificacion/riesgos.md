# A02 — Peligros y supuestos

| ID | Peligro / supuesto | Tratamiento y prueba |
|---|---|---|
| H01 | Entrada mientras existe potencia o movimiento residual. | Puerta física cerrada hasta aislamiento y parada confirmados; monitor usa posición y potencia reales de la escena. |
| H02 | Rearme con un operario o candado restante. | Conjuntos de ocupantes y titulares separados; SC-03/04/10. |
| H03 | RFID ausente pero zona ocupada. | No usar ausencia RFID como prueba de zona vacía; sensor desconocido bloquea. |
| H04 | Contacto pegado. | Leer realimentación; fallo enclavado y acceso denegado; no atribuir a software capacidad de abrir un contacto averiado. |
| H05 | Caída de comunicación o reinicio. | Watchdog en escena; arranque en estado no autorizado; SC-09/11. |
| H06 | Corte eléctrico con energía residual. | Variable física de velocidad/energía; no autorizar acceso por orden de parada sola. |
| H07 | Exclusión de transiciones peligrosas del modelo. | Documentar hipótesis del entorno y ejecutar SC-12 fuera de ellas; no eliminar intrusión para aparentar seguridad universal. |

S1: el acceso normal está controlado por una puerta física que permanece cerrada si la confirmación de aislamiento es falsa o desconocida. S2: las identidades no se suplantan en el MVP; sí se ensayan ID desconocida, pérdida y repetición. S3: las señales válidas poseen marca temporal; su caducidad está fijada antes del experimento. S4: el modelo nominal supone funcionamiento del seccionador y puerta; contacto pegado y apertura forzada son modos de fallo explícitos, no cubiertos por el teorema nominal. S5: se representa energía mecánica residual mediante velocidad hasta parada; no se representa gravedad, presión o múltiples fuentes reales. S6: el planificador ejecuta un único ciclo determinista; las entradas simultáneas se capturan juntas. S7: los escenarios de progreso suponen que operarios salen, liberan sus bloqueos y se atienden las órdenes habilitadas; la seguridad sola no garantiza vivacidad.

La propiedad `¬(presencia_real ∧ potencia_real)` se monitorea siempre. Con latencias o intrusión forzada puede violarse: reportar el contraejemplo y el supuesto roto. Para prevención por distancia, justificar que el tiempo mínimo de llegada desde el perímetro supera detección + decisión + apertura + parada mecánica + margen. Si no se modela esa distancia, no afirmar protección de acceso abierto.

Una parada segura sin orden de arranque es una espera permitida, no un fallo de disponibilidad. Para estudiar deadlock no basta agregar un evento vacío siempre habilitado: comprobar también posibilidad de completar mantenimiento/rearme bajo S7.
