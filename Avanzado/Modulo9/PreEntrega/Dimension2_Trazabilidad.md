# Dimensión 2 — Logs estructurados y trazabilidad (traceId)

## Panel operativo: el tablero del M8 con traceId

No se armó un panel nuevo. Se reutilizó la planilla de veredictos del M8, copiada como **`QA_Veredictos (09)`**. Cada ejecución del Juez agrega una fila desde n8n (nodo *Registrar veredicto*) con:

- las columnas del M8: fecha, origen, intento, pregunta, respuesta, exactitud, veredicto, crítica, ruta y `execution_id`;
- **siete columnas nuevas**: `traceId`, `timestamp`, `nodeName`, `toolOutput`, `systemPromptSnapshot`, `confidenceScore` y `log_json`.

La pestaña **KPIs** calcula, con fórmulas sobre esas filas, las ejecuciones totales, las que tienen traceId, la resolución autónoma, el HITL, la satisfacción y las horas ahorradas (captura en la Dimensión 1).

En la captura, las filas de arriba son del M8 y no tienen traceId. La última (ejecución 484) es del M9 y ya trae `traceId`, `timestamp`, `nodeName`, `toolOutput` y `systemPromptSnapshot`.

![QA_Veredictos (09): filas del M8 sin traceId y fila del M9 con las columnas de log](capturas/04_qa_veredictos_traceid.png)

## Esquema del log JSON (máquina-procesable)

El nodo **Armar log de auditoría**, en el sub-workflow `SUPERVISOR_Judge (M9)`, arma un objeto por cada decisión del Juez y lo guarda en la columna `log_json`. Antes de guardarlo **enmascara PII** (emails, DNI y teléfonos).

![Sub-workflow SUPERVISOR_Judge (M9) con el nodo Armar log de auditoría](capturas/02_supervisor_log_auditoria.png)

| Campo | Tipo | Qué registra |
|---|---|---|
| `timestamp` | ISO 8601 | Momento exacto de la decisión |
| `traceId` | texto | Id único del mensaje del paciente; el mismo en todas las ejecuciones relacionadas |
| `parentExecutionId` / `executionId` | texto | Ejecución del Manager que llamó / ejecución del Juez |
| `environment` | texto | Desarrollo o producción |
| `nodeName` | texto | Nodo que decidió (Juez) y `agentNode` que generó la respuesta (Agente RAG) |
| `toolOutput` | texto | Lo que devolvió la herramienta `consultar_conocimiento` (fragmentos con fuente y score), enmascarado y recortado a 1.500 caracteres |
| `systemPromptSnapshot` | objeto | Versión de la rúbrica del Juez + `sha256` de su prompt: dice qué instrucciones estaban vigentes |
| `confidenceScore` | 0–1 | `exactitud_factual` del Juez / 5 |
| `decision` | objeto | `estado_veredicto`, `ruta` (aceptar / corregir / escalar) e `intento` |

Log real de la ejecución 476 (primer intento, que el Juez mandó a corregir):

```json
{
 "timestamp": "2026-10-13T00:21:40.649Z",
 "traceId": "trc-20261013002123-473-gz6k",
 "parentExecutionId": "473",
 "executionId": "476",
 "environment": "desarrollo (n8n local)",
 "nodeName": "SUPERVISOR_Judge (M9) › Juez (LLM con JSON Schema)",
 "agentNode": "Agente RAG (Consultas)",
 "toolOutput": "[Fragmento 1] fuente: Diagnóstico por imágenes sin turno | sección: Horarios de atención para estudios sin turno | score: …",
 "systemPromptSnapshot": { "version": "juez-rubrica-v1 (M8)", "sha256": "35d6665b59a9" },
 "confidenceScore": 0.6,
 "decision": { "estado_veredicto": "CORREGIR", "ruta": "corregir", "intento": 1 }
}
```

**Versionado del prompt.** Cuando en el M9 se sumó el criterio de objetividad a la rúbrica (Dimensión 3), el snapshot pasó de `v1 · 35d6665b59a9` a **`juez-rubrica-v2 · d121785de282`**. Así, al auditar una decisión de hace un mes, se sabe con qué rúbrica se tomó.

## Cómo viaja el traceId por los sub-workflows

**Generar traceId** es el primer nodo después de *Normalizar entrada*, el punto donde se juntan chat, Gmail y Telegram. Crea `trc-<fecha>-<executionId del Manager>-<sufijo>`. Desde ahí se pasa **a mano** a cada llamada:

- un nodo Set **traceId → Worker N** antes de cada Worker;
- un input `traceId` en la herramienta RAG;
- un campo `traceId` en el caso que va al Juez.

Cada sub-workflow lo devuelve en su respuesta.

<svg viewBox="0 0 800 250" width="100%" xmlns="http://www.w3.org/2000/svg" font-family="Segoe UI, Arial" font-size="11">
<defs><marker id="f" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#0b3d5c"/></marker></defs>
<rect x="5" y="95" width="105" height="50" rx="6" fill="#eef2f6" stroke="#0b3d5c"/><text x="57" y="115" text-anchor="middle">Chat · Gmail</text><text x="57" y="131" text-anchor="middle">Telegram (voz)</text>
<rect x="135" y="95" width="120" height="50" rx="6" fill="#0b3d5c"/><text x="195" y="116" text-anchor="middle" fill="#fff" font-weight="bold">Generar traceId</text><text x="195" y="132" text-anchor="middle" fill="#fff">trc-…-473-gz6k</text>
<rect x="280" y="95" width="110" height="50" rx="6" fill="#eef2f6" stroke="#0b3d5c"/><text x="335" y="116" text-anchor="middle">Router +</text><text x="335" y="132" text-anchor="middle">Switch de intención</text>
<line x1="110" y1="120" x2="133" y2="120" stroke="#0b3d5c" marker-end="url(#f)"/><line x1="255" y1="120" x2="278" y2="120" stroke="#0b3d5c" marker-end="url(#f)"/>
<g stroke="#0b3d5c" fill="none"><path d="M390,110 C430,110 430,30 470,30" marker-end="url(#f)"/><path d="M390,115 C430,115 430,80 470,80" marker-end="url(#f)"/><path d="M390,125 C430,125 430,160 470,160" marker-end="url(#f)"/><path d="M390,130 C430,130 430,215 470,215" marker-end="url(#f)"/></g>
<rect x="472" y="12" width="175" height="36" rx="5" fill="#fff" stroke="#0b3d5c"/><text x="559" y="34" text-anchor="middle">Worker 1 Registrar / 4 Modificar</text>
<rect x="472" y="62" width="175" height="36" rx="5" fill="#fff" stroke="#0b3d5c"/><text x="559" y="84" text-anchor="middle">Worker 2 Confirmación</text>
<rect x="472" y="142" width="175" height="36" rx="5" fill="#fff" stroke="#0b3d5c"/><text x="559" y="164" text-anchor="middle">Worker 3 Consultar</text>
<rect x="472" y="197" width="175" height="36" rx="5" fill="#fff" stroke="#0b3d5c"/><text x="559" y="214" text-anchor="middle">Agente RAG → Tool RAG</text><text x="559" y="228" text-anchor="middle">→ SUPERVISOR_Judge</text>
<g fill="#0b3d5c" font-size="10"><text x="398" y="52">traceId</text><text x="425" y="100">traceId</text><text x="420" y="152">traceId</text><text x="398" y="198">traceId</text></g>
<g font-size="10" fill="#333"><text x="655" y="34">→ Agenda_Turnos (09)</text><text x="655" y="84">→ respuesta</text><text x="655" y="164">→ respuesta</text><text x="655" y="214">→ QA_Veredictos (09)</text></g>
<text x="135" y="175" font-size="10" fill="#333">También: Memoria_M9 (Ultimo_traceId)</text><text x="135" y="190" font-size="10" fill="#333">y asunto del email de log</text>
</svg>

![Manager AI Automation Avanzado - M9 (vista general)](capturas/03_manager_m9_vista_general.png)

**Evidencia: trazas reales de las pruebas del M9** (cada ejecución hija recibió el traceId del Manager):

| traceId | Pedido del paciente | Ejecuciones relacionadas | Dónde quedó |
|---|---|---|---|
| `trc-20261013001937-465-ptj8` | Sacar turno de cardiología | Manager 465 → **Worker 1** 466 → **Worker 2** 467 | Fila del turno en `Agenda_Turnos (09)` |
| `trc-20261013002059-470-vbzw` | ¿Qué turnos tengo pendientes? | Manager 470 → **Worker 3** 471 | `Memoria_M9.Ultimo_traceId` |
| `trc-20261013002123-473-gz6k` | Horario de tomografías + CUIT | Manager 473 → Tool RAG 474, 475 → **Juez** 476 (CORREGIR) → Tool RAG 477, 478 → **Juez** 479 (ACEPTADO) | 2 filas en `QA_Veredictos (09)` |
| `trc-20261013002017-469-igej` | Intento de prompt injection | Manager 469 (Router → FUERA_DE_ALCANCE) | Email de log |

**Auditoría retroactiva.** Para auditar un caso:

1. Filtrar `QA_Veredictos (09)` por `traceId`.
2. Ver cuántos intentos hubo, qué fragmentos leyó el agente (`toolOutput`), con qué rúbrica lo juzgó el Juez (`systemPromptSnapshot`) y qué decidió.

3. Con el mismo id, ubicar el turno en la agenda y la fila de memoria del paciente.

**Retención.**

- En producción, el Manager **no guarda ejecuciones exitosas** (compliance del M6). La pista de auditoría es el log estructurado y enmascarado.
- **Propuesta:** el detalle técnico de n8n solo se guarda durante las pruebas; los logs de auditoría (`QA_Veredictos`) se conservan 2 años.
