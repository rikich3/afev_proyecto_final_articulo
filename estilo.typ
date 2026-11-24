#let versalitas(contenido) = {
  show regex("\p{Ll}+"): texto => text(size: 0.8em, upper(texto.text))
  contenido
}

// Formato de conferencia IEEE en papel carta.
#let formato(body) = {
  set document(title: "Especificación formal de un entorno simulado para el enclavamiento de seguridad de una faja minera", author: "Equipo AFEV")
  set page(paper: "us-letter", margin: (top: 52pt, bottom: 1in, x: 49pt))
  set text(font: ("Times New Roman", "Nimbus Roman"), size: 10pt, lang: "es")
  // Interlineado de 12 pt, con sangria y sin espacio adicional entre parrafos.
  set par(justify: true, leading: 0.507em, first-line-indent: (amount: 1em, all: true), spacing: 0.507em)

  set heading(numbering: "I.A.")
  show heading.where(level: 1): encabezado => block(
    width: 100%, above: 10.5pt, below: 8pt, sticky: true,
  )[
    #set par(justify: false, first-line-indent: 0pt)
    #align(center)[#text(size: 10pt, weight: "regular")[
      #if encabezado.numbering != none {
        context counter(heading).display("I.")
        h(1em)
      }#versalitas(encabezado.body)
    ]]
  ]
  show heading.where(level: 2): encabezado => block(
    width: 100%, above: 10.5pt, below: 8pt, sticky: true,
  )[
    #set par(justify: false, first-line-indent: 0pt)
    #text(size: 10pt, weight: "regular", style: "italic")[
      #context numbering("A.", counter(heading).get().at(1))#h(1em)#encabezado.body
    ]
  ]

  // Las lineas de continuacion se alinean con el texto del item.
  set list(indent: 10pt, body-indent: 6.5pt, spacing: 0.507em)
  set enum(numbering: "1)", indent: 10pt, body-indent: 6.5pt, spacing: 0.507em)

  set figure(gap: 6pt, placement: auto)
  set figure.caption(separator: [.#h(0.5em)])
  show figure.caption: set text(size: 8pt)
  show figure.caption: set par(first-line-indent: 0pt)
  show figure.where(kind: table): set figure.caption(position: top)
  show figure.where(kind: table): set figure.caption(separator: [#linebreak()])
  show figure.where(kind: table): set figure(numbering: "I", supplement: [TABLA])
  show figure.where(kind: table): figura => {
    show figure.caption: versalitas
    figura
  }
  show figure.where(kind: image): set figure(supplement: [Fig.])
  show figure.where(kind: image): figura => {
    show figure.caption: set align(if figura.scope == "parent" { center } else { left })
    figura
  }
  show raw: set text(font: "Nimbus Mono PS", size: 8pt)
  set math.equation(numbering: "(1)")
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
#let tabla(columnas: (1fr, 1fr), ..celdas) = {
  set text(size: 8pt)
  set par(first-line-indent: 0pt, justify: false)
  table(
    columns: columnas,
    align: left + horizon,
    inset: (x: 4pt, y: 3pt),
    stroke: none,
    table.hline(stroke: 0.5pt),
    table.header(..celdas.pos().slice(0, columnas.len()), table.hline(stroke: 0.4pt)),
    ..celdas.pos().slice(columnas.len()),
    table.hline(stroke: 0.5pt),
  )
}
