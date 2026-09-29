# Guía para implementar y redactar un artículo defendible

## Ruta de menor esfuerzo útil

1. Construir una escena geométrica simple: cubo/faja, zona, puerta, dos avatares y testigos. Usar señales booleanas para láser/barrera y eventos ID para RFID. Separar orden de potencia, contacto real, seccionador y movimiento residual.
2. Escribir M0 con presencia-potencia y eventos pequeños. Probarlo antes de añadir LOTO en M1. Incorporar interfaz y fallos en M2, sin modelar toda la física en Event-B.
3. Implementar una función de transición pura en Python, estados enumerados, un solo bucle y prioridad de parada. Evitar concurrencia de hilos y GUI propia. Probar con snapshots sin simulador.
4. Conectar por ZeroMQ con pasos sincronizados. Medir desde el primer ciclo: un logger JSONL y un monitor independiente evitan reconstruir evidencia al final.
5. Ejecutar casos deterministas; después inyectar fallos y retardos. Mantener una sola zona y dos operarios para exhibir LOTO colectivo sin explosión de estados.
6. Convertir trazas a CSV/gráficos con Python y escribir semanalmente los hallazgos en las secciones Typst. Los diagramas se exportan como SVG, las capturas como PNG.

## Qué demostrar y qué no confundir

El objetivo principal es `∀z: ¬(Operario_En_Zona(z) ∧ Potencia_Activa(z))`, bajo hipótesis explícitas. Probarlo en Event-B requiere inicialización y preservación por cada evento, incluidas entradas del entorno. Un modelo que sólo permite entrar cuando la potencia es cero debe explicar el mecanismo físico que lo hace posible. En este MVP es el acceso enclavado y la verificación de energía cero; se ensaya también la intrusión forzada como límite.

M0 → M1 → M2 debe conservar relación de abstracción, fortalecimiento de guardas y simulación de acciones; clasificar eventos nuevos y justificar convergencia/variantes si corresponde. La traducción manual Python se verifica por correspondencia y pruebas, **no es generación de código demostrada**. Si el curso exige garantía formal hasta código ejecutable, acordar una herramienta de generación/verificación adicional y ampliar alcance; no presentar las pruebas de modelo como prueba del binario.

«Irreversible» significa no saltar liberaciones ni reutilizar autorizaciones del ciclo anterior. Una emergencia sí puede llevar de vuelta a fallo seguro. Seguridad, ausencia de deadlock y progreso son propiedades distintas: las últimas requieren estudiar entorno, equidad y esperas legítimas. ProB complementa las pruebas, pero una búsqueda acotada no demuestra todos los tamaños o configuraciones.

## Instrumentación que necesita el artículo

Aplicar A08. Registrar tiempo físico simulado, tiempo de detección, orden, realimentación y parada mecánica por incidente. Usar tiempo de simulación para respuesta de planta y reloj monotónico para coste de CPU; no restar relojes diferentes. La verdad física del monitor procede de posiciones/estados de la escena, no de RFID ni del estado interno del controlador. El monitor debe detectar una violación deliberada conocida.

No resumir diez mil ticks de una corrida como diez mil experimentos. Congelar protocolo, semillas y criterios antes de las corridas definitivas. Reportar n, fallos, corridas censuradas y valores ausentes. Conservar datos crudos, comandos, configuración y hashes. Usar tablas pequeñas de obligaciones por refinamiento y gráficos de latencia por escenario; mostrar las distribuciones antes que una única media. Cobertura de código es opcional; trazabilidad requisito→prueba es obligatoria.

## Normas y fuentes que conviene conocer

Las siguientes referencias orientan el diseño académico; consultar alcance y edición en fuente oficial. Los textos completos ISO/IEC pueden ser de pago: las fichas públicas permiten identificar alcance, no atribuir cumplimiento de cláusulas que no se revisaron. No es necesario adquirir software propietario para ejecutar el proyecto.

| Referencia | Uso en este proyecto | Fuente oficial |
|---|---|---|
| ISO 14118:2017 | Prevención de arranque inesperado; considerar energía almacenada además de potencia eléctrica. | https://committee.iso.org/standard/66460.html?browse=ics |
| ISO 13849-1:2023 | Marco de diseño de partes de control relacionadas con seguridad. No asignar PL a una simulación. | https://www.iso.org/standard/73481.html |
| IEC 62061:2021 + AMD1:2024 | Diseño/integración/validación de controles de seguridad de máquinas; contexto de seguridad funcional. No atribuir SIL al prototipo. | https://webstore.iec.ch/en/publication/93654 |
| OSHA 29 CFR 1910.147 | Referencia pública para procedimiento LOTO y control de energías peligrosas. Es estadounidense, no ley peruana. | https://www.osha.gov/laws-regs/regulations/standardnumber/1910/1910.147 |
| D. S. 024-2016-EM y modificatorias | Contexto peruano de seguridad y salud ocupacional minera. Verificar texto consolidado y artículos pertinentes antes de afirmar obligaciones legales. | https://sinia.minam.gob.pe/normas/aprueban-reglamento-seguridad-salud-ocupacional-mineria |
| ISO/IEC/IEEE 29148:2018 | Requisitos claros y trazables; adaptar estructura de A01. | https://www.iso.org/standard/72089.html |
| ISO/IEC/IEEE 29119-2:2021 | Organización del proceso y evidencia de pruebas. | https://www.iso.org/standard/79428.html |
| ISO/IEC 25010:2023 | Seleccionar atributos de calidad medibles; no medir todo el catálogo. | https://www.iso.org/standard/78176.html |

## Redacción, evidencia y revisión

- Pregunta concreta: si el enclavamiento formalizado evita energización incompatible y qué conserva la implementación simulada. Contribución: cadena trazable requisitos/modelo/controlador/evidencia, sin prometer novedad mundial.
- Resumen: problema, objetivo, método, resultados medidos y conclusión limitada. La base actual describe método y marca resultados pendientes; al finalizar incorporar cifras reales.
- Introducción: motivación, problema, preguntas y contribuciones. No afirmar frecuencias de accidentes, porcentajes ni causalidad de errores PLC sin fuente primaria verificable. El enunciado del curso no es evidencia epidemiológica.
- Trabajos relacionados: comparar 3–5 trabajos pertinentes por método, propiedades, validación y límites. La base bibliográfica de herramientas no basta para alegar una brecha en minería: añadir casos de enclavamiento comparables al revisar A04.
- Formalización: definir conjuntos, tipos, hipótesis, invariantes, un evento representativo y mapa de refinamientos. Mostrar resultados de Rodin con identificadores y versiones; capturas solas no reemplazan fuentes exportables.
- Evaluación: publicar protocolo, escenarios, oráculo independiente, denominadores y configuración. Separar demostración lógica, exploración finita y medición empírica.
- Discusión: sesgos del simulador, abstracción de sensores, fallo común, traducción manual, una sola zona, geometría y representatividad minera. Explicar contraejemplos y supuestos sin esconderlos en promedios.
- Conclusiones: responder cada pregunta con evidencia, sin generalizar a certificación o planta real.
- Figuras: texto legible al ancho de una columna; unidades en ejes, leyendas y procedencia. Evitar capturas de ventanas enteras si un recorte legible basta. Todo recurso en `img/`.
- Referencias: BibTeX y citas numéricas IEEE generadas por Typst; citar sólo fuentes consultadas. Guardar DOI y URL institucional. Revisar correspondencia de cada afirmación.

## Formato del ejemplo y compilación

`ejemplo_articulo.pdf` usa carta (612 × 792 pt), Times, título de 24 pt, cuerpo cercano a 10 pt, dos columnas y numeración romana. La plantilla reproduce esos rasgos con Liberation Serif (libre, métricamente cercana), márgenes laterales cercanos a 46/42 pt y separación de 16 pt. Resumen en español precedido de «Abstract» y «Keywords», como el ejemplo; títulos principales centrados, subtítulos alfabéticos en cursiva, pies pequeños y número de página inferior derecho. Bibliografía IEEE. No se copian contenido, errores tipográficos ni autores del ejemplo. Es una adaptación visual al documento facilitado; si una revista exige su plantilla oficial, prevalece ésta.

Editar autores/afiliación en `metadatos.typ`, no repetirlos en secciones. Compilar con `typst compile main.typ articulo.pdf`. Los recuadros de evidencia pendiente permiten compilar antes de generar capturas/gráficos. Después de producir todos los recursos A23, usar `typst compile --input evidencias=true main.typ articulo.pdf`; el compilador entonces exige los archivos reales. El JSON A24 usa null para mediciones no disponibles. No eliminar esas marcas hasta tener evidencia y completar A25/A26.
