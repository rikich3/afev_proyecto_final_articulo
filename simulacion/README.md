# A07 — Modelo de CoppeliaSim

Abre **`mina_integrada.ttt`** para inspeccionar la escena instrumentada.
`mina_modelada.ttt` es la base geométrica utilizada por el ejecutor. `mina.ttt` conserva
la primera escena de bloques y `inicial.ttt` conserva la escena vacía.
El generador `scripts/crear_escena.lua` reproduce el nuevo modelo en
CoppeliaSim EDU 4.10, usando figuras primitivas y las letras 3D incluidas en
el simulador. No requiere descargar modelos externos.

## Qué incluye

- Faja con banda superior y retorno, juntas visibles, rodillos, soportes,
  guardas laterales, motor y reductor.
- Perímetro de malla que permite ver el interior, postes amarillos y puerta
  con bisagra y tirador. La bisagra permite abrirla 90 grados hacia dentro.
- Dos operarios con extremidades, botas, chaleco reflectante, casco e ID.
- Panel con seccionador giratorio, parada de emergencia, botones identificados,
  dos candados, contacto de potencia y baliza.
- Lector RFID representado visualmente, sensor volumétrico de presencia y
  sensor de barrera en el acceso. Sus volúmenes de detección están ocultos.
- Plataforma, marcas de peligro, señalización y cámara encuadrada.

El script `scripts/planta.lua` actualiza articulaciones, velocidad, candados
y baliza. `scripts/watchdog.lua` mantiene su reloj, la sesión y la última
secuencia de latido. El supervisor envía órdenes por ZeroMQ. El canal de
observación registra posición de los operarios, contacto y velocidad. Los
cruces se representan por cambios de posición y eventos RFID.

## Generar de nuevo

1. Abre `inicial.ttt` y mantén la simulación detenida.
2. En la entrada de comandos de CoppeliaSim (commander), selecciona Lua.
3. Ejecuta esta línea completa; adapta la ruta si moviste el repositorio:

   ```lua
   dofile('/ruta/al/repositorio/simulacion/scripts/crear_escena.lua')
   ```

4. Guarda como `simulacion/mina_modelada.ttt`.

El generador no guarda archivos por su cuenta. Rechaza una escena que ya
contenga `/mina` para evitar duplicar objetos o perder ajustes manuales.
Si falla, retira los objetos de esa ejecución. Organiza las piezas en grupos
plegados; expándelos en el árbol cuando necesites editar sus detalles.

## Objetos de la planta

Las distancias están en metros. La zona abarca x = ±2.20, y = ±1.50;
los operarios comienzan fuera, en y = -2.12. El sensor de presencia cubre esa
zona desde z = 2.46 hacia abajo. La barrera cruza el acceso en y = -1.65,
z = 1.10. La configuración se guarda en los datos personalizados de `/mina`.

| Ruta | Uso |
|---|---|
| `/mina/faja` | Bastidor y conjunto transportador. |
| `/mina/faja/eje_rodillo_1` y `eje_rodillo_2` | Articulaciones de rotación continua. |
| `/mina/puerta` | Articulación de bisagra: 0 cerrada, π/2 abierta hacia dentro. |
| `/mina/operario_1` y `operario_2` | Cuerpos; trasladarlos mueve también sus extremidades y casco. |
| `/mina/sensor_presencia` | Proximidad volumétrica, de manejo explícito. |
| `/mina/sensor_barrera` | Proximidad de tipo rayo, de manejo explícito. |
| `/mina/panel/seccionador` | Articulación con recorrido de 90 grados. |
| `/mina/panel/bloqueo_1` y `bloqueo_2` | Candados personales representados visualmente. |
| `/mina/panel/contacto_potencia` | Indicador visual del estado del contacto simulado. |
| `/mina/lector_rfid` | Lector visual. El script genera los eventos RFID. |

Puedes comprobar el movimiento de la puerta con la simulación detenida:

```lua
sim.setJointPosition(sim.getObject('/mina/puerta'), math.pi / 2)
```

Para cerrarla, cambia `math.pi / 2` por `0`. Reproduce los ensayos con
los comandos del [README principal](../README.md). El script consulta los
sensores de proximidad contra los cuerpos de los avatares. El monitor calcula
ocupación mediante una envolvente horizontal y lee el circuito simulado.
El [rearme inhibido](../datos/evidencias/rearme_inhibido.png) corresponde
a SC-03-a.

```sh
luac -p simulacion/scripts/crear_escena.lua
luac -p simulacion/scripts/planta.lua
luac -p simulacion/scripts/watchdog.lua
```
