= Introducción

Durante el mantenimiento de una faja transportadora, detener el motor, aislar la energía y autorizar el ingreso son acciones distintas. Una orden de parada debe ir seguida de confirmaciones que permitan establecer cuándo la intervención puede comenzar. La prevención del arranque inesperado y el control de energías peligrosas proporcionan el contexto técnico de este problema @iso14118 @osha. El Reglamento de Seguridad y Salud Ocupacional en Minería sitúa el caso en el ámbito peruano @mineria.

En el caso estudiado, dos operarios comparten una zona de peligro. La salida de uno de ellos debe mantener inhibida la energización mientras el otro permanezca dentro. Además, la autorización de ingreso requiere aislamiento y parada confirmados, y la puesta en marcha exige una secuencia de rearme. Expresar estas condiciones mediante Event-B permite identificar las variables necesarias, formular invariantes y comprobar su preservación por cada evento. El trabajo aporta una especificación M0–M2 con 272 obligaciones demostradas y un protocolo para evaluar el controlador en la planta simulada.

El objetivo general es *especificar formalmente un entorno simulado para el enclavamiento de seguridad de una faja minera*. El alcance comprende una faja, una zona y dos operarios. La metodología parte de un modelo abstracto y lo refina con bloqueos, rearme e interfaz de planta. Un modelo finito complementa estas pruebas mediante NuSMV. El controlador Python se evalúa sobre una escena instrumentada en CoppeliaSim mediante un canal independiente de observación.

Los objetivos específicos son (1) modelar la exclusión y las autorizaciones de mantenimiento en Event-B, (2) verificar propiedades del comportamiento de acceso y rearme mediante Model Checking y (3) evaluar el controlador en una planta simulada con observación física independiente.

El artículo presenta (1) el estado del arte y los fundamentos de Event-B, (2) el caso de aplicación y sus requisitos, (3) los tipos, invariantes y eventos del modelo, (4) el modelo de estados y el protocolo de validación y (5) los resultados disponibles, su discusión y las conclusiones.
