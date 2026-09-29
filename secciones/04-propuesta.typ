#import "/estilo.typ": recurso, evidencia
= Propuesta del sistema

== Requerimientos

Los requerimientos del supervisor se delimitan a una faja, una zona de peligro y dos operarios. Se identifican mediante códigos estables para vincularlos con invariantes, eventos y escenarios de prueba. Su especificación y criterios de aceptación se conservan en #recurso("A01", "artefactos/especificacion/requisitos.md"), mientras que las hipótesis de validez se explicitan en #recurso("A02", "artefactos/especificacion/riesgos.md").

- *RF-01. Exclusión presencia–potencia:* el sistema debe impedir la coexistencia de operarios y potencia activa en la zona, bajo los supuestos de acceso controlado y funcionamiento establecidos.
- *RF-02. Aislamiento previo al acceso:* debe mantener el acceso cerrado hasta confirmar el aislamiento, la apertura del contacto y la ausencia de energía residual.
- *RF-03. Bloqueo individual:* debe conservar un bloqueo por operario y permitir su retiro únicamente al titular después de salir. Cualquier bloqueo restante debe impedir la energización.
- *RF-04. Rearme secuencial:* debe exigir zona libre, salida de todos los operarios, retiro de bloqueos, cierre de acceso y reconocimiento manual. El arranque requiere una orden posterior e independiente del reset.
- *RF-05. Respuesta ante peligro o fallo:* debe desactivar la orden de potencia y enclavar el fallo cuando detecte peligro, datos inválidos o caducados, o discrepancias entre señales.
- *RF-06. Prioridad de parada:* debe resolver órdenes simultáneas dando prioridad a parada, emergencia y fallo sobre reset y arranque.
- *RF-07. Inicio y reinicio seguros:* debe iniciar con la orden de potencia apagada y los permisos revocados. Los bloqueos deben conservarse o tratarse como desconocidos, impidiendo la reconexión automática.
- *RF-08. Registro de evidencia:* debe registrar entradas, decisiones, salidas y estado físico por corrida, identificando las versiones del modelo y del controlador.
- *RF-09. Supervisión de comunicación:* ante pérdida del cliente, un watchdog local debe ordenar la apertura del contacto simulado y bloquear el acceso, sin depender del proceso desconectado.
- *RF-10. Confirmación del corte:* debe detectar la negativa del contacto a abrir y denegar el acceso y el rearme; una orden de apagado no constituye confirmación de ausencia de potencia.

La aceptación combina pruebas de invariantes y evaluación de escenarios. Los presupuestos temporales se fijan previamente en el protocolo experimental como parámetros del laboratorio. La correspondencia entre cada requerimiento y su evidencia se documenta en #recurso("A16", "artefactos/validacion/trazabilidad.csv").

== Alcance y arquitectura

La planta simulada contiene una faja transportadora, dos operarios, sensores de presencia, identificación por eventos RFID, un contacto de potencia y un seccionador bloqueable. Se añade una puerta de acceso enclavada para representar el mecanismo que impide el ingreso normal antes de confirmar aislamiento y parada. La barrera fotoeléctrica se mantiene como sensor y no se confunde con esa restricción física.

La arquitectura de @fig-arquitectura separa adquisición, decisión, actuación y observación. Un único ciclo captura las entradas y procesa primero fallo o emergencia, luego parada y mantenimiento, y finalmente reset y arranque. El controlador se define como una transición pura de estado; el adaptador encapsula las llamadas a CoppeliaSim. El contrato se especifica en #recurso("A05", "artefactos/diseno/arquitectura.md").

#figure(image("/img/arquitectura.svg", width: 100%), caption: [Arquitectura propuesta y canal independiente de observación física.]) <fig-arquitectura>

El acceso se autoriza sólo después de abrir el seccionador, aplicar los bloqueos previstos y verificar la ausencia de energía residual. Los dos operarios aplican sus bloqueos antes de ingresar; el alcance mínimo no admite incorporaciones durante una intervención. Cada titular retira únicamente su propio bloqueo después de salir.

== Secuencia de rearme

La secuencia de @fig-rearme exige salida de todos los operarios, retiro de bloqueos por sus titulares, cierre de acceso, restablecimiento del circuito y reconocimiento manual. El reset prepara el sistema y no activa la potencia. El arranque requiere una orden nueva en un ciclo posterior. Un fallo invalida las autorizaciones acumuladas y conduce a fallo enclavado.

#figure(image("/img/rearme.svg", width: 100%), caption: [Secuencia de liberación. Ninguna etapa posterior puede omitir una anterior; un fallo revoca el permiso.]) <fig-rearme>

La irreversibilidad se entiende como imposibilidad de saltar etapas o reutilizar permisos antiguos. No impide retornar a un estado seguro. La escena canónica se conserva en #recurso("A07", "simulacion/mina.ttt"), y @fig-escena reserva la evidencia visual de su implementación.

#figure(evidencia("escena.png", [Vista de la faja, la zona y los operarios]), caption: [Banco de simulación. Captura pendiente de implementación.]) <fig-escena>
