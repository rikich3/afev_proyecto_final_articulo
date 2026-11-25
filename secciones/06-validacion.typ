#import "/estilo.typ": tabla
= Model Checking y protocolo de validación

== Modelo de estados y propiedades

La segunda parte del proyecto se desarrolla con NuSMV 2.6.0, que permite comprobar propiedades temporales de un modelo finito @nusmv26. Event-B establece la especificación por invariantes y NuSMV analiza un comportamiento de acceso y rearme. El modelo tiene once fases, desde inicio hasta marcha, mantenimiento, liberación y fallo. Las variables representan potencia, movimiento, aislamiento, puerta, presencia y bloqueo de cada operario. El modelo finito representa una selección de las fases y guardas del ciclo Event-B.

El entorno elige un evento por transición. La solicitud de mantenimiento conduce a parada, donde apertura del contacto y fin del movimiento se confirman por separado. Aislamiento y bloqueos habilitan la verificación de energía cero. El ingreso requiere permiso de acceso. La salida de ambos y el retiro de bloqueos permiten cerrar la puerta, restablecer el seccionador y reconocer el rearme. Emergencia revoca el permiso y conduce a fallo conservando ocupantes y bloqueos. La @fig-transiciones resume las guardas del ciclo. Los eventos cuyas guardas no se cumplen mantienen el estado.

#figure(image("/img/model-checking.svg", width: 100%), scope: "parent", placement: top, caption: [Transiciones de estado del ciclo nominal y su respuesta a emergencia. Las guardas aparecen entre corchetes.]) <fig-transiciones>

La @tab-propiedades[Tabla] presenta las propiedades del modelo nominal.

Se formularon tres propiedades LTL de seguridad y dos consultas CTL de alcanzabilidad. En estas expresiones, $G$ exige cumplimiento global y $E F$ expresa la existencia de un recorrido que alcanza la condición indicada. La posibilidad de esperar indefinidamente se conserva en el modelo. Para la comprobación se usó el motor simbólico de NuSMV con diagramas binarios de decisión. La opción `-r` habilitó el cálculo de los estados alcanzables.

#figure(tabla(
  columnas: (58pt, 44pt, 230pt, 1fr, 48pt),
  [*Propiedad*], [*Requisito*], [*Fórmula en NuSMV*], [*Condición comprobada*], [*Resultado*],
  [MC01 (LTL)], [RF-01],
  [`G !(ocupada & potencia)`],
  [Siempre se excluyen ocupación y potencia.], [Verdadera],
  [MC02 (LTL)], [RF-02],
  [`G (permiso_acceso ->` #linebreak() `(aislado & energia_cero & ambos_bloqueos))`],
  [El permiso implica aislamiento, parada y ambos bloqueos.], [Verdadera],
  [MC03 (LTL)], [RF-03],
  [`G (bloqueada -> !potencia)`],
  [Un bloqueo restante impide energización.], [Verdadera],
  [MC04 (CTL)], [—],
  [`EF (fase = MANTENIMIENTO & dentro1 & dentro2)`],
  [Existe ingreso de ambos operarios a mantenimiento.], [Verdadera],
  [MC05 (CTL)], [RF-04],
  [`EF (fase = LISTO & ciclo_completado)`],
  [Existe un ciclo de ingreso, salida y rearme.], [Verdadera],
), kind: table, scope: "parent", placement: top,
  caption: [Propiedades y resultados del modelo nominal en NuSMV.],
) <tab-propiedades>

El modelo presupone acceso controlado y funcionamiento nominal de puerta y seccionador. La campaña de simulación examina además fallos de sensores, cambios de sesión y latencias de la planta.


== Escenarios y preparación

El protocolo organiza requisitos, criterios y evidencia siguiendo el contexto metodológico de ISO/IEC/IEEE 29148 e ISO/IEC/IEEE 29119-2 @iso29148 @iso29119. Incluye trece escenarios de operación nominal, mantenimiento, bloqueos, órdenes incompatibles, retardos, sensores inválidos, contacto pegado, desconexión, identidades incorrectas, reinicio, intrusión y emergencia durante rearme. Los casos relacionan los estímulos con RF-01–RF-10.

Se ejecutaron tres pilotos en CoppeliaSim EDU 4.10 para arranque, mantenimiento y pérdida de comunicación. La campaña combinó 41 corridas deterministas, 90 con semillas reproducibles y cuatro de sensibilidad al paso de 10 o 20 ms. Cada corrida comenzó con la escena restablecida y verificó las precondiciones mediante un prefijo de operaciones nominales. Se conservaron versiones, parámetros, semilla y hash de cada traza.

El montaje sigue el enfoque de conectar un controlador a un modelo de planta para ensayar su respuesta @striffler2023. El monitor independiente evaluó la ocupación por geometría y la potencia mediante el contacto y el seccionador simulados. El supervisor leyó el sensor volumétrico y los eventos RFID por ZeroMQ. Para simular la desconexión se cerró el socket del supervisor y un segundo cliente leyó el historial que la escena registró con su propio reloj.

== Indicadores y criterios

La evidencia formal se expresa mediante obligaciones generadas y demostradas por versión. La evaluación de planta registra episodios de coexistencia presencia–potencia, intentos de rearme, fallos de respuesta y latencias por escenario. El origen de cada incidente identifica si se trata de presencia, caducidad de señal o pérdida de comunicación. La latencia de corte se define como

$ L = t_"contacto abierto" - t_"referencia". $

La referencia se fija según el caso, por ejemplo la orden de corte o el último latido aceptado. El protocolo registra aparte la parada mecánica. Las latencias usan tiempo simulado y se resumen mediante mediana, percentil 95 y máximo, con el número de incidentes evaluables. Un contacto que permanece cerrado conserva el estado de respuesta fallida y la latencia ausente. Los episodios de intrusión forzada se contabilizan aparte. Los tiempos propuestos son parámetros del laboratorio.
