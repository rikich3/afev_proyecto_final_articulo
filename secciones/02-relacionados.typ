#import "/estilo.typ": recurso
= Trabajos relacionados

Abrial y colaboradores presentan Rodin como una plataforma abierta para modelado y razonamiento en Event-B @rodin. Su enfoque proporciona la base metodológica para desarrollar especificaciones por refinamiento y analizar obligaciones de prueba. En este proyecto se aplica esa organización a la exclusión de potencia y a las autorizaciones de mantenimiento.

Leuschel y Butler describen ProB como un verificador de modelos para B @prob; la documentación de la herramienta incluye soporte para Event-B @prob-eventb. La exploración permite buscar estados problemáticos y conservar contraejemplos, complementando el razonamiento deductivo. El alcance de una exploración depende de los dominios y límites configurados y debe informarse junto al resultado.

Rohmer y colaboradores presentan el marco de simulación V-REP @vrep, antecedente de CoppeliaSim. En el banco propuesto, la API ZeroMQ vincula el simulador con un controlador externo y permite coordinar los pasos de ejecución @zmq. La simulación facilita observar secuencias y tiempos bajo condiciones repetibles; no sustituye la prueba de invariantes del modelo formal.

En un dominio próximo, Limbree y colaboradores estudian enclavamientos ferroviarios mediante descomposición y contratos con OCRA @ocra2016. Su trabajo aborda el crecimiento del espacio de estados al verificar estaciones mayores. La comparación orienta una futura extensión por zonas; el presente prototipo mantiene una sola zona y utiliza refinamiento Event-B, sin implementar verificación composicional con OCRA.

Cappart y colaboradores analizan enclavamientos ferroviarios mediante verificación estadística de modelos, considerando seguridad y disponibilidad @cappart2017. Su enfoque permite evaluar escenarios con confianza parametrizable sin reclamar exhaustividad. En este proyecto las corridas de CoppeliaSim constituyen evaluación experimental; no se presentan como verificación estadística de modelos, pues no se ha implementado ese procedimiento inferencial.

Estas referencias aportan fundamentos y dos comparaciones de enclavamiento en otro dominio, pero no establecen por sí mismas una revisión exhaustiva de aplicaciones mineras. La matriz de revisión #recurso("A04", "artefactos/literatura/revision.md") organiza la ampliación con casos comparables por propiedad, método y evidencia. La revisión final debe sustentar las diferencias del caso de estudio sin inferir ausencia de trabajos a partir de una búsqueda limitada.
