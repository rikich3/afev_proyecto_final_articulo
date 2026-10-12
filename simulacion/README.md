# A07 — Modelo de CoppeliaSim

Abre **`mina_modelada.ttt`** para ver la versión mejorada. `mina.ttt` conserva
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

Los colores, candados y luces son representaciones geométricas; aún no
indican estados eléctricos ni bloqueos activos. Play no ejecuta una secuencia
de seguridad. Las formas son estáticas, sin respuesta dinámica a colisiones.

## Generar de nuevo

1. Abre `inicial.ttt` y mantén la simulación detenida.
2. En la entrada de comandos de CoppeliaSim (commander), selecciona Lua.
3. Ejecuta esta línea completa; adapta la ruta si moviste el repositorio:

   ```lua
   dofile('/home/leeeen/UNSA/SEXTO_SEMESTRE/AFVE/p_final/afev_proyecto_final_articulo/simulacion/scripts/crear_escena.lua')
   ```

4. Guarda como `simulacion/mina_modelada.ttt`.

El generador no guarda archivos por su cuenta. Rechaza una escena que ya
contenga `/mina` para evitar duplicar objetos o perder ajustes manuales.
Si falla, retira los objetos de esa ejecución. Organiza las piezas en grupos
plegados; expándelos en el árbol cuando necesites editar sus detalles.

## Referencias para integrar el comportamiento

Las distancias están en metros. La zona abarca x = ±2.20, y = ±1.50;
los operarios comienzan fuera, en y = -2.12. El sensor de presencia cubre esa
zona desde z = 2.46 hacia abajo. La barrera cruza el acceso en y = -1.65,
z = 1.10. La configuración se guarda en los datos personalizados de `/mina`.

| Ruta | Uso futuro |
|---|---|
| `/mina/faja` | Bastidor y conjunto transportador. |
| `/mina/faja/eje_rodillo_1` y `eje_rodillo_2` | Articulaciones de rotación continua. |
| `/mina/puerta` | Articulación de bisagra: 0 cerrada, π/2 abierta hacia dentro. |
| `/mina/operario_1` y `operario_2` | Cuerpos; trasladarlos mueve también sus extremidades y casco. |
| `/mina/sensor_presencia` | Proximidad volumétrica, de manejo explícito. |
| `/mina/sensor_barrera` | Proximidad de tipo rayo, de manejo explícito. |
| `/mina/panel/seccionador` | Articulación con recorrido de 90 grados. |
| `/mina/panel/bloqueo_1` y `bloqueo_2` | Candados personales representados visualmente. |
| `/mina/panel/contacto_potencia` | Representación del contacto; falta realimentación física simulada. |
| `/mina/lector_rfid` | Representación del lector; faltan eventos de identidad. |

Puedes comprobar el movimiento de la puerta con la simulación detenida:

```lua
sim.setJointPosition(sim.getObject('/mina/puerta'), math.pi / 2)
```

Para cerrarla, cambia `math.pi / 2` por `0`. Esta prueba mueve la geometría;
la autorización de acceso aún no está implementada.

Los sensores deben evaluarse contra los operarios, por ejemplo mediante
`sim.checkProximitySensor(sensor, operario)`. No interpretes la lectura sin
configurar como ausencia de personas: el volumen también contiene la máquina
y el suelo. La integración final deberá considerar el cuerpo completo,
validez de datos, marcas temporales y ocupación física independiente.

## Comprobaciones y pendientes

Se comprobó en CoppeliaSim EDU 4.10.0 rev0: generación, rechazo de duplicados,
detección individual de ambos operarios fuera/dentro de la zona y cruzando el
rayo, apertura de puerta hacia dentro y guardado/reapertura. Los operarios y
la puerta se restauraron antes de guardar. La revisión visual de la versión
mejorada requiere abrirla en la interfaz; la prueba headless no verifica el
renderizado ni el comportamiento del controlador.

También se comprueba sintaxis con:

```sh
luac -p simulacion/scripts/crear_escena.lua
python herramientas/verificar.py
```

El repositorio no tiene un formateador Lua ni hooks de formato configurados.

Para cerrar A07 quedan la potencia, aislamiento y energía residual simulados,
la conexión de sensores e identidades al contrato A05, el watchdog local y sus
pruebas. Las articulaciones preparan la geometría para esa integración; aún
no impiden intrusiones o arranques incompatibles. El controlador Python de
A09/A11 también sigue pendiente.
