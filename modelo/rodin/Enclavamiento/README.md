# A06 — Modelo abstracto C0/M0

Modelo nativo generado y comprobado con **Rodin 3.10.0**. C0 y M0 pasan el
chequeo estático, y las **5 obligaciones generadas están demostradas**.
Las fuentes y árboles de prueba se conservan en este proyecto. Rodin regenera
las obligaciones `.bpo` y los estados `.bps` al construir el proyecto.
Las exportaciones legibles están en `../../export/C0.txt` y `M0.txt`.

## Importar en Rodin

1. Abre Rodin y usa `File > Import...`.
2. Selecciona `General > Existing Projects into Workspace` y continúa.
3. En `Select root directory`, elige esta carpeta:

   ```text
   /home/leeeen/UNSA/SEXTO_SEMESTRE/AFVE/p_final/afev_proyecto_final_articulo/modelo/rodin/Enclavamiento
   ```

4. Selecciona el proyecto `Enclavamiento`. Puedes activar `Copy projects into
   workspace` para trabajar sobre una copia. Pulsa `Finish`.
5. En Event-B Explorer, abre el contexto `C0` y la máquina `M0`.
6. Revisa `Proof Obligations` de M0: las cinco deben estar demostradas y la
   vista `Problems` no debe mostrar errores. Conserva las pruebas `.bpr`.

Si ya tienes otro proyecto llamado `Enclavamiento`, utiliza un workspace nuevo
o importa una copia con cuidado; no sobrescribas trabajo previo. Si importas
una copia, los cambios en ella no actualizan automáticamente los archivos del repo.

No se necesita el complemento temporal utilizado para comprobar el modelo:
los árboles sólo dependen de los probadores estándar de Rodin. Puedes volver
a ejecutar los probadores desde `Retry Auto Provers`; para las obligaciones
que lo necesiten, utiliza PP sin restricción de hipótesis. Las instrucciones
oficiales están en [Proof Obligation Commands](https://wiki.event-b.org/index.php/Proof_Obligation_Commands).

## Significado de C0 y M0

C0 fija una zona y dos operarios distintos:

- `partition(Z, {z1})`: Z contiene exclusivamente la zona z1.
- `partition(O, {o1}, {o2})`: O contiene exactamente o1 y o2, diferentes.

Hay una interpretación consistente: Z = {zona}, O = {persona1, persona2},
con las constantes correspondientes. Los axiomas no afirman la propiedad de
seguridad ni eliminan estados inseguros de antemano.

M0 conserva dos variables:

| Variable / invariante | Significado |
|---|---|
| `P ⊆ Z` (`inv_P`) | Zonas con potencia activa abstracta. |
| `U ⊆ O × Z` (`inv_U`) | Pares operario-zona que representan ocupación. |
| `ran(U) ∩ P = ∅` (`INV_01`) | Ninguna zona ocupada tiene potencia. |

`ran(U)` son las zonas ocupadas por al menos un operario. INV_01 expresa la
misma propiedad que `∀z ∈ Z: ¬(z ∈ P ∧ ∃o ∈ O: o ↦ z ∈ U)`.

| Evento | Guarda esencial | Acción |
|---|---|---|
| `INITIALISATION` | Ninguna. | `P := ∅`, `U := ∅`. |
| `Energizar(z)` | Zona válida, apagada y sin ocupantes. | Añadir z a P. |
| `Cortar(z)` | Zona energizada. | Retirar z de P. |
| `Ingresar(o,z)` | Operario/zona válidos, zona apagada y operario aún fuera. | Añadir o ↦ z a U. |
| `Salir(o,z)` | El par o ↦ z está en U. | Retirar ese par de U. |

Todos los eventos son ordinarios. No hay refinamiento previo ni eventos de
convergencia en M0, por lo que no se introduce una variante artificial.
La guarda de ingreso representa el supuesto de acceso normal controlado S1.
M0 abstrae el aislamiento detallado y el movimiento residual: que P esté vacío
no demuestra energía cero en CoppeliaSim.

## Pruebas conservadas

| Obligación | Estado |
|---|---|
| `INITIALISATION/INV_01/INV` | Demostrada. |
| `Energizar/INV_01/INV` | Demostrada. |
| `Cortar/INV_01/INV` | Demostrada. |
| `Ingresar/INV_01/INV` | Demostrada. |
| `Salir/INV_01/INV` | Demostrada. |

Rodin simplifica las obligaciones triviales de tipos y buena definición;
esta versión genera cinco obligaciones no triviales. La inicialización se
cierra por simplificación; los eventos se cierran con el probador PP no
restringido. Los estados nativos de la comprobación temporal indicaron
confianza 1000, `psManual=false` y pruebas sin ruptura. El hash de aquel
`M0.bps` se conserva como registro histórico; el archivo se regenera en Rodin. El registro está en `verificacion_m0.json` y
`verificacion.log`; los árboles efectivos están en `M0.bpr`.

La comprobación se ejecutó en un workspace temporal, usando la instalación
existente sin modificarla. Se probó además importación en otro workspace,
chequeo estático y reproducción de cada árbol guardado. La revisión visual
en tu interfaz y la revisión cruzada del equipo quedan pendientes.

## Secuencia para explicar o animar el modelo

Estos son pasos esperados, no resultados ejecutados con ProB:

1. Inicializar: potencia apagada y zona vacía.
2. Energizar z1: Ingresar queda deshabilitado; Cortar está habilitado.
3. Cortar z1 e ingresar o1: Energizar queda deshabilitado.
4. Ingresar o2: ahora ambos están dentro.
5. Salir o1: Energizar sigue deshabilitado porque o2 permanece dentro.
6. Salir o2: Energizar vuelve a estar habilitado.

Los eventos son abstractos: `Energizar` no implementa todavía la secuencia
reset/start de A05. M1 deberá fortalecer las guardas con bloqueos, aislamiento,
energía cero y fases; M2 añadirá observaciones, realimentación y fallos.

## Alcance de la evidencia

A06 cubre RF-01 bajo las hipótesis abstractas; prepara el refinamiento de los
otros requisitos. No demuestra comportamiento del controlador Python,
seguridad de una planta real, vivacidad general ni respuesta ante intrusión
forzada o fallos de sensores/actuadores. No se ha realizado exploración ProB
ni se inventan cantidades de estados/transiciones.

Estado: modelo y pruebas preparados; revisión cruzada del equipo pendiente.
