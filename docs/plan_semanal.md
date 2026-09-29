# Plan de siete semanas y cuatro integrantes

Presupuesto inicial: **8 h por integrante y semana**, 56 h por persona y **224 h de equipo**. Cada paquete A tiene 6 h de producción, 1 h de revisión cruzada y 1 h de coordinación/documentación; no se agregan reuniones fuera del presupuesto. Es una estimación: registrar horas reales y redistribuir si una desviación supera 2 h, conservando el objetivo de carga por persona. Los auxiliares G se incluyen en los paquetes, sin carga oculta.

I1 coordina integración y requisitos; I2 modelos/pruebas; I3 simulación; I4 experimentos y edición. Todos implementan, revisan y escriben; I1 realiza M2 y ProB para compartir la carga formal. Revisión cíclica: I2 revisa I1, I3 revisa I2, I4 revisa I3 e I1 revisa I4. Las pruebas formales reciben además lectura técnica de I1/I2 durante su hora de coordinación.

| Semana | I1 (8 h) | I2 (8 h) | I3 (8 h) | I4 (8 h) | Hito de salida |
|---|---|---|---|---|---|
| 1 | **A01** Alcance y requisitos | **A02** Peligros y supuestos | **A03** Entorno reproducible | **A04** Revisión bibliográfica | Alcance acordado, supuestos explícitos y herramientas accesibles. |
| 2 | **A05** Arquitectura y contrato | **A06** Modelo abstracto M0 | **A07** Escena mínima | **A08** Protocolo y escenarios | Arquitectura y M0 revisados; escena estática; protocolo fijado. |
| 3 | **A09** Controlador discreto | **A10** Refinamiento M1 LOTO | **A11** Adaptador CoppeliaSim | **A12** Pruebas del controlador | Ciclo nominal simulado; bloqueos individuales y pruebas unitarias. |
| 4 | **A13** Refinamiento M2 e interfaz | **A14** Evidencia de pruebas formales | **A15** Instrumentación y ejecutor | **A16** Monitores y trazabilidad | Instrumentación completa; M2 y primera auditoría de pruebas. |
| 5 | **A17** Exploración ProB | **A18** Integración y fallos | **A19** Datos crudos y manifiestos | **A20** Análisis reproducible | Experimentos congelados y ejecutados; resultados calculables. |
| 6 | **A21** Problema y fundamentos del artículo | **A22** Propuesta y formalización del artículo | **A23** Figuras y evidencia visual | **A24** Evaluación y discusión del artículo | Borrador completo con figuras y cifras derivadas de datos reales. |
| 7 | **A25** Auditoría de requisitos y fuentes | **A26** Reproducción independiente | **A27** Demostración y entrega técnica | **A28** Artículo final e integración editorial | Reproducción por otro integrante y entrega revisada. |

## Dependencias y trabajo diario

1. Semana 1: A01/A02 cierran juntos requisitos y supuestos; A03 prueba instalación y A04 registra fuentes. I1 mantiene G01/G02; I2 G03; I3 G04.
2. Semana 2: A05 publica primero el contrato; A06/A07/A08 se desarrollan usando ese contrato. El simulador no bloquea el modelo abstracto.
3. Semana 3: A09 y A11 comparten el contrato, probando primero con un adaptador falso; A12 consume las mismas entradas. A10 refina A06.
4. Semana 4: A13 depende de A10 y del contrato de A11; A14 audita primero M0/M1 y luego M2. A15/A16 fijan esquema y monitores antes de generar datos.
5. Semana 5: A17 usa modelos estables; A18 verifica el conjunto antes de congelar A19. A20 prepara cálculos con una corrida piloto y procesa los datos definitivos al cierre.
6. Semana 6: A21/A22 usan evidencias ya revisadas; A23 exporta gráficos desde A20; A24 integra cifras sin edición manual. Cada autor trabaja en sus archivos de sección.
7. Semana 7: A25 y A26 detectan inconsistencias; A27 registra la demostración de la versión congelada; A28 integra correcciones, G05 y PDF. Reejecutar solamente lo afectado por cambios.

## Equidad y contingencias

| Integrante | Paquetes | Producción | Revisión | Coordinación | Total |
|---|---:|---:|---:|---:|---:|
| I1 | 7 | 42 h | 7 h | 7 h | 56 h |
| I2 | 7 | 42 h | 7 h | 7 h | 56 h |
| I3 | 7 | 42 h | 7 h | 7 h | 56 h |
| I4 | 7 | 42 h | 7 h | 7 h | 56 h |

Si hay retraso, reducir decoración 3D, número de variantes de ruido y análisis opcionales; conservar una zona, dos operarios, M0/M1/M2, monitor físico independiente, escenarios críticos y reproducción. No compensar retrasos dejando obligaciones pendientes como si estuvieran demostradas. No incluir ROS, visión por cámara, hardware real, múltiples máquinas ni generación automática de código en el alcance mínimo. La redacción empieza con esta base y se actualiza semanalmente, aunque su revisión final figure en las semanas 6–7.
