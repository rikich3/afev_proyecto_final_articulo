#import "/estilo.typ": tabla
= Propuesta del sistema

== Caso de aplicación y requisitos

Dos operarios solicitan intervenir una faja en una zona delimitada. La secuencia prevista exige parar, abrir el seccionador, confirmar los bloqueos de ambos y verificar la ausencia de movimiento residual antes de habilitar el acceso. Al terminar, cada operario sale y retira su bloqueo. El rearme exige zona libre y una orden manual, seguida de una orden de arranque nueva. Si uno permanece dentro o conserva su bloqueo, la energización debe seguir inhibida. Este caso permite formular los requisitos siguientes.

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

Los requisitos se agrupan en exclusión y acceso (RF-01/02), participación individual y rearme (RF-03/04/06), respuesta a fallos (RF-05/07/09/10) y registro (RF-08). La aceptación combina obligaciones formales y escenarios con observación física. El protocolo fija los presupuestos temporales antes de las corridas finales.

== Alcance y arquitectura

La escena geométrica contiene una faja, dos operarios, sensores representados visualmente, un contacto, un seccionador y una puerta articulada. Un script Lua aplica las órdenes a la escena y modela la realimentación del contacto, la desaceleración y los eventos RFID de los cruces. El watchdog local conserva su reloj y la última secuencia aceptada. La barrera fotoeléctrica se distingue de la puerta: detectar un cruce no impide por sí mismo el ingreso.

La arquitectura de @fig-arquitectura separa adquisición, decisión, actuación y observación. El controlador Python implementa una transición de estado que prioriza fallo o emergencia y después parada. El adaptador ZeroMQ conecta el supervisor con el script de planta. El contrato distingue observaciones previas al paso, órdenes emitidas y confirmaciones físicas posteriores.

#figure(image("/img/arquitectura.svg", width: 100%), caption: [Arquitectura del enclavamiento simulado. El monitor consulta la planta por un canal independiente.]) <fig-arquitectura>

La @fig-clases presenta las entidades del dominio mediante atributos tipados, asociaciones y multiplicidades UML. Zona y Operario corresponden a los conjuntos portadores de Event-B. Potencia y ocupación se representan mediante las variables de M0. El bloqueo personal pertenece al refinamiento M1.

#figure(image("/img/clases-conceptuales.svg", width: 100%), caption: [Clases y multiplicidades UML del enclavamiento para una zona y dos operarios.]) <fig-clases>

La arquitectura exige que el permiso de acceso dependa de apertura del contacto, aislamiento y parada confirmados. La ocupación real procede de la geometría de la escena y la potencia real del circuito simulado. El monitor observa ambos valores para contrastar RF-01. El oráculo utiliza la posición de los avatares y el estado de la planta, con independencia de las lecturas RFID del controlador.

== Secuencia de rearme

La secuencia de @fig-rearme exige salida de todos los operarios, retiro de bloqueos por sus titulares, cierre de acceso, restablecimiento del circuito y reconocimiento manual. El reset prepara el sistema y no activa la potencia. El arranque requiere una orden nueva en un ciclo posterior. Un fallo invalida las autorizaciones acumuladas y conduce a fallo enclavado.

#figure(image("/img/rearme.svg", width: 100%), caption: [Liberación y rearme. La línea discontinua indica la transición a fallo desde cualquier etapa.]) <fig-rearme>

La secuencia conserva bloqueos y ocupantes hasta confirmar su liberación. Una emergencia revoca el permiso acumulado y exige recuperar condiciones seguras antes del rearme. La puerta y el seccionador se actúan mediante sus articulaciones en la escena.
