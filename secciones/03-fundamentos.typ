= Fundamentos

== Enclavamiento y control de energía

El enclavamiento condiciona la energización y el acceso a estados de seguridad definidos. El procedimiento de bloqueo y etiquetado, denominado LOTO, incorpora el aislamiento y el control de energía almacenada @osha. Karimi y colaboradores documentaron la aplicación de métodos alternativos al bloqueo sin evaluación previa del riesgo en organizaciones de Quebec @karimi2019. Para el caso estudiado, un seccionador representa el aislamiento y dos bloqueos representan la participación individual de los operarios. Una puerta limita el ingreso y los sensores aportan observaciones sobre presencia y estado de la planta.

La evaluación de riesgos y los resguardos se contextualizan en ISO 12100 e ISO 14119 @iso12100 @iso14119. ISO 13849-1 e IEC 62061 proporcionan referencias para el diseño de controles relacionados con seguridad @iso13849 @iec62061. La parada de emergencia y la ubicación de medios de protección se contextualizan en ISO 13850 e ISO 13855 @iso13850 @iso13855. Estas referencias orientan la delimitación de funciones del prototipo académico, cuya evidencia corresponde al modelo y al entorno simulado.

== Event-B y Rodin

Event-B expresa el sistema mediante contextos y máquinas. Los contextos declaran conjuntos, constantes y axiomas. Las máquinas contienen variables, invariantes y eventos. Los eventos pueden declarar parámetros. Sus guardas determinan cuándo se habilitan y sus acciones describen el cambio de estado. Los refinamientos introducen detalle y requieren demostrar una relación con el nivel anterior @abrial2010.

Rodin genera obligaciones para comprobar que la inicialización establece los invariantes y que los eventos los preservan @rodin. Para una propiedad de exclusión, esto exige considerar tanto la energización como el ingreso y la salida de personas. La posibilidad de completar una intervención constituye una pregunta adicional sobre progreso, bajo condiciones del entorno. La distinción entre seguridad y vivacidad permite formular ambas preguntas por separado @lamport1977.

== Estado abstracto y observación física

El modelo abstracto representa ocupación y potencia mediante conjuntos. En los ensayos, el controlador leyó las señales de los sensores y emitió órdenes. Un monitor independiente consultó la ocupación geométrica y el estado físico del contacto. Esta arquitectura permite contrastar la decisión lógica con la respuesta de la planta. La apertura del contacto y la parada mecánica se midieron como sucesos diferentes, pues el movimiento residual condiciona el ingreso de mantenimiento.
