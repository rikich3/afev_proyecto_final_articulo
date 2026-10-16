#import "/estilo.typ": recurso
= Introducción

Una orden de parada no constituye, por sí sola, evidencia de aislamiento de la energía ni de ausencia de personas en una zona de intervención. En una faja transportadora, el mantenimiento exige coordinar presencia, aislamiento, bloqueos personales y autorización de arranque. La prevención del arranque inesperado y el control de energías peligrosas proporcionan el contexto técnico de este estudio @iso14118 @osha. En Perú, el Reglamento de Seguridad y Salud Ocupacional en Minería constituye una referencia de dominio cuya aplicación específica requiere revisar el texto y sus modificatorias @mineria.

*Definición del problema.* Para el caso acotado de una faja, una zona de peligro y dos operarios, hace falta una especificación verificable que impida energizar la zona mientras haya presencia o bloqueos activos, y que condicione el acceso al aislamiento confirmado. También se necesita comprobar que el controlador y sus observaciones físicas simuladas respeten esa especificación. Una orden lógica de apagado, una señal de presencia o un evento RFID, por separado, no demuestran aislamiento físico ni ausencia de personas.

*Objetivo general.* Especificar y evaluar, en un entorno simulado, un supervisor de enclavamiento para una faja minera que coordine presencia, aislamiento, bloqueos personales y rearme seguro.

*Objetivos específicos.* (1) Definir requisitos e invariantes de seguridad y organizarlos mediante refinamientos Event-B. (2) Establecer la correspondencia entre el modelo y un controlador conectado a CoppeliaSim. (3) Evaluar escenarios nominales y de fallo con un monitor independiente, registrando las limitaciones y la evidencia obtenida.

El alcance se restringe a una faja, una zona y dos operarios; no incluye instalación real ni certificación industrial. La contribución propuesta es una cadena trazable entre requisitos, refinamientos, controlador y evidencia experimental. El alcance y los criterios verificables se documentan en #recurso("A01", "artefactos/especificacion/requisitos.md"). El registro #recurso("G01", "artefactos/artefactos.md") establece las ubicaciones canónicas de los recursos. La evaluación cuantitativa descrita en este artículo permanece pendiente de ejecución.
