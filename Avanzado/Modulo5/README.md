# Módulo 5 — El Cerebro Documental de la IA (RAG con LlamaCloud)

Quinta etapa del proyecto integrador **AgendaBot** (curso AI Automation Avanzado, Coderhouse). Este módulo **parte de cómo quedó el Módulo 4** (multi-agente + memoria + integraciones OAuth2 + los 4 guardrails) y le suma el **cerebro documental**: un **RAG** (*Retrieval-Augmented Generation*) para consultar conocimiento **no estructurado** (manuales, políticas) de forma verificable y sin alucinar.

> **Barrido de la clase 5 completo** (133 min) → ver [`resumen-clase.md`](resumen-clase.md) y la guía visual (artifact "Módulo 5 — RAG": recorrido minutado + diagramas + las 5 piezas del entregable).

## Estado — RAG implementado (rehecho desde el M4, 2026-10-07)
- **Workflows n8n** (el Manager se volvió a crear a partir del M4, apuntado a los recursos del M5):
  - `AI Automation Avanzado - M5.json` (Manager, `ciy1C6pB26Urfmlj`): M4 + ruta **INFO** → **Agente RAG** + circuito de ingesta **▶ Ingerir KB**.
  - `Tool_ConsultarConocimiento (M5).json` (`aEnYAA9K1l7YAwRj`): herramienta del agente con **Top-K = 5 y Min Score = 0.60** (Cohere → Qdrant `/points/search`).
  - `Worker1..4 (M5).json`: sin cambios respecto del M4, salvo los IDs de recursos.
- **Base de conocimiento:** 16 documentos de `documentacion/` → **LlamaParse (Agentic)** → `kb_md/*.md` → chunking por sección → **Qdrant** `kb_lodetincho_m5` (195 fragmentos).
- **Planilla** `Agenda_Turnos (05)` = `14NKpW0fGnngPTZmkgQssOQdj6-K4wVI13mIARFapT8A`. **Memoria** en `Memoria_Agente`, tabla `Memoria_M5` (`tblfxL2XyvTGtnvfl`).
- **Pre-entrega:** `PreEntrega/PreEntrega_Modulo5_JulioMartinWaisburd.pdf`, generado con `PreEntrega/build_pdf.py` a partir de `Pieza1..5_*.md` y `capturas/`. Validación ciega: 5/5.
- **Runbook:** [`scripts/README.md`](scripts/README.md).
- **Intento 1** (In-Memory/Gemini → Qdrant, ingesta directa de los .docx): archivado en n8n como "M5 (intento 1)" y en el tag de git `m5-intento1`.

## Contenido de la carpeta
- Workflows (JSON): Manager, herramienta RAG y 4 workers.
- `documentacion/`: los .docx fuente. `kb_md/`: markdown parseado por LlamaParse.
- `PreEntrega/`: las 5 piezas (.md), capturas, `build_pdf.py` y el PDF.
- `scripts/`: parseo, carga, verificación, auditoría y export.
- `Agenda_Turnos (05)…`, `Memoria_M5…`, `modulo5.config.json` (artefactos de datos del módulo).

## Consigna oficial (Checkpoint de Ingesta Documental y Cerebro Documental)
Entregable: un único PDF `PreEntrega_Modulo5_NombreApellido.pdf` con **5 piezas** (cada una = un criterio de rúbrica):
1. Captura del **Data Source en LlamaCloud** (jerarquía de títulos + tablas como celdas) + 2–3 líneas.
2. Captura del nodo **Vector Store Retrieve Tool** con **Top-K** y **Minimum Score** + justificación del balance precisión/costo.
3. Captura de la estructura del **System Prompt RAG** (citar fuentes + regla "No sé").
4. **Reporte de validación** de 5 preguntas ciegas (tabla + métrica de precisión + análisis crítico).
5. **Plan de gobernanza** (cada cuánto se revisa, responsable, criterio de baja/reemplazo).

## Pendiente
- Reconectar la credencial **Gmail account** en n8n (venció el token OAuth): sin eso fallan la rama de log y la respuesta por email.
- Revisar y subir el PDF de la pre-entrega.

> Convención: una base Airtable `Memoria_Agente` con una tabla por módulo (`Memoria_M3/M4/M5`). Cada módulo tiene su carpeta `0N` en Drive con su propia `Agenda_Turnos`.
