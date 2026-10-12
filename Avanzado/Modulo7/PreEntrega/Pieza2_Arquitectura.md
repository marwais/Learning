# 2. Arquitectura del sistema multi-agente y mapa de permisos

La coreografía es la de AgendaBot (construido del M1 al M6): un **Router** clasifica cada pedido y un **triaje determinista** (Switch) lo deriva a especialistas con alcance acotado. Ningún agente hace "todo"; los que escriben datos son workers sin LLM, y el único que redacta texto libre (Agente RAG) está controlado por un validador.

<div class="diagrama">
<svg viewBox="0 0 760 440" xmlns="http://www.w3.org/2000/svg" font-family="Segoe UI, Arial, sans-serif" font-size="10">
<defs><marker id="f" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#4b5563"/></marker></defs>
<g fill="#eef2f6" stroke="#0b3d5c" stroke-width="1">
<rect x="8" y="60" width="110" height="34" rx="5"/><rect x="8" y="110" width="110" height="34" rx="5"/><rect x="8" y="160" width="110" height="34" rx="5"/>
</g>
<g font-weight="600" fill="#0b3d5c"><text x="63" y="81" text-anchor="middle">Chat web</text><text x="63" y="131" text-anchor="middle">Email (Gmail)</text><text x="63" y="175" text-anchor="middle">Telegram</text></g>
<text x="63" y="188" text-anchor="middle" fill="#374151">voz (Whisper) o texto</text>
<text x="63" y="45" text-anchor="middle" font-weight="700" fill="#6b7280">CANALES</text>
<rect x="148" y="95" width="120" height="66" rx="6" fill="#fff7e6" stroke="#b45309"/>
<text x="208" y="116" text-anchor="middle" font-weight="600">Normalizar entrada</text><text x="208" y="131" text-anchor="middle">+ memoria del paciente</text><text x="208" y="146" text-anchor="middle" fill="#374151">(Airtable, sesión)</text>
<text x="208" y="45" text-anchor="middle" font-weight="700" fill="#6b7280">CONTEXTO</text>
<rect x="298" y="95" width="120" height="66" rx="6" fill="#e8f1fb" stroke="#1d4ed8" stroke-width="1.5"/>
<text x="358" y="116" text-anchor="middle" font-weight="700" fill="#1d4ed8">Router (AI Agent)</text><text x="358" y="131" text-anchor="middle">Claude Sonnet 4.6</text><text x="358" y="146" text-anchor="middle" fill="#374151">→ JSON: intent + datos</text>
<rect x="308" y="190" width="100" height="34" rx="5" fill="#ecfdf5" stroke="#047857"/>
<text x="358" y="211" text-anchor="middle" font-weight="600" fill="#047857">Triaje (Switch)</text>
<text x="358" y="45" text-anchor="middle" font-weight="700" fill="#6b7280">ORQUESTACIÓN</text>
<g fill="#ffffff" stroke="#047857">
<rect x="452" y="55" width="140" height="30" rx="5"/><rect x="452" y="93" width="140" height="30" rx="5"/><rect x="452" y="131" width="140" height="30" rx="5"/>
<rect x="452" y="170" width="140" height="46" rx="5" stroke="#1d4ed8"/><rect x="452" y="228" width="140" height="30" rx="5" stroke="#1d4ed8"/><rect x="452" y="270" width="140" height="30" rx="5" stroke="#6b7280"/>
</g>
<g text-anchor="middle"><text x="522" y="68" font-weight="600">W1 Registrar turno</text><text x="522" y="80" fill="#374151">Sheets: alta</text>
<text x="522" y="106" font-weight="600">W4 Modificar turno</text><text x="522" y="118" fill="#374151">Sheets: editar fila</text>
<text x="522" y="144" font-weight="600">W3 Consultar turno</text><text x="522" y="156" fill="#374151">Sheets: solo lectura</text>
<text x="522" y="184" font-weight="600" fill="#1d4ed8">Agente RAG (Claude)</text><text x="522" y="197" fill="#374151">consultar_conocimiento</text><text x="522" y="209" fill="#374151">Qdrant: solo lectura</text>
<text x="522" y="241" font-weight="600" fill="#1d4ed8">Validador (Claude Haiku)</text><text x="522" y="253" fill="#374151">respaldo en fragmentos</text>
<text x="522" y="283" font-weight="600" fill="#374151">Fuera de alcance</text><text x="522" y="295" fill="#374151">respuesta fija</text></g>
<text x="522" y="45" text-anchor="middle" font-weight="700" fill="#6b7280">ESPECIALISTAS</text>
<g fill="#ffffff" stroke="#0b3d5c">
<rect x="608" y="72" width="146" height="44" rx="5"/><rect x="608" y="180" width="146" height="44" rx="5"/>
</g>
<rect x="608" y="300" width="146" height="44" rx="5" fill="#fef2f2" stroke="#b91c1c" stroke-width="1.5"/>
<rect x="608" y="370" width="146" height="44" rx="5" fill="#f9fafb" stroke="#6b7280"/>
<g text-anchor="middle"><text x="681" y="89" font-weight="600">W2 Confirmación</text><text x="681" y="102" fill="#374151">Gmail: borrador · HubSpot</text>
<text x="681" y="197" font-weight="600">Respuesta al paciente</text><text x="681" y="210" fill="#374151">chat · email · voz (ElevenLabs)</text>
<text x="681" y="317" font-weight="700" fill="#b91c1c">Escalado HITL</text><text x="681" y="330" fill="#b91c1c">Slack con botones (propuesto)</text>
<text x="681" y="387" font-weight="600" fill="#374151">Trazabilidad</text><text x="681" y="400" fill="#374151">log Slack/Gmail · memoria</text></g>
<text x="681" y="45" text-anchor="middle" font-weight="700" fill="#6b7280">SALIDAS</text>
<g stroke="#4b5563" stroke-width="1.1" fill="none" marker-end="url(#f)">
<path d="M118,77 L148,118"/><path d="M118,127 L148,128"/><path d="M118,177 L148,140"/>
<path d="M268,128 L298,128"/><path d="M358,161 L358,190"/>
<path d="M408,200 C430,200 430,70 452,70"/><path d="M408,203 C432,203 432,108 452,108"/><path d="M408,207 C434,207 434,146 452,146"/>
<path d="M408,210 L452,193"/><path d="M408,216 C430,216 430,285 452,285"/>
<path d="M522,216 L522,228"/>
<path d="M592,70 C600,70 600,94 608,94"/><path d="M592,108 C600,108 600,94 608,94"/>
<path d="M592,243 C600,243 600,204 608,204"/><path d="M592,146 C600,146 600,196 608,196"/><path d="M592,285 C600,285 600,212 608,212"/>
<path d="M681,116 L681,180"/>
</g>
<g stroke="#b91c1c" stroke-width="1.2" stroke-dasharray="4 3" fill="none" marker-end="url(#f)">
<path d="M358,224 C358,322 500,322 608,322"/>
</g>
<text x="470" y="340" fill="#b91c1c">señales críticas (pieza 3)</text>
<g stroke="#9ca3af" stroke-width="1" stroke-dasharray="2 3" fill="none" marker-end="url(#f)"><path d="M681,344 L681,370"/></g>
</svg>
</div>

*Línea continua: delegación. Línea roja: escalado a humano. Los especialistas devuelven JSON al Manager; ninguno se comunica directamente con otro.*

## Fichas de los agentes

| Rol | Misión | System Prompt constitutivo (extracto) | Herramientas | Entrega (JSON → a quién) |
|---|---|---|---|---|
| **Router** (AI Agent, Claude Sonnet 4.6) | Entender el pedido y extraer datos; no responde al paciente | "Clasificá en una taxonomía CERRADA: CREAR_TURNO, MODIFICAR_TURNO, CONSULTAR_TURNO, INFO, FUERA_DE_ALCANCE… No calcules fechas; extraé solo números… No inventes datos." | Memoria de sesión; contexto de Airtable | `{intent, nombre, motivo, dia, mes, hora, *_ref, email}` + `riesgo` (propuesto, pieza 3) → Contrato de datos → Switch |
| **W1 Registrar turno** (sin LLM) | Dar de alta un turno validado | — (regla determinista) | Sheets `Agenda_Turnos`: alta | `{ok, id_turno, fecha, hora}` → W2 |
| **W4 Modificar turno** (sin LLM) | Reprogramar o cancelar el turno identificado | — | Sheets: actualizar la fila del turno | `{ok, id_turno, estado}` → W2 |
| **W3 Consultar turno** (sin LLM) | Listar los turnos de la persona | — | Sheets: solo lectura | `{mensaje, turnos[]}` → respuesta |
| **W2 Confirmación** (sin LLM) | Armar la confirmación en lenguaje claro | Plantilla fija | HubSpot (contactos) y Gmail (borrador), escritos por nodos del Manager a continuación | `{mensaje}` → HubSpot (contacto) y Gmail (borrador) |
| **Agente RAG** (AI Agent, Claude Sonnet 4.6) | Responder consultas informativas con la base documental | "Usá EXCLUSIVAMENTE los fragmentos de consultar_conocimiento… Regla 'No sé'… Citá la fuente… Canal de voz: máximo 200 caracteres." | `consultar_conocimiento` (Qdrant, Top-K 5, Min Score 0,60); memoria del paciente | `{respuesta, fragmentos}` → Validador |
| **Validador** (Claude Haiku 4.5) | Auditar cada respuesta del RAG contra los fragmentos del turno | "Aprobá solo si cada dato concreto está respaldado por los fragmentos recuperados." | — | `{aprobado, motivo}` → si rechaza, sale una respuesta segura |
| **Resumidor de memoria** (Claude) | Consolidar la charla cada 5 mensajes | "Resumen analítico, no transcripción; datos clave." | Airtable `Memoria_M6`: upsert | `{resumen, datos_clave, estado}` → Airtable |

## Context Engineering: qué recibe cada sub-workflow

| Destino | Recibe | No recibe (a propósito) |
|---|---|---|
| Router | Mensaje actual, estado del caso, resumen de la última charla, datos clave del paciente, canal | Agenda completa, base documental |
| Workers de turnos | Solo el JSON del contrato (nombre, motivo, fecha, hora, email, turno de referencia) | Historial de chat, memoria |
| Agente RAG | Pregunta, memoria del paciente (solo para personalizar) y los fragmentos recuperados **en ese turno** | Datos de turnos de otras personas |
| Validador | Pregunta, respuesta propuesta y fragmentos | Memoria, historial |
| Escalado HITL (propuesto) | Resumen del caso, señal crítica detectada, últimos 3 mensajes, contacto | Audios (se descartan, pieza 7 del M6) |

## Mapa de permisos por rol (mínimo privilegio)

**L** = lectura · **E** = escritura · **L/E** = ambas · — = sin acceso. Cada rol accede solo a lo que necesita su misión.

| Rol | Sheets `Agenda_Turnos` | Airtable `Memoria` | Qdrant (base documental) | Gmail | HubSpot | Slack | Telegram |
|---|---|---|---|---|---|---|---|
| Router (agente) | — | — (el contexto se lo pasa el Manager) | — | — | — | — | — |
| Manager (orquestación) | L (turnos de la persona) | L/E (solo su tabla) | — | E (borradores, respuesta en el hilo, log interno) | — | E (`#soporte`) | E (solo al mismo `chat_id`) |
| W1 Registrar turno | E (alta de fila) | — | — | — | — | — | — |
| W4 Modificar turno | L/E (solo la fila del turno) | — | — | — | — | — | — |
| W3 Consultar turno | L | — | — | — | — | — | — |
| Confirmación (W2 + contacto) | — | — | — | E (borrador) | L/E (solo contactos) | — | — |
| Agente RAG | — | L (memoria del paciente) | L | — | — | — | — |
| Validador | — | — | — | — | — | — | — |
| Resumidor de memoria | — | E (upsert en su tabla) | — | — | — | — | — |
| Escalado HITL (propuesto) | — | L | — | E (reenvío a coordinación) | — | L/E (mensaje y botones) | — |
| Ingesta de la base (manual) | — | — | E | — | — | — | — |

**Ajustes para llegar a este mapa** (hoy varias credenciales tienen más alcance que el necesario):
- **Google:** una cuenta de servicio con acceso solo a la planilla del módulo, y una credencial de solo lectura para W3; hoy es una credencial OAuth con acceso a todo el Drive.
- **Airtable:** token con *scope* a la tabla del módulo y sin permiso de borrado.
- **Qdrant:** clave de solo lectura para la herramienta RAG; la de escritura, solo para la ingesta manual.
- **HubSpot:** *scopes* solo de contactos, sin deals ni borrado. **Slack:** bot limitado al canal de soporte.
- **Gmail:** al paciente nunca se le envía un correo nuevo sin revisión: queda como borrador.
- **OpenAI y ElevenLabs:** límite de gasto mensual.
