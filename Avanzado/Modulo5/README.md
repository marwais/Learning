# Módulo 5 — (kickoff)

Quinta etapa del proyecto integrador **AgendaBot** (curso AI Automation Avanzado, Coderhouse). Este módulo **parte de cómo quedó el Módulo 4** (multi-agente + memoria + integraciones OAuth2 + los 4 guardrails) y le sumará lo que pida la consigna del M5.

> Según el puente del M4, el M5 es el **"cerebro documental"** de la IA: un **RAG** para leer conocimiento **no estructurado**. Falta el barrido del video y la consigna oficial; esto es solo el andamiaje inicial.

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

## Pendiente
- Barrido del video de la clase 5 + resumen/guía.
- Consigna oficial del M5 (RAG / cerebro documental) e implementación sobre este workflow.
- `resumen-clase.md` y el entregable del módulo.

> Convención: una base Airtable `Memoria_Agente` con una tabla por módulo (`Memoria_M3/M4/M5`). Cada módulo tiene su carpeta `0N` en Drive con su propia `Agenda_Turnos`.
