#import "estilo.typ": formato
#import "metadatos.typ": titulo, autores, afiliacion, correos
#show: formato

#align(center)[
  #set par(justify: false, first-line-indent: 0pt)
  #set text(hyphenate: false)
  #text(size: 24pt, weight: "regular", titulo)
  #v(10pt)
  #text(size: 10.8pt, autores)
  #linebreak()
  #text(size: 9.8pt, style: "italic", afiliacion)
  #linebreak()
  #text(size: 9.8pt, style: "italic", correos)
]
#v(8pt)
#columns(2, gutter: 16pt)[
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
