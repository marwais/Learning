# Anexo C. Inventario de workflows

## Workflows de n8n

| Workflow | Id | Disparador | Guarda ejecuciones |
|---|---|---|---|
| AgendaBot · Receptor | `B2DUAOSmq20splvS` | Webhook `POST /webhook/agendabot` | Sí |
| AgendaBot · Canal Telegram | `XXtibnyFxPu2piNu` | Telegram | **No** (audio del paciente) |
| AgendaBot · Manager | `zLiXJWDV3i8OGJCK` | Llamada de un canal · Gmail · chat | Sí |
| AgendaBot · Worker 1 a 4 (registrar, confirmar, consultar, modificar) | `NQW5Mkmm0zJc6UJQ` · `8kgru7BieMefNVvz` · `CJKVcfkXPu6oNk8D` · `wT9rHHVpMreJFqwO` | Llamada del Manager | Sí |
| AgendaBot · Herramienta RAG | `Ukqb3UUpTZhgnULF` | Llamada del agente | Sí |
| AgendaBot · Juez (supervisor) | `x0qFeyPW15wSX0hD` | Llamada del Manager | Sí |
| AgendaBot · Escalado humano | `jdJ7DV9keYZgP5MU` | Llamada del Manager | Sí |
| AgendaBot · Respuesta de voz | `H9xkLlYia4GNS3YJ` | Llamada del Manager o del escalado | **No** (audio sintetizado) |
| AgendaBot · Errores | `UBZ3dbNmFMFuYrAR` | Error Trigger (Error Workflow del Manager, del Receptor y de los canales) | Sí |
| AgendaBot · Freno de mano | `7QEDGdClm8kswbM9` | Webhook `POST /webhook/freno-de-mano` (con token) | Sí |
| AgendaBot · Ingesta KB | `1MTk7AYPCxH8R2rh` | Manual | Sí |
| AgendaBot · Simulacro de falla | `6rEbc1LKZmGBQCIp` | Webhook (prueba de la rama de error) | Sí |

### Los especialistas por dentro

![AgendaBot · Receptor: valida, genera el traceId, bloquea duplicados y responde 202 antes de procesar](capturas/sub_receptor.png)

![AgendaBot · Canal Telegram: nota de voz, transcripción, pedido pendiente cuando el email se dicta y pase al Manager](capturas/sub_canal_telegram.png)

![AgendaBot · Juez (supervisor): veredicto con esquema JSON, registro en QA_Veredictos y salida segura si el veredicto es inválido](capturas/sub_juez.png)

![AgendaBot · Herramienta RAG: embedding de la consulta y búsqueda en Qdrant con Top-K y puntaje mínimo](capturas/sub_rag.png)

![AgendaBot · Worker 1 · Registrar turno](capturas/sub_worker1.png)

![AgendaBot · Worker 2 · Confirmación](capturas/sub_worker2.png)

![AgendaBot · Worker 3 · Consultar turnos](capturas/sub_worker3.png)

![AgendaBot · Worker 4 · Modificar turno](capturas/sub_worker4.png)

![AgendaBot · Escalado humano: aviso con botones en Slack, recordatorio y respuesta al paciente por su canal](capturas/sub_escalado.png)

![AgendaBot · Respuesta de voz: síntesis, envío y descarte del audio](capturas/sub_respuesta_voz.png)

![AgendaBot · Errores: alerta al equipo y aviso de demora al paciente por su canal](capturas/sub_errores.png)

![AgendaBot · Freno de mano: cambio de estado con token y aviso en Slack](capturas/sub_freno.png)

![AgendaBot · Simulacro de falla: API externa caída a demanda, para probar la rama de error](capturas/sub_simulacro.png)

![AgendaBot · Ingesta KB: recrea la colección y carga la documentación por secciones](capturas/sub_ingesta_kb.png)
