# Convención de commits y versiones

Cada commit reúne un cambio coherente que se puede revisar por separado. Su
asunto sigue la forma `tipo(alcance): descripción`, en español, en presente y
sin punto final. El alcance identifica el entregable o componente principal.

| Tipo | Uso |
|---|---|
| `feat` | Modelo, simulación o capacidad nueva. |
| `fix` | Corrección de un error comprobado. |
| `data` | Trazas, manifiestos, capturas o resultados de una campaña. |
| `test` | Pruebas u oráculos sin cambio funcional. |
| `docs` | Artículo, figuras, guías y trazabilidad editorial. |
| `chore` | Mantenimiento del repositorio o sus herramientas. |

Alcances habituales: `event-b`, `verificacion`, `simulacion`, `campana`,
`articulo` y `repo`. Ejemplos:

```text
feat(event-b): completa refinamientos M1 y M2 con pruebas Rodin
data(campana): registra 138 corridas y resultados reproducibles
docs(articulo): integra modelo y resultados en manuscrito de siete paginas
fix(simulacion): corrige la inhibicion del rearme tras intrusion
```

Si cambia un contrato de datos o un paso de reproducción de forma
incompatible, se usa `tipo(alcance)!:` y se explica la migración en el cuerpo
del commit. El cuerpo también indica cómo se verificó un cambio cuando el
resultado no es evidente por los archivos modificados. No se reescribe el
historial compartido: las correcciones posteriores llevan su propio commit.

Las etiquetas siguen `vMAJOR.MINOR.PATCH`:

- `MAJOR`: cambia el alcance o el método central del trabajo.
- `MINOR`: añade un entregable verificable o una campaña nueva.
- `PATCH`: corrige texto, figuras, código o datos sin ampliar el alcance.

Las versiones `0.x` son candidatas durante la revisión académica. Una
etiqueta solo se crea después de compilar el PDF, ejecutar las verificaciones
disponibles y actualizar `artefactos/entrega/manifest.sha256`. `v1.0.0`
identificará la entrega aceptada por el equipo y la docente; una etiqueta no
equivale por sí sola a esa aceptación. Para inspeccionar una versión:

```sh
git log --oneline --decorate
git show v0.9.0
sha256sum -c artefactos/entrega/manifest.sha256
```
