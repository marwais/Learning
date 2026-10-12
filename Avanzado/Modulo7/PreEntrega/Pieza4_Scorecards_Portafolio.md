# 4. Scorecards y versión de portafolio

Los agentes razonan con dos rúbricas fijas y públicas para el equipo, de modo que la misma entrada dé siempre la misma decisión y cada decisión cite su evidencia.

## Scorecard A — Validación de respuestas informativas (implementada)

La usa el **Validador** (Claude Haiku) sobre cada respuesta del Agente RAG. La evidencia son **los fragmentos de la base documental recuperados en ese mismo turno**; nada de lo que dice la respuesta puede salir de otro lado.

| Criterio | Pregunta que se hace | Evidencia exigida | Si falla |
|---|---|---|---|
| 1. Respaldo de cada dato | ¿Cada dato concreto sobre la clínica (teléfonos, mails, profesionales, horarios, precios, cifras, direcciones, servicios) está en los fragmentos? Saludos, el nombre del paciente y la sugerencia de llamar a la Central de Turnos no cuentan como datos | Texto de los fragmentos | **Rechazo** → sale la respuesta segura: "No cuento con ese dato en la documentación de la clínica…" |
| 2. Cita de fuente | Si la respuesta usa datos de los fragmentos, ¿incluye al menos una cita `[Fuente: …]`? | La cita | Rechazo |
| 3. Regla "No sé" | Si la respuesta dice que no tiene el dato, ¿se abstiene de agregar datos ausentes de los fragmentos? | Fragmentos | Rechazo |
| Excepción | Un saludo o una respuesta sin datos de la clínica se aprueba aunque no haya fragmentos | — | — |

Los fragmentos que recibe el validador son solo los recuperados **en ese turno**: si el agente no consultó la base, el validador recibe "(el asistente no consultó la base documental)" y cualquier dato concreto queda sin respaldo.

**Salida:** `{aprobado: true|false, motivo}`. Resultado en el M5: 5 de 5 respuestas correctas en la validación ciega y 0 falsos rechazos del validador en la regresión.

## Scorecard B — Prioridad y ruta de cada pedido (diseño)

La aplica el **triaje**, armado con nodos **IF y Switch** de n8n (sin código), con los datos que extrae el Router. Puntaje de 0 a 100; **cada criterio rojo alcanza por sí solo el umbral de escalado**, para que la rúbrica coincida con el semáforo de la pieza 3. Las listas de palabras clave (urgencias, dinero y temas legales) salen de un **protocolo escrito y versionado** por la dirección médica y la administración: es la evidencia documental contra la que se puntúa.

| Criterio | Peso | Cómo se puntúa | Evidencia |
|---|---|---|---|
| Señal clínica de alarma | 35 % | 35 si aparece una palabra o patrón de la lista de urgencias | Texto del mensaje (y transcripción si fue audio) |
| Dinero, aspecto legal o datos sensibles | 25 % | 25 si menciona reintegro, cobro, cobertura, reclamo, abogado, denuncia, historia clínica o datos de otra persona | Texto del mensaje |
| Riesgo de abandono (churn) | 20 % | 20 si tiene más de 2 cancelaciones en 30 días | Planilla de turnos y memoria (Airtable) |
| Confianza del entendimiento | 20 % | 10 con una falla de comprensión o un audio ilegible; 20 con dos seguidas | Contrato de datos y evaluación de la transcripción |

| Puntaje | Ruta |
|---|---|
| 0–9 | 🟢 Autónomo (flujo normal) |
| 10–19 | 🟡 Autónomo, sin congelamiento, con auditoría diaria |
| 20 o más | 🔴 Escalado forzado a Slack (pieza 3) |

Cualquier criterio rojo suma 20 o más por sí solo: **una urgencia, un tema de dinero o legal, un riesgo de churn o dos fallas seguidas siempre llegan a un humano**.

## Versión de portafolio (anonimizada)

**Asistente de turnos multicanal con IA para una clínica ambulatoria.** Diseño y construcción, en n8n (low-code: la lógica de decisión vive en nodos visuales y agentes; el código se limita a dar formato a los datos), de un sistema multi-agente que atiende la central de turnos por chat, email y notas de voz. Un agente clasificador entiende el pedido; especialistas acotados registran, modifican y consultan turnos en la agenda; un agente de conocimiento responde con la documentación oficial y un segundo modelo audita cada respuesta antes de enviarla. Incluye memoria del paciente, respuesta por voz de menos de 200 caracteres, protección de datos (los audios no se guardan) y un semáforo de riesgo que deriva urgencias, reclamos y temas de dinero a una persona. **Resultados esperados del piloto:** 60 % de resolución autónoma, más de 120 horas mensuales liberadas y atención las 24 horas. *Stack:* n8n, Claude (Anthropic), Qdrant, Whisper, ElevenLabs, Google Sheets, Airtable, HubSpot, Gmail, Slack y Telegram.
