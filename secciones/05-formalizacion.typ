#import "/estilo.typ": recurso, tabla
= Especificación formal

== Estado abstracto e invariantes

Sean $Z$ el conjunto de zonas y $O$ el conjunto de operarios. La instancia experimental utiliza $Z = {z_1}$ y $O = {o_1, o_2}$. El conjunto $P subset.eq Z$ identifica zonas con potencia activa y $U subset.eq O times Z$ relaciona operarios con su ubicación. La propiedad central INV-01 es:

$ forall z in Z: not (z in P and exists o in O: (o,z) in U). $

En M0, una inicialización candidata establece $P = emptyset$ y $U = emptyset$. El evento abstracto de energización exige ausencia de ocupantes. El evento de ingreso normal exige aislamiento. Esta guarda representa el acceso físicamente controlado de la arquitectura; no elimina la necesidad de estudiar intrusiones fuera de ese supuesto.

En M1 se incorpora $L subset.eq O times Z$, que registra titulares de bloqueos, y una variable de fase. INV-02 exige que una zona con cualquier bloqueo no pertenezca a $P$. INV-03 impide habilitar acceso sin aislamiento y energía cero. INV-04 exige que el arranque ocurra únicamente desde la fase lista, sin ocupantes, bloqueos ni fallos, y con una nueva orden de inicio. Los tipos y las fases también forman parte de los invariantes.

== Refinamientos y eventos

#figure(tabla(
  [*Nivel*], [*Responsabilidad*],
  [M0 · A06], [Exclusión presencia–potencia.],
  [M1 · A10], [Bloqueos personales y rearme secuencial.],
  [M2 · A13], [Sensado, orden, realimentación y fallos.],
), kind: table, caption: [Responsabilidad de los niveles de refinamiento.])

Un evento representativo $"RetirarBloqueo"(o,z)$ requiere $(o,z) in L$, ausencia de $o$ en la zona y fase de liberación. Su acción elimina sólo $(o,z)$ de $L$ y conserva la potencia desactivada. El último retiro no energiza automáticamente; aún deben cumplirse cierre, reset y arranque. Los eventos de parada y fallo revocan permisos de rearme.

M2 distingue señales observadas, órdenes de salida y confirmaciones. La relación de abstracción debe explicar cómo los estados concretos representan presencia y potencia, y qué hipótesis permiten preservar INV-01. Si se permite ingreso no controlado mientras la potencia tarda en caer, esa exclusión puede ser falsa: no es válido obtener la prueba redefiniendo potencia como la mera orden de apagar.

El proyecto nativo se conserva en #recurso("A06", "modelo/rodin/Enclavamiento/"). Las exportaciones #recurso("A13", "modelo/export/M2.txt") y la matriz #recurso("A13", "artefactos/diseno/correspondencia.csv") vinculan guardas y acciones con el controlador. La implementación Python es una traducción manual con evidencia de correspondencia; no se afirma generación automática de código formalmente certificado.

== Obligaciones y alcance de la prueba

La evidencia #recurso("A14", "artefactos/verificacion/obligaciones.csv") identifica obligaciones de inicialización, preservación y refinamiento por versión. Se distinguen pruebas automáticas, interactivas y pendientes. Los eventos nuevos deben clasificarse y, cuando corresponda, justificar convergencia mediante variantes. Una obligación pendiente limita cualquier afirmación de verificación completa.

ProB explora instancias finitas y busca contraejemplos. El informe #recurso("A17", "artefactos/verificacion/prob.md") debe registrar dominios, estados, transiciones, límites y completitud. Para analizar progreso se distingue la espera segura de un deadlock no previsto; un evento vacío siempre habilitado no demuestra que el mantenimiento pueda finalizar. Los supuestos del entorno se conservan en #recurso("A02", "artefactos/especificacion/riesgos.md").
