#import "/estilo.typ": listado, tabla
= Especificación formal

== Contexto y tipos de datos

El contexto C0 fija una zona y dos operarios mediante los conjuntos portadores $Z$ y $O$ y las constantes $z_1$, $o_1$ y $o_2$. La máquina M0 ve C0. El @lst-contexto reproduce los axiomas y los invariantes de tipo de las fuentes nativas.

#listado([Axiomas de C0 e invariantes de M0.])[
```text
CONTEXT C0
SETS Z O
CONSTANTS z1 o1 o2
AXIOMS
  axm1: partition(Z, {z1})
  axm2: partition(O, {o1}, {o2})
END

MACHINE M0
SEES C0
VARIABLES P U
INVARIANTS
  inv_P: P ⊆ Z
  inv_U: U ⊆ O × Z
  INV_01: ran(U) ∩ P = ∅
```
] <lst-contexto>

$P$ contiene las zonas energizadas y $U$ los pares operario–zona que representan ocupación. La expresión $o_1 mapsto z_1 in U$ indica que el primer operario está dentro. El rango $op("ran")(U)$ contiene las zonas ocupadas por al menos una persona. Así, INV-01 expresa RF-01 al exigir que las zonas ocupadas y energizadas sean disjuntas. El contexto fija los individuos, mientras que el invariante restringe los estados alcanzables de la máquina.

== Eventos y preservación de RF-01

La inicialización establece $P := emptyset$ y $U := emptyset$. El @lst-energizar muestra las guardas del evento de energización.

#listado([Evento Energizar y guarda de zona libre.])[
```text
EVENT Energizar
  ANY z
  WHERE
    grd1: z ∈ Z
    grd2: z ∉ P
    grd3: z ∉ ran(U)
  THEN
    act1: P ≔ P ∪ {z}
  END
```
] <lst-energizar>

La guarda `grd3` habilita la energización únicamente cuando la zona está libre. `Ingresar(o,z)` exige $o in O$, $z in Z$, $z in.not P$ y $o in.not op("dom")(U)$, y añade el par $o mapsto z$ a $U$. `Salir(o,z)` elimina ese par y `Cortar(z)` retira la zona de $P$. La guarda de ingreso presupone acceso normal controlado. En M0, la ausencia de potencia es abstracta. Los refinamientos incorporan el aislamiento y la confirmación de la parada.

Considérese $U = {(o_1,z_1), (o_2,z_1)}$ y $P = emptyset$. Tras `Salir(o1,z1)`, permanece $U = {(o_2,z_1)}$. En consecuencia, $z_1 in op("ran")(U)$ y `Energizar(z1)` sigue deshabilitado. Sólo después de la salida del segundo operario queda satisfecha la guarda de ocupación de RF-01. La identidad de cada operario permite comprobar además la titularidad de los bloqueos personales en RF-03.

== Refinamientos M1 y M2

La @tab-niveles[Tabla] resume los tres niveles de especificación.

#figure(tabla(
  [*Nivel y estado*], [*Contenido*],
  [M0, nativo y comprobado], [Ocupación, potencia y exclusión RF-01.],
  [M1, nativo y comprobado], [Bloqueos personales, aislamiento y rearme.],
  [M2, nativo y comprobado], [Observaciones, órdenes, confirmaciones y fallos.],
), kind: table, caption: [Alcance de los niveles de especificación.]) <tab-niveles>

M1 refina M0 y ve C1, que extiende C0 con diez fases. Incorpora $L subset.eq O times Z$, los bloqueos por titular, y confirmaciones booleanas abstractas de aislamiento, energía cero, puerta y permiso. INV-02 establece $op("ran")(L) inter P = emptyset$. INV-03 exige que el permiso implique mantenimiento, potencia apagada, aislamiento, energía cero y bloqueos de ambos operarios. INV-04 restringe la energización a marcha con zona libre y sin bloqueos. El modelo tiene dieciocho eventos.

`AplicarBloqueo` exige coincidencia entre solicitante y titular. `FinalizarMantenimiento` requiere la salida de todos antes de la liberación. El evento del @lst-retiro representa RF-03. Conserva $P$ y $U$ y modifica exclusivamente el bloqueo del titular.

#listado([Evento RetirarBloqueo y guardas del titular.])[
```text
EVENT RetirarBloqueo
  ANY o, z, solicitante
  WHERE
    grd1: o ∈ O
    grd2: z ∈ Z
    grd3: o ↦ z ∈ L
    grd4: solicitante = o
    grd5: o ∉ dom(U)
    grd6: fase = LIBERACION
  THEN
    act1: L ≔ L ∖ {o ↦ z}
  END
```
] <lst-retiro>

El último retiro habilita el cierre y el restablecimiento, manteniendo la potencia apagada. `Reset` alcanza LISTO con zona libre, sin bloqueos y condiciones seguras confirmadas. Sólo un evento posterior `Energizar` puede activar potencia. La representación del solicitante sigue la hipótesis de identidad confiable. Todos los eventos son ordinarios. La prueba establece seguridad y refinamiento, mientras que convergencia y progreso universal quedan fuera de esta evidencia.

M2 separa la orden del contactor de su confirmación. El invariante `enlace_potencia` establece `contacto_real = bool(P ≠ ∅)`. Una orden de corte revoca el mando, pero $P$ conserva la potencia hasta una confirmación de apertura. Una confirmación distinta registra la parada mecánica. Los invariantes de enlace también relacionan el seccionador, la puerta y el movimiento con las variables de M1.

El contexto C2 fija un paso nominal de 20 ms y límites de tres pasos para el sensor y la apertura del contacto, y cinco para el heartbeat. Al vencer un plazo, `TickCaducado` enclava el fallo y revoca la orden, el permiso efectivo y la autorización de rearme. Si la apertura sigue pendiente al vencer su plazo, el evento registra el diagnóstico. El reinicio conserva los bloqueos e invalida el heartbeat de la sesión anterior. Estas transiciones especifican RF-05, RF-07, RF-09 y RF-10 con un reloj abstracto que debe avanzar en planta durante la desconexión.
