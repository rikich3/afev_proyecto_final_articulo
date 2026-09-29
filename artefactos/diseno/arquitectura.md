# A05 — Arquitectura mínima

`escenario → CoppeliaSim → snapshot → controlador puro → orden → CoppeliaSim`; un monitor independiente toma verdad física y el registrador conserva ambos canales. Ver `img/arquitectura.svg`.

## Capas

- Event-B/Rodin: C0/M0 (presencia-potencia), C1/M1 (aislamiento, bloqueos y fase), M2 (sensado, comandos y realimentación). Probar inicialización, preservación y refinamiento en cada nivel.
- `software/controlador.py`: `step(estado, snapshot, ordenes) -> (nuevo_estado, salidas, eventos)`, sin llamadas al simulador. En pruebas se usa un adaptador falso.
- `software/adaptador.py`: única dependencia de ZeroMQ. Un cliente y `sim.setStepping(True)`; leer snapshot consistente, evaluar parada/fallo, actualizar estado, escribir salidas, avanzar con `sim.step()` y observar el resultado.
- `simulacion/scripts/watchdog.lua`: se ejecuta en escena independientemente del cliente; al caducar heartbeat revoca permiso y abre contacto nominal. En modo stepping, un cliente caído puede detener los pasos: probar watchdog también con avance autónomo o un supervisor de escena, documentando su reloj. No afirmar respuesta en tiempo real si el reloj simulado está congelado.
- `software/monitores.py`: comprueba invariantes a partir de verdad física; nunca toma la decisión del controlador como oráculo.

## Contrato de entrada y salida

Snapshot inmutable: `tick`, `t_sim_s`, `laser_ocupado`, `barrera_libre`, `puerta_cerrada`, `rfid_eventos`, `sensor_valid`, `sensor_age_s`, `contacto_cerrado`, `seccionador_abierto`, `velocidad_m_s`, `emergencia`. Entradas de usuario: solicitar mantenimiento, aplicar/retirar bloqueo de ID, salir, reset y start. Verdad física adicional sólo para evaluación: `ocupantes_reales`, `potencia_real`, `energia_residual`. Salidas: `orden_contactor`, `permiso_acceso`, `alarma`, `motivo_rechazo`. Unidades SI, booleanos y IDs enumerados, sin floats para fases o identidades.

Prioridad: fallo/emergencia/presencia peligrosa → parada/aislamiento → mantenimiento → retiro de bloqueos → reset → start. Fallo en el mismo snapshot anula reset/start. Start se acepta sólo como nueva orden en un ciclo posterior al reset; una orden mantenida no es un nuevo flanco.

## Secuencia y trazabilidad

Marcha → parada solicitada → aislamiento confirmado → bloqueos aplicados → energía cero verificada → mantenimiento → todos fuera → cada titular retira su bloqueo → cerrar acceso/restablecer circuito → reset manual → listo → start nuevo → marcha. En la demostración ambos operarios aplican sus bloqueos antes del acceso; no admitir nuevos operarios durante mantenimiento en el MVP. En cualquier fase, un fallo lleva a fallo enclavado y reinicia permisos de rearme. No hay salto hacia delante ni reutilización de permisos de un ciclo anterior; sí se permite retroceder a estado seguro.

`artefactos/diseno/correspondencia.csv` registrará variable concreta, abstracción, evento Event-B, función Python, pre/postcondición y test. La traducción a Python es manual y revisada: las pruebas Rodin no demuestran automáticamente ese código.
