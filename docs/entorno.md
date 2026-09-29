# A03 — Entorno gratuito y reproducible

| Herramienta | Uso mínimo | Fuente oficial |
|---|---|---|
| CoppeliaSim EDU | Planta, sensores y fallos simulados. Gratuito para uso educativo elegible; no confundir con software sin restricciones de licencia. | https://coppeliarobotics.com/eduRegister |
| Rodin / Event-B | Contextos, máquinas, refinamiento y obligaciones de prueba. | https://wiki.event-b.org/index.php/Main_Page |
| ProB | Animación y exploración de estados Event-B; código bajo EPL. | https://prob.hhu.de/w/index.php?title=ProB_for_Event-B ; https://prob.hhu.de/w/index.php?title=ProBLicence |
| Python + cliente ZeroMQ | Controlador externo; un proceso. | https://manual.coppeliarobotics.com/en/zmqRemoteApiOverview.htm |
| pytest | Pruebas parametrizadas de transiciones y escenarios. | https://docs.pytest.org/en/stable/getting-started.html |
| Hypothesis (opcional) | Secuencias aleatorias con reducción de contraejemplos. | https://hypothesis.readthedocs.io/en/latest/stateful.html |
| Matplotlib | Gráficos SVG a partir de CSV, sin edición manual de cifras. | https://matplotlib.org/stable/users/explain/quick_start.html |
| Typst CLI + Liberation Serif | Compilación local gratuita del artículo. | https://typst.app/docs/ |

Recomendación: Python estándar (`dataclasses`, `enum`, `json`, `csv`, `time`, `hashlib`) para la mayor parte del software. Añadir sólo cliente CoppeliaSim, pytest y Matplotlib; Hypothesis después del ciclo mínimo. No se requiere ROS, servidor web, base de datos, MATLAB, LabVIEW ni PLC comercial. No introducir un segundo formalismo como Alloy sin una pregunta concreta que Event-B/ProB no resuelvan.

1. Instalar Rodin y ProB compatibles entre sí; crear proyecto de prueba y conservar versiones exactas de ambos y del JRE utilizado. Elegir una versión estable disponible al comenzar, no asumir que la última combinación es compatible.
2. Instalar CoppeliaSim EDU y verificar acceso educativo. Guardar versión/build, motor físico, paso, SO y unidades. Probar cliente de la documentación oficial antes de construir escena.
3. Crear entorno: `python -m venv .venv`, activarlo e instalar `coppeliasim-zmqremoteapi-client pytest matplotlib`. Una vez probado el piloto, producir `requirements.txt` con versiones exactas; no se proporciona un lock ficticiamente probado.
4. Registrar commits, hashes de escena/modelos, configuración ProB, CPU/RAM y semillas en cada manifiesto. Publicar el entorno usado, no datos personales innecesarios.
5. Comandos previstos después de implementar: `python -m pytest`, `python experimentos/ejecutar.py --config experimentos/escenarios.json`, `python analisis/metricas.py`, `python analisis/figuras.py`. Son el contrato de CLI a implementar, todavía no comandos disponibles.
6. Comandos disponibles para la base: `typst compile main.typ articulo.pdf` y `python herramientas/verificar.py`.

La base editorial se verificará con la versión local de Typst; la escena y los modelos no se consideran instalados o ejecutados por esa comprobación.
