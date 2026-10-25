# A18 — Integración y fallos

Las pruebas `tests/test_integracion.py` ejecutan el ciclo adquirir → decidir →
actuar → observar usando `PlantaDeterminista`. Comprueban el arranque seguro,
el corte por watchdog y que un contacto pegado se mantiene como estado físico
observable. Esta planta es un doble local: no abre CoppeliaSim ni produce
evidencia de latencia o comportamiento de la escena.

Para cerrar A18 con CoppeliaSim se debe reemplazar el doble por el adaptador
ZeroMQ, conservar las mismas pruebas y registrar trazas de SC-07, SC-08, SC-09
y SC-11. La prueba de watchdog requiere que el reloj de la escena avance aun
cuando el cliente deje de enviar heartbeat.
