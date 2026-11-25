# A25. Auditoría de originalidad y atribución

**Fecha:** 23 de noviembre de 2026. **Objeto:** prosa del manuscrito Typst,
referencias bibliográficas y fuentes aportadas para el estilo editorial.

## Revisión de la versión IEEE

El cotejo de once textos y su CSV corresponden a la versión anterior del
manuscrito. Tras el ajuste IEEE se repitió el cotejo literal de la prosa
con el ejemplo disponible en `ejemplo_articulo.pdf`. Se examinaron 229
oraciones y no se hallaron coincidencias de cinco o más palabras consecutivas
con ese archivo. Esta medición se limita al ejemplo disponible.

La versión IEEE contiene 27 referencias. Se cotejaron con sus fichas
editoriales las entradas sobre [ProB](https://doi.org/10.1007/s10009-007-0063-9),
[OCRA](https://doi.org/10.1007/978-3-319-33951-1_10) y
[NuSMV](https://doi.org/10.1007/3-540-45657-0_29). Las normas y los manuales
técnicos se mantienen para documentar el marco normativo y las herramientas.

## Cotejo de texto

Se extrajo el texto de los seis artículos de ejemplo facilitados por el equipo
y de cinco fuentes académicas citadas: el artículo de [Rodin](https://www.southampton.ac.uk/~tsh2n14/publications/journals/rodin-sttt2010.pdf),
el artículo de [ProB](https://eprints.soton.ac.uk/258341/), el estudio de
[OCRA](https://arxiv.org/abs/1605.06245), el estudio de
[Cappart et al.](https://arxiv.org/abs/1605.02529) y el artículo de
[V-REP/CoppeliaSim](https://www.coppeliarobotics.com/coppeliaSim_v-rep_iros2013.pdf).
Una copia duplicada de uno de los ejemplos se descartó por hash. Se
normalizaron mayúsculas, tildes y signos, y se cotejaron **204 oraciones** de
las secciones 00–08 con **11 textos únicos**. El resultado por oración está
en [`originalidad.csv`](originalidad.csv), generado por
[`herramientas/auditar_originalidad.py`](../../herramientas/auditar_originalidad.py).
Para repetirlo, reunir los PDF originales en un directorio y ejecutar:

```sh
python herramientas/auditar_originalidad.py /ruta/fuentes/*.pdf \
  --salida artefactos/entrega/originalidad.csv
```

**Resultado:** ninguna oración contiene cinco o más palabras consecutivas
iguales a las de ese corpus. Seis oraciones comparten cuatro palabras; son
expresiones comunes como «el caso de aplicación» y «un lenguaje de
especificación». La búsqueda identifica coincidencia literal en prosa. No
detecta por sí misma traducciones, paráfrasis cercanas, coincidencias en
tablas/fórmulas ni fuentes ausentes del corpus. Tampoco estima un porcentaje
de Turnitin.

## Medición de similitud local con software libre

Se compiló y ejecutó [Sherlock](https://github.com/diogocabral/sherlock)
(licencia Unlicense; SHA-256 del `sherlock.c` usado:
`5561d6977e97c8c66d59b3232919b16c03bb23d9141a938ade7cf24f9a608df9`).
Se normalizaron mayúsculas, tildes y signos con la función `palabras` del
comprobador local y se comparó la prosa de las secciones 00–08 con los mismos
11 textos. Con `-z 0` (sin descarte de firmas), Sherlock informó **0 % en
cada comparación por pares** tanto con cadenas de tres (`-n 3`) como de cinco
palabras (`-n 5`). Su porcentaje es una razón entre firmas de *dos archivos*
y se trunca a un entero: ese cero no significa que no existan frases comunes.

Para medir directamente qué parte de la prosa coincide con *alguna* fuente,
`herramientas/auditar_originalidad.py` cuenta una sola vez cada palabra que
pertenece a una cadena coincidente dentro de una oración:

| Longitud mínima de la cadena | Palabras cubiertas / 3342 | Cobertura local |
|---|---:|---:|
| 3 palabras | 255 / 3342 | 7,63 % |
| 4 palabras | 28 / 3342 | 0,84 % |
| 5 palabras | 0 / 3342 | 0,00 % |

Las coincidencias de cuatro palabras corresponden a siete expresiones breves
de uso general, entre ellas «el caso de aplicación» y «la verificación de
sistemas». El denominador contiene la prosa seleccionada de 204 oraciones;
excluye bibliografía, código, fórmulas y leyendas. Las cifras son **cobertura
literal frente al corpus local**, no un índice de plagio ni una predicción del
resultado de Turnitin, cuya base de comparación incluye otros documentos.
El procedimiento y los porcentajes se reproducen con el comando de la sección
anterior.

## Revisión de atribución por sección

| Sección | Afirmaciones externas cotejadas | Resultado |
|---|---|---|
| Resumen e introducción | Arranque inesperado y control de energía: [ISO 14118](https://www.iso.org/standard/66460.html) y [OSHA 1910.147](https://www.osha.gov/laws-regs/regulations/standardnumber/1910/1910.147); marco minero: [D. S. 024-2016-EM](https://www.gob.pe/institucion/osinergmin/normas-legales/741887-024-2016-em). | Las ideas externas tienen citas próximas; objetivo, alcance y resultados proceden del proyecto. |
| Estado del arte | Rodin y ProB se describen conforme a sus artículos; soporte Event-B según [ProB](https://prob.hhu.de/w/index.php/ProB_for_Event-B); [OCRA](https://arxiv.org/abs/1605.06245) y [Cappart et al.](https://arxiv.org/abs/1605.02529) sustentan las dos comparaciones ferroviarias; la API [ZeroMQ](https://manual.coppeliarobotics.com/en/zmqRemoteApiOverview.htm) sustenta la comunicación externa. | Se verificó el sentido de cada paráfrasis contra el resumen o pasaje pertinente. No se observó traslado textual de los artículos de ejemplo. |
| Fundamentos | La explicación de Event-B/Rodin coincide con los conceptos del artículo de Rodin y el libro de Abrial; la distinción seguridad/vivacidad está en [Lamport (1977)](https://lamport.azurewebsites.net/pubs/proving.pdf). El alcance de las normas se contrastó con sus fichas públicas. | Atribución adecuada al nivel de generalidad usado. No se afirma haber revisado cláusulas completas de normas de pago. |
| Propuesta y formalización | Requisitos, arquitectura, fragmentos Event-B y diagramas corresponden a los artefactos y modelos del repositorio. | Contenido técnico propio del proyecto; no se halló coincidencia literal extensa en el corpus. |
| Validación | La sintaxis y capacidad de NuSMV están respaldadas por su [manual 2.6](https://nusmv.fbk.eu/userman/v26/nusmv.pdf). ISO/IEC/IEEE 29148 y 29119-2 se citan solo por su ámbito metodológico público. | Escenarios, parámetros y criterios son decisiones del proyecto. |
| Resultados y conclusiones | Cifras, casos y limitaciones se vinculan con logs, manifiestos y trazabilidad del repositorio. | Son resultados internos; no requieren atribución bibliográfica externa. |

## Verificación bibliográfica

Se aplicó el procedimiento de la skill externa
[`citation-verification`](https://www.skills.sh/kalarislabs/research-agent-skills/citation-verification)
de Kalaris Labs: DOI, título, primer autor y año se cotejaron con índices
bibliográficos y, para normas/manuales, con páginas del organismo emisor.
El comprobador automático marcó varias normas, documentación técnica y el
reglamento peruano como «no encontrados» porque sus títulos no son artículos
indexados. Se confirmaron en las páginas oficiales; esa marca no indica una
referencia inventada. El aparente desacuerdo del título del libro de Abrial
procede de que el registro DOI abrevia el subtítulo; la ficha de
[Cambridge University Press](https://www.cambridge.org/core/books/modeling-in-eventb/F39FF5F1B60F0AA585718B8E6A4F9DD7)
confirma el título completo y la edición impresa de 2010.

Se completaron los metadatos y DOI de ProB y Lamport, se reemplazaron dos
enlaces por páginas oficiales más directas y se retiró una entrada que no
aparecía citada. Quedan **21 entradas, todas citadas**.

## Alcance de la conclusión

En las fuentes examinadas no se encontró copia literal extensa ni una
paráfrasis atribuida a una fuente equivocada. La revisión semántica de normas
se limitó a sus fichas públicas. Para una decisión institucional sobre
similitud se necesita el informe oficial y examinar cada coincidencia en su
contexto. Los borradores previamente depositados también pueden generar
coincidencias con el propio trabajo.
