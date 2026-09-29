#block[
#set text(size: 9pt, weight: "bold")
#set par(first-line-indent: 1.5em, leading: 0.4em)
_Abstract—_ El arranque de maquinaria durante una intervención de mantenimiento exige controlar conjuntamente la presencia de personas, el aislamiento de energía y la autorización de puesta en marcha. Este trabajo propone un enclavamiento para una faja minera con una zona de peligro y dos operarios. La especificación utiliza Event-B y refinamientos sucesivos para expresar exclusión entre presencia y potencia, bloqueos individuales y rearme secuencial. Rodin sustenta la verificación deductiva y ProB complementa la exploración de estados. Un controlador Python se conecta a CoppeliaSim EDU para evaluar el comportamiento mediante escenarios nominales, órdenes simultáneas y fallos inyectados. La evaluación distingue el estado lógico de la potencia física simulada y registra tiempos de detección, corte y parada. Se presenta una base metodológica reproducible; las obligaciones descargadas y los resultados cuantitativos permanecen pendientes de ejecución. Las conclusiones se limitan al modelo, sus supuestos y la evidencia simulada, sin atribuir certificación industrial.

_Keywords—Enclavamiento, Event-B, verificación formal, LOTO, minería, CoppeliaSim._
]
