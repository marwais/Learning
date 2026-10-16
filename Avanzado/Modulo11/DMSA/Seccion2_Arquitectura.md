# 2. Arquitectura del sistema en n8n

## 2.1 El ecosistema: un coordinador y sus especialistas

AgendaBot no es un único flujo: son **14 workflows independientes** de n8n (versión comunitaria, en Docker). Un **Manager** coordina y delega cada tarea en un especialista: el patrón *Manager-Worker*. Cada canal de entrada es un adaptador propio y cada capacidad delicada (supervisión, escalado, voz, alertas) es un sub-workflow que se puede probar y cambiar por separado.

<svg viewBox="0 0 780 490" width="100%" xmlns="http://www.w3.org/2000/svg" font-family="Segoe UI, Arial, sans-serif">
  <defs>
    <marker id="fin" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#374151"/></marker>
    <marker id="ini" markerWidth="8" markerHeight="8" refX="1" refY="4" orient="auto"><path d="M8,0 L0,4 L8,8 z" fill="#374151"/></marker>
  </defs>
  <text x="8" y="12" font-size="10" font-weight="700" fill="#0b3d5c">1 · EL PACIENTE ESCRIBE POR SU CANAL</text>
  <g font-size="10.5" text-anchor="middle">
    <rect x="10" y="18" width="160" height="42" rx="8" fill="#eef2f6" stroke="#0b3d5c"/><text x="90" y="35" font-weight="700">Web, app o CRM</text><text x="90" y="51" fill="#4b5563" font-size="9.5">Receptor: responde al instante</text>
    <rect x="185" y="18" width="160" height="42" rx="8" fill="#eef2f6" stroke="#0b3d5c"/><text x="265" y="35" font-weight="700">Telegram</text><text x="265" y="51" fill="#4b5563" font-size="9.5">texto o nota de voz</text>
    <rect x="360" y="18" width="160" height="42" rx="8" fill="#eef2f6" stroke="#0b3d5c"/><text x="440" y="35" font-weight="700">Email</text><text x="440" y="51" fill="#4b5563" font-size="9.5">Gmail</text>
    <rect x="535" y="18" width="160" height="42" rx="8" fill="#eef2f6" stroke="#0b3d5c"/><text x="615" y="35" font-weight="700">Chat</text><text x="615" y="51" fill="#4b5563" font-size="9.5">web de la clínica</text>
  </g>
  <g stroke="#374151" stroke-width="1.6" marker-end="url(#fin)"><line x1="90" y1="60" x2="90" y2="92"/><line x1="265" y1="60" x2="265" y2="92"/><line x1="440" y1="60" x2="440" y2="92"/><line x1="615" y1="60" x2="615" y2="92"/></g>
  <path d="M735,95 L735,39 L699,39" fill="none" stroke="#15803d" stroke-width="1.8" stroke-dasharray="5 3" marker-end="url(#fin)"/>
  <text x="748" y="160" font-size="9.5" fill="#15803d" transform="rotate(-90 748 160)">respuesta por el mismo canal</text>
  <rect x="10" y="95" width="715" height="78" rx="12" fill="#0b3d5c"/>
  <text x="367" y="115" text-anchor="middle" font-size="13" font-weight="700" fill="#fff">2 · COORDINADOR (Manager): recorre las 10 etapas y delega</text>
  <text x="367" y="137" text-anchor="middle" font-size="10.5" fill="#dbe7f0">1 Entrada · 2 Código de seguimiento y repetidos · 3 Triaje rojo y freno de mano · 4 Memoria y clasificación · 5 Turnos</text>
  <text x="367" y="155" text-anchor="middle" font-size="10.5" fill="#dbe7f0">6 Consulta de turnos · 7 Consultas informativas · 8 Registro y memoria · 9 Respuesta · 10 Despacho</text>
  <g font-size="9.5" fill="#0b3d5c"><text x="52" y="292" font-weight="700">3 · ESPECIALISTAS</text><text x="52" y="305" font-weight="700">Y SUS HERRAMIENTAS</text><text x="52" y="320">↕ el coordinador pide</text><text x="52" y="333">y recibe el resultado</text></g>
  <g font-size="10" text-anchor="middle">
    <rect x="10" y="205" width="150" height="62" rx="8" fill="#eef7f1" stroke="#15803d"/><text x="85" y="221" font-weight="700" fill="#166534">Datos del coordinador</text><text x="85" y="236">Memoria (Airtable)</text><text x="85" y="250">CRM (HubSpot) · Gmail</text><text x="85" y="263" fill="#4b5563" font-size="9">pedidos repetidos</text>
    <rect x="172" y="205" width="88" height="62" rx="8" fill="#fff" stroke="#0b3d5c"/><text x="216" y="230" font-weight="700">Workers 1 a 4</text><text x="216" y="246" fill="#4b5563" font-size="9">registran y</text><text x="216" y="258" fill="#4b5563" font-size="9">consultan turnos</text>
    <rect x="270" y="205" width="88" height="62" rx="8" fill="#fff" stroke="#0b3d5c"/><text x="314" y="230" font-weight="700">Búsqueda</text><text x="314" y="246" fill="#4b5563" font-size="9">en la biblioteca</text><text x="314" y="258" fill="#4b5563" font-size="9">(5 mejores, ≥ 0,60)</text>
    <rect x="368" y="205" width="88" height="62" rx="8" fill="#fff4e5" stroke="#c2410c"/><text x="412" y="230" font-weight="700" fill="#9a3412">Juez</text><text x="412" y="246" font-size="9">revisa respuestas</text><text x="412" y="258" font-size="9">y acciones (≥ 4/5)</text>
    <rect x="466" y="205" width="88" height="62" rx="8" fill="#fde8e8" stroke="#b91c1c"/><text x="510" y="230" font-weight="700" fill="#991b1b">Escalado</text><text x="510" y="246" font-size="9">a una persona</text><text x="510" y="258" font-size="9">con botones</text>
    <rect x="564" y="205" width="88" height="62" rx="8" fill="#fff" stroke="#0b3d5c"/><text x="608" y="230" font-weight="700">Voz</text><text x="608" y="246" fill="#4b5563" font-size="9">respuesta hablada</text><text x="608" y="258" fill="#4b5563" font-size="9">sin guardar audio</text>
    <rect x="662" y="205" width="88" height="62" rx="8" fill="#fde8e8" stroke="#b91c1c"/><text x="706" y="230" font-weight="700" fill="#991b1b">Errores y freno</text><text x="706" y="246" font-size="9">alertas y</text><text x="706" y="258" font-size="9">pausa general</text>
  </g>
  <g stroke="#374151" stroke-width="1.6" marker-end="url(#fin)" marker-start="url(#ini)">
    <line x1="85" y1="176" x2="85" y2="202"/><line x1="216" y1="176" x2="216" y2="202"/><line x1="314" y1="176" x2="314" y2="202"/>
    <line x1="412" y1="176" x2="412" y2="202"/><line x1="510" y1="176" x2="510" y2="202"/><line x1="608" y1="176" x2="608" y2="202"/><line x1="706" y1="176" x2="706" y2="202"/>
  </g>
  <g stroke="#374151" stroke-width="1.6" marker-end="url(#fin)">
    <line x1="216" y1="267" x2="216" y2="303"/><line x1="314" y1="267" x2="314" y2="303"/><line x1="412" y1="267" x2="412" y2="303"/>
    <line x1="510" y1="267" x2="510" y2="303"/><line x1="608" y1="267" x2="608" y2="303"/><line x1="706" y1="267" x2="706" y2="303"/>
  </g>
  <text x="418" y="287" font-size="9" fill="#9a3412">registra cada veredicto</text>
  <g font-size="9.5" text-anchor="middle">
    <rect x="172" y="306" width="88" height="40" rx="7" fill="#eef7f1" stroke="#15803d"/><text x="216" y="322">Agenda</text><text x="216" y="336" fill="#4b5563">Google Sheets</text>
    <rect x="270" y="306" width="88" height="40" rx="7" fill="#eef7f1" stroke="#15803d"/><text x="314" y="322">Biblioteca oficial</text><text x="314" y="336" fill="#4b5563">Qdrant</text>
    <rect x="368" y="306" width="88" height="40" rx="7" fill="#eef7f1" stroke="#15803d"/><text x="412" y="322">Veredictos</text><text x="412" y="336" fill="#4b5563">log de auditoría</text>
    <rect x="466" y="306" width="88" height="40" rx="7" fill="#fde8e8" stroke="#b91c1c"/><text x="510" y="322">Equipo humano</text><text x="510" y="336" fill="#4b5563">en Slack</text>
    <rect x="564" y="306" width="88" height="40" rx="7" fill="#eef7f1" stroke="#15803d"/><text x="608" y="322">Telegram</text><text x="608" y="336" fill="#4b5563">ElevenLabs</text>
    <rect x="662" y="306" width="88" height="40" rx="7" fill="#eef7f1" stroke="#15803d"/><text x="706" y="322">Slack · email</text><text x="706" y="336" fill="#4b5563">Telegram</text>
  </g>
  <path d="M510,346 L510,364 L40,364 L40,269" fill="none" stroke="#b91c1c" stroke-width="1.5" stroke-dasharray="4 3" marker-end="url(#fin)"/>
  <text x="275" y="378" text-anchor="middle" font-size="9.5" fill="#991b1b">la persona aprueba, edita, rechaza o responde: su decisión vuelve al coordinador</text>
  <rect x="10" y="390" width="740" height="92" rx="10" fill="#f7f9fb" stroke="#0b3d5c" stroke-dasharray="5 3"/>
  <text x="380" y="410" text-anchor="middle" font-size="12" font-weight="700" fill="#0b3d5c">4 · Correlación del <tspan font-family="Consolas, monospace">traceId</tspan> (código de seguimiento)</text>
  <g font-size="10.5" text-anchor="middle">
    <text x="380" y="430">Lo crea el Receptor (o el coordinador) → viaja a cada Worker, a la búsqueda, al Juez y al escalado</text>
    <text x="380" y="448">→ queda en la agenda, en el contacto de HubSpot, en los veredictos, en los escalados, en el log de auditoría y en cada alerta</text>
    <text x="380" y="466" fill="#4b5563">Con un solo código se reconstruye qué pidió el paciente, qué decidió el Juez, quién aprobó y qué se escribió.</text>
  </g>
</svg>

| Workflow | Función |
|---|---|
| **Receptor** | Recibe pedidos por webhook, valida, responde al instante y le pasa el pedido al Manager sin esperarlo |
| **Canal Telegram** | Recibe texto o notas de voz, transcribe (Whisper), descarta el audio, maneja el email dictado y pasa el pedido al Manager |
| **Manager** (coordinador) | Coordina el recorrido en 10 etapas (2.2) |
| **Worker 1 a 4** | Registrar, confirmar, consultar y modificar turnos en la agenda |
| **Herramienta RAG** | Búsqueda en la biblioteca oficial con Top-K y puntaje mínimo |
| **Juez (supervisor)** | Auditoría con rúbrica JSON de respuestas y acciones |
| **Escalado humano** | Registra el caso, avisa en Slack con botones y permite responderle al paciente |
| **Respuesta de voz** | Sintetiza y envía la nota de voz; no guarda ejecuciones |
| **Errores** | Alerta al equipo ante cualquier falla, con el `traceId` y los datos del paciente |
| **Freno de mano** | Pausa el sistema: todos los pedidos pasan a atención humana |
| **Ingesta KB** | Carga manual de la biblioteca oficial cuando cambian los documentos |

## 2.2 El recorrido de un pedido en 10 etapas

El lienzo del Manager está ordenado de izquierda a derecha en **10 etapas numeradas**, cada una en un marco con su explicación.

![Lienzo general del Manager: las 10 etapas](capturas/manager_general.png)

**1 · Entrada por canales.** Los cuatro canales llegan a un formato común (nombre, mensaje, canal, contacto). El email pasa antes por un filtro que frena las respuestas automáticas.

![Etapa 1](capturas/manager_etapa_01.png)

**2 · Trazabilidad e idempotencia.** Cada pedido recibe su `traceId` y una clave única por canal. Si la clave ya está registrada, el pedido se descarta: no se procesa ni se responde dos veces.

![Etapa 2](capturas/manager_etapa_02.png)

**3 · Seguridad: triaje y freno de mano.** Antes de cualquier modelo de IA, reglas fijas buscan señales del semáforo rojo (urgencia médica, dinero, reclamo legal, historia clínica). Ante una señal, el paciente recibe un texto fijo (en una urgencia, el 107 y la guardia 24 h) y el caso pasa a una persona. Con el freno de mano activo, todo va a atención humana.

![Etapa 3](capturas/manager_etapa_03.png)

**4 · Memoria y clasificación.** Se recupera la memoria del paciente y el coordinador clasifica el pedido (crear, modificar o consultar un turno; información; fuera de alcance) y extrae los datos.

![Etapa 4](capturas/manager_etapa_04.png)

**5 · Gestión de turnos con Juez.** La acción se resuelve contra la agenda y **el Juez la audita antes de escribir**. Si la acepta, los Workers registran o cambian el turno, se confirma, el contacto queda en HubSpot con sus metadatos y se arma el borrador de confirmación. Si la acción es dudosa, queda congelada y se aprueba o rechaza en Slack. Si faltan datos, se le pide al paciente lo que falta; el email, siempre por escrito.

![Etapa 5: vista general](capturas/manager_etapa_05.png)

![Etapa 5: después del veredicto, Workers, confirmación, CRM y avisos](capturas/manager_etapa_05b.png)

**6 · Consulta de turnos.** El Worker 3 lista los turnos futuros de la persona (solo lectura).

![Etapa 6](capturas/manager_etapa_06.png)

**7 · Consultas informativas con Juez.** El agente responde solo con la biblioteca oficial, cita la fuente o dice «No sé». El Juez evalúa cada respuesta: la acepta, la manda a corregir (como máximo dos veces) o la pasa a una persona en Slack para aprobarla o editarla.

![Etapa 7: agente, Juez y correcciones](capturas/manager_etapa_07a.png)

![Etapa 7: aprobación o edición humana y respuesta](capturas/manager_etapa_07b.png)

**8 · Registro y memoria.** Log de trazabilidad (si el email de log falla, una rama de error avisa a Slack y el pedido sigue), aviso a soporte y actualización de la memoria; cada 5 mensajes se resume la conversación.

![Etapa 8](capturas/manager_etapa_08.png)

**9 · Respuesta y comprensión.** Se arma la respuesta final. Si una misma persona tiene dos pedidos seguidos que el sistema no puede atender, el segundo pasa a una persona.

![Etapa 9](capturas/manager_etapa_09.png)

**10 · Despacho por el canal.** La respuesta sale por donde llegó: Telegram en voz (si el paciente habló) o en texto, el webhook (por Telegram o como borrador de Gmail), el chat o el email.

![Etapa 10](capturas/manager_etapa_10.png)

## 2.3 Asincronía e idempotencia

Un sistema externo (la web de turnos, una app o el CRM) manda `POST /webhook/agendabot` con `request_id`, `mensaje`, `nombre` y `email` o `tg_chat_id`. El **Receptor responde enseguida** y le pasa el pedido al Manager **sin esperarlo**; el análisis, el Juez y el registro ocurren en segundo plano, y el resultado sale por el canal del paciente.

| Situación (medido el 16/10/2026, corrida C) | Respuesta del Receptor | `traceId` |
|---|---|---|
| Consulta nueva | **202** "recibido" en 0,082 s | `trc-20261016024626-822-08y4` |
| El mismo `request_id` reenviado | **200** "duplicado", mismo `traceId`, sin procesar | `trc-20261016024626-822-08y4` |
| Petición sin `request_id` ni canal de respuesta | **400** con la lista de datos faltantes | — |
| Promedio de las 16 peticiones | 0,083 s (máximo 0,131 s) | — |

Las capas que evitan duplicar registros y envíos:

1. **Pedido:** la clave (`wh-` + `request_id`, `tg-` + id del mensaje de Telegram, `gm-` + id del email) se busca en la Data Table `pedidos_procesados` antes de procesar. La consulta y el registro tardan milisegundos, así que un reintento inmediato ya encuentra la clave.
2. **Agenda:** el Worker 1 escribe con *append or update* por ID (`T-` + clave), de modo que un reintento actualiza la misma fila en lugar de crear otra. Además, pedir un turno que ya existe responde "ya tenés ese turno; no hice cambios".
3. **CRM:** el contacto se escribe con *upsert* por email.
4. **Envíos:** un pedido repetido nunca llega a la etapa de despacho, así que no se manda dos veces la misma respuesta.

## 2.4 Memoria persistente y acople contextual

**Memoria de largo plazo** (Airtable, tabla `Memoria_Pacientes`, una fila por paciente): `Session_ID`, fecha de actualización, resumen consolidado, estado del caso, datos clave (paciente, motivo, turno), contador de mensajes y último `traceId`. Recorrido:

1. **Lectura:** se busca la fila del paciente por `Session_ID` (su email o su chat de Telegram).
2. **Paciente nuevo:** se crea la fila con *upsert*, sin campos vacíos que se inyecten en el prompt.
3. **Contexto:** el coordinador recibe el resumen y los datos clave; el agente de consultas, solo lo necesario para entender la pregunta.
4. **Conteo:** cada mensaje suma uno.
5. **Resumen:** al pasar los 5 mensajes, un modelo económico (Haiku 4.5) resume la conversación en JSON.
6. **Actualización:** *upsert* por `Session_ID`, sin duplicar filas.

**Memoria de sesión:** las últimas interacciones de la conversación, separadas para el coordinador y para el agente de consultas. Así el agente no arrastra contexto que no le corresponde.

**Contratos de datos entre especialistas.** Cada sub-workflow recibe solo los campos que necesita (un nodo *Set* antes de cada delegación los filtra y agrega el `traceId`) y devuelve una salida uniforme. Si un sub-workflow falla, la ejecución se corta y la rama de error avisa al equipo (2.5).

| Sub-workflow | Recibe (obligatorio) | Devuelve | Destinatario |
|---|---|---|---|
| AgendaBot · Receptor | `request_id`, `mensaje` (texto), `email` o `tg_chat_id`; opcional `nombre` | 202 `{estado, `traceId`, request_id, detalle}` · 200 "duplicado" · 400 `{estado, faltan[]}` | Sistema externo y Manager |
| Worker 1 (alta) | `traceId`, `idemKey`, `nombre`, `motivo`, `fecha` (dd/mm/aaaa), `hora` (hh:mm), `email` | `{`traceId`, status: "success", data: {id, nombre, fecha, hora, motivo, estado, email}}` | Manager → Worker 2 |
| Worker 4 (cambio) | `traceId`, `id` del turno, nueva `fecha` y/o `hora` | Igual que el Worker 1, con estado "Reprogramado" | Manager → Worker 2 |
| Worker 2 (confirmación) | Datos del turno confirmado | `{data: {mensaje}}` | Manager → paciente |
| Worker 3 (consulta) | `traceId`, `nombre` | `{data: {mensaje}}` con la lista de turnos futuros | Manager → paciente |
| Herramienta RAG | `consulta` (texto) | Fragmentos con fuente, sección y puntaje, o `SIN_RESULTADOS` | Agente de consultas |
| Juez | `tipo_caso` (RESPUESTA o ACCION), `pregunta`, `respuesta`, fragmentos o acción propuesta, agenda y fecha | `{exactitud_factual: 1..5, estado_veredicto: ACEPTADO / CORREGIR / RECHAZADO, critica, ruta}` | Manager (sigue, corrige o congela) |
| AgendaBot · Escalado humano | `traceId`, `categoria`, `canal`, `sessionId`, `mensaje`, `respuesta_fija`, contacto | Registro en `escalados` y decisión de la persona | Equipo en Slack → paciente |
| AgendaBot · Respuesta de voz | `texto_voz` (máx. 200 caracteres), `tg_chat_id` | `{enviado, audio_destruido: true}` | Paciente (Telegram) |

## 2.5 Robustez: qué pasa cuando algo falla

- **Reintentos:** cada API externa (Sheets, HubSpot, Airtable, Gmail, Slack, Telegram, modelos, Cohere, Qdrant) se reintenta 3 veces, con 2 segundos entre intentos.
- **Error Workflow:** cualquier falla del Manager, del Receptor o de un canal dispara el workflow **Errores**. Este workflow recupera la ejecución fallida, avisa en Slack **en castellano** (qué pasó, dónde, quién es el paciente, su mensaje y el `traceId`) y le avisa al paciente que hay demoras, por Telegram o por email.
- **Rama de error visible:** si falla el email de log, una rama avisa a Slack y el pedido sigue su curso.
- **Falla segura:** una acción congelada que nadie aprueba en 15 minutos **no se ejecuta**. El paciente recibe "tu pedido quedó en revisión".
- **Simulacro:** el workflow *Simulacro de falla* permite probar la alerta en cualquier momento.

**Fallas reales durante las pruebas y cómo respondió el sistema:**

| Qué pasó | Qué hizo el sistema | Qué se corrigió |
|---|---|---|
| Las planillas nuevas no estaban compartidas con la cuenta de n8n (Google respondió 403) | Alerta en Slack con el `traceId` y el paciente | Se compartieron las planillas con la cuenta de Google que usa n8n |
| Venció la autorización de Gmail | Alerta; el log falló pero el pedido siguió por la rama de error | Se reconectó la credencial; el retorno de OAuth quedó en localhost |
| Se agotó el saldo de la API de IA | Alerta: "Sin saldo en la API del proveedor de IA: hay que cargar crédito"; el triaje y las alertas siguieron andando | Se cargó crédito; se agregó la traducción de errores |
| La red pública bloqueó el túnel de Cloudflare | Telegram dejó de recibir; el resto siguió | Túnel con dominio fijo (ngrok, puerto 443) que se reconecta solo |
| Corte de red mientras una acción esperaba aprobación | La acción no se ejecutó (falla segura) | — |

## 2.6 La biblioteca oficial, con disciplina

- **Fuente única:** 16 documentos oficiales de la clínica, procesados con LlamaParse, divididos por secciones con su ruta de títulos (195 fragmentos) e indexados en Qdrant con embeddings de Cohere. Los datos de la razón social y fiscales se reemplazaron por datos ficticios (anonimización).
- **Búsqueda con umbral:** se devuelven los 5 fragmentos más parecidos (Top-K 5), pero **solo si superan un puntaje de 0,60**. Si ninguno lo supera, el agente responde **«No sé: ese dato no figura en la documentación de la clínica»** en lugar de inventar.
- **Citas con metadatos reales:** cada respuesta cierra con `[Fuente: documento — sección]`, tomada del fragmento recuperado.

**Equivalencia con el nodo nativo de n8n:**

| | *Vector Store Retrieve Tool* nativo de n8n | Herramienta implementada (*AgendaBot · Herramienta RAG*) |
|---|---|---|
| Nombre y descripción para el agente | Sí | Sí ("consultar_conocimiento") |
| Top-K | Sí | Sí (5) |
| Puntaje mínimo | **No disponible** | **Sí (0,60)**: por esto se implementó como sub-workflow |
| Conexión al índice | Qdrant | Qdrant (`kb_lodetincho`), por su API de búsqueda |
| Salida | Fragmentos | Fragmentos con fuente, sección y puntaje, o `SIN_RESULTADOS` |
