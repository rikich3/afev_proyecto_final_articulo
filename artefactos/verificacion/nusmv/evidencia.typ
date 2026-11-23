#let registro = json("manifiesto.json")

#set document(
  title: "Anexo A. Evidencia de Model Checking con NuSMV",
  author: "Equipo AFEV",
)
#set page(paper: "us-letter", margin: (x: 18mm, y: 17mm), numbering: "1")
#counter(page).update(8)
#set text(font: "Liberation Sans", size: 9pt, lang: "es")
#set par(justify: true, leading: 0.42em, spacing: 0.6em)
#show table.cell: set text(size: 8pt)

#text(size: 15pt, weight: "bold")[Anexo A. Evidencia de Model Checking con NuSMV]
#v(3pt)

*Proyecto:* Enclavamiento de seguridad de una faja minera \
*Fecha:* 23 de noviembre de 2026 · *Herramienta:* NuSMV 2.6.0 · *Modelo:* `modelo/nusmv/enclavamiento.smv`

#v(5pt)
#block(width: 100%, inset: 9pt, fill: rgb("#f3f6fa"), stroke: 0.5pt + rgb("#9cadc0"))[
  *Resultado reproducido.* Las cinco propiedades del modelo nominal fueron
  verdaderas. Se exploraron 119 estados alcanzables, con diámetro 36. El
  control negativo fue falso, como se esperaba. Al retirar la guarda de
  permiso en una copia temporal, MC01 pasó a falsa y NuSMV generó un
  contraejemplo de intrusión.
]

#v(7pt)
*Propiedades verificadas en el modelo nominal*

#table(
  columns: (13mm, 1fr, 25mm, 24mm),
  inset: 4pt,
  stroke: 0.35pt + rgb("#b8c4d0"),
  fill: (x, y) => if y == 0 { rgb("#e7edf4") } else { white },
  [*ID*], [*Fórmula*], [*Tipo*], [*Resultado*],
  [MC01], [`G !(ocupada & potencia)`], [Seguridad LTL], [Verdadera],
  [MC02], [`G (permiso_acceso -> (aislado & energia_cero & ambos_bloqueos))`], [Seguridad LTL], [Verdadera],
  [MC03], [`G (bloqueada -> !potencia)`], [Seguridad LTL], [Verdadera],
  [MC04], [`EF (fase = MANTENIMIENTO & dentro1 & dentro2)`], [Alcance CTL], [Verdadera],
  [MC05], [`EF (fase = LISTO & ciclo_completado)`], [Alcance CTL], [Verdadera],
)

#v(8pt)
*Controles de sensibilidad*

- *Control negativo:* `G !potencia` resultó falso. El contraejemplo del
  log nominal alcanza `fase = MARCHA` con `potencia = TRUE` tras `start`.
- *Intrusión forzada:* se retiró solo la guarda `permiso_acceso` de
  `ingresar1` en una copia temporal. En el contraejemplo, el estado 1.3
  tiene `fase = MARCHA` y `potencia = TRUE`; tras `ingresar1`, el estado 1.4
  tiene además `dentro1 = TRUE` y `ocupada = TRUE`. MC01 resulta falsa.

#v(6pt)
*Líneas decisivas de los registros*

#block(width: 100%, inset: 7pt, fill: rgb("#f7f8fa"), stroke: 0.35pt + rgb("#ccd3dc"))[
  #set text(font: "Liberation Mono", size: 7pt)
  #set par(leading: 0.18em)
  #raw(registro.resultados.at(2) + "\n" + registro.resultados.at(5) +
    "\n-- specification  G !(ocupada & potencia)  is false  [intrusion.log]", block: true)
]

#v(7pt)
*Trazabilidad y reproducción*

El comando `python herramientas/verificar_nusmv.py --bin /ruta/al/NuSMV`
regenera `ejecucion.log`, `intrusion.log` y `manifiesto.json`. El script
comprueba automáticamente los cinco resultados verdaderos, el control
negativo y la falsación de MC01. El modelo y el ejecutable se identifican
mediante SHA-256 en el manifiesto.

#block(width: 100%, inset: 8pt, fill: rgb("#f7f8fa"), stroke: 0.35pt + rgb("#ccd3dc"))[
  *SHA-256 del modelo:* \
  #text(font: "Liberation Mono", size: 7pt)[#registro.sha256_modelo] \
  *Archivos primarios:* `modelo/nusmv/enclavamiento.smv`,
  `artefactos/verificacion/nusmv/ejecucion.log`, `intrusion.log` y
  `manifiesto.json`.
]

#v(6pt)
#text(size: 8pt, fill: rgb("#495664"))[
  *Alcance:* estas propiedades se verificaron en un modelo finito del ciclo
  nominal, bajo el supuesto de acceso controlado. La consulta existencial
  MC04/MC05 no demuestra terminación universal del mantenimiento.
]
