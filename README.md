# AFEV — Enclavamiento de seguridad para minería

Base de planificación y artículo para una faja, una zona y dos operarios; Event-B/Rodin, ProB, Python y CoppeliaSim EDU. Este repositorio contiene documentación inicial y un artículo compilable. Los modelos ejecutables, la escena, el controlador y los experimentos son entregables planificados; aún no se han implementado ni validado.

## Por dónde empezar

1. Consultar [artefactos/artefactos.md](artefactos/artefactos.md): códigos, rutas, responsables, estados y semanas.
2. Leer [plan de siete semanas](docs/plan_semanal.md): 28 paquetes, 56 h por integrante, 224 h de equipo.
3. Revisar [guía de proyecto y artículo](docs/guia_proyecto.md) y [entorno](docs/entorno.md).
4. Usar [requisitos](artefactos/especificacion/requisitos.md), [supuestos](artefactos/especificacion/riesgos.md), [arquitectura](artefactos/diseno/arquitectura.md) y [protocolo](artefactos/validacion/protocolo.md) como bases de trabajo.
5. Completar autores en `metadatos.typ` y desarrollar las secciones de `secciones/`.

## Compilar y verificar

```sh
typst compile main.typ articulo.pdf
python herramientas/verificar.py
```

La plantilla es local, sin paquetes externos. Requiere Typst y Liberation Serif/Liberation Mono; en este entorno se usa Typst 0.15.0. El PDF sigue el estilo de `ejemplo_articulo.pdf`: carta, dos columnas, título Times compatible de 24 pt, cuerpo 10 pt, numeración romana y bibliografía IEEE.

Una vez generadas las capturas y gráficas reales de A23:

```sh
typst compile --input evidencias=true main.typ articulo.pdf
```

Los datos faltantes de `artefactos/resultados/resumen.json` son `null`, nunca ceros inventados. La base redacta arquitectura, formalización propuesta y método; los resultados y las conclusiones se actualizan sólo con evidencia. Las referencias a rutas planificadas son contratos de ubicación, no afirmaciones de que el software exista.

## Entrega final

A25 audita citas/cifras/trazabilidad; A26 reproduce; A27 empaqueta; A28 integra y compila. El registro diferencia archivos disponibles de entregables pendientes. La evidencia formal se limita a las hipótesis del modelo; la simulación no constituye certificación industrial.
