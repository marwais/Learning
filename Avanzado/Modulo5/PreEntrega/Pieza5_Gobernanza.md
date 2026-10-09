# Pieza 5 — Plan de gobernanza de la base de conocimiento (RAG)

**Base de conocimiento:** 16 documentos institucionales de la Clínica LoDeTincho (sitio anonimizado). **Parseo:** LlamaParse, tier Agentic → markdown versionado en `kb_md/`. **Indexado:** n8n, un fragmento por sección → embeddings Cohere `embed-multilingual-v3.0` → **Qdrant persistente**, colección `kb_lodetincho_m5` (195 fragmentos). **Recuperación:** Top-K = 5, Minimum Score = 0.60. **Generación:** Claude Sonnet 4.6, con memoria del paciente. **Validación de salida:** Claude Haiku 4.5.

Objetivo: mantener la base **vigente, consistente y verificable**, y definir **cada cuánto se revisa, quién es responsable y con qué criterio se da de baja o se reemplaza un documento**.

---

## 1. Roles y responsabilidades

| Rol | Responsable | Función |
|---|---|---|
| **Dueño del conocimiento** | Referente administrativo/clínico de la institución | Aprueba qué entra a la base, valida la exactitud y autoriza bajas y reemplazos. Es la fuente de verdad ante conflictos. |
| **Curador técnico** | Responsable del flujo n8n | Ejecuta el parseo y la re-ingesta, controla el *chunking*, el Top-K, el Min Score y el system prompt, y corre las validaciones. |
| **Revisor de calidad** | Rotativo (puede ser el curador) | Corre el set de preguntas ciegas, registra la precisión y las alucinaciones, y abre acciones correctivas. |
| **Responsable de seguridad** | Referente de sistemas | Gestiona credenciales y API keys, accesos y anonimización. |

---

## 2. Cadencia de revisión

| Qué se revisa | Frecuencia | Responsable | Disparador adicional |
|---|---|---|---|
| **Vigencia de contenidos** (cartilla, horarios, canales de contacto, novedades) | **Mensual** | Dueño del conocimiento | Cualquier cambio operativo real (alta o baja de un profesional o servicio, cambio de horario o canal) |
| **Calidad del RAG** (set de preguntas ciegas + precisión) | **Mensual** y **después de cada re-ingesta** | Revisor de calidad | Respuestas reportadas como incorrectas |
| **Fidelidad del parseo** (texto parseado contra documento original) | **Después de cada re-parseo** | Curador técnico | Cambio de tier o versión de LlamaParse |
| **Consistencia entre documentos** (datos repetidos en conflicto) | **Trimestral** | Dueño del conocimiento | Respuestas que muestran dos valores |
| **Parámetros del RAG** (Top-K, Min Score, chunking, prompt, modelo) | **Trimestral** (recalibrar el umbral con preguntas dentro y fuera de la base) | Curador técnico | Caída de precisión o fallas de recuperación recurrentes |
| **Datos con vencimiento** (certificados impositivos, novedades con fecha) | **Antes de cada vencimiento** | Dueño del conocimiento | Fecha de fin de vigencia (por ejemplo, certificado de IIBB hasta el 31/10/2026) |
| **Seguridad y credenciales** (API keys, tokens OAuth) | **Trimestral** | Responsable de seguridad | Credencial vencida o sospecha de exposición |

---

## 3. Ciclo de vida del documento

1. **Alta:** el Dueño aprueba el documento → se anonimiza → se guarda el `.docx` en `documentacion/` → `python scripts/update_kb.py` (parsea con LlamaParse y carga el markdown en n8n) → en n8n, **▶ Ingerir KB (RAG)** (recrea la colección de Qdrant y la vuelve a llenar) → `python scripts/verify_qdrant.py`.
2. **Actualización:** se cambia **siempre el documento fuente**, nunca el índice ni el markdown a mano. Se re-parsea solo ese documento y se re-ingiere. Como la ingesta recrea la colección, nunca conviven dos versiones del mismo contenido.
3. **Baja o reemplazo:** se aplican los criterios de la sección 4. Se borra o reemplaza el `.docx` (y su `.md`) y se re-ingiere.
4. **Trazabilidad:** documentos, markdown parseado, workflows exportados y scripts se versionan en Git. Cada respuesta del bot cita `[Fuente: documento — sección]`.

---

## 4. Criterios de baja o reemplazo

Un documento **se da de baja o se reemplaza** cuando:

- **Quedó desactualizado:** un horario, profesional, canal o política que ya no rige. Un dato vencido indexado es peor que no tenerlo, porque induce respuestas falsas con apariencia de verdad (y con cita).
- **Venció su vigencia:** novedades con fecha, certificados o convenios. Si no se renuevan, se retiran en la fecha de fin.
- **Fue derogado o discontinuado:** un servicio que dejó de ofrecerse.
- **Existe una versión nueva:** se reemplaza el archivo; no conviven versiones.
- **Contradice a otra fuente** y el Dueño define cuál prevalece: la fuente perdedora se corrige o se retira.
- **Contiene datos personales o sensibles**, o **rompe la anonimización:** se corrige o se retira.

Toda baja o reemplazo la **aprueba el Dueño** y la **ejecuta el Curador**. Queda registrada en el historial de commits.

---

## 5. Hallazgos de esta entrega y acciones

| Hallazgo | Evidencia | Acción |
|---|---|---|
| **Dato en conflicto:** camas de internación | 160 (*Institucional — Filosofía*) contra 140 (*Residencias*). El bot informa ambos valores con su fuente. | El Dueño define el valor vigente y se corrige el documento erróneo. Revisión trimestral de cifras repetidas. |
| **Anonimización incompleta** | *Datos impositivos* y *Política de confidencialidad* nombran a "OMINT"; el bot atribuye esos datos a "la clínica". | Completar la anonimización o aclarar en el documento la relación entre la clínica y la razón social. |
| **El parser alteró texto** | LlamaParse (tier Agentic) cambió "Billinghurst" por "Billinghamurst" y "lodetincho" por "lodetinho" en 5 documentos. | Control automático después de cada parseo: comparar las palabras del `.md` contra el texto del `.docx` y revisar las diferencias antes de ingerir. |
| **Datos en tablas con recuperación frágil** | En la pregunta de IIBB Mendoza, la primera búsqueda devolvió 0 fragmentos sobre 0.60; recuperó al reformular. | Enriquecer los fragmentos de tabla con una frase descriptiva, o sumar búsqueda híbrida (palabras clave + vectores). |
| **Tablas con varias normas en una celda** | En la regresión, el bot respondió "19/12 y 30/99" para la percepción de IIBB Mendoza (correcto: 30/99); el validador no lo detecta porque el texto existe en la fuente. | Enriquecer los fragmentos de tabla con una frase que nombre cada columna; revisar las respuestas sobre tablas en el set ciego. |
| **Datos con vencimiento** | Certificados de no retención con vigencia hasta el 31/07/2026 y el 31/10/2026. | Agendar la revisión antes de cada vencimiento (sección 2). |

---

## 6. Control de calidad

- **Set de preguntas ciegas:** al menos 5, con al menos una cuya respuesta esté fuera de la base y una basada en una tabla. Se renuevan las preguntas en cada corrida, para no "entrenar al examen", y se registran la precisión, las alucinaciones, la fidelidad de la cita y las fallas de recuperación.
- **Umbral de aceptación:** **≥ 80 % de precisión y 0 alucinaciones.** Por debajo, se abre una acción correctiva antes de dar la base por "sana". Último resultado: 5/5 y 0 alucinaciones (pieza 4).
- **Recalibración del Min Score:** si cambia el modelo de embeddings o el chunking, se repite la calibración (scores de preguntas dentro y fuera de la base) antes de fijar el umbral.
- **Validador de salida:** cada respuesta del RAG queda marcada como `aprobada`, `rechazada` o `no disponible`, con el motivo. En cada revisión mensual se leen los rechazos: un rechazo repetido sobre el mismo tema indica un documento faltante, un fragmento mal cortado o una regla del prompt que hay que ajustar. El validador controla respaldo, no interpretación (ver pieza 4), así que no reemplaza al set de preguntas ciegas.
- **Herramienta de auditoría:** `python scripts/ver_ejecuciones.py` muestra, para las últimas consultas, la intención detectada, la respuesta enviada, el resultado del validador (y la respuesta bloqueada, si la hubo), las búsquedas que hizo el agente y los scores obtenidos.

---

## 7. Infraestructura y riesgos operativos

- **Vector store persistente:** Qdrant en Docker con volumen propio, así que la base sobrevive a reinicios. Solo se re-ingiere cuando cambia la documentación.
- **Credenciales con vencimiento:** durante esta entrega **venció el token OAuth de Gmail**, y la rama de log y respuesta por email falló hasta reconectarlo. Se incluye en la revisión trimestral de credenciales, y la alerta es cualquier ejecución en error.
- **Sub-workflows publicados:** en n8n 2.x, la herramienta RAG y los workers solo se pueden llamar si están **publicados**. Después de editarlos, hay que volver a publicar.
- **URL de webhooks:** `WEBHOOK_URL` tiene que apuntar a una URL viva. Un túnel temporal caído deja sin funcionar el chat y los webhooks.
- **Costo de parseo:** el tier Agentic consume unos 400 créditos por re-parseo completo (plan gratis: 10.000). Se re-parsea solo lo que cambió (`parse_kb.py` sin `--force`).
- **Dependencia de proveedores:** LlamaCloud, Cohere y Anthropic. Ante una caída, el bot sigue respondiendo con la base ya indexada (Qdrant es local); solo se frena la re-ingesta si falla LlamaParse o Cohere.

---

## 8. Seguridad y privacidad

- La base contiene **solo información pública institucional**: no se ingieren datos de pacientes.
- Las API keys (n8n, LlamaCloud) viven en `scripts/.env`, fuera de Git. Las de Cohere y Anthropic, como credenciales cifradas de n8n.
- La anonimización de la marca se verifica en cada alta (ver hallazgo "OMINT").

---

## Resumen ejecutivo

La base se revisa **mensualmente** (vigencia y calidad, con preguntas ciegas), **después de cada re-parseo** (fidelidad del texto) y **trimestralmente** (consistencia, parámetros del RAG y credenciales). El **Dueño del conocimiento** aprueba altas, bajas y reemplazos, y el **Curador técnico** los ejecuta re-parseando y re-ingiriendo, siempre desde el documento fuente. Un documento se **retira o reemplaza** cuando queda desactualizado, vence, se deroga, aparece una versión nueva, contradice a otra fuente o rompe la privacidad o la anonimización. La calidad se exige en **≥ 80 % de precisión y 0 alucinaciones**, y la trazabilidad la dan la cita de fuente en cada respuesta y el versionado en Git.
