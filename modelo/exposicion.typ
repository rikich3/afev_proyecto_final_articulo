== Estructura conceptual y notación UML

Las clases principales son Zona, Operario y Faja: permiten identificar el ámbito de peligro, las personas y el equipo cuya potencia se controla. Bloqueo representa la autorización individual de mantenimiento. El diagrama utiliza cajas con nombre y atributos tipados, asociaciones y multiplicidades según UML @uml. Se omiten operaciones porque se presenta un modelo de dominio; las transiciones se especifican como eventos Event-B.

#figure(image("/img/clases.svg", width: 100%), caption: [Clases del dominio. SVG vectorial; las multiplicidades corresponden al caso de una zona, una faja y dos operarios. Bloqueo pertenece al refinamiento previsto.])

Zona y Operario corresponden a los conjuntos Z y O; la asociación «ocupa» se representa mediante U. La potencia de la faja se abstrae como pertenencia de su zona a P. Bloqueo se representará mediante una relación L en M1. Esta correspondencia es conceptual: Event-B no declara clases UML. La multiplicidad de ocupación expresa el diseño previsto; el tipo declarado de U en M0 es una relación y no una función parcial. La guarda de ingreso impide agregar otra ubicación para un operario ya presente.

== Tipos de datos en Event-B

El contexto C0 declara dos conjuntos portadores y sus elementos. Los axiomas de partición fijan una zona y dos operarios distintos. Se reproduce la exportación textual del contexto existente:

#block(breakable: false)[#raw(read("/modelo/export/C0.txt"), block: true)]

En M0, P es un conjunto de zonas, tipado por el invariante P ⊆ Z; U es una relación entre operarios y zonas, tipada por U ⊆ O × Z. Por tanto, sus tipos son respectivamente ℙ(Z) y ℙ(O × Z). El par o ↦ z representa una asociación de ocupación; dom(U) contiene los operarios presentes y ran(U) las zonas ocupadas. El conjunto vacío ∅ representa ausencia de elementos. La asignación ≔ modifica una variable, mientras que ∈, ⊆ y = expresan predicados. Los tipos y las propiedades se escriben en la notación matemática de Event-B @handbook.

== Máquina, invariantes y eventos implementados

La siguiente transcripción procede de M0, la máquina disponible en el repositorio. INITIALISATION establece ausencia de potencia y ocupación. Energizar exige que la zona no esté ocupada; Ingresar exige que no tenga potencia abstracta. Cortar y Salir eliminan elementos de P y U, respectivamente.

#for fragmento in read("/modelo/export/M0.txt").split("

") {
  block(breakable: false, raw(fragmento, block: true))
}

El invariante INV_01 establece que ninguna zona ocupada pertenece al conjunto de zonas con potencia. Por ejemplo, Ingresar añade o ↦ z a U únicamente si z ∉ P; Energizar añade z a P únicamente si z ∉ ran(U). Ambas guardas preservan la exclusión. La inicialización satisface la propiedad porque ambos conjuntos están vacíos. El registro de Rodin conservado documenta cinco obligaciones generadas y demostradas; esta edición no ejecuta nuevamente esas pruebas.

M0 representa potencia y presencia abstractas. La condición z ∉ P no equivale a una confirmación de aislamiento ni de energía residual nula. Bloqueos, fases de rearme, sensores y realimentación requieren los refinamientos M1/M2, todavía pendientes. Los conjuntos, relaciones y eventos anteriores son el modelado implementado; no se atribuyen a M0 los requisitos completos del supervisor.
