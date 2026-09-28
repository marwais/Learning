# Módulo 5 — El Cerebro Documental de la IA (Arquitecturas RAG con LlamaCloud)

**Curso:** AI Automation Avanzado (Coderhouse) · **Clase en vivo:** 2h 13m (133 min)
**Deck:** "Clase 5 — AI Automation Avanzado V2" (Coderhouse 2026, 38 slides)
**Guía visual:** artifact "Módulo 5 — RAG" (recorrido minutado + diagramas + las 5 piezas del entregable).

---

## Resumen

Hasta acá el agente **pensaba** (M2), **recordaba** (M3) y **actuaba** sobre apps reales (M4). El M5 le da lo que le faltaba: **conocimiento de negocio verificable**. Un LLM es un "genio aislado": sabe del mundo general pero no conoce tus precios, tus políticas ni tu manual de atención, y cuando le preguntan algo específico **alucina**. **RAG** (*Retrieval-Augmented Generation*) resuelve eso: en vez de responder de memoria, el flujo **recupera** los fragmentos relevantes de tus documentos y recién ahí **genera** la respuesta apoyándose en ellos.

Distinción que ordena el módulo: **memoria ≠ conocimiento**. La memoria (M4) recuerda *la conversación* con este usuario; el conocimiento (RAG) es la *base documental del negocio*: estable, compartida y auditable. La clase alterna teoría del deck, una infografía Sin RAG / Con RAG, y una demo larga en n8n (template "Demo: RAG in n8n" + el workflow real "Clase3_Avanzado" con Cohere + Simple Vector Store + Validator).

Idea central: el valor no es "cargar un PDF"; es **ingerir bien** (parseo + chunking), **recuperar con criterio** (Top-K / Minimum Score) y **contener al modelo** (System Prompt con cita de fuente y la regla del "No sé"), más una **gobernanza** que mantenga la base viva.

---

## Recorrido minutado (barrido completo)

Marcas: `slide` = deck · `n8n` = demo en vivo · `infografía` = imagen anotada · `plataforma` = temario Coderhouse.

| Min | Tema | Tipo |
|----:|------|------|
| 00–18 | Apertura y encuadre de la clase (cámara off) | — |
| 18–38 | **¿Por qué RAG?** — "El genio aislado", "Memoria vs conocimiento", "El paradigma RAG" | slide |
| 38–48 | **Sin RAG vs Con RAG** — explicación anotada del flujo de recuperación | infografía |
| 48–60 | **AI Agent sin RAG** — el agente responde genérico ("None of your tools were used"); doc de gobernanza NexusCorp | n8n |
| 60–75 | **Template "Demo: RAG in n8n"** — Load Data Flow + Retriever Flow; **vectorización / tokens**; Embeddings OpenAI | n8n |
| 75–95 | AI Agent "resumime tus servicios" → nodo **Gmail Send**; slide **"El System Prompt RAG — un embudo de contención"** | n8n / slide |
| 95–115 | **RAG en ejecución** — Embeddings de *La Odisea* en chunks; nodo **"Answer questions with a vector store"** (`Limit = 4`); workflow real **Clase3_Avanzado** (Cohere + Simple Vector Store + Validator) | n8n |
| 115–125 | **La consigna** — Checkpoint de Ingesta Documental: las 5 piezas del PDF + tabla de 5 preguntas ciegas | plataforma |
| 125–133 | **Actividades y cierre** — Clínica de Chunking, Hallucination Courtroom, Desafío de Diseño | plataforma |

---

## Conceptos clave (5 unidades)

1. **El cerebro documental** — el "genio aislado" alucina; RAG = recuperar + generar. Memoria (conversación) ≠ conocimiento (base documental estable y auditable).
2. **Procesamiento de documentos** — parseo con **LlamaCloud / LlamaParse** (preserva jerarquía de títulos y tablas como celdas, no texto plano); **chunking** (evitar la *orphaned reference*): 3 estrategias — **tamaño fijo**, **por estructura/headers**, **semántica**; **vectorización** con embeddings (mismo modelo para indexar y para buscar).
3. **Conexión de la base en n8n** — dos flujos: **Load Data Flow** (Upload → Insert Data to Store → Data Loader → Embeddings) y **Retriever Flow** (Chat → AI Agent + Chat Model + **Vector Store Retrieve Tool**). Parámetros del retrieve: **Top-K (Limit)** = cuántos fragmentos; **Minimum Score** = umbral de similitud. Balance **precisión ↔ costo de tokens**.
4. **Instrucciones de sistema (System Prompt RAG)** — "embudo de contención": **cuándo buscar** (términos de los manuales → activar la herramienta), **cuándo no** (saludos/cortesía sin consultar), **la regla dorada** (si no está en los fragmentos → *"No cuento con ese dato"*), y **citar la fuente** con etiqueta `[Manual: nombre]` para que sea auditable.
5. **Mantenimiento y gobernanza** — cada cuánto se revisa, quién es responsable, criterio para eliminar/reemplazar un documento. **Triaje de fallos** ("Hallucination Courtroom"): ¿existía el documento? → ¿fue indexado? → ¿la búsqueda lo encontró (Top-K/Min Score)? → ¿el re-ranker lo descartó?

### Actividades de la clase
- **Clínica de Chunking Avanzado** — proponer 3 estrategias de segmentación y justificar cuál preserva mejor el contexto.
- **Hallucination Courtroom (Triaje de Fallos)** — diagnosticar por qué el RAG dio una respuesta incorrecta, con el checklist de 4 preguntas.
- **Desafío de Diseño** — escalar una arquitectura RAG a miles de documentos.

---

## La demo en vivo

**Load Data Flow:** `Upload file → Insert Data to Store → Default Data Loader → Embeddings OpenAI` (indexa una vez).
**Retriever Flow:** `Chat Trigger → AI Agent (+ Chat Model + Memory) → Vector Store Retrieve Tool → (Gmail Send)` (consulta en cada mensaje).
Ambos comparten el **mismo nodo de embeddings** (indexar ⇄ buscar). En el workflow real *Clase3_Avanzado* el vector store se alimenta desde una planilla y un **Validator** controla la salida antes de escribir la respuesta.

---

## El entregable — `PreEntrega_Modulo5_NombreApellido.pdf` (5 piezas = 5 criterios de rúbrica)

1. **Captura del Data Source en LlamaCloud** — que se vea la jerarquía de títulos preservada y las tablas como celdas; + 2–3 líneas (qué documento y qué limpiaste).
2. **Captura del nodo Vector Store Retrieve Tool** — con **Top-K** y **Minimum Score**; + 2–3 líneas justificando el balance precisión/costo de tokens.
3. **Captura de la estructura del System Prompt RAG** — con la instrucción de citar fuentes y la regla del "No sé".
4. **Reporte de validación** — 5 preguntas ciegas en tabla, con métrica de precisión y análisis crítico de las fallas (ejemplo de la clase: **4/5 = 80%**; la falla del caso 5 fue de recuperación por sinónimo ambiguo → agregar chunk específico o ajustar Minimum Score).
5. **Plan de gobernanza** — cada cuánto se revisa, quién es el responsable, criterio para eliminar/reemplazar.

> Si falta una pieza, ese criterio queda en cero. El PDF con las capturas lo arma el alumno a mano; en el repo quedan versionados los workflows, la config y esta guía.

---

## Puente desde el Módulo 4

El M5 **parte del flujo del M4** (multi-agente + memoria + integraciones OAuth2 + guardrails) y le suma el cerebro documental. El agente pasa de leer/escribir **datos estructurados** (planillas, CRM) a consultar **conocimiento no estructurado** (manuales, políticas) de forma verificable y sin alucinar. Para llevar: *cargar un documento es fácil; el valor está en ingerir bien, recuperar con criterio y contener al modelo.*
