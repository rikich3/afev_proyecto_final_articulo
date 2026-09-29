// Adaptación visual de ejemplo_articulo.pdf; sin paquetes externos.
#let formato(body) = {
  set document(title: "Enclavamiento de seguridad para una faja minera", author: "Equipo AFEV")
  set page(paper: "us-letter", margin: (top: 57pt, bottom: 72pt, left: 46pt, right: 42pt),
    numbering: "1", number-align: right + bottom)
  set text(font: "Liberation Serif", size: 10pt, lang: "es")
  set par(justify: true, leading: 0.48em, first-line-indent: 1.6em, spacing: 0.7em)
  set heading(numbering: "I.A.")
  show heading.where(level: 1): it => block(width: 100%, above: 15pt, below: 8pt)[
    #set par(justify: false, first-line-indent: 0pt)
    #align(center)[#text(size: 10pt, weight: "regular")[
      #if it.numbering != none { context counter(heading).display("I."); h(0.6em) }#upper(it.body)
    ]]
  ]
  show heading.where(level: 2): it => block(width: 100%, above: 9pt, below: 5pt)[
    #set par(justify: false, first-line-indent: 0pt)
    #text(size: 10pt, weight: "regular", style: "italic")[
      #context numbering("A.", counter(heading).get().at(1)) #h(0.4em) #it.body
    ]
  ]
  set figure(gap: 5pt)
  set figure.caption(separator: [. ])
  show figure.caption: set text(size: 8pt)
  show figure.where(kind: table): set figure.caption(position: top)
  show figure.where(kind: table): set figure(numbering: "I", supplement: [TABLA])
  show figure.where(kind: image): set figure(supplement: [Figura])
  show raw: set text(font: "Liberation Mono", size: 8pt)
  show bibliography: set text(size: 8pt)
  body
}
#let ruta(p) = text(font: "Liberation Mono", size: 7.6pt, p.replace("/", "/\u{200b}"))
#let recurso(codigo, ubicacion) = [#codigo (#ruta(ubicacion))]
#let evidencia(archivo, descripcion, alto: 30mm) = {
  if sys.inputs.at("evidencias", default: "false") == "true" {
    image("/img/" + archivo, width: 100%)
  } else {
    block(width: 100%, height: alto, inset: 8pt, stroke: 0.5pt + gray)[
      #align(center + horizon)[#text(size: 9pt)[*Evidencia pendiente*\
      #descripcion\ #ruta("img/" + archivo)]]
    ]
  }
}
#let tabla(..celdas) = {
  set text(size: 8.5pt)
  set par(first-line-indent: 0pt, justify: false)
  table(columns: (1fr, 1fr), inset: 4pt, stroke: 0.3pt + gray, ..celdas)
}
