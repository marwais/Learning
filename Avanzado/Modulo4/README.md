# Módulo 4 — Ecosistema de Herramientas e Integraciones

Cuarta entrega del proyecto integrador **AgendaBot** (curso AI Automation Avanzado, Coderhouse). El M4 **extiende** el workflow del M3 (nunca lo reemplaza) y suma la capa de **integraciones con herramientas reales vía OAuth2** y los **guardrails** de la rúbrica.

## Consigna (Checkpoint 4)

Interconectar el sistema multi-agente con **≥ 3 herramientas reales** vía OAuth2 (CRM tipo HubSpot/Salesforce, casilla de email de soporte, canal de notificación tipo Slack) y blindarlo con **4 controles preventivos**:

| # | Nodo | Previene |
|---|------|----------|
| ① | **IF anti auto-reply** (modo OR: `Auto-reply`, `Out of office`, `Undeliverable`, `no-reply@`) → Stop | bucle infinito de auto-respuestas |
| ② | **Look up** por email antes del Create (existe → Update / no existe → Create) | Error **409** (duplicado) |
| ③ | **Create Draft** (Gmail/Outlook) | guardrail HITL — la IA no envía sola |
| ④ | **Set** de limpieza + validación del payload (`From`, `Subject`, `BodyText`) | Error **400** (payload mal formado) |

**Entregable:** `checkpoint4_nombre_apellido.json` importable en un repositorio GitHub público (sin credenciales privadas). *El `.docx`/`.pdf` los genera el usuario a mano.*

## Contenido de la carpeta

Artefactos versionados de este módulo (convención de export por módulo):

- **Workflows n8n** (`{name,nodes,connections,settings}` vía API n8n):
  - `AI Automation Avanzado - M4.json` (Manager, `z0hgFQa3TPxlWFQn`) — **38 nodos**: agenda+memoria (M2+M3) + circuito de integración por email.
  - `checkpoint4_Waisburd_Julio_Martin.json` — **entregable** (mismo workflow exportado para importar/evaluar).
  - `Worker1_RegistrarTurno (M4).json` · `Worker2_Confirmacion (M4).json` · `Worker3_ConsultarTurno (M4).json` · `Worker4_ModificarTurno (M4).json`
- **Planilla Agenda_Turnos (04)** (Google Sheets `1FnfK-V607EYWt8jKoiuStdJ19iP9iikDlFOXcvIEb_U`, carpeta Drive `04`):
  - `Agenda_Turnos (04).csv` · `Agenda_Turnos (esquema).json` · `Agenda_Turnos (recrear).py`
- **Memoria Airtable** — base única `Memoria_Agente` (`appO1XQ6layHvQx6e`), tabla `Memoria_M4` (`tblaESzgrn2cxeBLT`):
  - `Memoria_M4 (esquema).json` · `Memoria_M4 (create_table payload).json` · `Memoria_M4 (recrear).py` · `Memoria_M4 (registros).csv`
- **Documentación:** `resumen-clase.md` (barrido minutado + conceptos).

## Estado

- Scaffolding M4 completo (Drive `04`, planilla, Manager + 4 workers duplicados del M3, tabla `Memoria_M4`). Token Airtable 200 OK.
- **Circuito de integración construido** sobre el workflow M4 (12 nodos nuevos, sin tocar la agenda+memoria existente):
  `Email entrante (Gmail Trigger) → ① IF anti auto-reply →` [true → Frenar] / [false → `④ Set limpieza → ② Buscar contacto (HubSpot) → Contacto existe?`] → [Actualizar / Crear] `→ Redactar respuesta (AI Agent + Anthropic) → ③ Crear borrador (Gmail) → Notificar (Slack)`.
- **Pendiente (requiere login en n8n):** conectar credenciales **OAuth2 de HubSpot** (nodos Buscar/Actualizar/Crear contacto) y **Slack** (Notificar). Gmail y Anthropic ya usan las credenciales existentes. Luego re-exportar el `checkpoint4_...json` final y subirlo al repo GitHub público.

> Convención: una base Airtable `Memoria_Agente` con una tabla por módulo (`Memoria_M3`, `Memoria_M4`, …) para reusar el permiso del token. Recrear = `create_table` sobre la base existente.
