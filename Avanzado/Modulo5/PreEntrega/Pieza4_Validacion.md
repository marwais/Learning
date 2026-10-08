# Pieza 4 — Reporte de validación (5 preguntas ciegas)

**Sistema evaluado:** AgendaBot M5, de punta a punta: chat → Router (intent INFO) → Agente RAG (Claude Sonnet 4.6) → herramienta `consultar_conocimiento` (Qdrant, Top-K = 5, Min Score = 0.60, embeddings Cohere multilingual v3) → respuesta.
**Protocolo:** 5 preguntas que **no se usaron** en la calibración del umbral ni como ejemplo en el prompt; una de ellas con respuesta **fuera de la base**. Cada respuesta se verificó contra el markdown fuente (`kb_md/`).

## Resultados

| # | Pregunta | Dato esperado (fuente) | Respuesta del RAG | Cita emitida | Resultado |
|---|---|---|---|---|---|
| 1 | ¿Cuánto dura la residencia de Clínica Médica y cuántas vacantes tiene? | 4 años; 9 vacantes (5 LoDeTincho + 4 Clínica del Sol) — *Residencias* | "4 años, en modalidad becario… 9 en total — 5 para Clínica LoDeTincho y 4 para Clínica del Sol" | Residencias — Clínica Médica; Residencias › Ingreso | ✅ Correcto (pregunta de dos partes) |
| 2 | ¿Hasta qué hora puedo hacerme una tomografía sin contraste un sábado? | Sáb., dom. y feriados de 08:00 a 20:00 — *Diagnóstico por imágenes sin turno* | "hasta las 20:00 hs, con ingreso desde las 08:00 hs"; aclara que con contraste requiere turno | Diagnóstico por imágenes › Horarios de atención | ✅ Correcto |
| 3 | ¿Quién lidera las cirugías de labio leporino en pediatría? | Dr. Ricardo Bennun — *Nuevas prestaciones pediátricas* | "liderado por el Dr. Ricardo Bennun, especialista en cirugía plástica infantil y craneofacial" | Nuevas prestaciones pediátricas; Especialidades › Cirugía Plástica y Craneofacial Pediátrica | ✅ Correcto |
| 4 | ¿Qué resolución aplica como agente de percepción de Ingresos Brutos en Mendoza? | R.G. (ATM) 30/99 — *Datos impositivos*, **dato en tabla** | "agente de percepción bajo la R.G. (ATM) 30/99… retención R.G. (ATM) 19/12"; suma el certificado de no retención 22/07–31/10/2026 (nota 10 de la tabla) | Datos impositivos › Impuestos Provinciales; Notas aclaratorias | ✅ Correcto (ver análisis) |
| 5 | ¿Cuál es el horario de visitas para los pacientes internados? | **No está en la base** | "La documentación no especifica el horario general de visitas"; menciona textualmente que el parte médico de Guardia se da de 12 a 13 h durante la visita | Preguntas Frecuentes (parte médico) | ✅ Correcto (no inventó) |

## Métricas

- **Precisión (respuesta correcta y fiel a la fuente): 5/5 = 100 %.**
- **Fidelidad de la cita:** en 5/5 respuestas la sección citada contiene el dato usado.
- **Alucinaciones** (datos no presentes en la base): **0**.
- **Contingencia:** 1/1. La pregunta fuera de la base no recibió un dato inventado.

## Análisis crítico

- **#4: la recuperación de datos en tablas es frágil.** La primera búsqueda ("agente de percepción Ingresos Brutos Mendoza resolución") devolvió **0 fragmentos sobre 0.60**: un fragmento que es sobre todo una tabla genera un embedding "pobre" para una consulta corta. El dato apareció en la **reformulación** que exige el prompt. *Mejora propuesta:* enriquecer los fragmentos de tabla con una frase descriptiva ("Tabla de resoluciones de IIBB por provincia…") o sumar búsqueda híbrida (palabras clave + vectores).
- **#4: atribución.** El agente dice "la clínica actúa como agente", pero el documento habla de **OMINT S.A. de Servicios**: la anonimización de la base quedó incompleta en *Datos impositivos*. No es una alucinación del modelo, es un defecto de la fuente, y se registró en gobernanza (pieza 5).
- **#5: la contingencia no usó la frase fija.** Respondió que el dato no está y agregó un hecho relacionado **textual** (el parte médico), con cita. Es útil y no inventa, pero se aparta del formato literal pedido. Se acepta como correcto y queda como punto de ajuste fino.
- **Hallazgos de la calibración (fuera del set ciego) que mejoraron el sistema:**
  - Ante "¿Atienden mascotas?", el agente **dedujo una ausencia** a partir de la lista de especialidades. Se agregó la regla "la ausencia de un dato no es un dato".
  - Ante "¿Cuántas camas tiene?", reportó **ambos valores en conflicto** (160 según *Institucional* y 140 según *Residencias*), cada uno con su fuente.
  - El Router mandaba consultas informativas (CUIT, veterinaria) a FUERA_DE_ALCANCE. Se agregó una definición explícita de INFO.
- **Comparación con la primera versión.** Con *chunking* genérico, sin umbral y con otro modelo, la precisión había sido 3/5: un dato de contacto inventado y una especialidad no recuperada. Los cambios que explican la mejora son el **chunking por sección** (Cardiología ahora es un fragmento propio con sus profesionales), el **Minimum Score** y las reglas de fidelidad del prompt.
- **Limitaciones de la medición.** La muestra es chica (n = 5), los LLM no son deterministas (la misma pregunta puede variar levemente) y el evaluador es el mismo autor. El plan de gobernanza fija un set ampliado y periódico.
