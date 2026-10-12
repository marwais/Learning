# 2. Arquitectura multi-agente y mapa de permisos

Router que clasifica, triaje (Switch) que deriva, especialistas acotados; quien escribe datos no usa LLM y el único que redacta texto libre pasa por un validador.

{{DIAGRAMA}}

| Rol | Misión | System Prompt constitutivo (extracto) | Herramientas | Entrega (JSON → a quién) |
|---|---|---|---|---|
| **Router** (Claude Sonnet 4.6) | Entender el pedido; no responde | "Taxonomía CERRADA: CREAR, MODIFICAR, CONSULTAR, INFO, FUERA_DE_ALCANCE. No inventes datos." | Memoria de sesión | `{intent, nombre, motivo, fecha, hora, email}` + `riesgo` (propuesto) → Switch |
| **W1 / W4** Registrar y modificar (sin LLM) | Alta o reprogramación | Reglas deterministas | Sheets: alta / editar fila | `{ok, id_turno, estado}` → W2 |
| **W3** Consultar (sin LLM) | Listar los turnos de la persona | — | Sheets: lectura | `{mensaje, turnos[]}` → respuesta |
| **W2** Confirmación (sin LLM) | Confirmación clara | Plantilla fija | HubSpot y Gmail (borrador), vía el Manager | `{mensaje}` → HubSpot y Gmail (borrador) |
| **Agente RAG** (Claude Sonnet 4.6) | Responder con la base documental | "Usá EXCLUSIVAMENTE los fragmentos… 'No sé'… Citá la fuente… Voz: máx. 200 car." | Qdrant: lectura (Top-K 5, Min Score 0,6) | `{respuesta, fragmentos}` → Validador |
| **Validador** (Claude Haiku 4.5) | Auditar cada respuesta del RAG | "Todo dato concreto, en los fragmentos; cita obligatoria." | — | `{aprobado, motivo}` → respuesta o texto seguro |
| **Resumidor de memoria** (Claude) | Consolidar la charla cada 5 mensajes | "Resumen analítico, no transcripción." | Airtable: upsert | `{resumen, datos_clave, estado}` → Airtable |

**Context Engineering:** Router → mensaje, canal, estado, resumen y datos clave del paciente · workers → solo el JSON del contrato · Agente RAG → pregunta, memoria (solo para personalizar) y fragmentos **de ese turno** · validador → pregunta, respuesta y fragmentos.

**Permisos por rol (mínimo privilegio).** L = lectura · E = escritura · — = sin acceso.

| Rol | Sheets Agenda | Airtable Memoria | Qdrant | Gmail | HubSpot | Slack | Telegram |
|---|---|---|---|---|---|---|---|
| Router (agente) | — | — | — | — | — | — | — |
| Manager (orquestación) | L | L/E | — | E | — | E | E |
| W1 Registrar | E | — | — | — | — | — | — |
| W4 Modificar | L/E | — | — | — | — | — | — |
| W3 Consultar | L | — | — | — | — | — | — |
| Confirmación (W2) | — | — | — | E | L/E | — | — |
| Agente RAG | — | L | L | — | — | — | — |
| Resumidor de memoria | — | E | — | — | — | — | — |
| Escalado HITL | — | L | — | E | — | L/E | — |

El Router no lee bases (el Manager le pasa el contexto) y el Validador no accede a ningún conector; solo la ingesta manual escribe en Qdrant. Alcances: Gmail solo borradores y hilo; Slack solo `#soporte`; Telegram solo el mismo chat; HubSpot solo contactos; Airtable solo su tabla. **Ajustes:** cuenta de servicio de Google limitada a la planilla; claves de Qdrant de lectura y de escritura separadas; límite de gasto en OpenAI y ElevenLabs.
