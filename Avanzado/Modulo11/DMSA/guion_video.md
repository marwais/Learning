# Guion del video (opcional, máx. 3 minutos)

**Objetivo:** mostrar el flujo activo de punta a punta. La consigna pide un "enlace público de máx. 3 minutos mostrando el flujo activo", incluido en el PDF o en los comentarios. Mostrar **resultados**, no solo el lienzo (lo pide la presentación del proyecto final).

## Antes de grabar (5 minutos)
- [ ] n8n y el túnel arriba: `powershell -ExecutionPolicy Bypass -File Avanzado\scripts\levantar_ngrok.ps1` → "Túnel ngrok OK".
- [ ] Freno de mano desactivado (Data Table `control_m11`: `freno_de_mano = no`).
- [ ] Abrir en pestañas: el lienzo del Manager (n8n), #soporte (Slack), Telegram (celular o escritorio), HubSpot (Contactos), `Agenda_Turnos (11)` y Gmail (Borradores).
- [ ] Usar un nombre de prueba (por ejemplo "Carla Demo") y una especialidad y fecha que no estén en la agenda.
- [ ] Grabar con la herramienta de Windows (Win + Alt + R) o con OBS; voz en off o texto en pantalla.
- [ ] Subir a YouTube como **"No listado"** (o a Drive con acceso por link) y pegar el enlace en el PDF.

## Escenas

| Tiempo | En pantalla | Qué decir (o texto en pantalla) |
|---|---|---|
| 0:00 – 0:15 | Portada del DMSA o el lienzo general del Manager | "AgendaBot es la Central de Turnos digital de la Clínica LoDeTincho: atiende las 24 horas por Telegram, email, web y chat, con un supervisor que controla cada respuesta y personas que deciden lo delicado." |
| 0:15 – 0:55 | **Telegram**: mandar un audio: *"Hola, soy Carla Demo, quiero un turno de dermatología para el 18 de diciembre a las 10 de la mañana."* El bot responde **en audio** pidiendo el email y debajo la aclaración por texto. Escribir el email. Llega la confirmación. | "Le pido un turno por voz. Como el email por voz se transcribe mal, me lo pide por escrito, pero responde en el mismo formato en que le hablé. Escribo el email y queda confirmado." |
| 0:55 – 1:20 | **Agenda_Turnos (11)**: la fila nueva con el `traceId` y Asistencia "pendiente". **HubSpot**: el contacto con Origen = AgendaBot, código de seguimiento, turno y "Resultado del Supervisor: ACEPTADO". **Gmail**: el borrador de confirmación. | "El turno queda en la agenda, el contacto en el CRM con su origen y su código de seguimiento, que es la base para facturar sin discusiones, y la confirmación como borrador para revisión humana." |
| 1:20 – 1:50 | **Telegram**: *"Quiero un turno de traumatología para el 2 de octubre de 2026 a las 11."* (fecha pasada) + email por texto. **Slack**: aparece "acción congelada por el Juez" con la crítica y los botones Aprobar / Rechazar. Tocar **Rechazar** ("Visit Site" en el aviso de ngrok). | "Ahora un pedido con un error: la fecha ya pasó. El Juez lo detecta antes de escribir nada, congela la acción y la manda a una persona en Slack. Rechazo, y el paciente recibe que su pedido quedó en revisión." |
| 1:50 – 2:25 | **Telegram**: audio *"Tengo un dolor muy fuerte en el pecho y me falta el aire."* Respuesta inmediata con el 107 y la guardia. **Slack**: el caso con el nombre del paciente, el link para abrir el chat y lo que sabe la memoria. Tocar **Tomo el caso** → escribir la respuesta o dejar la de por defecto → llega a Telegram en audio. | "Una urgencia no la resuelve la IA: el triaje la detecta antes, responde al instante con la guardia y avisa al equipo con todo lo necesario para contactar al paciente. Tomo el caso y le respondo desde Slack." |
| 2:25 – 2:45 | **Terminal o Postman**: `POST /webhook/agendabot-m11` → **202** con el `traceId` en una décima de segundo; el mismo `request_id` otra vez → **200 "duplicado"**. Simulacro de falla → alerta en castellano en #soporte. | "Un sistema externo también puede pedir turnos por webhook: responde al instante y procesa en segundo plano, sin duplicar si reintenta. Y si una API externa se cae, el equipo recibe una alerta clara." |
| 2:45 – 3:00 | Cuadro de ROI del DMSA | "En las pruebas, 16 de 16 casos resueltos como se esperaba, con un costo de menos de 2 centavos de dólar por consulta. Libera unas 183 horas por mes de trabajo repetitivo: capacidad para atender más pacientes sin sumar personal." |

## Consejos
- Si una respuesta tarda, cortá en la edición: el proceso en segundo plano toma de 6 a 15 segundos.
- No muestres el `.env` ni las pantallas de credenciales de n8n: **exponer claves puede reprobar la entrega**.
- Si el túnel se cayó, volvé a correr `levantar_ngrok.ps1` (el dominio no cambia).
