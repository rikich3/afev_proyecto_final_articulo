# Model Checking del enclavamiento en NuSMV

La parte 2 admite NuSMV o UPPAAL. Se eligió NuSMV 2.6.0, disponible en el
entorno local. Este modelo finito especifica una zona y dos operarios y se
comprueba con BDD. La correspondencia con los refinamientos Event-B y con la
implementación Python sigue pendiente de revisión.

## Reproducción

Con NuSMV en PATH:

```sh
python herramientas/verificar_nusmv.py
```

En el entorno usado:

```sh
python herramientas/verificar_nusmv.py --bin /home/sauls/Descargas/NuSMV-2.6.0-Linux/bin/NuSMV
```

El script conserva logs y hashes de modelo, binario y logs en
`artefactos/verificacion/nusmv/`. La prueba de intrusión se ejecuta sobre una
copia temporal generada retirando únicamente la guarda de ingreso del primer
operario. El log incluye el contraejemplo de MC01.

El modelo, `ejecucion.log`, `intrusion.log` y `manifiesto.json` conservan
las cinco propiedades, el control negativo, el contraejemplo y los hashes
para revisión. Esta evidencia técnica permanece en el repositorio y no
se incorpora como anexo al PDF del artículo.

El diagrama `transiciones.dot` resume los cambios de fase, las guardas y las
acciones principales. Los eventos inválidos conservan el estado. El archivo
SMV contiene las actualizaciones completas. Cada transición procesa un evento.
Los ensayos de órdenes simultáneas pertenecen a la validación del controlador.

## Propiedades

| ID | Fórmula | Interpretación | Resultado esperado |
|---|---|---|---|
| MC01 | `G !(ocupada & potencia)` | Exclusión física abstracta, bajo acceso controlado | true |
| MC02 | `G (permiso_acceso -> (aislado & energia_cero & ambos_bloqueos))` | Permiso compatible con aislamiento, parada y bloqueos | true |
| MC03 | `G (bloqueada -> !potencia)` | Un bloqueo restante impide energizar | true |
| MC04 | `EF (fase = MANTENIMIENTO & dentro1 & dentro2)` | Existe un recorrido de ingreso de ambos operarios | true |
| MC05 | `EF (fase = LISTO & ciclo_completado)` | Existe un ciclo que ingresa a ambos, los evacua y rearma | true |
| Control negativo | `G !potencia` | Nunca se energiza | false |

`G` es el operador LTL de cumplimiento global exigido en la consigna. `EF`
es una comprobación CTL adicional de alcanzabilidad. El entorno puede esperar
indefinidamente. Las consultas existenciales comprueban posibilidad de completar
el ciclo, sin garantizar progreso universal. El permiso es una variable de
estado actualizada por transiciones, de modo que MC02 comprueba su conservación.

## Alcance

Se separan potencia y movimiento residual. La apertura del contacto y la parada
se confirman en transiciones diferentes. No se representan segundos, plazos de
respuesta ni física de motores. La sesión de comunicación, el reinicio con estado
persistente y los sensores defectuosos requieren extensiones o pruebas separadas.
Puerta y seccionador nominales impiden ingreso sin autorización. La copia de
intrusión explora la ruptura de esa hipótesis. Emergencia revoca el permiso y
mantiene ocupantes y bloqueos. La recuperación con bloqueos pendientes puede
quedar a la espera de un procedimiento adicional y no se afirma progreso desde
cada estado de fallo.

El modelo nominal verificado alcanza 119 estados y tiene diámetro 36 en la
versión registrada. Los hashes identifican el modelo al que corresponden.
