# A01 — Alcance y requisitos

Prototipo académico enteramente simulado de un supervisor de enclavamiento para **una faja transportadora, una zona de peligro y dos operarios identificables**. Geometría sencilla y sensores simulados; RFID se representa por eventos de identidad, sin emular radiofrecuencia. Láser y barrera aportan presencia/estado, no identidad confiable. Un contacto de potencia, un seccionador bloqueable, una barrera de acceso y energía residual simplificada completan el banco. La barrera física añadida hace explícito cómo se impide entrar antes de aislar: no confundir una barrera fotoeléctrica con una puerta física.

## Requisitos y criterios de aceptación propuestos

| ID | Requisito | Evidencia / criterio |
|---|---|---|
| RF-01 | Excluir presencia y potencia en la misma zona bajo los supuestos A02. | INV-01 en Rodin; cero estados físicos inseguros en corridas dentro de supuestos. |
| RF-02 | Aislar antes de autorizar mantenimiento; verificar contacto abierto y energía residual nula. | SC-02/08; acceso cerrado hasta confirmación. |
| RF-03 | Mantener un bloqueo por operario; sólo su titular lo retira después de salir. | SC-03/10; cualquier bloqueo impide conectar. |
| RF-04 | Rearmar sólo después de zona libre, salida de todos, retiro de bloqueos, cierre de acceso y reconocimiento manual; arrancar por orden separada. | SC-04/05; reset nunca activa potencia y un start anterior al reset no se reutiliza. |
| RF-05 | Ante peligro, dato inválido/caducado o discrepancia, desactivar orden de potencia y enclavar fallo. | SC-06/07/09; registrar tiempo de corte y confirmación. |
| RF-06 | Resolver órdenes simultáneas dando prioridad a parada/fallo sobre reset/start. | SC-05; ambas permutaciones de cada pareja y entradas en el mismo ciclo. |
| RF-07 | Arrancar y reiniciar con potencia ordenada apagada, permisos revocados y bloqueos conservados o estado desconocido bloqueante. | SC-11; no reconectar automáticamente. |
| RF-08 | Registrar entradas, decisiones, salida física y evidencia por corrida. | A15/A16; trazas completas y versión de modelo/controlador identificada. |
| RF-09 | Ante pérdida del cliente, el watchdog local abre el contacto simulado y bloquea acceso. | SC-09; inyección sin pedir al cliente desconectado que actúe. |
| RF-10 | Detectar negativa del contacto a abrir; denegar acceso/rearme. | SC-08; orden apagada no equivale a potencia física apagada. |

Los límites temporales son parámetros de laboratorio fijados en A08, no valores normativos. La ausencia de falsas alarmas es una métrica secundaria, nunca motivo para omitir el corte conservador.

## Fuera del alcance

Instalación real, diseño de electrónica de seguridad, certificación SIL/PL, propagación electromagnética RFID/láser y propiedades materiales de una faja minera. El prototipo representa el procedimiento LOTO; un registro RFID o una variable no reemplaza el aislamiento físico ni los candados personales.
