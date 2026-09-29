#import "/estilo.typ": recurso, evidencia, tabla
#let resultados = json("/artefactos/resultados/resumen.json")
#let valor(k) = { let v = resultados.at(k, default: none); if v == none { [Pendiente] } else { str(v) } }
= Resultados y discusión

== Evidencia cuantitativa

Esta base no contiene pruebas Rodin ejecutadas ni corridas de CoppeliaSim. La tabla siguiente lee el resumen de #recurso("A24", "artefactos/resultados/resumen.json"); los campos sin medición permanecen explícitamente pendientes. El análisis reproducible de A20 debe generar este resumen desde las evidencias, conservando la versión utilizada.

#figure(tabla(
  [*Indicador*], [*Resultado*],
  [PO generadas], valor("po_total"),
  [PO demostradas], valor("po_descargadas"),
  [Corridas ejecutadas], valor("corridas"),
  [Violaciones físicas], valor("violaciones_fisicas"),
  [Latencia p95 (ms)], valor("latencia_p95_ms"),
), kind: table, caption: [Resumen de evidencia. «Pendiente» no equivale a cero.])

#figure(evidencia("obligaciones.svg", [Pruebas por modelo y estado]), caption: [Estado de obligaciones por refinamiento. Gráfico pendiente de evidencia A14.])

#figure(evidencia("latencia.svg", [Distribución de tiempos por escenario]), caption: [Latencias de respuesta simulada. Gráfico pendiente de datos A19–A20.])

La presentación definitiva separará resultados por escenario, tamaño de muestra y condición de supuesto. No se mezclará la intrusión forzada con el funcionamiento nominal en una única tasa. La proporción de fallos de respuesta acompañará los percentiles calculados sobre respuestas observadas. Las tablas completas se conservan en #recurso("A20", "datos/procesados/resumen.csv").

== Interpretación prevista

La primera pregunta se responderá con obligaciones vigentes y exploración finita documentada. La segunda requiere correspondencia entre transiciones formales y trazas físicas, no sólo coincidencia de estados internos. La tercera se responderá con los escenarios de retardo, contacto pegado e intrusión, indicando cuáles permanecen dentro de las hipótesis y cuáles las contradicen.

Si aparece una violación dentro del alcance, se conservará la traza y se revisará el requisito, modelo, traducción o simulador antes de repetir los experimentos afectados. Si no aparecen violaciones en las corridas, el resultado se limita a esas condiciones: una observación empírica sin fallos no establece una cota universal de seguridad. La discusión final debe reflejar los resultados obtenidos y no anticipar la aceptación de las tres preguntas.
