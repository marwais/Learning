# 4. Scorecards y versión de portafolio

Los agentes razonan con rúbricas fijas: la misma entrada da siempre la misma decisión y cada decisión cita su evidencia.

## Scorecard A — Validación de respuestas informativas (implementada)

La aplica el **Validador** (Claude Haiku) a cada respuesta del Agente RAG. Evidencia: **los fragmentos de la base documental recuperados en ese mismo turno**.

| Criterio | Pregunta | Si falla |
|---|---|---|
| 1. Respaldo de cada dato | ¿Cada dato concreto (teléfonos, mails, profesionales, horarios, precios, cifras, direcciones, servicios) está en los fragmentos? Saludos y la sugerencia de llamar a la Central no cuentan como datos | **Rechazo** → respuesta segura: "No cuento con ese dato en la documentación de la clínica…" |
| 2. Cita de fuente | Si usa datos de los fragmentos, ¿incluye al menos un `[Fuente: …]`? | Rechazo |
| 3. Regla "No sé" | Si dice que no tiene el dato, ¿se abstiene de agregar datos ausentes? | Rechazo |
| Excepción | Un saludo sin datos de la clínica se aprueba aunque no haya fragmentos | — |

Salida: `{aprobado, motivo}`. En el M5: 5 de 5 respuestas correctas en validación ciega y 0 falsos rechazos del validador.

## Scorecard B — Prioridad y ruta de cada pedido (diseño)

La aplica el triaje, armado con nodos **IF y Switch** (sin código), con los datos que extrae el Router. Puntaje de 0 a 100; cada criterio rojo alcanza solo el umbral de escalado (coincide con el semáforo). Las listas de palabras clave salen de un **protocolo escrito y versionado** por la dirección médica: es la evidencia documental.

| Criterio | Peso | Cómo se puntúa | Evidencia |
|---|---|---|---|
| Señal clínica de alarma | 35 % | 35 si aparece una palabra o patrón de la lista de urgencias | Mensaje o transcripción |
| Dinero, legal o datos sensibles | 25 % | 25 si menciona reintegro, cobro, cobertura, reclamo, abogado, denuncia, historia clínica o datos de terceros | Texto del mensaje |
| Riesgo de abandono (churn) | 20 % | 20 si tiene más de 2 cancelaciones en 30 días | Planilla de turnos y memoria |
| Confianza del entendimiento | 20 % | 10 con una falla de comprensión o audio ilegible; 20 con dos seguidas | Contrato de datos |

**Ruta:** 0–9 → 🟢 autónomo · 10–19 → 🟡 autónomo, con auditoría diaria · 20 o más → 🔴 escalado a Slack. **Una urgencia, un tema de dinero o legal, un churn o dos fallas seguidas siempre llegan a un humano.**

## Versión de portafolio (anonimizada)

**Asistente de turnos multicanal con IA para una clínica ambulatoria.** Diseño y construcción en n8n (low-code: la lógica vive en nodos visuales y agentes; el código solo da formato a los datos) de un sistema multi-agente que atiende la central de turnos por chat, email y notas de voz. Un agente clasificador entiende el pedido; especialistas acotados registran, modifican y consultan turnos; un agente de conocimiento responde con la documentación oficial y un segundo modelo audita cada respuesta antes de enviarla. Incluye memoria del paciente, respuesta por voz breve, protección de datos (los audios no se guardan) y un semáforo de riesgo que deriva urgencias, reclamos y temas de dinero a una persona. **Resultados esperados del piloto:** 60 % de resolución autónoma, más de 120 horas mensuales liberadas y atención las 24 horas. *Stack:* n8n, Claude, Qdrant, Whisper, ElevenLabs, Google Sheets, Airtable, HubSpot, Gmail, Slack y Telegram.
