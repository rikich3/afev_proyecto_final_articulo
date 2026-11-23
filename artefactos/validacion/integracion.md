# A18. Integración del supervisor con CoppeliaSim

La escena de cada corrida se carga desde `mina_modelada.ttt`. En los casos
de marcha y mantenimiento, el ejecutor alcanza la precondición por órdenes
y espera confirmaciones de planta. Se usa el mismo controlador Python que
ejercita la suite local. Las corridas instrumentadas usan CoppeliaSim real
por ZeroMQ. El resumen y las filas por corrida se generan desde los datos y
manifiestos en `datos/`.

| Caso | Estímulo y observación registrada |
|---|---|
| SC-02-a | Orden de mantenimiento en marcha. La apertura antecede a parada, aislamiento, bloqueos y acceso. |
| SC-03-a | Sale el operario 1 y el 2 queda dentro. Se conserva potencia apagada y ambos bloqueos ante retiro de candado, reset y start. |
| SC-07-b | Las retransmisiones conservan el origen de la señal. El fallo se enclava a 60 ms de antigüedad. |
| SC-08-a | El contacto pegado permanece cerrado. Se registra `CONTACTO_NO_ABRE` y la entrada sigue denegada. La latencia de apertura es nula. |
| SC-09-a | Se cierra el socket de control con el reloj autónomo. El observador consulta el registro de la escena. La caducidad se observa a 100 ms y la apertura a 120 ms de último latido. |
| SC-09-b | Repetir la secuencia no renueva el latido. Actúa el mismo reloj local. |
| SC-09-c | Se cierra el socket en modo stepping y el reloj se detiene. La latencia de corte queda sin evaluar. |
| SC-11-a/b/c | El cambio de sesión invalida el latido anterior y revoca mando y rearme. Con los dos operarios en mantenimiento, se preservan los bloqueos. Se prueba también confirmación desconocida y evacuación. |
| SC-12-a/b | Una intrusión deliberada rompe el supuesto de acceso controlado. El monitor detecta presencia y potencia, incluso bajo la supresión deliberada de lecturas del controlador. |
| SC-13-b | Movimiento residual persistente tras la apertura inhibe aislamiento y acceso. Se registra fallo al vencer el plazo de parada. |

El [manifiesto índice](../../datos/manifest.csv) identifica los archivos
de cada caso. Las capturas [de mantenimiento](../../datos/evidencias/mantenimiento_ambos.png)
y [de rearme inhibido](../../datos/evidencias/rearme_inhibido.png) se
vinculan por hash y tick a SC-02-a y SC-03-a deterministas.

Durante la preparación se corrigieron tres supuestos del ejecutor.
El bloqueo debe esperar el reconocimiento por el supervisor del seccionador
abierto. El retardo requiere llenar antes el historial de muestras. Los ciclos
de jitter previos al estímulo pertenecen a la preparación. Los límites
temporales y los criterios de seguridad conservaron sus valores.
SC-13-b se alineó con la guarda de parada confirmada de `Aislar` en M2.
