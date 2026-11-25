#import "/estilo.typ": tabla
#let registro = json("/modelo/rodin/Enclavamiento/verificacion_m0.json")
#let registro_m1 = json("/artefactos/verificacion/rodin/verificacion_m1.json")
#let registro_m2 = json("/artefactos/verificacion/rodin/m2/verificacion_m2.json")
#let ensayo = json("/artefactos/resultados/resumen.json")
= Resultados y discusión

== Evidencia formal disponible

Rodin 3.10.0 completó el chequeo estático de los tres niveles (@tab-obligaciones[Tabla]). Las pruebas se reprodujeron desde los árboles guardados en un segundo espacio de trabajo. Los registros vinculan la evidencia con las versiones exactas de las fuentes mediante SHA256.

#figure(tabla(
  [*Máquina*], [*Demostradas / generadas*],
  [M0], [#registro.obligaciones_demostradas / #registro.obligaciones_generadas],
  [M1], [#registro_m1.M1_demostradas / #registro_m1.M1_generadas],
  [M2], [#registro_m2.M2_demostradas / #registro_m2.M2_generadas],
), kind: table, caption: [Obligaciones de prueba por máquina Event-B.]) <tab-obligaciones>

En M0, la inicialización establece INV-01. `Energizar` y `Ingresar` la preservan mediante las guardas de zona libre y potencia apagada, respectivamente. `Cortar` y `Salir` conservan la disjunción al retirar elementos. M1 añade obligaciones sobre bloqueos, permiso y rearme. M2 incorpora caducidad de señales, confirmación de potencia y revocación de permisos.

La estrategia utilizó simplificación, PP y veriT mediante el complemento SMT de Rodin. La reproducción comprobó #registro_m2.total_comprobadas obligaciones. Los resultados establecen la seguridad inductiva de las máquinas bajo sus hipótesis.

ProB 1.16.1 analizó 10 000 y 20 000 estados de M2 en dos búsquedas sin contraejemplos observados. La segunda acotó sesiones, secuencias y edades. Ambas alcanzaron su límite de estados, por lo que sus resultados se circunscriben a la exploración realizada.

== Resultados de Model Checking

NuSMV comprobó las cinco propiedades de la @tab-propiedades[Tabla] sobre un espacio de 119 estados alcanzables, con diámetro 36. El diámetro indica la mayor distancia mínima desde los estados iniciales en número de transiciones. MC01–MC03 se satisfacen globalmente. MC04 y MC05 confirman la existencia de recorridos de mantenimiento y rearme. Como el entorno puede esperar indefinidamente, el modelo no garantiza que toda intervención termine.

Como control negativo se evaluó `G !potencia`, que resultó falsa y produjo un arranque como contraejemplo. Después se retiró la guarda de permiso del ingreso del primer operario en una copia temporal del modelo. MC01 resultó falsa en esa copia y el log conservó la secuencia de intrusión durante energización. Este resultado identifica la dependencia de la propiedad respecto del acceso controlado. Los archivos de reproducción conservan fórmulas, comandos y hashes del modelo, el ejecutable y las salidas.

== Validación en CoppeliaSim

De #ensayo.campana corridas de campaña, #ensayo.oraculos_cumplidos cumplieron el criterio de su caso. El caso SC-09-c se clasificó como no evaluable para tiempo de corte porque el reloj se congeló al mantener el modo por pasos tras la desconexión. Las otras corridas de desconexión dejaron avanzar el reloj local. En SC-09-a, el corte ocurrió a #ensayo.corte_watchdog_sc09a.p95_ms ms del último latido aceptado (p95, $n = #ensayo.corte_watchdog_sc09a.n$ al paso nominal), dentro del presupuesto simulado de 140 ms. La @tab-corridas[Tabla] presenta cuatro casos representativos.

#figure(tabla(
  [*Caso*], [*Observación de planta*],
  [SC-02-a], [40 ms hasta apertura tras la orden y 320 ms adicionales hasta la parada.],
  [SC-03-a], [Con el operario 2 dentro, ambos bloqueos permanecieron y el arranque quedó inhibido.],
  [SC-08-a], [El contacto pegado quedó cerrado. Se diagnosticó el fallo y se denegó la entrada.],
  [SC-12-a/b], [El monitor detectó las dos intrusiones forzadas con potencia.],
), kind: table, caption: [Resultados representativos de las corridas instrumentadas.]) <tab-corridas>

El monitor registró #ensayo.violaciones_fisicas episodios presencia–potencia en los casos evaluables dentro de los supuestos. La @fig-escena muestra el rearme inhibido tras la salida de un operario. El contacto pegado fue una respuesta física fallida en la planta, aunque se cumplió el criterio de diagnóstico. La sensibilidad de SC-09-a mantuvo 120 ms entre último latido y apertura con pasos de 10 y 20 ms.

#figure(image("/img/escena.png", width: 96%), caption: [SC-03-a en CoppeliaSim. El operario de chaleco naranja está fuera y el de chaleco amarillo permanece en la zona. La traza confirma potencia desactivada y ambos bloqueos aplicados.]) <fig-escena>

== Amenazas a la validez

La planta reproduce contactos, movimiento residual y cruces discretos de los avatares. La desaceleración es un parámetro de simulación. Los tiempos observados dependen de la discretización y de esa parametrización. La elección del nivel de detalle de la planta es parte del diseño de los ensayos de puesta en marcha virtual @striffler2023. El acceso controlado y la confiabilidad del sensado condicionan la exclusión. Las intrusiones de SC-12 ilustran la ruptura de esos supuestos. El alcance se limita a una zona y dos operarios. La correspondencia entre M2 y el controlador Python se contrasta mediante guardas y casos trazables (@tab-correspondencia[Tabla]), distinguiendo lo demostrado en el modelo de lo observado por el monitor en simulación. La fidelidad respecto de una especificación Event-B puede formularse mediante obligaciones de prueba específicas @mashkoor2017.

#figure(tabla(
  columnas: (48pt, 168pt, 78pt, 1fr),
  [*Req.*], [*Guarda / invariante en Event-B*], [*Escenarios*], [*Observación del monitor y simulación*],
  [RF-01], [INV-01; `z ∉ ran(U)`, `z ∉ P` (M0).], [SC-01, SC-02, SC-12], [0 violaciones bajo supuestos; 2 intrusiones detectadas en SC-12.],
  [RF-02], [INV-03/07; parada, aislamiento y ambos bloqueos (M1/M2).], [SC-02, SC-08, SC-13], [Permiso habilitado solo tras apertura, energía cero y bloqueos.],
  [RF-03], [INV-02; `solicitante = o`, `o ∉ dom(U)` (M1).], [SC-03, SC-04, SC-10], [Retiro indebido rechazado; bloqueo restante inhibe arranque.],
  [RF-04], [INV-04; zona libre, sin bloqueos, `Reset` y `Energizar` (M1).], [SC-01, SC-03–05, SC-13], [El reset no energiza; exige una orden `start` posterior.],
  [RF-05, RF-07], [INV-05/06/08; caducidad, invalidez y reinicio seguro (M2).], [SC-06, SC-07, SC-11], [Fallo enclavado, mando revocado y bloqueos conservados.],
  [RF-06], [Prioridad de fallo y parada en `step()` (controlador).], [SC-05], [Fallo y parada prevalecen sobre `start` en orden directo e inverso.],
  [RF-09], [INV-05/06; `RecibirHeartbeat` y `TickCaducado` (M2).], [SC-09], [Corte local del watchdog a 120 ms (p95); SC-09-c reloj congelado.],
  [RF-10], [INV-05/07; `orden_contactor` frente a `contacto_real` (M2).], [SC-08], [Fallo de apertura diagnosticado; acceso y rearme denegados.],
), kind: table, scope: "parent", placement: top,
  caption: [Correspondencia entre el modelo Event-B, el controlador Python y las observaciones de simulación.],
) <tab-correspondencia>
