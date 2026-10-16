# Anexo A. Gobernanza de datos

**Regla de oro:** ninguna clave ni token real aparece en los workflows, en los prompts ni en este documento. Las claves viven en el almacén de credenciales cifrado de n8n o en un archivo `.env` local excluido del control de versiones. Abajo figuran **solo los nombres**.

## A.1 Variables de entorno

| Variable | Dónde | Para qué |
|---|---|---|
| `WEBHOOK_URL` | Contenedor de n8n | Dirección pública del sistema (dominio fijo del túnel): webhooks, Telegram y botones de Slack |
| `N8N_EDITOR_BASE_URL` | Contenedor de n8n | Dirección local del editor (`http://localhost:5678`): retorno de las autorizaciones OAuth de Google |
| `N8N_API_KEY` | `.env` | Scripts de despliegue, pruebas y exportación por la API de n8n |
| `N8N_BASE`, `QDRANT_URL`, `QDRANT_COLLECTION`, `EMBED_DIM` | `.env` | Direcciones de n8n y de la base de conocimiento (colección `kb_lodetincho`, 1.024 dimensiones) |
| `LLAMA_CLOUD_API_KEY` | `.env` | Procesamiento de los documentos oficiales con LlamaParse (ingesta) |
| `NGROK_AUTHTOKEN`, `NGROK_DOMAIN` | `.env` | Túnel público con dominio fijo |
| `FRENO_TOKEN` | `.env` | Token del encabezado `X-Freno-Token` para activar o desactivar el freno de mano |

## A.2 Credenciales de n8n (solo nombres)

| Credencial | Tipo | Usada por |
|---|---|---|
| Anthropic account | API de Anthropic (Claude) | Manager (coordinador, agente, resumen) y Juez |
| OpenAI account | API de OpenAI (Whisper) | AgendaBot · Canal Telegram |
| ElevenLabs account | API de ElevenLabs | AgendaBot · Respuesta de voz |
| Cohere n8n | API de Cohere (embeddings) | Herramienta RAG e Ingesta KB |
| Qdrant local | API de Qdrant | AgendaBot · Ingesta KB |
| Google Sheets account / Gmail account | OAuth 2 de Google | Agenda, veredictos, borradores, respuestas y avisos |
| Airtable AgendaBot | Token de Airtable | Memoria del paciente |
| HubSpot AgendaBot (App Token) | App privada de HubSpot | Contactos (solo lectura y escritura de contactos) |
| Slack account | OAuth 2 de Slack | Avisos, aprobaciones y escalados |
| Telegram account | Bot de Telegram | Canal Telegram, respuestas y avisos |
| n8n API (alertas) | Encabezado | Errores: lee la ejecución fallida |
| Freno de mano | Encabezado | Protege el webhook del freno de mano |

## A.3 Estructuras de datos

| Tabla | Dónde | Campos | Clave |
|---|---|---|---|
| `Agenda_Turnos` | Google Sheets | ID, Fecha, Hora, Nombre, Motivo, Estado, Email, `traceId`, Asistencia | ID = `T-` + clave del pedido |
| `Memoria_Pacientes` | Airtable | Session_ID, Fecha de Actualización, Resumen Consolidado, Estado del Caso, Datos Clave, Mensajes, Ultimo_traceId | Session_ID |
| `QA_Veredictos` | Google Sheets | fecha, origen, caso, intento, pregunta y respuesta (enmascaradas), exactitud_factual, estado_veredicto, crítica, ruta, `traceId`, versión del prompt, log JSON | `traceId` + intento |
| `pedidos_procesados` | Data Table de n8n | clave, `traceId`, canal | clave |
| `escalados` | Data Table de n8n | `traceId`, categoría, canal, sesión, mensaje, estado, decisión | `traceId` |
| `control` | Data Table de n8n | clave (`freno_de_mano`), valor (`si`/`no`), actualizado_por | clave |
| `sesiones` / `pendientes` | Data Tables de n8n | Fallas de comprensión y pedidos que esperan el email por escrito | sesión |
| Contacto | HubSpot | email, nombre, `agendabot_origen`, `agendabot_trace_id`, `agendabot_canal`, `agendabot_ultima_interaccion`, `agendabot_turno`, `agendabot_veredicto_juez`, `agendabot_aprobado_por`, `agendabot_version` | email |
| Biblioteca oficial | Qdrant | contenido del fragmento y metadatos: fuente, sección (ruta de títulos), archivo | id del fragmento |

## A.4 Parámetros de conexión

| Conexión | Parámetro |
|---|---|
| Petición de pedidos | `POST {WEBHOOK_URL}/webhook/agendabot` · cuerpo JSON: `request_id`, `mensaje`, `nombre`, `email` y/o `tg_chat_id` (o el encabezado `Idempotency-Key`) |
| Freno de mano | `POST {WEBHOOK_URL}/webhook/freno-de-mano` · encabezado `X-Freno-Token` · cuerpo `{"activo": true/false, "quien": "…"}` |
| Base de conocimiento | Qdrant `/collections/kb_lodetincho/points/search` · Top-K 5 · puntaje mínimo 0,60 |
| Modelos | Coordinador y agente: `claude-haiku-4-5`; Juez: `claude-sonnet-4-6`; voz: `eleven_multilingual_v2` (es); transcripción: Whisper (es) |

## A.5 Proveedores: desarrollo hoy, requisito para producción y alternativa empresarial

| Proveedor | Desarrollo (hoy) | Requisito para producción | Alternativa empresarial de privacidad |
|---|---|---|---|
| **Anthropic** (Claude) | API con saldo prepago, una sola clave | Claves separadas para desarrollo y producción, tope de gasto y alerta de saldo; acuerdo de procesamiento de datos | Claude en una nube privada (AWS Bedrock o Google Vertex) en la región del cliente |
| **OpenAI** (Whisper) | API pública | Clave de producción con tope; sin retención de datos | Whisper autoalojado en el servidor de la clínica |
| **ElevenLabs** (voz) | Plan Creator | Plan con acuerdo comercial; voz licenciada | Síntesis de voz autoalojada |
| **Cohere** (embeddings) | API pública | Clave de producción | Modelo de embeddings autoalojado |
| **Qdrant** (biblioteca) | Docker local | Qdrant Cloud o servidor propio con respaldo | Instancia privada en la red de la clínica |
| **Google** (Sheets, Gmail) | OAuth de una cuenta personal en modo prueba | Cuenta de servicio de Google Workspace de la clínica, con acceso solo a sus planillas | Agenda en una base de datos propia (Postgres) |
| **HubSpot** (CRM) | App privada con permisos de contactos | Permisos mínimos (solo contactos); el permiso de esquema se otorga solo para crear propiedades | CRM de la clínica con API |
| **Slack** | Espacio de trabajo de prueba | Canal privado del equipo, con bot limitado a ese canal | Slack Enterprise o Microsoft Teams |
| **Telegram** | Bot de prueba | Bot oficial de la clínica | WhatsApp Business API |
| **Airtable** (memoria) | Plan gratuito | Plan Team, con token limitado a la tabla | Tabla en la base de datos propia |
| **n8n y túnel** | Docker local y túnel ngrok con dominio fijo | n8n en un servidor con dominio y certificado propios; sin túnel | n8n autoalojado en la red de la clínica (sector salud regulado) |

## A.6 Privacidad

- **Audios:** la nota de voz del paciente se procesa en el Canal Telegram y la respuesta hablada en *Respuesta de voz*. **Ninguno de los dos guarda ejecuciones** (ni con éxito ni con error), y al Manager solo le llega texto. Verificado en n8n: esos workflows no tienen ejecuciones registradas, mientras que el Manager sí guarda las suyas como evidencia.
- **Log de auditoría:** el nombre, el email, el DNI y el teléfono se enmascaran antes de guardarse (`[NOMBRE]`, `[EMAIL]`, `[DNI]`, `[TEL]`).
- **Biblioteca anonimizada:** la razón social, el CUIT, el ingreso bruto y el domicilio fiscal de la empresa de origen se reemplazaron por datos ficticios.
- **Mínimo privilegio:** cada credencial tiene solo los permisos que su función necesita (por ejemplo, HubSpot solo contactos).
