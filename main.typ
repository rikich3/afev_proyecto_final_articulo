#import "estilo.typ": formato
#import "metadatos.typ": titulo, autores, afiliacion, correos
#show: formato

#align(center)[
  #set par(justify: false, first-line-indent: 0pt)
  #set text(hyphenate: false)
  #text(size: 24pt, weight: "regular", titulo)
  #v(10pt)
  #text(size: 11pt, autores)
  #linebreak()
  #text(size: 10pt, afiliacion)
  #linebreak()
  #text(size: 10pt, correos)
]
#v(10pt)
#columns(2, gutter: 12pt)[
  #include "secciones/00-resumen.typ"
  #include "secciones/01-introduccion.typ"
  #include "secciones/02-relacionados.typ"
  #include "secciones/03-fundamentos.typ"
  #include "secciones/04-propuesta.typ"
  #include "secciones/05-formalizacion.typ"
  #include "secciones/06-validacion.typ"
  #include "secciones/07-resultados.typ"
  #include "secciones/08-conclusiones.typ"
  #include "secciones/09-referencias.typ"
]
