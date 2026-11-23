# Verificación nativa de M1

C1 extiende C0 con diez fases distintas. M1 refina M0, conserva P/U e incorpora
L, fase y confirmaciones abstractas de aislamiento, energía cero, puerta y
permiso. La variable intervencion distingue parada normal y mantenimiento.
El modelo tiene 18 eventos. Rodin 3.10 generó 79 obligaciones de M1, todas
cerradas. M0 conserva cinco obligaciones demostradas. Los logs informan
84 comprobadas en total. C1 no generó obligaciones no triviales.

## Reproducción

Requiere Rodin 3.10 y JDK 21. El script copia la instalación y el proyecto a un
directorio temporal. Compila una aplicación headless de verificación contra
las API de Rodin y conserva fuentes y árboles nativos del proyecto.

```sh
python herramientas/verificar_rodin.py --rodin /ruta/a/rodin --java-home /ruta/al/jdk21
python herramientas/verificar_rodin.py --rodin /ruta/a/rodin --java-home /ruta/al/jdk21 --replay
```

La demostración utiliza simplificación automática y PP no restringido en las
obligaciones abiertas. El modo replay crea árboles vacíos e intenta reproducir
los esqueletos guardados. No invoca PP como alternativa en ese modo. Si un árbol
no se reproduce, termina con error. Ambos modos verifican que las pruebas no
estén rotas y tengan confianza 1000.

`verificacion_m1.json` y `reproduccion_m1.json` identifican las fuentes y logs
por SHA256. `estados.csv` registra las 84 obligaciones. Los .bpo/.bps son
regenerables. Los árboles .bpr y las fuentes .buc/.bum del proyecto son la
base importable. El artículo informa los conteos por máquina.

## Interpretación de las propiedades

- RF-01 se conserva por refinamiento de Energizar, Cortar, Ingresar y Salir.
  SolicitarMantenimiento también refina Cortar. La guarda P={z} explicita la
  instancia de una sola zona y permite que el corte la desenergice por completo.
- INV_02 prohíbe energizar una zona con un bloqueo.
- INV_03 exige permiso compatible con fase, corte, aislamiento, parada,
  ambos bloqueos y puerta abierta.
- INV_04 restringe la potencia a marcha, con zona vacía, sin bloqueos y puerta
  cerrada. inv_listo establece las condiciones de reset antes de Energizar.
- inv_titulares conserva bloqueos para todos los ocupantes identificados.
  RetirarBloqueo exige solicitante=o, titular fuera y fase LIBERACION.
- FinalizarMantenimiento exige U vacío. Cada retiro y el restablecimiento
  mantienen la potencia apagada. Reset alcanza LISTO y Energizar es otro evento.

## Alcance de la demostración

Las confirmaciones de M1 son abstractas y confiables bajo los supuestos S1–S5.
Puerta, sensores, temporización, contacto pegado y reinicio físico se abordan
en M2 y en la validación de planta. La identidad del solicitante sigue S2.

Todos los eventos son ordinarios. Los eventos añadidos preservan P/U y refinan
skip. La evidencia establece refinamiento y seguridad, sin una demostración de
convergencia o de progreso universal. La alcanzabilidad existencial del modelo
NuSMV es evidencia separada y su correspondencia completa con M1 debe revisarse.
No hay un evento vacío añadido para aparentar ausencia de deadlocks.
