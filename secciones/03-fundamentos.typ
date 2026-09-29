= Fundamentos

== Enclavamiento y aislamiento de energía

Un enclavamiento condiciona las acciones de una máquina a estados y permisos establecidos. Para mantenimiento, la política de bloqueo y etiquetado exige distinguir la señal de control del aislamiento de las fuentes de energía. La referencia pública LOTO considera también la liberación de energía almacenada @osha. En este trabajo los candados personales y el seccionador se representan mediante estados explícitos; la identidad RFID no se interpreta como un dispositivo físico de aislamiento.

La identificación de peligros y la delimitación del equipo se contextualizan en ISO 12100, que establece principios de evaluación y reducción del riesgo @iso12100. Para el acceso controlado, ISO 14119 trata los dispositivos de enclavamiento asociados a resguardos @iso14119. Esta distinción sustenta la separación conceptual entre puerta, sensor de presencia y autorización de acceso en la arquitectura propuesta.

ISO 14118 aborda la prevención de arranques inesperados @iso14118. ISO 13849-1 proporciona un marco para partes de control relacionadas con seguridad @iso13849. IEC 62061 aborda el diseño, la integración y la validación de sistemas de control relacionados con la seguridad de máquinas @iec62061. Se utilizan como contexto de diseño; una simulación y un conjunto de invariantes no permiten asignar un nivel de prestaciones ni declarar conformidad integral con esas normas.

La función de parada de emergencia se contextualiza en ISO 13850 @iso13850. La ubicación de los medios de protección respecto del acercamiento del cuerpo humano corresponde al ámbito de ISO 13855 @iso13855. Para el banco, estas referencias motivan distinguir parada solicitada, parada efectiva y posibilidad física de ingreso. Se emplean los alcances publicados de las normas, sin atribuir conformidad con cláusulas no evaluadas.

== Event-B y refinamiento

Event-B expresa el estado mediante conjuntos, variables e invariantes y define su evolución por eventos con guardas y acciones. La verificación debe establecer que la inicialización satisface los invariantes y que cada evento habilitado los preserva. Los refinamientos incorporan detalle manteniendo una relación con el nivel abstracto @rodin. La exposición de Abrial desarrolla la notación y las reglas de obligaciones de prueba, y sirve de referencia para estructurar los niveles del caso de estudio @abrial2010.

La distinción entre propiedades de seguridad y vivacidad aparece en el trabajo de Lamport sobre corrección de programas concurrentes @lamport1977. La comprobación de seguridad no implica automáticamente progreso. Un estado sin potencia puede ser una espera legítima o un bloqueo indeseado según el protocolo y las acciones disponibles. Por ello, la evaluación separa invariantes, análisis de estados y posibilidad de completar la secuencia de mantenimiento bajo hipótesis explícitas del entorno.

== Verdad física y observación

Se distinguen presencia física, presencia detectada, orden de potencia y potencia realimentada. Esta separación evita declarar segura una escena únicamente porque el controlador ordenó apagar. El tiempo hasta la apertura del contacto y el tiempo hasta la parada mecánica son observaciones diferentes; ambos condicionan cuándo se autoriza el acceso.
