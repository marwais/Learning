# Módulo 8 — Evaluación Automática y Mejora Continua de Agentes

**Curso:** AI Automation Avanzado (Coderhouse) · **Clase en vivo:** 06/10/2026, 2h 02m (122 min) — "Evaluación Automática y Mejora Continua de Agentes"
**Material de la unidad:** documento "Módulo 8" en Drive (unidades 1–3) + en la plataforma la unidad 4 "Simulación y A/B testing de arquitecturas agénticas" y el Podcast EP 8.

> Barrido por cuadros **cada 1 minuto** de punta a punta. Claude ve slides y demos, **no el audio**.

---

## Resumen

El M8 agrega la **capa de supervisión**: un **Juez** (otro LLM, con su propio prompt y modelo) evalúa la respuesta del agente contra una **rúbrica en JSON**, y un **Switch** reacciona: aceptar, corregir (el agente reintenta con la crítica, con tope de intentos) o escalar a un humano. Después se miden **precisión, HITL y coste** con un A/B de arquitecturas y se proyecta a escala. "Supervisar no es observar: es juzgar y reaccionar."

---

## Recorrido de la clase

| Min | Tema | Tipo |
|----:|------|------|
| 00–10 | Apertura (cámara apagada) y docente en cámara | — |
| 12 | **Agenda**: 1) el supervisor AI-as-a-Judge · 2) métricas de valor · 3) mejora continua · 4) break · 5) práctica en vivo: tu supervisor + A/B · 6) Pre-entrega 8: QA automatizado y dashboard | slide |
| 13–20 | **Autonomía sin supervisión es riesgo — por qué no alcanza el self-critique**: un agente inteligente no basta, tiene que ser fiable y auditable; pedirle al mismo agente que se revise sufre sesgo de confirmación; la solución es separar roles (Ejecutor hace, Juez evalúa contra una rúbrica) | slide |
| 21–23 · 38 · 41–42 | **¿Qué mira el Juez? — el contexto de la ejecución**: query original, contexto RAG, logs de herramientas, respuesta final | slide |
| 24–26 · 44 · 47–49 | **La rúbrica en JSON — cuantificar para automatizar**: el Juez devuelve score, estado (aprobado/corregir/rechazado), errores y justificación; umbrales: score < 8 reintenta, rechazado escala, score ≥ 9 sale automático; por criticidad: "horarios de oficina" con 7 alcanza, "configurar firewall" exige 10 | slide |
| 27–37 · 39–40 · 43 · 45–46 · 50–58 | **Demo n8n (sobre el clasificador del M7)**: se agrega un nodo **Revisor** (AI Agent + Cohere) después del AI Clasificador. Errores en vivo ("No prompt specified": el agente esperaba `chatInput`; se pasa a *Define below*). System prompt: "Auditor Senior de Calidad de IA (LLM-as-a-Judge)…"; prompt con **criterios** (precisión de clasificación, contexto RAG, herramientas, calidad y tono) y **estructura JSON** (`evaluacion_general` con puntaje, estado "Aprobado / Requiere Revisión / Fallido", `resumen_ejecutivo`, `detalle_criterios`, hallazgos, desviaciones, `sugerencia_prompt`); se activa *Require Specific Output Format*. Resultado: puntaje 0,6 / "Requiere Revisión" | demo |
| 59 | Salida del modelo (Cohere `command-a-03-2025`) | demo |
| 60 | **Las cuatro rutas — la reacción del sistema**: 1) aceptar (sale al canal y se guarda como ejecución exitosa) · 2) corregir (vuelve al Ejecutor con el feedback, máximo 2 intentos) · 3) reintentar (no encontró info: cambia de herramienta o amplía el contexto) · 4) escalar (sigue mal o hay riesgo: Wait for Webhook y aprobación humana en Slack) | slide |
| 61–74 | Demo: **IF** sobre la salida del Revisor ("contiene Aprobado") → rama true/false; iteraciones del prompt del Juez | demo |
| 75 | Plataforma: "Checkpoint: supervisor, mejora y dashboards listos para validación" | plataforma |
| 80–90 | Demo **HITL**: Slack *Send and Wait for Response* (tipo Approval) y luego **Gmail › Send and Wait** ("REVISION", botones Approve/Decline); error de OAuth de Gmail y reconexión; el mail llega con el JSON del Juez y los botones; IF sobre `data.approved` | demo |
| 92 | **"Supervisar no es observar: es juzgar y reaccionar."** Eso transforma un juguete de IA en un sistema de grado industrial | slide |
| 96–99 | **El error del conteo — ejecutar no es valor**: "procesó 5.000 correos": si 2.000 fueron alucinados es riesgo acumulado; el valor tiene 3 caras (ROI económico, reducción de fricción, precisión técnica); ¿cuánto ahorramos y qué tan seguro es? Demo: nodo **Summarize** (Count) | slide + demo |
| 100–113 | Plataforma: unidad 2 (ROI y TCO, HITL Rate, latencia percibida, KPIs técnicos: tool-call success, alucinación en RAG, fallback, planning depth; "Consultant's Dashboard"; errores: medir sin baseline, *tokens drift*, sobre-automatización) y unidad 3 (versionado de prompts, taxonomía de errores, reescritura guiada) | plataforma |
| 115–121 | Demo **ciclo de corrección**: nodo **Reescribir** (AI Agent) en la rama *false* del IF: "Reescribir {{ salida del Revisor }} para que cumpla con los criterios de revisión" → vuelve a pasar por la revisión | demo |

## Ideas que se aplican al proyecto
- **Separar Ejecutor y Juez** (no self-critique) y darle al Juez el contexto completo: query, contexto recuperado, respuesta.
- **Salida estructurada** del Juez; un Switch/IF que no dependa de texto libre.
- **Corrección con tope** (máximo 2) y **escalado humano** con Wait / Send and Wait.
- **Medir** precisión, HITL y coste, no cantidad de ejecuciones.
