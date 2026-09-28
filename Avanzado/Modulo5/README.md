# Módulo 5 — El Cerebro Documental de la IA (RAG con LlamaCloud)

Quinta etapa del proyecto integrador **AgendaBot** (curso AI Automation Avanzado, Coderhouse). Este módulo **parte de cómo quedó el Módulo 4** (multi-agente + memoria + integraciones OAuth2 + los 4 guardrails) y le suma el **cerebro documental**: un **RAG** (*Retrieval-Augmented Generation*) para consultar conocimiento **no estructurado** (manuales, políticas) de forma verificable y sin alucinar.

> **Barrido de la clase 5 completo** (133 min) → ver [`resumen-clase.md`](resumen-clase.md) y la guía visual (artifact "Módulo 5 — RAG": recorrido minutado + diagramas + las 5 piezas del entregable).

## Estado (scaffolding listo, partió del M4)
- **Workflows n8n** (duplicados del M4, repuntados a la carpeta/tabla del M5):
  - `AI Automation Avanzado - M5.json` (Manager, `f1Yl3BRwYouF660l`)
  - `Worker1_RegistrarTurno (M5).json` (`OhqlaD9owJHhZ0Xp`)
  - `Worker2_Confirmacion (M5).json` (`Ft8psvxAlilfFKuw`)
  - `Worker3_ConsultarTurno (M5).json` (`mC0rTN5ylCLiu6gX`)
  - `Worker4_ModificarTurno (M5).json` (`47lULDxTZa8YGKjj`)
- **Planilla** `Agenda_Turnos (05)` = `14NKpW0fGnngPTZmkgQssOQdj6-K4wVI13mIARFapT8A`, en carpeta Drive `05` (`1EGOcl6iRqRqRDee712UVaa_nk0ZfnCDN`). Columnas: ID, Fecha, Hora, Nombre, Motivo, Estado, Email.
- **Memoria** en la base única `Memoria_Agente` (`appO1XQ6layHvQx6e`), tabla **`Memoria_M5`** (`tblfxL2XyvTGtnvfl`). Mismos campos que M4.
- Credenciales reutilizadas (instancia): Gmail OAuth2, Slack OAuth2, HubSpot App Token, Anthropic, Google Sheets, Airtable.

## Contenido de la carpeta
- Workflows (JSON) del Manager + 4 workers.
- `Agenda_Turnos (05).csv` + `Agenda_Turnos (05) (esquema).json`.
- `Memoria_M5 (esquema).json` · `Memoria_M5 (create_table payload).json` · `Memoria_M5 (recrear).py` · `Memoria_M5 (registros).csv`.
- `modulo5.config.json` (config de export por módulo).

## Consigna oficial (Checkpoint de Ingesta Documental y Cerebro Documental)
Entregable: un único PDF `PreEntrega_Modulo5_NombreApellido.pdf` con **5 piezas** (cada una = un criterio de rúbrica):
1. Captura del **Data Source en LlamaCloud** (jerarquía de títulos + tablas como celdas) + 2–3 líneas.
2. Captura del nodo **Vector Store Retrieve Tool** con **Top-K** y **Minimum Score** + justificación del balance precisión/costo.
3. Captura de la estructura del **System Prompt RAG** (citar fuentes + regla "No sé").
4. **Reporte de validación** de 5 preguntas ciegas (tabla + métrica de precisión + análisis crítico).
5. **Plan de gobernanza** (cada cuánto se revisa, responsable, criterio de baja/reemplazo).

## Pendiente
- Implementar el RAG sobre este workflow: **LlamaCloud Data Source + Vector Store Retrieve Tool** (Top-K/Minimum Score) + **System Prompt RAG** (cita de fuente + "No sé").
- Correr la validación de las 5 preguntas ciegas y armar el PDF de entrega (a mano).

> Convención: una base Airtable `Memoria_Agente` con una tabla por módulo (`Memoria_M3/M4/M5`). Cada módulo tiene su carpeta `0N` en Drive con su propia `Agenda_Turnos`.
