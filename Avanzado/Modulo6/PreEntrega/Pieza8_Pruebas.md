# 8. Pruebas de punta a punta y hallazgos

Pruebas con notas de voz reales desde Telegram (11/10/2026), leídas de las ejecuciones de n8n:

| # | Nota de voz (transcripción de Whisper) | Ruta | Respuesta hablada | Resultado |
|---|---|---|---|---|
| 308 | "Y agéndame otro para una tomografía para el 11 de octubre a las 21.30." | CREAR_TURNO → Worker 1 → planilla 06 | "Hola Juan Carlos, tu turno de tomografía para el 11/10/2026 a las 21:30 quedó Asignado." (87 car., audio 6 s) | ✅ turno registrado y confirmado por voz |
| 321 | "¿Me decís que profesionales atienden cardiología?" | INFO → Agente RAG → validador (aprobada) | "Cardiología tiene tres profesionales. Dr. Fairman Enrique, Dra. Carolina Granada Ayala y Dr. Flavio Delfino. ¿Querés turno con alguno?" (134 car., audio 10 s) | ✅ dato de la base documental, con cita en el texto |
| 323 | "Sí, con Delfino para mañana a las 11 y 22." | turno (repregunta con memoria) | confirmación de 89 caracteres, audio 6 s | ✅ usó el contexto de la charla |
| 320 | (silencio) → "Subtítulos realizados por la comunidad de Amara.org" | contingencia | aviso por texto | ✅ alucinación detectada |
| 331 | "¿Y el precio del dólar blue ahora?" | FUERA_DE_ALCANCE | mensaje de límite (106 car.) | ✅ |
| 302 | Dicho: "Mi email es mwaisburd arroba gmail.com" → Whisper: "Mi email es mwhisbord arroba gmail.com" | turno | — | ❌ email mal transcripto → se agregó "pedir email por escrito" |

**Hallazgos**

- **Latencia:** de 18 a 21 s por pedido completo, contra el objetivo de 6–8 s de la unidad 4. Whisper tarda ~2 s y ElevenLabs ~2,5 s; el resto es el Manager heredado (Router, RAG, validador, memoria, logs de Slack y Gmail en serie). Próxima mejora: mandar el audio antes de los logs y la memoria.
- **Whisper alucina ante silencio** (pieza 6): la contingencia no puede limitarse a "texto vacío".
- **Los datos exactos no van por voz:** emails y listas largas se piden o entregan por escrito.
- **Telegram reintenta entregas** si el webhook demora: hace falta filtrar por `update_id`.
