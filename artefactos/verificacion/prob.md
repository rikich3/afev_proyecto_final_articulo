# A17. Exploración complementaria de M2 con ProB

Se exportó M2 desde Rodin mediante el traductor del complemento
ProB for Rodin 3.2.3.202611190957. La
[exportación](prob/M2.eventb) contiene los contextos y los refinamientos
que usa M2. Se ejecutó ProB CLI 1.16.1. Los hashes de las fuentes,
la exportación y los logs se conservan en el [manifiesto](prob/manifiesto.json).

| Búsqueda | Estados analizados | Transiciones | Eventos observados, con preparación | Contraejemplos encontrados |
|---|---:|---:|---:|---:|
| Límite de estados | 10 000 | 138 770 | 29 | 0 |
| Alcance acotado | 20 000 | 377 178 | 35 | 0 |

En ambas ejecuciones se alcanzó el límite de estados. ProB avisó de
enumeración acotada para parámetros enteros como la secuencia de latido.
La segunda exploración observó el ingreso, la salida y la liberación.
`Restablecer` quedó sin visitar en su alcance. Los conteos de cobertura
incluyen los eventos de inicialización y preparación reportados por ProB.
Los resultados se circunscriben a las búsquedas y complementan la prueba
inductiva de Rodin. NuSMV verifica el ciclo nominal en su modelo finito.

## Reproducción

Abre el modelo en Rodin con el complemento instalado y exporta M2
mediante **ProB Classic → Export for use in ProB Classic**. También puedes
ejecutar directamente el archivo conservado, desde este directorio:

```sh
probcli prob/M2.eventb -bf -mc 10000 -global_time_out 30000 \
  -p MAXINT 12 -p MAX_OPERATIONS 50 -p MAX_INITIALISATIONS 10 -c
probcli prob/M2.eventb -bf -mc 20000 -global_time_out 30000 \
  -p MAXINT 12 -p MAX_OPERATIONS 50 -p MAX_INITIALISATIONS 10 \
  -scope 'sesion <= 1 & secuencia_heartbeat <= 2 & edad_sensor <= 4 & edad_heartbeat <= 6 & edad_apertura <= 4' -c
```

[Documentación oficial de exportación](https://prob.hhu.de/w/index.php?title=Tutorial_Rodin_Exporting)
