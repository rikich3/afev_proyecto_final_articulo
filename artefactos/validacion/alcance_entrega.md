# Alcance de las dos partes

- Parte 1. Especificación Event-B y pruebas Rodin para una faja, una zona y dos
  operarios. La docente debe confirmar la sustitución de VDM++ indicada en la
  consigna original.
- Parte 2. Model Checking con NuSMV 2.6.0, una de las herramientas admitidas
  por la consigna. Cubre un modelo de estados del comportamiento nominal con
  tres propiedades de seguridad, dos de alcanzabilidad y controles negativos.
  El [anexo PDF de NuSMV](../verificacion/nusmv/evidencia.pdf) reúne los
  resultados y remite a los logs y hashes reproducibles.
- Demostración de la planta. El artículo incorpora una captura y una tabla
  breve. El repositorio conserva escena, código, datos y reproducción.
- La presentación y el video quedan fuera del alcance acordado.

La [matriz](trazabilidad.csv) enlaza requisitos, fenómenos simulados,
elementos de Event-B y propiedades aplicables de NuSMV. La
[correspondencia con Python](../diseno/correspondencia.csv) describe guardas
y confirmaciones cubiertas por pruebas. El artículo distingue prueba
formal, análisis finito y observaciones de simulación.

El reinicio ensayado cambia la sesión del supervisor y revoca el mando, con
la escena activa. La persistencia ante un corte total del equipo y el
refinamiento formal del código quedan fuera del experimento.
