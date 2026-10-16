# Anexo C. Inventario de workflows y operación

## C.1 Workflows de n8n

| Workflow | Id | Disparador | Guarda ejecuciones |
|---|---|---|---|
| Receptor (M11) | `B2DUAOSmq20splvS` | Webhook `POST /webhook/agendabot-m11` | Sí |
| Canal Telegram (M11) | `XXtibnyFxPu2piNu` | Telegram | **No** (audio del paciente) |
| AI Automation Avanzado - M11 (Manager) | `zLiXJWDV3i8OGJCK` | Llamada de un canal · Gmail · chat | Sí |
| Worker1_RegistrarTurno / Worker2_Confirmacion / Worker3_ConsultarTurno / Worker4_ModificarTurno | `NQW5Mkmm0zJc6UJQ` · `8kgru7BieMefNVvz` · `CJKVcfkXPu6oNk8D` · `wT9rHHVpMreJFqwO` | Llamada del Manager | Sí |
| Tool_ConsultarConocimiento | `Ukqb3UUpTZhgnULF` | Llamada del agente | Sí |
| SUPERVISOR_Judge | `x0qFeyPW15wSX0hD` | Llamada del Manager | Sí |
| Escalado humano (M11) | `jdJ7DV9keYZgP5MU` | Llamada del Manager | Sí |
| Respuesta de voz (M11) | `H9xkLlYia4GNS3YJ` | Llamada del Manager o del escalado | **No** (audio sintetizado) |
| Errores (M11) | `UBZ3dbNmFMFuYrAR` | Error Trigger (Error Workflow del Manager, del Receptor y de los canales) | Sí |
| Freno de mano (M11) | `7QEDGdClm8kswbM9` | Webhook `POST /webhook/freno-m11` (con token) | Sí |
| Ingesta KB (M11) | `1MTk7AYPCxH8R2rh` | Manual | Sí |
| Simulacro de falla (M11) | `6rEbc1LKZmGBQCIp` | Webhook (prueba de la rama de error) | Sí |

## C.2 Cómo se levanta el sistema

1. Abrir Docker Desktop y correr `powershell -ExecutionPolicy Bypass -File Avanzado\scripts\activar_aqui.ps1`. El script:
   - desactiva el sistema en la otra computadora del proyecto, si estaba activo;
   - actualiza el repositorio;
   - levanta Qdrant y el túnel con dominio fijo (`levantar_ngrok.ps1`);
   - activa los workflows del último módulo.
2. Verificar: el dominio público responde y los 14 workflows quedan activos (salvo la Ingesta KB, que es manual).
3. Prueba de humo: `python Avanzado\Modulo11\scripts\probar_webhook.py <request_id> "¿Qué estudios se hacen sin turno?" --email <email> --esperar`.
4. Batería completa: `python Avanzado\Modulo11\scripts\bateria_m11.py <corrida>`.

## C.3 Video (opcional)

Demostración de 3 minutos del flujo activo: **[enlace pendiente]**. El guion está en `DMSA/guion_video.md`.
