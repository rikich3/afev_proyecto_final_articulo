# A20 — Análisis reproducible

`analisis/metricas.py` lee archivos JSONL por corrida y genera
`datos/procesados/resumen.csv` junto con el JSON usado por el artículo. Cuenta
episodios físicos de RF-01 por transición a estado inseguro, no ticks. Las
latencias ausentes se conservan como valores nulos y no entran al percentil.

Ejecutar después de disponer de trazas reales:

```sh
python analisis/metricas.py
```

El repositorio no contiene datos de CoppeliaSim todavía; por tanto no se debe
generar ni confirmar un resumen calculado a partir de fixtures de prueba.
