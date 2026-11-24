# A26. Reproducción de la entrega

Desde la raíz del repositorio:

1. Instalar las dependencias y abrir CoppeliaSim según el README.
2. Reproducir M0–M2 con `herramientas/verificar_rodin.py --replay`. El
   resultado registrado abarca 272 obligaciones en un espacio nuevo.
3. Ejecutar `herramientas/verificar_nusmv.py` con NuSMV 2.6.0 para comprobar
   cinco propiedades, dos controles negativos y 119 estados alcanzables.
4. Reproducir las búsquedas limitadas de M2 con
   [las instrucciones de ProB](../verificacion/prob.md).
5. Ejecutar la suite Python con `python -m pytest -q`.
6. Ejecutar el grupo `todo` en un directorio vacío, con las capturas en
   `evidencias/` dentro de ese directorio. Analizar con `python -m analisis.campana`.
   Comparar conteos, clasificación, tiempos y estado de planta. Los IDs de
   corrida y los tiempos de pared cambian en una reproducción.
7. Compilar `typst compile main.typ articulo.pdf` con Times New Roman
   disponible. Si la fuente está en un directorio aparte, añadir
   `--font-path /ruta/a/fuentes`. Ejecutar `python herramientas/verificar.py`
   y comprobar las siete páginas con `pdfinfo articulo.pdf`. Confirmar la
   fuente incrustada con `pdffonts articulo.pdf`.
8. Comprobar las huellas de la distribución con
   `sha256sum -c artefactos/entrega/manifest.sha256`.

Se reprodujo la campaña localmente tras corregir las comprobaciones del
ejecutor. La segunda ejecución conserva el conjunto final de 138 corridas.
La reproducción por otro integrante requiere su propio entorno y registro.
