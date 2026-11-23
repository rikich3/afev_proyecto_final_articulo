# M2 — interfaz y fallo concreto

C2 extiende C1 con los límites nominales del protocolo. M2 refina M1 y conserva
sus variables. Las observaciones concretas se relacionan mediante invariantes
con potencia, aislamiento, puerta y parada abstractas.

## Comportamiento

`SolicitarArranque` ordena potencia y `Energizar` confirma el cierre en otro
evento. `OrdenarParada` y `OrdenarMantenimiento` apagan la orden manteniendo
potencia hasta `Cortar` o `SolicitarMantenimiento`, que confirman apertura.
La apertura exige que el contacto no esté pegado. La parada mecánica tiene su
propia confirmación posterior. Así, una orden apagada puede coexistir con un
contacto físicamente cerrado.

El fallo es una variable concreta enclavada. La fase abstracta M1 se conserva
hasta la correspondiente confirmación. El permiso efectivo de ingreso es
`permiso_acceso` y se revoca ante fallo aunque el permiso abstracto M1 todavía
exista. Se mantienen los ocupantes y bloqueos. Si el contacto sigue cerrado,
el fallo inicia la espera de apertura o conserva su edad si ya estaba en curso.
`ConfirmarParada` registra que terminó el movimiento aunque el fallo siga
enclavado. La salida y liberación segura siguen disponibles.

La autorización `rearme_vigente` sólo se concede por un reset manual y se
consume en Energizar. Todos los fallos y el reinicio la revocan. Recuperar una
señal o recibir heartbeat no elimina el fallo. `ReconocerFallo` exige energía
cero, zona libre, puerta cerrada y señales reconciliadas. Puede reconocer el
fallo durante la preparación con aislamiento confirmado y los bloqueos
conservados. Después hace falta reset para autorizar otro arranque.
`ResetListo` representa ese reset concreto cuando M1 ya conservaba LISTO.
`CancelarArranque` permite revocar una autorización o una orden de arranque
antes de confirmarse el cierre del contacto.

## Tiempo y calidad de señales

El reloj local avanza con eventos Tick, independientemente de la recepción de
heartbeat. C2 fija paso nominal de 20 ms, sensor 3 ticks, heartbeat 5 ticks y
apertura 3 ticks. Las edades se comparan con >= en la frontera del límite.
TickCaducado enclava fallo y apaga orden/permiso al vencer cualquier plazo.
La igualdad también activa el diagnóstico de contacto que no abre.

El modelo declara un paso abstracto nominal. No demuestra una cota de tiempo
real del proceso Python ni del simulador. La sensibilidad a 10 ms requiere
reexpresar los mismos plazos en ticks. Tampoco garantiza que el entorno
planifique un Tick: esa hipótesis temporal debe implementarse y ensayarse en
la planta. Las variables de edad y secuencia son naturales sin límite global.

`datos_validos` indica calidad estructural. Las edades representan frescura.
Una observación ausente/inválida o distinta de los ocupantes identificados
provoca fallo. `ActualizarSensor` restaura una observación coherente y su edad,
pero conserva el fallo enclavado. Un heartbeat sólo se acepta si la sesión
coincide y la secuencia aumenta. El reinicio cambia la sesión, marca el
heartbeat como vencido y conserva potencia, ocupación y bloqueos de planta.
Las órdenes iniciales son apagadas.

## Propiedades

- enlace_potencia relaciona contacto real con P mediante equivalencia.
- INV_05 exige orden y permiso efectivo apagados en fallo.
- INV_06 exige permiso abstracto, señales válidas y frescas y ocupación coherente.
- INV_07 exige corte, aislamiento, parada y ambos bloqueos para el permiso efectivo.
- INV_08 condiciona la orden de marcha a zona libre, ausencia de bloqueos,
  señales válidas/frescas, puerta cerrada y ausencia de permiso de ingreso.
- inv_espera mantiene orden apagada durante la espera de apertura real.
- inv_rearme_fallo e inv_rearme_orden impiden reutilizar una autorización en fallo.

Puerta y seccionador se confirman nominalmente. La intrusión y una observación
física falsa quedan fuera de los supuestos nominales y deben detectarse en la
simulación. Los eventos son ordinarios. La evidencia formal se interpreta como
seguridad y refinamiento. La correspondencia con NuSMV/Python, la convergencia
y el progreso universal requieren trabajo adicional.

## Reproducción

Se usó Rodin 3.10 y JDK 21 con el [complemento oficial SMT 1.5.0](https://sourceforge.net/projects/rodin-b-sharp/files/Plugin_SMT_Solvers/1.5.0/)
y la configuración veriT incluida. Instala y habilita esa configuración en
Rodin antes de ejecutar ambos comandos. El probador usa, según la obligación,
reescrituras, PP y veriT sin restringir la selección de hipótesis.

```sh
python herramientas/verificar_rodin.py --rodin /ruta/a/rodin --java-home /ruta/al/jdk21 --modelo M2
python herramientas/verificar_rodin.py --rodin /ruta/a/rodin --java-home /ruta/al/jdk21 --modelo M2 --replay
```

La salida se registra por obligación en `estados.csv`. Los manifiestos
identifican las fuentes y los registros por SHA256. La demostración y la
reproducción se realizan en copias temporales de la instalación y del proyecto.
