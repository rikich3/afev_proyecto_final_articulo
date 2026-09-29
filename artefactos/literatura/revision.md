# A04 — Revisión bibliográfica inicial

Fuentes consultadas para la base: documentación oficial de Rodin/Event-B, ProB, CoppeliaSim y fichas oficiales de normas. Referencias metodológicas identificadas abajo. La bibliografía del artículo contiene 21 referencias citadas. Esta selección incorpora dos estudios ferroviarios comparables metodológicamente y no constituye todavía una revisión exhaustiva de enclavamientos mineros.

| Fuente | Aporte utilizable | Límite / uso |
|---|---|---|
| Abrial et al., Rodin (2010), DOI 10.1007/s10009-010-0145-y | Herramienta para modelado, refinamiento y razonamiento Event-B. | No demuestra el controlador Python de este proyecto. |
| Leuschel y Butler, ProB (2003), repositorio Southampton | Animación y model checking de B; documentación actual para soporte Event-B. | Citar artículo para fundamento y documentación para capacidades actuales. |
| Rohmer et al., V-REP (2013), DOI 10.1109/IROS.2013.6696520 | Marco de simulación precursor de CoppeliaSim. | La API actual se documenta con manual ZeroMQ, no con el artículo antiguo. |
| ISO 14118 y documentación LOTO pública | Arranque inesperado y aislamiento de energías. | Orientación de dominio, no resultados de un sistema comparable. |

Fuentes primarias: https://eprints.soton.ac.uk/271058/1/main.pdf ; https://eprints.soton.ac.uk/258341/ ; https://www.coppeliarobotics.com/coppeliaSim_v-rep_iros2013.pdf .

Durante A04: buscar «Event-B safety interlocking», «formal verification lockout tagout» y «mining conveyor safety controller». Seleccionar 3–5 trabajos con texto accesible, DOI/URL verificable, propiedad estudiada, método y evidencia; descartar publicidad sin evaluación. Registrar motores, fecha y criterios, y contrastar de forma explícita con el alcance de una zona/dos operarios. No escribir «no existen trabajos» a partir de una búsqueda limitada.

## Ampliación bibliográfica del artículo

| Clave BibTeX | Fuente y aporte | Uso en el artículo |
|---|---|---|
| abrial2010 | Abrial, *Modeling in Event-B* (Cambridge, 2010), DOI 10.1017/CBO9781139195881. | Notación, refinamiento y obligaciones. |
| lamport1977 | Lamport, *Proving the Correctness of Multiprocess Programs* (IEEE, 1977). | Distinción seguridad/vivacidad. |
| ocra2016 | Limbree et al., preprint arXiv:1605.06245 (2016). | Contratos y descomposición de enclavamientos ferroviarios; comparación, no implementación propia. |
| cappart2017 | Cappart et al., HASE (2017), DOI 10.1109/HASE.2017.10. | Verificación estadística de enclavamientos; diferencias frente a experimentos de simulación. |
| iso12100 | ISO 12100:2010. | Contexto de evaluación y reducción de riesgos. |
| iso14119 | ISO 14119:2024. | Dispositivos de enclavamiento asociados a resguardos. |
| iso13850 | ISO 13850:2015. | Función de parada de emergencia. |
| iso13855 | ISO 13855:2024. | Posicionamiento de medios de protección. |
| iec62061 | IEC 62061:2021+AMD1:2024. | Sistemas de control de seguridad de máquinas. |
| iso29148 | ISO/IEC/IEEE 29148:2018. | Ingeniería de requisitos. |
| iso29119 | ISO/IEC/IEEE 29119-2:2021. | Procesos de pruebas. |
| hypothesis-stateful | Documentación oficial de Hypothesis, *Stateful tests*. | Generación opcional de secuencias de acciones. |

Verificación: metadatos y alcances cotejados con editoriales, organismos normativos, repositorios de autores y documentación oficial; URLs en `referencias.bib`. Para los dos estudios ferroviarios, la comparación se limita al método y alcance descritos en sus resúmenes públicos. Las normas se citan por su alcance público, sin afirmar revisión integral de sus cláusulas. Las 21 entradas aparecen citadas en las secciones y se imprimen en la bibliografía IEEE del PDF.
