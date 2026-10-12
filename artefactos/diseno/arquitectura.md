# A05 — Arquitectura y contrato del enclavamiento

Estado: contrato de diseño definido; pendiente de revisión cruzada del equipo.
Este documento fija las interfaces para A06, A07 y A08. No afirma que el
controlador, la planta funcional o las pruebas formales estén implementados.

## 1. Alcance y decisiones

Una faja, una zona y dos operarios (`1` y `2`), conforme a A01/A02. La puerta
controla el acceso normal; la barrera fotoeléctrica detecta tránsito y el sensor
volumétrico representa presencia. RFID aporta eventos de identidad. La ausencia
de un evento RFID no demuestra que la zona esté vacía.

Se distinguen orden de contactor, contacto real, seccionador, bloqueos personales
y movimiento residual. Ordenar apagado no confirma aislamiento. La condición
para autorizar entrada es contacto abierto, seccionador abierto, parada
confirmada, ambos bloqueos aplicados y señales válidas. La salida de los
operarios debe seguir disponible cuando se deniega una nueva entrada.

Un único proceso Python ejecuta ciclos discretos, con una función de transición
pura y un adaptador ZeroMQ. Un watchdog Lua reside en la escena. La observación
física y los registros usan un canal separado de las entradas del controlador.
Ver [diagrama](../../img/arquitectura.svg).

## 2. Componentes y responsabilidades

Las rutas siguientes son contratos de ubicación; salvo la geometría de A07,
los componentes ejecutables siguen planificados.

| Componente | Responsabilidad | Entregable |
|---|---|---|
| Event-B/Rodin | C0/M0: presencia y potencia; C1/M1: aislamiento, bloqueos y fases; M2: señales, órdenes, realimentación y fallos. | A06/A10/A13 |
| `software/estado.py` | Tipos del estado, fases, IDs y motivos; sin acceso al simulador. | A09 |
| `software/controlador.py` | `step(estado, snapshot, ordenes) -> (nuevo_estado, salidas, eventos)`; transición determinista sin efectos externos. | A09 |
| `software/adaptador.py` | Adquirir snapshot, transportar salidas y heartbeat, avanzar la escena y recoger observaciones. Único componente Python que usa ZeroMQ. | A11 |
| Planta CoppeliaSim | Geometría, posiciones, sensores, contacto, seccionador, puerta y velocidad residual; aplica órdenes con retardos y fallos explícitos. | A07/A11/A18 |
| `simulacion/scripts/watchdog.lua` | Detectar caducidad del heartbeat, revocar permiso de entrada y ordenar apertura del contacto nominal, conservando fallo local hasta rearme válido. | A07/A18 |
| `software/monitores.py` | Evaluar ocupación y potencia físicas; no usar el estado del controlador como oráculo. | A16 |
| `software/telemetria.py` | Registrar entradas, decisiones, rechazos, salidas y observación física. | A15 |
| Ejecutor y análisis | Preparar escenarios/semillas, ejecutar corridas y derivar métricas desde datos crudos. | A08/A15/A20 |

Event-B se vincula al controlador mediante correspondencia manual revisada;
las pruebas del modelo no constituyen prueba automática del código Python.

## 3. Contrato de entrada: snapshot

`Snapshot` es un valor inmutable capturado al comienzo de un ciclo. Las
magnitudes usan unidades SI. Los booleanos desconocidos se representan con
`null`, nunca con un valor que autorice marcha. Los flotantes deben ser finitos.
Un formato o tipo incorrecto se trata como fallo de entrada.

| Campo | Tipo / unidad | Significado |
|---|---|---|
| `tick` | entero ≥ 0 | Índice de adquisición dentro de una corrida. |
| `t_sim_s` | real ≥ 0, s | Tiempo físico simulado de adquisición. |
| `laser_ocupado` | booleano o `null` | Presencia observada por el sensor volumétrico. El nombre conserva el contrato inicial; no emula física láser. |
| `barrera_libre` | booleano o `null` | Haz del acceso no interrumpido; no equivale a zona vacía. |
| `puerta_cerrada` | booleano o `null` | Realimentación del cierre físico, no la orden de cierre. |
| `rfid_eventos` | lista de eventos | Eventos de ingreso/salida identificados, definidos abajo. Lista vacía no borra ocupantes registrados. |
| `contacto_cerrado` | booleano o `null` | Realimentación del contacto de potencia. |
| `seccionador_abierto` | booleano o `null` | Realimentación del aislamiento por seccionador. |
| `bloqueos_confirmados` | conjunto de IDs o `null` | Titulares cuyos bloqueos en escena están confirmados. |
| `velocidad_m_s` | real o `null`, m/s | Velocidad medida de la banda; para parada se utiliza su valor absoluto. |
| `emergencia` | booleano o `null` | Estado observado de parada de emergencia. |
| `fallo_watchdog` | booleano o `null` | Fallo local enclavado por pérdida de heartbeat. |
| `heartbeat_vigente` | booleano o `null` | La escena recibe una secuencia vigente de la sesión activa; distingue causa activa de fallo ya enclavado. |
| `calidad_senales` | mapa de calidad | Por señal crítica: `{valid: bool, age_s: real o null}`. Incluye lector RFID aunque no produzca eventos. |
| `sensor_valid` | booleano | Resumen: todas las señales críticas son conocidas, válidas y no caducadas. Se comprueba contra `calidad_senales`. |
| `sensor_age_s` | real o `null`, s | Máxima antigüedad entre las señales críticas; `null` si alguna no tiene marca conocida. |

Se consideran críticas las señales de presencia, barrera, puerta, contacto,
seccionador, bloqueos, velocidad, emergencia, watchdog, heartbeat y lector RFID. La edad
se calcula desde la marca de origen, no desde la última retransmisión: una
señal congelada no rejuvenece por leerla otra vez. `age_s < 0`, marcas futuras,
campos desconocidos o edad mayor o igual al timeout invalidan el snapshot.

Los conjuntos se transportan como listas ordenadas sin duplicados. Los IDs de
eventos, órdenes y sesiones son cadenas no vacías; las secuencias son enteros
crecientes, y las fases y acciones son enumeraciones.

Evento RFID: `{event_id, operario_id, accion, t_sim_s}`, con identificador de
evento único en la corrida, `operario_id` en `{1, 2}` y `accion` en
`{ingreso, salida}`. Un ID ajeno o evento repetido se rechaza y se registra;
no altera bloqueos ni concede permisos. El controlador conserva el conjunto
de ocupantes identificados y no lo sustituye por ausencia de lecturas.

La observación del controlador puede incluir fallos inyectados. El monitor
consulta por separado posiciones y estados físicos reales de la escena.

## 4. Contrato de órdenes de usuario

Una orden es `{command_id, tipo, operario_id, solicitante_id}`. `command_id` es único por
corrida. `operario_id` es obligatorio para las acciones personales y `null`
para las generales. `solicitante_id` identifica al emisor personal en un canal
simulado confiable y es `null` para órdenes generales. En aplicación/retiro
de bloqueo debe coincidir con `operario_id`; una diferencia se rechaza como
`TITULAR_DISTINTO`. El ejecutor de pruebas puede inyectar esa diferencia.
Los IDs representan titulares bajo el supuesto S2;
no constituyen un mecanismo de autenticación industrial.

| `tipo` | Efecto permitido / condición |
|---|---|
| `stop` | Solicitar parada y revocar cualquier autorización de arranque. |
| `solicitar_mantenimiento` | Abrir un ciclo de intervención y comenzar parada/aislamiento. |
| `abrir_seccionador` | Solicitar aislamiento después de ordenar corte; esperar realimentación. |
| `aplicar_bloqueo` | Aplicar el bloqueo del titular con aislamiento confirmado. |
| `solicitar_ingreso` | Pedir entrada del titular; sólo con autorización y bloqueos previstos confirmados. |
| `solicitar_salida` | Facilitar salida; no borra ocupación hasta confirmar el evento de salida. |
| `retirar_bloqueo` | Retirar únicamente el bloqueo propio después de confirmar salida y en fase de liberación. |
| `cerrar_acceso` | Solicitar cierre cuando todos han salido; esperar confirmación. |
| `cerrar_seccionador` | Restablecer circuito sólo con zona libre, sin bloqueos y puerta cerrada. No activa el contactor. |
| `reset` | Reconocimiento manual con condiciones seguras; prepara `LISTO` y mantiene potencia ordenada apagada. |
| `start` | Activar contactor sólo desde `LISTO`, con condiciones seguras y orden nueva posterior al reset. |

El adaptador convierte un botón mantenido en un único evento de flanco. Repetir
un `command_id` no crea una orden nueva. Las órdenes rechazadas no se encolan
para ejecutarse después. Órdenes personales incompatibles para el mismo titular
se rechazan juntas (`ORDENES_CONFLICTIVAS`), sin modificar sus bloqueos.

## 5. Salidas y actuación

| Campo | Tipo | Significado |
|---|---|---|
| `orden_contactor` | booleano | `true`: solicitar cierre; `false`: solicitar apertura. |
| `permiso_acceso` | booleano | Permitir nuevas entradas; no bloquea la salida de quien está dentro. |
| `orden_puerta` | `MANTENER`, `ABRIR`, `CERRAR` | Solicitud mecánica, sujeta al permiso de entrada y a salida segura. |
| `orden_seccionador` | `MANTENER`, `ABRIR`, `CERRAR` | Solicitud al actuador simulado; no implica confirmación. |
| `acciones_bloqueo` | lista de `{operario_id, accion}` | Solicitudes validadas de aplicación/retiro; la planta confirma el resultado en el siguiente snapshot. |
| `reset_watchdog` | booleano | Solicitud excepcional de reconocimiento local tras recuperación de comunicación y reset seguro. |
| `alarma` | booleano | Indicar fallo enclavado. |
| `motivo_rechazo` | código o `null` | Motivo principal del ciclo; cada rechazo conserva su motivo en `eventos`. |

Valores iniciales/fallback: contactor apagado, entrada denegada, alarma activa,
ninguna acción de bloqueo y ninguna solicitud de cierre de seccionador. No se
borra un bloqueo al arrancar o reiniciar. Si su recuperación es desconocida,
el sistema queda en `FALLO` hasta reconciliarlo con la planta.

Códigos de rechazo mínimos: `DATO_INVALIDO`, `DATO_CADUCADO`,
`EMERGENCIA_ACTIVA`, `WATCHDOG_CADUCADO`, `PRESENCIA_PELIGROSA`,
`CONTACTO_NO_ABRE`, `AISLAMIENTO_NO_CONFIRMADO`, `ENERGIA_RESIDUAL`,
`BLOQUEO_PENDIENTE`, `OPERARIO_DENTRO`, `ID_DESCONOCIDA`,
`EVENTO_REPETIDO`, `TITULAR_DISTINTO`, `ORDENES_CONFLICTIVAS`, `FASE_INCORRECTA` y
`START_NO_NUEVO`. No se resume una ausencia de respuesta como corte exitoso.

La planta conserva estados separados de las órdenes. Un contacto pegado puede
seguir cerrado después de recibir apagado: se registra fallo, se deniega
entrada/rearme y el monitor evalúa la potencia física que realmente persiste.
El watchdog no puede forzar físicamente la apertura de un contacto averiado.

## 6. Prioridad y ciclo determinista

1. Validar snapshot y órdenes; comprobar emergencia, watchdog, datos caducados,
   discrepancias y presencia incompatible con energización/movimiento.
   Para comprobar identidad/presencia, incorporar primero los eventos RFID
   válidos del snapshot a una copia de ocupantes, sin conceder permisos ni
   borrar bloqueos. Así, un ingreso y su detección en el mismo ciclo no se
   interpretan como discrepancia por usar identidades del ciclo anterior.
2. Ante fallo, enclavar `FALLO`, apagar contactor, denegar entrada y revocar
   permisos de rearme. La presencia esperada durante mantenimiento aislado
   no es por sí sola una emergencia.
3. En ausencia de fallo, priorizar `stop` y la solicitud de mantenimiento.
4. Procesar acciones de aislamiento, bloqueos, ingreso/salida y liberación
   compatibles con la fase. Confirmaciones del mismo ciclo se toman sólo
   del snapshot, no de las órdenes recién emitidas.
5. Procesar `reset` y finalmente `start`, sin saltar fases. Como máximo una
   transición de fase por ciclo; comandos que requieran la fase nueva se rechazan.
6. Emitir salidas, registrar decisiones, enviar heartbeat y avanzar un paso.
   Observar después la planta para el monitor y el registro físico.

El orden de la lista no decide la prioridad. Fallo/emergencia vence a todas
las órdenes; stop/mantenimiento vence a reset/start. Si reset y start coinciden,
reset puede aceptarse y start se rechaza: hace falta un nuevo flanco en un
ciclo posterior. Un fallo recibido junto con reset no se reconoce en ese ciclo.
La recuperación del fallo requiere que desaparezca la causa, condiciones
seguras y un reset posterior; nunca provoca marcha automática.
Se distingue una causa activa de su memoria enclavada: con heartbeat recuperado
y un fallo de watchdog aún enclavado, reset puede solicitar `reset_watchdog`,
manteniendo `FALLO` y contactor apagado hasta confirmar que la escena lo borró.
Sólo entonces el reconocimiento pendiente permite pasar a `LISTO`; no admite
start en ese mismo ciclo. No se exige borrar el fallo antes de poder reconocerlo.

La comparación orden/realimentación respeta los plazos del actuador de A08.
Durante una apertura pendiente se mantienen potencia ordenada apagada y
entrada denegada; al alcanzar el plazo sin confirmación se declara
`CONTACTO_NO_ABRE`. No exigir una respuesta instantánea al actuador simulado.

La adquisición y el envío forman un solo lote por ciclo. El adaptador usa
stepping para que la escena no cambie entre las lecturas. Se registran snapshot
prepaso y observación postpaso con el mismo `tick`, distinguiendo sus tiempos;
no se atribuye al snapshot un resultado físico que ocurrió después.

## 7. Fases y condiciones

| Fase | Condición / siguiente avance permitido |
|---|---|
| `INICIO_SEGURO` | Potencia ordenada apagada, entrada denegada; reconciliar bloqueos y estado físico. Un reset seguro prepara `LISTO`. |
| `LISTO` | Zona libre, sin bloqueos, puerta cerrada, seccionador restablecido, contacto abierto, parada confirmada y señales válidas. Sólo start nuevo permite `MARCHA`. |
| `MARCHA` | Entrada denegada. Stop conduce a parada; mantenimiento abre una intervención y conduce a `PARADA_SOLICITADA`. |
| `PARADA_SOLICITADA` | Contactor apagado; confirmar apertura antes de continuar a `AISLAMIENTO`. |
| `AISLAMIENTO` | Solicitar apertura del seccionador; su confirmación permite `BLOQUEO`. |
| `BLOQUEO` | Aplicar y confirmar bloqueos de ambos operarios antes de continuar a `VERIFICACION_CERO`. |
| `VERIFICACION_CERO` | Verificar contacto abierto, aislamiento y velocidad dentro del umbral; sólo entonces pasar a `MANTENIMIENTO`. |
| `MANTENIMIENTO` | Entrada autorizada bajo condiciones seguras; registrar ingresos/salidas. No admitir titulares adicionales. |
| `LIBERACION` | Tras finalizar la intervención y confirmar todos fuera, retirar bloqueos por sus titulares. |
| `RESTABLECIMIENTO` | Sin bloqueos y con zona libre, cerrar puerta y luego seccionador, esperando sus confirmaciones. Reset seguro prepara `LISTO`. |
| `FALLO` | Potencia ordenada apagada, entrada denegada y permisos invalidados. Recuperar condiciones seguras y reconciliar bloqueos antes de reset. |

Finalizar una intervención se solicita con `cerrar_acceso`: desde mantenimiento
sólo se acepta si todos los titulares están fuera y la zona está libre; primero
conduce a liberación, sin cerrar la salida antes de confirmar evacuación.
Un stop fuera de una intervención conduce a parada segura y posterior reset;
no obliga a aplicar bloqueos personales si nadie solicita mantenimiento.
Al confirmar contacto abierto y parada en ese caso, se permanece seguro hasta
reset; no se abre el seccionador ni se entra en la rama de bloqueo. El estado
conserva si hay una intervención activa para distinguir ambas rutas.

Condición de parada: `abs(velocidad_m_s) <= epsilon_parada_m_s`, con medición
válida y presupuesto temporal fijado en A08. No se calcula energía en joules
sin una masa/inercia modelada: `energia_residual` en la observación es un
booleano que indica movimiento residual por encima de ese umbral.

El rearme verifica tanto ocupantes identificados vacíos como sensor de zona
libre y barrera libre. Una discrepancia entre canales revoca permiso y requiere
reconciliación, nunca elegir el canal que autorice marcha. Fallo revoca fases y
permisos, pero conserva titulares y bloqueos.

La configuración A08 debe proporcionar paso, caducidad de señales, periodo y
timeout de heartbeat, plazo de apertura del contacto y `epsilon_parada_m_s`.
Tiempos positivos y umbral no negativo; cualquier parámetro ausente bloquea
la ejecución. A05 define sus usos, A08 fija y justifica sus valores.

## 8. Watchdog, tiempo y observación independiente

El heartbeat transporta `{sesion_id, secuencia}`. Sólo una secuencia nueva de
la sesión activa renueva su recepción; repetir el mismo valor no evita timeout.
La escena mide la edad con su reloj de simulación y valida la sesión antes de
aplicar salidas. Una sesión nueva arranca desarmada y exige reconciliación/reset.
Un heartbeat posterior al timeout no elimina por sí solo el fallo enclavado.

El permiso efectivo de entrada requiere permiso del controlador, heartbeat
vigente, aislamiento y parada confirmados. El contactor nominal sólo puede
cerrarse con orden válida y sin fallo local. La pérdida del cliente revoca
ambos permisos; `reset_watchdog` se acepta localmente sólo con comunicación
recuperada y condiciones seguras confirmadas.

En stepping, un cliente caído puede detener el reloj y la escena. El ensayo de
watchdog debe hacerse con avance autónomo o un supervisor independiente que
mantenga los pasos; documentar esa configuración en SC-09. No atribuir respuesta
en tiempo real a una escena congelada ni mezclar relojes.

El monitor recibe `tick`, `t_sim_s`, `ocupantes_reales`, `potencia_real`,
`energia_residual`, `velocidad_real_m_s`, `puerta_real_cerrada` y
`seccionador_real_abierto`, directamente de posiciones/estados de planta.
La ocupación se obtiene de la intersección del cuerpo del operario con la zona,
no únicamente del centro del torso. Los límites geométricos incluyen su borde.
La potencia real depende del circuito físico simulado, no de la orden Python.

Tiempo simulado: edades de señales, retardos y latencias de planta. Reloj
monotónico del anfitrión: coste de CPU, registrado como `t_wall_ns`. No restar
un tiempo de simulación de uno de reloj monotónico.

## 9. Trazabilidad y revisión de A05

| Requisitos | Decisión arquitectónica | Escenarios A08 |
|---|---|---|
| RF-01/02 | Acceso enclavado, confirmación de aislamiento/parada y monitor físico. | SC-01/02/06/08/12/13 |
| RF-03 | Identidades, bloqueos confirmados y retiro personal tras salida. | SC-03/04/10 |
| RF-04/06 | Prioridades, fases y reset/start en ciclos separados. | SC-01/04/05/13 |
| RF-05/10 | Calidad y edad de señales, realimentación, fallo enclavado. | SC-06/07/08 |
| RF-07 | Inicio desarmado, reconciliación de bloqueos y sesión de comunicación. | SC-11 |
| RF-08 | Canal de registro de entradas/salidas y verdad física independiente. | Todos |
| RF-09 | Watchdog local con reloj que avanza durante la pérdida del cliente. | SC-09 |

`artefactos/diseno/correspondencia.csv` se completa en A13 con variable concreta,
abstracción, evento Event-B, función Python, pre/postcondición y prueba.
A05 fija el contrato; no anticipa resultados de esa correspondencia.

Para cerrar la revisión cruzada, otro integrante debe comprobar que documento
y diagrama coinciden, que todo requisito RF tiene responsable e interfaz,
y que fallos, reinicio, reset/start simultáneos y salida de operarios están
resueltos. Registrar dudas y aprobación del revisor en este documento.

Revisión técnica de consistencia documental: realizada durante la preparación.
Revisor del equipo / fecha / observaciones: pendiente.
