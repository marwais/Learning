# Pieza 5 — Plan de gobernanza de la base de conocimiento (RAG)

**Base de conocimiento:** documentación de LoDeTincho (sitio institucional anonimizado), ingerida como vector store del agente RAG de AgendaBot. **Ingesta/parseo:** LlamaCloud (LlamaParse, tier *agentic*). **Vector store:** In-Memory (n8n) con embeddings Cohere `embed-multilingual-v3.0`, recuperación Top-K = 4. **Generación:** Gemini `gemini-flash-lite-latest`.

Objetivo del plan: mantener la base **vigente, consistente y verificable**, y definir con claridad **cada cuánto se revisa, quién es responsable y bajo qué criterio se elimina o reemplaza un documento**.

---

## 1. Roles y responsabilidades

| Rol | Responsable | Función |
|-----|-------------|---------|
| **Dueño del conocimiento** (Knowledge Owner) | Referente administrativo/clínico de la institución | Aprueba qué documentos entran, valida su exactitud y autoriza bajas/reemplazos. Fuente de verdad ante conflictos. |
| **Curador técnico** (Data/RAG Steward) | Responsable del flujo n8n | Ejecuta la ingesta/re-indexado, controla chunking, Top-K y el System Prompt; corre las validaciones periódicas. |
| **Revisor de calidad** | Rotativo (puede ser el mismo curador) | Corre el set de preguntas ciegas, registra precisión y alucinaciones, abre acciones correctivas. |
| **Responsable de seguridad** | Referente de sistemas | Gestiona credenciales (rotación de API keys), anonimización y accesos. |

---

## 2. Cadencia de revisión (cada cuánto se revisa)

| Qué se revisa | Frecuencia | Responsable | Disparador adicional |
|---------------|-----------|-------------|----------------------|
| **Vigencia de contenidos** (precios, horarios, cartilla, teléfonos, novedades) | **Mensual** | Dueño del conocimiento | Ante cualquier cambio operativo real (nueva especialidad, cambio de horario/teléfono, baja de un servicio) |
| **Validación de calidad** (set de preguntas ciegas + métrica de precisión) | **Mensual** y tras cada re-indexado | Revisor de calidad | Caída de precisión reportada por usuarios |
| **Consistencia entre documentos** (conflictos de datos) | **Trimestral** | Dueño del conocimiento | Al detectar respuestas contradictorias |
| **Parámetros del RAG** (Top-K, chunking, System Prompt, modelo) | **Trimestral** | Curador técnico | Fallas recurrentes de recuperación o alucinación |
| **Seguridad** (rotación de keys, accesos) | **Trimestral** | Responsable de seguridad | Sospecha de exposición de una key |

---

## 3. Ciclo de vida del documento

**Alta (ingesta):** el Dueño aprueba el documento → se anonimiza (marca institucional → LoDeTincho) → se parsea en LlamaCloud verificando que preserve jerarquía de títulos y tablas como celdas → se versiona en el repo (`Avanzado/Modulo5/documentacion/`) → se re-indexa el vector store.

**Actualización:** cualquier cambio se hace **sobre el documento fuente** (`.docx`), se re-versiona en el repo y se **re-corre la ingesta** (`▶ Ingerir KB`), que limpia e inserta la versión nueva (`Clear Store` activo). Nunca se edita el índice a mano.

**Baja / reemplazo:** ver criterios abajo.

---

## 4. Criterios de eliminación o reemplazo de un documento

Se **da de baja o reemplaza** un documento cuando:

- **Quedó desactualizado** (precio, horario, teléfono, cartilla o política que ya no rige). Un dato vencido indexado es peor que no tenerlo: induce respuestas incorrectas con apariencia de verdad.
- **Fue derogado o discontinuado** (un servicio/novedad que dejó de ofrecerse).
- **Existe una versión nueva** que lo sustituye: se reemplaza el `.docx`, se re-versiona y se re-indexa (no conviven dos versiones del mismo contenido).
- **Genera conflicto con otra fuente** y el Dueño define cuál prevalece (la fuente no ganadora se corrige o se retira).
- **Contiene datos sensibles o personales** que no deberían estar en la base (se retira o se anonimiza).

Regla operativa: toda baja/reemplazo la **aprueba el Dueño del conocimiento** y la **ejecuta el Curador** re-corriendo la ingesta; queda registrada en el historial de commits del repo (trazabilidad).

---

## 5. Reconciliación de conflictos (caso detectado)

Durante la validación se detectó un **conflicto real**: la cantidad de camas figura como **160** en *Institucional/Filosofía* y **140** en *Residencias*. 
- *Acción:* el Dueño define el valor correcto y se corrige el documento erróneo; hasta entonces se prioriza la fuente institucional. 
- *Prevención:* en la revisión trimestral de consistencia se buscan datos numéricos repetidos entre documentos y se unifican.

---

## 6. Control de calidad del RAG

- **Set de preguntas ciegas** (mínimo 5, incluyendo una fuera de la base): se corre mensualmente y tras cada re-indexado. Se registra **precisión** y se listan **alucinaciones** y **fallas de recuperación**.
- **Umbral de aceptación sugerido:** ≥ 80 % de precisión. Por debajo, se abre acción correctiva antes de considerar la base "sana".
- **Hallazgos de esta validación y sus mitigaciones:**
  - *Alucinación de datos de contacto* → endurecer el System Prompt ("listá solo datos textuales de los fragmentos") y/o guardrail que verifique mails/teléfonos contra los chunks.
  - *Falla de recuperación en listados* (Cardiología) → subir Top-K a 6–8 para consultas de listado y mejorar el chunking de Especialidades (un chunk por especialidad con su encabezado).
- **Auditabilidad:** toda respuesta basada en la base cierra con `[Manual: LoDeTincho - <sección>]`; la respuesta de contingencia ("No cuento con ese dato") no lleva cita. Esto permite rastrear el origen de cada dato.

---

## 7. Gestión técnica e infraestructura

- **Volatilidad del vector store:** el store In-Memory se **borra si se reinicia n8n** → tras cada reinicio hay que re-correr `▶ Ingerir KB`. Para producción se recomienda migrar a un vector store persistente (Pinecone/Qdrant/PGVector).
- **Límites de cuota (rate limit):** el free tier del proveedor de LLM devuelve **429** ante ráfagas. Mitigación aplicada: correr las consultas **espaciadas** (Loop + Wait) y **retry con backoff**. Para volumen real se requiere tier pago o control de concurrencia.
- **Resiliencia de proveedor:** ante incidentes del LLM (p. ej. 503), el agente tiene **retry automático**; como plan de contingencia se puede conmutar el modelo (este RAG quedó independizado en Gemini, separado del Anthropic del resto de AgendaBot).
- **Versionado:** documentos, workflows y configuración se versionan en Git (repo del proyecto) para trazabilidad y rollback.

---

## 8. Seguridad y privacidad

- **Anonimización** de la marca institucional en toda la base (LoDeTincho).
- **Rotación de API keys** (Cohere, Gemini) ante cualquier exposición; no se hardcodean en los nodos más allá de las credenciales cifradas de n8n.
- **Datos personales:** no se ingieren datos de pacientes ni información sensible en la base de conocimiento (solo información pública institucional).

---

## Resumen ejecutivo

La base se **revisa mensualmente** (vigencia + calidad) y **trimestralmente** (consistencia, parámetros, seguridad); el **Dueño del conocimiento** aprueba altas/bajas/reemplazos y el **Curador técnico** los ejecuta re-indexando; un documento se **elimina o reemplaza** cuando queda desactualizado, se deroga, aparece una versión nueva, entra en conflicto no resuelto o contiene datos sensibles. La calidad se controla con preguntas ciegas (umbral ≥ 80 %) y la trazabilidad se garantiza con la cita de fuente y el versionado en Git.
