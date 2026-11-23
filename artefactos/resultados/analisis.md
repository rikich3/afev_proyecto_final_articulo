# A20. Análisis de la campaña CoppeliaSim

`python -m analisis.campana` verifica hashes de trazas y capturas y
regenera tres CSV y el resumen consumido por Typst. Las estadísticas
se calculan por corrida, agrupadas por caso, campaña y paso. Cada
medida conserva su origen temporal. Se usa rango más próximo para p95.

| Grupo | Corridas | Oráculo cumplido | No evaluable |
|---|---:|---:|---:|
| Piloto | 3 | 3 | 0 |
| Determinista | 41 | 40 | 1 |
| Estocástico | 90 | 90 | 0 |
| Sensibilidad | 4 | 4 | 0 |

Las 138 corridas registraron 3495 observaciones. En SC-09-c, mantener
stepping al cerrar el cliente congeló el reloj. Las otras corridas
SC-09-a con paso nominal abrieron a 120 ms del último latido aceptado
(`n=31` en la campaña principal, p95 y máximo de 120 ms). Con
20 ms de paso, SC-02-a abrió a 40 ms de la orden y la parada siguió
320 ms después. En SC-06-a, con datos caducados a 60 ms de edad, la
sensibilidad dio 30 y 40 ms desde esa caducidad hasta el corte con
pasos de 10 y 20 ms, respectivamente.

Se observaron cero episodios RF-01 en las corridas evaluables dentro
de los supuestos. SC-12-a produjo un episodio deliberado de 40 ms y
SC-12-b uno de al menos 220 ms, censurado al terminar la observación.
En SC-08-a se detectó el contacto pegado y no hubo apertura durante
el ensayo. Ese caso cumple el criterio de diagnóstico y conserva la
clasificación física `no_respondido`.

Los tiempos son de simulación. La dispersión igual a cero en diferentes
semillas de SC-09-a se explica por el reloj discreto y los retardos de
planta fijos. El protocolo declara también metas de cobertura de todos los
eventos M2. Esta campaña contrasta guardas seleccionadas mediante casos
y no estima cobertura exhaustiva de eventos Event-B.
