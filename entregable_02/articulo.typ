#import "../estilo.typ": formato
#import "../metadatos.typ": titulo, autores, afiliacion
#show: formato

#align(center)[
  #set par(justify: false, first-line-indent: 0pt)
  #set text(hyphenate: false)
  #text(size: 24pt, titulo)
  #v(8pt)
  #text(size: 10pt, autores)
  #linebreak()
  #text(size: 9pt, style: "italic", afiliacion)
  #linebreak()
  #text(size: 9pt, style: "italic", [Arequipa, Perú])
]
#v(8pt)
#columns(2, gutter: 16pt)[
  #set par(first-line-indent: 0pt)
  *Resumen—* El mantenimiento de una faja transportadora requiere coordinar la presencia de operarios, el aislamiento de energía y la autorización de puesta en marcha. Este segundo entregable define el problema, los objetivos, los trabajos relacionados y los requisitos funcionales de un supervisor de enclavamiento para una faja minera, una zona de peligro y dos operarios. La propuesta utiliza Event-B para expresar propiedades de seguridad y plantea una evaluación posterior en CoppeliaSim. Se recuperan del avance previo las representaciones mediante conjuntos, secuencias, mapas y un registro de zona, distinguiéndolas del modelo abstracto implementado. El repositorio conserva C0/M0 y un registro de cinco obligaciones demostradas, además de una escena geométrica del banco. Los refinamientos, el controlador y los experimentos integrados permanecen pendientes. El alcance es un prototipo académico simulado.

  *Palabras clave—* Enclavamiento, Event-B, seguridad, faja transportadora, requisitos, CoppeliaSim.
  #set par(first-line-indent: 1.6em)

  = Definición del problema

  Una orden de parada no confirma por sí sola que una faja transportadora esté aislada, que se haya eliminado su energía residual o que no existan personas en su zona de peligro. La prevención del arranque inesperado constituye el contexto de seguridad del caso de estudio @iso14118. En una intervención de mantenimiento, la decisión de arrancar depende de condiciones distribuidas: ubicación de operarios, bloqueos personales, estado del acceso, aislamiento y confirmación de potencia.

  El problema consiste en especificar un supervisor que coordine esas condiciones e impida autorizar acceso o energización incompatibles con ellas. El caso se limita a una faja, una zona y dos operarios identificables. La identificación RFID se representa mediante eventos de identidad; los sensores aportan presencia o estado y no sustituyen el aislamiento ni los bloqueos personales.

  La pregunta central es: ¿cómo especificar y comprobar las reglas de un enclavamiento que mantenga la exclusión entre presencia y potencia y exija una secuencia explícita de liberación antes de un nuevo arranque? La verificación abstracta y la evaluación de la planta simulada requieren evidencias distintas; una prueba de una variable lógica no demuestra por sí sola que una máquina física esté sin energía.

  = Objetivos

  == Objetivo general

  Especificar y evaluar, en un entorno simulado, un supervisor de enclavamiento para una faja minera que coordine presencia, aislamiento, bloqueos personales y rearme seguro.

  == Objetivos específicos

  + Definir requisitos e invariantes de seguridad y organizarlos mediante refinamientos Event-B.
  + Establecer la correspondencia entre el modelo, un controlador y la planta simulada en CoppeliaSim.
  + Evaluar escenarios nominales y de fallo mediante observación independiente, registrando la evidencia y las limitaciones del prototipo.

  = Trabajos relacionados

  Abrial y colaboradores presentan Rodin como una plataforma que integra modelado y prueba en Event-B @rodin. Su aporte es la organización por niveles de abstracción y la conservación de propiedades mediante refinamiento. Este trabajo adopta esa estructura para los permisos de acceso y potencia; la existencia de Rodin no constituye evidencia de corrección del controlador propuesto.

  Limbree y colaboradores estudian enclavamientos ferroviarios con OCRA, descomposición y contratos @ocra2016. La verificación composicional busca afrontar el crecimiento del espacio de estados. La comparación sugiere una posible extensión por zonas; el caso actual mantiene una sola zona y no implementa verificación composicional.

  Cappart y colaboradores aplican verificación estadística a enclavamientos ferroviarios, considerando seguridad y disponibilidad @cappart2017. Su método obtiene conclusiones con confianza parametrizable sin reclamar exhaustividad. La evaluación prevista en CoppeliaSim se limita a escenarios de simulación; todavía no incorpora un procedimiento de verificación estadística.

  Estas tres referencias aportan una base metodológica y casos de enclavamiento de otro dominio. El aporte propuesto es una cadena trazable entre requisitos, modelo, controlador y observación para el caso minero acotado. La revisión debe ampliarse con estudios específicos de seguridad minera antes de afirmar novedad respecto de ese dominio.

  ProB aporta animación y exploración de estados para B @prob. Se contempla como complemento a la prueba deductiva; su exploración no se ha ejecutado en este avance. La API ZeroMQ de CoppeliaSim documenta la conexión con clientes externos @zmq y sustenta el adaptador previsto para el controlador.

  = Requerimientos funcionales

  Cada requisito conserva el identificador de la especificación del repositorio. Los seis prioritarios se acompañan de criterios de aceptación propuestos; estos criterios no se presentan como pruebas ya ejecutadas.

  *RF-01. Exclusión presencia–potencia.* El sistema debe impedir la coexistencia de operarios y potencia activa en la zona bajo los supuestos de acceso controlado. *Aceptación:* preservación del invariante de exclusión y ausencia de estados físicos inseguros en los escenarios dentro de supuestos.

  *RF-02. Aislamiento previo al acceso.* Debe mantener el acceso cerrado hasta confirmar aislamiento, apertura del contacto y energía residual nula. *Aceptación:* ninguna orden de acceso mientras falte una confirmación.

  *RF-03. Bloqueo individual.* Debe conservar un bloqueo por operario y permitir su retiro únicamente al titular después de salir. *Aceptación:* un bloqueo restante impide energizar; un tercero no puede retirarlo.

  *RF-04. Rearme secuencial.* Debe exigir salida de todos, retiro de bloqueos, cierre de acceso y reset manual; el arranque requiere una orden nueva y posterior. *Aceptación:* reset no energiza y una orden de start anterior no se reutiliza.

  *RF-05. Respuesta ante peligro o fallo.* Debe desactivar la orden de potencia y enclavar fallo ante peligro, señal inválida o caducada, o discrepancia. *Aceptación:* revocación de permisos y registro del corte y su confirmación.

  *RF-06. Prioridad de parada.* Debe resolver órdenes simultáneas dando prioridad a parada, emergencia y fallo sobre reset y arranque. *Aceptación:* el orden de recepción no altera esa prioridad en un mismo ciclo.

  La especificación completa también contempla inicio seguro (RF-07), registro de evidencia (RF-08), watchdog local ante desconexión (RF-09) y confirmación de apertura del contacto (RF-10). Los límites temporales pertenecen al banco de laboratorio y deben fijarse antes de las corridas.

  = Modelo y avance disponible

  El avance conceptual organiza la información mediante un registro de zona: identificador, ocupantes, bloqueos, potencia activa, aislamiento, energía residual y acceso habilitado. Los conjuntos describen miembros sin orden; los mapas relacionan una zona con sus ocupantes o titulares de bloqueos, y una secuencia conserva el historial ordenado de eventos. El diagrama de clases VDM++ del avance representa esa organización inicial; el desarrollo formal principal del artículo es Event-B.

  En M0, $Z$ es el conjunto de zonas, $O$ el de operarios, $P subset.eq Z$ las zonas con potencia abstracta y $U subset.eq O times Z$ la relación de ocupación. El invariante central es:

  $ op("ran")(U) inter P = emptyset. $

  Los eventos de energización e ingreso comprueban respectivamente ausencia de ocupantes y ausencia de potencia. Este modelo presupone acceso normal controlado y todavía no representa energía residual, retardos ni fallos de sensado.

  #figure(image("../img/arquitectura.svg", width: 100%), caption: [Arquitectura propuesta. El controlador y la integración dinámica permanecen pendientes.])

  C0/M0 y sus árboles de prueba están presentes en el repositorio. El registro local de verificación del 7 de octubre de 2026 informa cinco obligaciones generadas y cinco demostradas. Se cita ese registro conservado; no se afirma una nueva ejecución de Rodin para esta entrega. Las obligaciones se limitan al modelo M0 y sus supuestos.

  La escena #raw("simulacion/mina_modelada.ttt") contiene la geometría de la faja, acceso, operarios, sensores y panel. Su representación visual no equivale a un controlador de seguridad integrado: potencia, aislamiento, identidad y watchdog aún necesitan comportamiento.

  = Validación prevista y próximos pasos

  El protocolo define trece escenarios que incluyen operación nominal, mantenimiento, bloqueos múltiples, saltos de secuencia, concurrencia, retardos y fallos. Se prevé registrar entradas, decisiones, salidas y estado físico con un monitor independiente. El tiempo hasta apertura del contacto y el tiempo hasta parada mecánica son medidas distintas.

  El siguiente trabajo comprende los refinamientos M1/M2, la correspondencia con el controlador y la integración dinámica del simulador. Las capturas de Rodin y de la escena deberán identificar la versión y el estado real observado. No existen todavía corridas integradas ni resultados de latencia en este entregable.

  = Conclusiones del avance

  El segundo entregable establece un problema delimitado, objetivos verificables, antecedentes metodológicos y requisitos identificables. El avance conceptual y M0 proporcionan una base para continuar; la validez del supervisor completo depende de cerrar los refinamientos e integrar y evaluar su comportamiento. Las conclusiones se limitan al estado documentado del prototipo académico.

  #bibliography("referencias.bib", style: "ieee", title: [Referencias])
]
