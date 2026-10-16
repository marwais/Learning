# Módulo 11 — Proyecto Final Integrador

Última etapa de **AgendaBot**: ensamblar todo en un sistema **asincrónico, idempotente y supervisado** (Componente A, en n8n) y defenderlo en el **DMSA** (Componente B, PDF `Waisburd_JulioMartin_ProyectoFinal_AI_Experto.pdf`). **Plazo: 13/11/2026 20:59.**

- Consigna completa, rúbrica y pasos de la clínica de integración → [`consigna.md`](consigna.md)
- Clase y teoría → [`resumen-clase.md`](resumen-clase.md). La clase es la misma del M10.
- Devoluciones de los profesores (P1 a P4) → [`devoluciones.md`](devoluciones.md)

## Estado
- [x] Material relevado: consigna, presentación "Proyecto final - Trabajo Final V2", deck del profe y devoluciones.
- [x] M11 duplicado del M9 con [`scripts/duplicar_m9_a_m11.py`](scripts/duplicar_m9_a_m11.py): 7 workflows, sub-workflows publicados y **Manager M11 inactivo**. El M9 sigue en producción hasta que el M11 esté listo.
- [x] Recursos propios: `Agenda_Turnos (11)` y `QA_Veredictos (11)` (copias de las 09 con sus datos), `Memoria_M11` en Airtable y carpeta Drive `Entregas/Trabajo Final`.
- [x] Esqueleto del DMSA: [`DMSA/build_pdf.py`](DMSA/build_pdf.py), que lee `DMSA/Seccion1..4_*.md` y `DMSA/capturas/`.
- [x] **Plan aprobado por el usuario (14/10/2026).** El M11 pasó a producción: Manager M9 desactivado, Manager M11 activo.
- [x] Ramas de error y reintentos ([`scripts/robustez_m11.py`](scripts/robustez_m11.py)):
  - workflow **Errores (M11)** (`UBZ3dbNmFMFuYrAR`, Error Workflow del Manager y del Receptor): lee la ejecución fallida y alerta a Slack (#soporte) con el nodo, el error, el traceId y el paciente; si el paciente escribió por Telegram, le avisa que hay demoras. Para que n8n 2.x lo ejecute tiene que estar publicado;
  - *Retry on Fail* (3 intentos cada 2 s) en las APIs externas;
  - se guardan las ejecuciones con error y con éxito;
  - **Simulacro de falla (M11)** (`POST /webhook/simulacro-falla-m11`) sirve para probar la alerta.
- [x] Idempotencia:
  - nodo **Control de idempotencia** en el Manager, con clave `tg-`/`gm-`/`chat-` por pedido;
  - Worker 1 con *append or update* por `ID = T-<clave>`;
  - alta de memoria en Airtable con *upsert* por Session_ID.
- [x] **Petición asincrónica**: workflow **Receptor (M11)** (`B2DUAOSmq20splvS`, [`scripts/receptor_m11.py`](scripts/receptor_m11.py)) en `POST /webhook/agendabot-m11`:
  - valida la petición: 400 si falta un dato;
  - responde **202 con el traceId en ~0,2 s**; si el `request_id` ya se recibió, responde 200 "duplicado" con el traceId original;
  - le pasa el pedido al Manager sin esperarlo;
  - el resultado sale por Telegram (si el pedido trae `tg_chat_id`) o como **borrador de Gmail**.

  La idempotencia del webhook vive en el Receptor porque n8n guarda la memoria del workflow recién al terminar la ejecución: en el Manager (~20 s) un reintento inmediato no veía la clave.
- [x] Ajuste de lógica ([`scripts/ajustes_logica_m11.py`](scripts/ajustes_logica_m11.py)): si se pide un turno que ya existe, la respuesta es "Ya tenés ese turno… no hice cambios" (antes figuraba como reprogramado y se reescribía la agenda).
- [x] **Juez antes de consolidar** ([`scripts/juez_acciones_m11.py`](scripts/juez_acciones_m11.py)):
  - el Supervisor suma una **rúbrica de acciones** (`juez-rubrica-v3`, sha256 `f31f947dc69f`, mismo esquema JSON);
  - antes de los Workers 1 y 4: *Preparar auditoría de acción → Supervisor (Juez) — acción*. Con ACEPTADO (exactitud ≥ 4) se escribe; si no, la acción **se congela** en *Aprobar acción (Slack)*, con botones Aprobar/Rechazar y una espera máxima de 15 minutos. Sin aprobación, el paciente recibe "quedó en revisión" y no se toca la agenda;
  - la agenda, HubSpot, el borrador de confirmación y la memoria quedan después del veredicto.
- [x] **Modularidad** ([`scripts/modular_m11.py`](scripts/modular_m11.py)):
  - **Canal Telegram (M11)** (`XXtibnyFxPu2piNu`) tiene el disparador, el filtro de repetidos, la voz con Whisper, el audio ilegible y el email dictado, y termina en *Pasar al Manager* (sin esperar). El Manager ya no depende del túnel para publicarse;
  - **Ingesta KB (M11)** (`1MTk7AYPCxH8R2rh`, manual) es la carga de la base de conocimiento;
  - el Manager bajó de 115 a 94 nodos. Su disparador interno es *Llamada de un canal (Receptor / Telegram)*.
- [x] **Emails con HITL** (devolución de la P4), revisado: las confirmaciones de turno y los resultados del webhook salen como **borrador**; *Responder INFO (email)* envía solo después del veredicto ACEPTADO o de la aprobación humana en Slack; *Responder al paciente (email)* solo manda avisos fijos del sistema (faltan datos, turno existente, en revisión).
- [x] **Refinamientos por las devoluciones P5 y P6** ([`scripts/refinamientos_devoluciones_m11.py`](scripts/refinamientos_devoluciones_m11.py)):
  - «No sé» literal en el Agente RAG y en el Juez (`juez-rubrica-v3.1`, sha256 `5d369ceb1dc7`). Probado: "¿tiene estacionamiento?" → "No sé: ese dato no figura en la documentación de la clínica." (Juez ACEPTADO);
  - purga de audios: **Respuesta de voz (M11)** (`H9xkLlYia4GNS3YJ`) y Canal Telegram no guardan ejecuciones.
- [ ] Probar el Canal Telegram con un mensaje de texto y una nota de voz reales (lo hace el usuario). Prioridad 2 y 3.
- [x] **Decisión No-Code** (15/10/2026, tras releer la consigna de la P7). El "100 % No-Code" era para el informe de diseño del M7, y la devolución apuntaba a una frase del portafolio ("low-code… el código solo da formato"). No se migran los 32 nodos *Code*. Lo que el M7 diseñó sin código (triaje, escalado con botones) y todo lo nuevo se arma con nodos visuales. En el DMSA no se habla de "código personalizado" ni de "low-code".
- [x] **Prioridad 2: seguridad** ([`scripts/seguridad_p2_m11.py`](scripts/seguridad_p2_m11.py)), todo con nodos visuales:
  - **Triaje de señales rojas** antes del Router: Switch con el protocolo `triaje-v1` (urgencia médica, dinero, reclamo legal, historia clínica). El paciente recibe una respuesta fija (en una urgencia, el 107 y la guardia 24 h) y el caso pasa a **Escalado humano (M11)** (`jdJ7DV9keYZgP5MU`): se registra en la Data Table `escalados_m11` y llega a #soporte con los botones *Tomo el caso / Falso positivo*, con 15 minutos de espera y recordatorio;
  - **Freno de mano**: Data Table `control_m11` y workflow **Freno de mano (M11)** (`7QEDGdClm8kswbM9`, `POST /webhook/freno-m11` con el header `X-Freno-Token`; el token está en `Modulo5/scripts/.env`). Activo, todo pasa a atención humana;
  - **Idempotencia en Data Table** `pedidos_procesados_m11` (se graba al instante y queda como registro auditable). El **Receptor quedó sin nodos Code**, y el Manager tiene *Clave de idempotencia → Buscar pedido → ¿Pedido nuevo? → Registrar pedido (upsert)*.
- [ ] **Reconectar la credencial "Gmail account" en n8n** (venció el 15/10): sin eso fallan los borradores y las respuestas por email (Errores (M11) lo alerta).
- [x] **Resto de la Prioridad 2** (15/10/2026):
  - **Privacidad de la base**: los nombres, el CUIT, el IIBB y el domicilio fiscal reales pasan a datos ficticios ([`kb/anonimizacion.json`](kb/anonimizacion.json)) en `Modulo5/kb_md`, en la Ingesta KB (M11) y en Qdrant (17 fragmentos re-indexados con Cohere por [`scripts/mantenimiento_m11.py`](scripts/mantenimiento_m11.py), un workflow temporal que usa las credenciales de n8n y se borra al terminar);
  - **Privacidad del log**: el Juez enmascara el nombre del paciente (`[NOMBRE]`), además del email, el DNI y el teléfono;
  - **Columna Asistencia** en `Agenda_Turnos (11)`: el Worker 1 la carga como "pendiente" y la recepción la marca (KPI de facturación del M10);
  - **Aviso de demoras por email** en Errores (M11), para quien escribió por email o webhook;
  - **Dos fallas de comprensión seguidas → una persona** ([`scripts/comprension_m11.py`](scripts/comprension_m11.py), Data Table `sesiones_m11`, nodos visuales): FUERA_DE_ALCANCE o "No pude procesar" dos veces en 30 minutos → "No logro ayudarte…" + Escalado humano;
  - **Rama de error visible** en *Log de trazabilidad*: si falla el email de log, avisa a Slack y el pedido sigue.
- [x] **CRM como fuente de verdad** ([`scripts/crm_hubspot_m11.py`](scripts/crm_hubspot_m11.py)):
  - se crearon 8 propiedades de contacto en HubSpot (`agendabot_origen`, `_trace_id`, `_canal`, `_ultima_interaccion`, `_turno`, `_veredicto_juez`, `_aprobado_por`, `_version`), con el scope `crm.schemas.contacts.write` habilitado temporalmente por el usuario;
  - **bug heredado del M4 corregido**: "Crear contacto" y "Actualizar contacto" tenían las operaciones `create` y `update`, que el nodo HubSpot v2.1 no tiene. n8n no daba error y el contacto **nunca** se escribía. Ahora los dos nodos hacen `upsert` por email (idempotente) con nombre y metadatos;
  - probado: contacto creado con origen AgendaBot, traceId, canal, "Alta: cardiología · 09/12/2026 10:00", "ACEPTADO (exactitud 5/5)", aprobado por "Juez" y versión.
- [x] Gmail reconectado (15/10/2026). `levantar_tunel.ps1` ahora pasa `N8N_EDITOR_BASE_URL=http://localhost:5678/`, así el retorno de OAuth de Google usa localhost y no el túnel (con el túnel, Google daba `redirect_uri_mismatch`).
- [ ] Riesgo de mantenimiento: HubSpot avisa que el nodo de n8n usa versiones de su API que se dan de baja **después de septiembre de 2027** (lo cubre el abono de soporte del M10).
- [x] **Canal Telegram: pedido pendiente** ([`scripts/telegram_pendiente_m11.py`](scripts/telegram_pendiente_m11.py)). Era un hueco del M6, encontrado en la prueba del usuario del 15/10: al pedir "escribime el email por texto", el canal descartaba el pedido del audio y el email llegaba suelto ("¿En qué te puedo ayudar?"). Ahora la transcripción se guarda en la Data Table `pendientes_m11`; cuando llega un texto con @ (dentro de 30 min) se une con el pedido y recién ahí pasa al Manager. Se respeta el formato del paciente: si habló, el pedido del email sale **por voz** ("Anoté tu pedido… escribímelo por texto") y debajo una aclaración por texto ("Para evitar errores, el email te lo pido por escrito, por favor.").
- [x] **Datos faltantes** ([`scripts/faltan_datos_m11.py`](scripts/faltan_datos_m11.py), pedido del usuario):
  - el aviso dice "Faltan datos que son necesarios para poder agendar turnos: fecha, hora y email." (o "…para poder modificar el turno: …");
  - si falta el email y el paciente está en Telegram, el pedido queda en `pendientes_m11` y se le pide el email por escrito: por voz si habló, más la aclaración por texto. Cuando lo escribe, el Canal Telegram lo une con el pedido original.
- [x] **Túnel con dominio fijo (ngrok)** ([`../scripts/levantar_ngrok.ps1`](../scripts/levantar_ngrok.ps1)), 15/10/2026. La red pública "ACCESOGRAL 3" bloquea el puerto 7844 (Cloudflare) y deja el 443. ngrok sale por el 443, el dominio `snore-iodine-grooving.ngrok-free.dev` no cambia y el agente se reconecta solo, así que Telegram, el webhook y los botones de Slack ya no se caen con cada corte. `NGROK_AUTHTOKEN` y `NGROK_DOMAIN` van en `Modulo5/scripts/.env` (fuera de git). `activar_aqui.ps1` usa ngrok si está configurado; si no, Cloudflare. Probado desde la red pública: webhook 202 en 0,96 s y Canal Telegram registrado. Plan gratuito: un dominio por cuenta, y en el navegador (botones de Slack) aparece un aviso de ngrok con un clic extra.
- [x] **Alertas útiles para el equipo** ([`scripts/alertas_identidad_m11.py`](scripts/alertas_identidad_m11.py), pedido del usuario):
  - las alertas de falla salen **en castellano** (sin saldo, credencial vencida, sin permisos, saturación, sin conexión…), con el detalle técnico original entre paréntesis, el **mensaje del paciente** que originó el caso, su nombre y cómo contactarlo;
  - el aviso de casos rojos suma la identidad del paciente (nombre y link `t.me/@usuario` de Telegram, o el email) y lo que la **memoria** sabe de él (datos clave y resumen). El Canal Telegram ahora guarda el `@usuario`.
- [x] **Responder al paciente desde Slack** ([`scripts/responder_paciente_m11.py`](scripts/responder_paciente_m11.py); es el "Responder con plantilla" del M7). Después de *Tomo el caso*, Slack pide la respuesta (texto libre, 10 minutos) y AgendaBot la envía por el canal del paciente: por Telegram, en audio si habló o en texto si escribió; por email, solo si hay una respuesta escrita. Por defecto, en Telegram: "Nos estaremos comunicando en breve para continuar." Queda registrada en `escalados_m11`.
- [x] Saldo de Anthropic recargado por el usuario (15/10/2026); verificado con una consulta de punta a punta.
- [ ] ~~**Saldo de la API de Anthropic agotado** (15/10/2026, 14:36): el Router devolvió "credit balance is too low". Sin crédito se paran Router, RAG y Juez; el triaje, el freno de mano y las alertas siguen andando. Lo carga el usuario en console.anthropic.com → Plans & Billing.~~
- [x] **Lienzo legible del Manager** ([`scripts/lienzo_m11.py`](scripts/lienzo_m11.py)), por la devolución de la P8 y la Sección 2 del DMSA. Los 129 nodos quedaron en carriles de izquierda a derecha, sin superposiciones, y **10 marcos numerados** con una explicación cada uno: 1 Entrada · 2 Trazabilidad e idempotencia · 3 Seguridad · 4 Memoria y clasificación · 5 Gestión de turnos con Juez · 6 Consulta de turnos · 7 Consultas informativas con Juez · 8 Registro y memoria · 9 Respuesta y comprensión · 10 Despacho. Solo cambian posiciones y notas, no la lógica.
- [ ] **Prioridad 3: evidencias y DMSA.**

**Pruebas** (14–15/10/2026) con [`scripts/probar_webhook.py`](scripts/probar_webhook.py) y [`scripts/ver_ejecucion.py`](scripts/ver_ejecucion.py):

| Prueba | Resultado |
|---|---|
| Consulta informativa | 202 en 0,26 s; en segundo plano: Router → RAG → Juez ACEPTADO → borrador de Gmail |
| Mismo request_id 1 s después | 200 "duplicado" con el mismo traceId, sin procesar |
| Petición sin request_id ni canal | 400 con la lista de faltantes |
| Alta de turno | fila `T-wh-prueba-m11-004` con el traceId del Receptor y el borrador de confirmación |
| Mismo turno con otro request_id | "Ya tenés un turno… no hice cambios" |
| Falla real (403 de Sheets) y simulacro | alerta en Slack con el traceId y el paciente |
| Alta clara (dermatología 27/11 15:00) | Juez ACEPTADO → fila `T-wh-prueba-m11-007` |
| Alta con fecha pasada (02/10/2026) | Juez CORREGIR 2/5 ("la fecha es anterior a la fecha actual…") → acción congelada esperando aprobación en Slack; nada escrito |
| Pedido ambiguo ("el jueves a la tarde") | el Router no inventa la fecha → "faltan datos (fecha)" |
| «No sé» ("¿tiene estacionamiento?") | "No sé: ese dato no figura en la documentación de la clínica." (Juez ACEPTADO) |
| Urgencia ("dolor muy fuerte en el pecho… me falta el aire") | triaje → respuesta fija con el 107 y la guardia, sin pasar por la IA; caso en `escalados_m11` y aviso con botones en Slack |
| Freno de mano | token falso → 403; activado → la consulta va directo a atención humana; desactivado → vuelve a la normalidad |
| Duplicado con Data Table | 200 "duplicado" con el traceId original |
| Nota de voz real por Telegram ("turno para un fulemonólogo…, mi email es mwhore.gmail.com") | el Router entendió neumonología; **el Juez congeló el alta** (CORREGIR 2/5: "el email no tiene formato válido, le falta el @") → aprobación en Slack |
| Dos pedidos fuera de alcance seguidos | 1.º: respuesta normal y falla registrada; 2.º: "No logro ayudarte…" y caso en `escalados_m11` |
| Alta con nombre en el texto | log de auditoría: "Hola, soy [NOMBRE]… Mi mail es [EMAIL]" |

Los veredictos reales del Juez en JSON, para la Sección 3 del DMSA, están en [`DMSA/evidencias/`](DMSA/evidencias/).

> Las planillas (11) se compartieron como editor con `mwquiero@gmail.com`, la cuenta de las credenciales de Google en n8n, igual que las 09. Sin eso, Sheets devolvía 403.
>
> El túnel gratuito de Cloudflare se cae seguido. Mientras el disparador de Telegram siga en el Manager, cada caída impide publicarlo (n8n no puede registrar el webhook): hay que correr `Modulo6/scripts/levantar_tunel.ps1`. Se resuelve al pasar Telegram a un workflow propio.
>
> Las pruebas dejaron un contacto `prueba.m11@example.com` en HubSpot y borradores en Gmail.

## Recursos del M11
| Recurso | ID |
|---|---|
| Manager `AI Automation Avanzado - M11` | `zLiXJWDV3i8OGJCK` (inactivo) |
| Supervisor `SUPERVISOR_Judge (M11)` | `x0qFeyPW15wSX0hD` |
| Tool RAG `Tool_ConsultarConocimiento (M11)` | `Ukqb3UUpTZhgnULF` |
| Workers 1–4 (M11) | `NQW5Mkmm0zJc6UJQ` · `8kgru7BieMefNVvz` · `CJKVcfkXPu6oNk8D` · `wT9rHHVpMreJFqwO` |
| Agenda_Turnos (11) | `19rWr4cy1pVmiDi5iv3Nkr3gZn4ExF12Ep5OkMrxxaWk` |
| QA_Veredictos (11) | `1IYqouMdEh8s0ecJEdDMWjtObglgDA1Nd8E84nWdSEQk` (la pestaña "Untitled" no se renombra: n8n la busca por nombre) |
| Memoria_M11 (Airtable, base `Memoria_Agente`) | `tblaIZxUOLY1T8g40` |
| Drive `Entregas/Trabajo Final` | `15y6JMd_aVrDFc_hL_yMcVolUFcXkUcV7` (subcarpeta `Del Profe`) |
| Base de conocimiento (Qdrant) | `kb_lodetincho_m5` (compartida, sin cambios) |

> Las planillas (11) se copiaron con los datos del M9. Antes de las pruebas finales conviene vaciar las filas de prueba (dejar los encabezados), así la auditoría del DMSA muestra solo casos del M11.
>
> El M11 existe solo en el n8n de **LOBO**. `activar_aqui.ps1` usa el último módulo que encuentre en el n8n local, así que en WOLVERINE sigue con el M9 hasta que se copie la base de n8n.

## Diagnóstico: qué tiene el M9 frente a los criterios del final
| Criterio de aceptación | Situación del M9 (revisada en los JSON el 14/10/2026) |
|---|---|
| 1. Webhook que responde de inmediato + proceso asincrónico | ✘ No hay nodo Webhook. Los disparadores son chat de n8n (sincrónico), Gmail Trigger y Telegram Trigger |
| 2. Juez **antes** de consolidar datos o registrar en el CRM | ✘ Parcial. El Juez evalúa solo las respuestas informativas. El alta y la modificación de turnos (Workers 1 y 4), el contacto en HubSpot y el guardado de memoria se ejecutan sin pasar por el Juez |
| 3. Despacho a un canal externo | ✔ Telegram, Gmail y Slack conectados |
| 4. Modular, sin monolitos | ~ Manager + 4 Workers + Tool RAG + Juez, pero el Manager tiene 99 nodos e incluye la ingesta de la base de conocimiento y el manejo de los tres canales |
| 5. RAG con citas y "No sé" | ✔ Top-K 5, Min Score 0,60, cita la fuente y el prompt instruye "No sé" |
| 6. Reintentos y fallas sin duplicados | ✘ Parcial. Telegram filtra los `update_id` repetidos y HubSpot busca antes de crear, pero el Worker 1 hace *append* (un reintento duplica el turno). Solo el modelo RAG tiene *Retry on Fail* |
| Ramas de error que alerten al equipo | ✘ No hay *Error Workflow* ni ramas de error en las APIs externas. Además, el Manager tiene `saveDataErrorExecution: none`: **las ejecuciones con error no se guardan** |
| Sin secretos en prompts ni textos | ✔ Las claves están en las credenciales de n8n y en `.env` (fuera de git) |

## Plan: lo que hay que construir
La consigna pide que el final **implemente lo que en las pre-entregas quedó solo diseñado**. Todo lo que sigue es una **propuesta, sin confirmar**, ordenada por prioridad.

**Prioridad 1: criterios de aceptación (35 % de la nota)**
1. **Webhook asincrónico:** `POST /agendabot` que responde enseguida con `202 {estado: "recibido", traceId}` y procesa en segundo plano. El resultado sale por un canal: Telegram, borrador de Gmail o Slack.
2. **Juez antes de consolidar:** ampliar el Supervisor para que también evalúe las **acciones** (alta y cambio de turno, contacto en el CRM, guardado de memoria): datos completos, coherencia con el pedido, que no sea un duplicado y que respete el semáforo. Con `exactitud_factual < 4` o una acción dudosa, la acción **se congela** y va a la cola de aprobación en Slack (*Send and Wait*). Solo después se escribe.
3. **Idempotencia:** una clave por pedido (canal + id del mensaje o de la petición). Antes de procesar se busca en un registro de pedidos procesados, el Worker 1 pasa a *append or update* por ID, y los envíos (Gmail, Telegram, Slack) se marcan como hechos para no repetirlos.
4. **Ramas de error y reintentos:** un workflow `Errores (M11)` con *Error Trigger* que avise a Slack con el traceId y mande un aviso al paciente, configurado como *Error Workflow* de todos los workflows. Además, *Retry on Fail* en las APIs externas (Sheets, HubSpot, Airtable, Gmail, Slack, Telegram, Cohere, Qdrant y los modelos), salida de error en los nodos críticos y guardar las ejecuciones con error.
5. **Modularidad:** sacar la ingesta de la base de conocimiento a su propio workflow y evaluar Workers para el CRM y para el despacho (Manager más chico).
6. **Email con HITL** (devolución de la P4): el envío directo solo después de un veredicto ACEPTADO; en cualquier otro caso, borrador.

**Prioridad 2: lo diseñado en M7, M9 y M10 que todavía no está construido**
7. **Triaje de señales rojas antes del Router** (M7, Pieza 3 y Scorecard B): palabras y patrones de urgencia, dinero, temas legales e historia clínica → respuesta fija (con la guardia 24 h si es una urgencia) → Slack con botones *Tomar el caso / Responder con plantilla / Descartar* y espera de 15 minutos.
8. **Metadatos en el CRM** (M10 y slide de trazabilidad del profe): `Origen = AgendaBot`, traceId, canal, última interacción, versión del workflow, resultado del Juez y escalado. Hay que crear las propiedades en HubSpot.
9. **Agenda:** columna `Asistencia`; el código de seguimiento (traceId) ya existe.
10. **Freno de mano** (M10): una bandera que se cambia desde Slack o la planilla. Si está activa, todo pasa a la atención humana.
11. **Respaldo ante demoras del modelo** (M10): un reintento y después el mensaje "Estamos con demoras…" más el aviso a Slack. **Dos fallas de comprensión seguidas** → humano (M7).
12. **Pendientes de privacidad** (M8/M9): enmascarar el nombre del paciente en el log y anonimizar la razón social real en la base (`Datos impositivos`).

**Prioridad 3: evidencias y DMSA (25 % + 12 % + 8 %)**
13. Batería de pruebas de punta a punta (incluido un reintento forzado para mostrar que no duplica y una API caída para mostrar la alerta) y métricas de precisión del Juez.
14. **3 veredictos reales del Juez en JSON plano**, capturas nítidas del lienzo (las saca el usuario: el lienzo grande congela Chrome), resultados visibles (mensaje despachado, fila en la agenda, contacto en el CRM, panel de KPIs).
15. ROI con modelos económicos: el M9 ya calculó el costo con el agente en Haiku (US$ 52,99/mes en tokens). Variables de entorno y estructuras de tablas, sin valores secretos. Video opcional de 3 minutos.

## Próximo paso
Confirmar el plan (o ajustarlo) y empezar por la Prioridad 1, en orden: Error Workflow (para ver las fallas desde el principio), idempotencia, Juez sobre las acciones y webhook asincrónico.
