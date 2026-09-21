# Módulo 1 — Checkpoint 1: Agente Base (Tools Agent)

Primera versión del **proyecto integrador** del curso *AI Automation Avanzado*.
Agente autónomo en n8n que actúa como **Coordinador de Agenda** ("AgendaBot").

## Entregable
- `checkpoint1_julio_waisburd.json` — flujo de n8n exportado (importable en n8n → *Import from File*).

## Arquitectura del flujo
| Nodo | Rol |
|------|-----|
| **When chat message received** | Disparador (Chat Trigger) que captura el mensaje del usuario |
| **AI Agent** (Tools Agent) | Cerebro; System Prompt modular (Rol → Ámbito → Objetivo → Reglas → Escalamiento) + guardrail de **máx. 8 iteraciones** |
| **Anthropic Chat Model** | Modelo de razonamiento (Claude Sonnet 5) |
| **Agenda_Turnos** (Google Sheets Tool) | Herramienta lateral: consulta/registra turnos. Descripción semántica extensa; columnas completadas por el modelo vía `$fromAI` |
| **Reporte de observabilidad** (Gmail) | Nodo final que envía el resultado del agente como log de supervisión humana |

## Validación
Probado con *Execute Workflow*: recorrido en verde, ciclo ReAct (modelo invocado 2×),
la tool se activó de forma autónoma y escribió la fila del turno, y se envió el email de observabilidad.

## Cómo crece (próximos módulos)
No se rehace desde cero: se parte de este `.json` y se extiende — memoria/contexto (M3),
integraciones reales (M4), RAG (M5), voz (M6)… hasta el Proyecto Final Integrador (M11).
