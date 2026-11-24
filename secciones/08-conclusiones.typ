= Conclusiones

La especificación Event-B conserva la exclusión entre ocupación y potencia bajo el supuesto de acceso controlado. Rodin reprodujo 272 obligaciones en M0–M2. Los refinamientos añadieron bloqueos personales, rearme y respuesta a pérdida de confirmaciones. NuSMV comprobó tres propiedades de seguridad y dos de alcanzabilidad en el ciclo nominal.

En CoppeliaSim, la salida de un operario conservó el enclavamiento mientras el segundo permanecía dentro. El watchdog revocó el mando ante pérdida de latidos y el monitor identificó presencia con potencia en las dos intrusiones forzadas. El ensayo de contacto pegado mostró que el diagnóstico por realimentación no equivale a apertura física del circuito simulado.

Una ampliación a más zonas u operarios requiere revisar las hipótesis, regenerar las obligaciones y repetir la exploración. Para extender el alcance experimental, conviene parametrizar la desaceleración a partir de mediciones de planta e incorporar fallos de puerta y seccionador.
