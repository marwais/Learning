# Pieza 4 — Reporte de validación (5 preguntas ciegas)

**Sistema evaluado:** Agente RAG de LoDeTincho (n8n) · **Recuperación:** Vector Store In-Memory con **Top-K = 4** · **Embeddings:** Cohere `embed-multilingual-v3.0` · **LLM de generación:** Google Gemini `gemini-flash-lite-latest` · **Ejecución:** en bucle de a 1 pregunta con espera de 15 s entre consultas (para respetar el rate limit del free tier).

> Nota: durante la validación la API de Anthropic tenía un incidente activo (503) y Gemini free tier devolvía 429 al enviar las 5 consultas en ráfaga; se resolvió corriendo las preguntas **espaciadas** (Loop + Wait). Esto quedó documentado como riesgo operativo en el plan de gobernanza (pieza 5).

## Tabla de resultados

| # | Pregunta | Dato esperado (fuente) | Respuesta del RAG | Cita emitida | Resultado |
|---|----------|------------------------|-------------------|--------------|-----------|
| 1 | ¿A qué teléfono y por qué canales puedo solicitar un turno? | 0800-666-6587; WhatsApp +54911 4493-2017; miportalclinicas.com.ar (doc *Turnos/Inicio*) | Teléfono 0800-666-6587 y WhatsApp +549 11 4493-2017 correctos, **pero agregó "Mail: mwquiero@gmail.com"** que NO figura en la base | `[Manual: LoDeTincho - Clínica LoDeTincho — Inicio]` | ⚠️ Parcial (alucinación de un dato) |
| 2 | ¿Qué profesionales atienden Cardiología? | Dr. Fairman Enrique / Dra. Carolina Granada Ayala / Dr. Flavio Delfino (doc *Especialidades*) | Listó especialidades cardíacas **relacionadas** (Ecocardiografía, Eco Doppler, Electrofisiología, Cardiología Infantil) pero **no** los tres cardiólogos exactos | `[Manual: LoDeTincho - Pacientes — Especialidades]` | ⚠️ Falla de recuperación (no trajo el fragmento exacto) |
| 3 | ¿La maternidad cuenta con UCIN? | Sí, UCIN nivel 3 (doc *Maternidad*) | "Sí, UCIN nivel 3, máxima complejidad, para recién nacidos de alto riesgo…" — correcto y completo | `[Manual: LoDeTincho - Maternidad en Clínica LoDeTincho]` | ✅ Correcto |
| 4 | ¿Cuántas camas de internación tiene la clínica? | 160 camas (doc *Institucional/Filosofía*) | "160 camas para internación" — correcto | `[Manual: LoDeTincho - Institucional — Filosofía]` | ✅ Correcto |
| 5 | ¿Cuánto sale una consulta particular sin obra social? | **No está en la base** | "No cuento con ese dato. Te sugiero comunicarte con la Central de Turnos." | (sin cita, correcto) | ✅ Correcto (regla de contingencia) |

## Métrica

**Precisión: 3/5 = 60 %** (respuestas completas y fieles a la fuente: #3, #4, #5). Las preguntas #1 y #2 fueron parcialmente correctas con fallas identificadas.

## Análisis crítico de las fallas

- **#1 — Alucinación de un dato de contacto.** El modelo respondió correctamente teléfono y WhatsApp (presentes en la base) pero **agregó un mail que no existe en la documentación**. Es una alucinación aditiva: aunque citó la fuente, incorporó un dato no respaldado.
  - *Acción correctiva:* endurecer el System Prompt ("listá **únicamente** los canales de contacto que aparezcan textualmente en los fragmentos; no completes con datos plausibles"). Alternativa: post-validación con un guardrail que verifique que los mails/teléfonos de la respuesta existan en los chunks recuperados.

- **#2 — Falla de recuperación por granularidad de chunk.** La entrada exacta "Cardiología → Dr. Fairman / Dra. Granada / Dr. Delfino" no entró en el Top-K = 4; se recuperaron fragmentos de especialidades cardíacas vecinas. El agente respondió con lo disponible en vez de decir "no sé", porque *algo* relacionado sí se recuperó.
  - *Acción correctiva:* (a) subir Top-K a 6–8 para consultas de listado; (b) mejorar el *chunking* de la sección Especialidades (un chunk por especialidad con su encabezado, para que "Cardiología" y su cuerpo médico queden juntos y sean recuperables); (c) reforzar el prompt para distinguir "la especialidad exacta consultada" de "especialidades relacionadas".

- **Observación de gobernanza (dato en conflicto).** La cantidad de camas figura como **160** en *Institucional/Filosofía* y como **140** en *Residencias*. El RAG tomó 160 (fuente institucional). Es un conflicto de fuentes a reconciliar → ver pieza 5.

## Aciertos destacados

- La **regla de contingencia "No cuento con ese dato" funcionó** perfecto (#5): ante una consulta fuera de la base, no inventó.
- La **cita de fuente** `[Manual: LoDeTincho - <sección>]` se emitió en las 4 respuestas basadas en la documentación y se **omitió** correctamente en la respuesta de contingencia (#5).
- Las respuestas fieles (#3, #4) reprodujeron el dato exacto de la fuente correcta.
