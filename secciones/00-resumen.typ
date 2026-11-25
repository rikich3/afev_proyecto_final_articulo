#block[
#set text(size: 9pt, weight: "bold")
#set par(first-line-indent: (amount: 10pt, all: true), leading: 0.44em, spacing: 0.44em)
_Resumen_—Durante el mantenimiento de una faja minera, el ingreso exige confirmar el aislamiento y el arranque debe quedar inhibido mientras haya operarios en la zona de peligro. El objetivo fue especificar formalmente el enclavamiento de seguridad en un entorno simulado. Se modelaron una zona y dos operarios mediante refinamientos en Event-B, se verificó el ciclo nominal con NuSMV y se ensayó el controlador en CoppeliaSim con un monitor independiente. Rodin demostró 272 obligaciones de prueba y NuSMV verificó cinco propiedades temporales. En la simulación, 134 de 135 corridas cumplieron el criterio previsto y en una no se pudo medir el tiempo de corte. El monitor detectó dos intrusiones con potencia activa al forzar el ingreso. Bajo los supuestos de acceso controlado y sensado confiable, la especificación preservó la exclusión entre ocupación y potencia y la simulación corroboró la inhibición del rearme con un operario dentro.

_Palabras clave_—Enclavamiento de seguridad, Event-B, faja minera, simulación, verificación de modelos.
]
