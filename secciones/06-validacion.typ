#import "/estilo.typ": recurso, tabla
= Validación experimental

== Diseño y reproducción

ISO/IEC/IEEE 29148 proporciona el contexto de ingeniería de requisitos @iso29148, mientras que ISO/IEC/IEEE 29119-2 describe procesos de pruebas de software @iso29119. En este estudio se toman como referencias para organizar requisitos identificables, criterios de aceptación y evidencia de ejecución; no se declara una evaluación de conformidad normativa.

El protocolo #recurso("A08", "artefactos/validacion/protocolo.md") define trece escenarios: operación nominal, mantenimiento, bloqueos múltiples, saltos de secuencia, concurrencia, retardo, sensor inválido, contacto pegado, pérdida de comunicación, identidad incorrecta, reinicio, intrusión y fallo durante rearme. Se incluyen estímulos que contradicen las hipótesis nominales para determinar sus límites de manera observable.

Cada corrida restablece la escena y conserva escenario, semilla y configuración. El plan inicial utiliza una ejecución por caso determinista y treinta semillas por cada escenario con variación temporal seleccionado. La cantidad definitiva se registra después del piloto. El paso nominal propuesto es 20 ms, con sensibilidad a 10 ms; estos valores definen el banco académico y no un requisito industrial.

La fuente de telemetría es #recurso("A15", "software/telemetria.py"). Las trazas #recurso("A19", "datos/crudos/<run_id>.jsonl") se acompañan de manifiestos con versiones, hashes y parámetros. Se registran entradas, estado previo, evento, estado posterior, salidas, verdad física y violaciones. El monitor consulta posiciones y estados reales de la escena sin reutilizar el resultado del controlador como oráculo.

Como extensión de las pruebas parametrizadas, Hypothesis permite generar secuencias de acciones mediante pruebas con estado @hypothesis-stateful. Su uso opcional puede explorar órdenes repetidas, retiros de bloqueos y fallos intercalados. Las secuencias que revelen errores se conservarán como casos de regresión; esta generación de pruebas no sustituye las obligaciones de Rodin.

== Medidas y criterios

La descarga de pruebas se expresa mediante la fracción de obligaciones demostradas respecto de las generadas para una versión. La cobertura de requisitos cuenta aquellos con evidencia aprobada; se informa por separado de la cobertura de eventos. Para episodios de peligro se mide:

$ L = t_"contacto abierto" - t_"peligro físico". $

El análisis descompone detección, decisión y actuación, y mide además el tiempo hasta la parada mecánica. Todos esos tiempos usan el reloj de simulación; el coste computacional utiliza un reloj monotónico separado. Una falta de apertura se registra como fallo de respuesta, sin descartarla del denominador ni asignarle una latencia cero.

Los criterios principales son ausencia de violaciones físicas dentro de los supuestos, ausencia de rearme indebido y satisfacción de los límites temporales previamente establecidos para el laboratorio. Mediana, percentil 95 y máximo se calculan por escenario, junto a tamaño muestral y fallos. Los intervalos se estiman a nivel de corridas, evitando tratar ticks correlacionados como observaciones independientes.

== Fallos y amenazas a la validez

El watchdog se ejecuta en la escena, separado del cliente. Su evaluación debe garantizar que el reloj que gobierna la caducidad avance aun cuando el cliente deje de enviar mensajes; una simulación congelada en modo stepping no demuestra respuesta temporal ante desconexión. Ante contacto pegado, el resultado esperado es denegar acceso y señalar fallo, no atribuir al software un corte físico imposible.

La validez externa está limitada por una zona, dos operarios, geometría simplificada y ausencia de electrónica real. La validez interna depende del oráculo y del registro: se introduce una violación conocida para comprobar sensibilidad del monitor. La matriz #recurso("A16", "artefactos/validacion/trazabilidad.csv") enlaza requisitos, propiedades, funciones, escenarios y evidencia. La reproducción independiente se documenta en #recurso("A26", "artefactos/entrega/reproduccion.md").
