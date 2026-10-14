# 2. Roadmap de despliegue por horizontes

La autonomía no se enciende de un día para otro: **se gana por etapas**. Cada fase le da al sistema un poco más de libertad solo después de demostrar, con números, que la anterior funciona. En todas las fases rige el **semáforo de riesgo**: lo rojo (una urgencia médica, un reclamo o amenaza legal, un tema de dinero, un pedido de historia clínica) **nunca** lo resuelve el sistema; lo pasa a una persona y, ante una urgencia, indica de inmediato la guardia 24 h.

| | Fase 0 · Modo sombra | Fase 1 · Piloto de solo lectura | Fase 2 · Escritura controlada | Fase 3 · Autonomía supervisada |
|---|---|---|---|---|
| **Horizonte** | Días 10 a 24 (después de una semana de preparación) | Días 25 a 45 | Días 46 a 75 | Desde el día 76 |
| **Qué puede hacer** | Leer los pedidos reales y **proponer** la respuesta o la acción | Responder **consultas informativas** (con la fuente citada) y decirle al paciente qué turnos tiene | **Proponer** altas, cambios y cancelaciones de turnos y la actualización del CRM | Resolver solo lo **verde** (consultas, altas con datos completos, confirmaciones) y lo **amarillo** (reprogramar, cancelar) |
| **Qué tiene prohibido** | Contestarle al paciente; escribir en la agenda o el CRM | Crear, cambiar o cancelar turnos; escribir en el CRM (deriva a una persona) | Ejecutar una acción sin aprobación humana; tocar dinero o historia clínica | Salirse de las políticas: todo lo rojo se congela y pasa a una persona |
| **Quién valida** | La coordinadora de la Central revisa cada propuesta en Slack | El Supervisor de calidad revisa cada respuesta; la coordinadora audita una muestra diaria del 10 % | Una administrativa aprueba o edita cada acción con un botón en Slack | El Supervisor de calidad en cada respuesta informativa; auditoría diaria de lo amarillo; revisión semanal de indicadores |
| **Qué riesgo mitiga** | Errores de criterio: se detectan antes de que lleguen a un paciente | Información incorrecta, sin ningún riesgo sobre los datos de la clínica | Turnos mal cargados o duplicados: ninguna acción se ejecuta sin una persona | El costo y la demora de la atención manual, con vuelta atrás si bajan los indicadores |
| **Criterio de salida** | 200 casos reales con ≥ 90 % de propuestas aceptadas sin cambios, 100 % de casos rojos detectados y registro completo de cada caso | ≥ 95 % de respuestas correctas (Supervisor + muestra humana), ninguna respuesta inventada y 100 % de escalados correctos | ≥ 95 % de acciones aprobadas sin editar, < 1 % de turnos con datos incompletos y ningún duplicado | Se sostiene mientras los indicadores no bajen; si caen, vuelve a la Fase 2 |

**El freno de mano.** En cualquier fase, la coordinadora puede pausar el sistema desde Slack. Los pedidos pasan a la atención humana con su historial y no se pierde ninguno.

## Estrategia de respaldo (fallback)

Qué pasa cuando algo falla, para que el paciente nunca quede sin respuesta y la agenda nunca quede a medias:

| Situación | Qué hace el sistema |
|---|---|
| El servicio de inteligencia artificial tarda o no responde | Reintenta una vez. Si vuelve a fallar, le dice al paciente "Estamos con demoras: te respondemos en unos minutos", avisa al equipo en Slack con el código del caso y la consulta pasa a la atención humana |
| El Supervisor de calidad no puede revisar una respuesta | La respuesta **no sale** sin revisión: pasa a una persona por Slack |
| El Supervisor rechaza una respuesta | Se corrige y se vuelve a revisar, como máximo dos veces; si sigue mal, pasa a una persona |
| Falla la agenda o el CRM a mitad de un registro | El turno no queda a medias: el código de seguimiento evita registrar dos veces el mismo pedido, y el caso queda marcado para revisión |
| El paciente no se entiende (dos veces seguidas) | Se ofrece la atención humana en lugar de insistir |
| Cae un canal (email o Telegram) | Se reintenta el envío y, si no sale, se avisa al equipo con el contacto del paciente |
| Urgencia médica, a cualquier hora | Respuesta fija con el teléfono de la guardia 24 h y aviso inmediato al equipo |
