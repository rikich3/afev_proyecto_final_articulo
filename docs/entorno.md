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
3. Crear un entorno virtual, activarlo e instalar `requirements.txt`.
4. Consultar en el [README](../README.md) los comandos para verificar, ejecutar y analizar.
5. Compilar con `typst compile main.typ articulo.pdf` y comprobar la estructura con `python herramientas/verificar.py`.

## Entorno utilizado para la campaña

Se ejecutó CoppeliaSim EDU 4.10.0 rev0 en Linux x86_64 con Python 3.12.11,
cliente ZeroMQ 2.0.4 y paso nominal de 20 ms. La sensibilidad volvió a
ejecutar dos casos a 10 y 20 ms. `requirements.txt` fija las dependencias
directas. El simulador aplica un modelo discreto de desaceleración en Lua.
Los manifiestos conservan la versión reportada por CoppeliaSim, el sistema,
los parámetros y las huellas de la escena, el catálogo y el código.

El instalador Ubuntu 24.04 usado en Arch necesitó cargar `libsodium.so.23`
para el complemento ZeroMQ. En una instalación compatible se utiliza la
biblioteca provista por el sistema. Para la campaña se restringió el enlace
del servidor a `127.0.0.1`.
