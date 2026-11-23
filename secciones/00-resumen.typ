#block[
#set text(size: 9pt, weight: "regular")
#set par(first-line-indent: 1.5em, leading: 0.4em)
_Abstract—_ El mantenimiento de una faja minera requiere impedir el arranque mientras haya personas en la zona de peligro y confirmar el aislamiento antes del ingreso. El objetivo es especificar formalmente un entorno simulado para el enclavamiento de seguridad de una faja minera. Se utiliza Event-B para modelar una zona y dos operarios, NuSMV para analizar el ciclo nominal y CoppeliaSim para evaluar el controlador. Rodin demuestra 272 obligaciones de prueba y NuSMV comprueba cinco propiedades. Los ensayos de planta corroboran el orden de acceso y la inhibición del rearme con un operario dentro. El monitor detecta la coexistencia de ocupación y potencia en dos intrusiones forzadas. La exclusión demostrada depende de los supuestos de acceso controlado y sensado.

_Keywords—Enclavamiento de seguridad, Event-B, verificación formal, faja minera._
]
