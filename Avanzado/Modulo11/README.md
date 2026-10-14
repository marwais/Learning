# Módulo 11 — Proyecto Final Integrador

Última etapa de **AgendaBot**: ensamblar todo en un sistema **asincrónico, idempotente y supervisado** (Componente A, en n8n) y defenderlo en el **DMSA** (Componente B, PDF `Waisburd_JulioMartin_ProyectoFinal_AI_Experto.pdf`). **Plazo: 13/11/2026 20:59.**

- Consigna completa, rúbrica y pasos de la clínica de integración → [`consigna.md`](consigna.md)
- Clase y teoría → [`resumen-clase.md`](resumen-clase.md). La clase es la misma del M10.
- Devoluciones de los profesores (P1 a P4) → [`devoluciones.md`](devoluciones.md)

## Estado
- [x] Material relevado: consigna, presentación "Proyecto final - Trabajo Final V2", deck del profe y devoluciones.
- [x] M11 duplicado del M9 con [`scripts/duplicar_m9_a_m11.py`](scripts/duplicar_m9_a_m11.py): 7 workflows, sub-workflows publicados y **Manager M11 inactivo**. El M9 sigue en producción hasta que el M11 esté listo.
- [x] Recursos propios: `Agenda_Turnos (11)` y `QA_Veredictos (11)` (copias de las 09 con sus datos), `Memoria_M11` en Airtable y carpeta Drive `Entregas/Trabajo Final`.
- [x] Esqueleto del DMSA: [`DMSA/build_pdf.py`](DMSA/build_pdf.py), que lee `DMSA/Seccion1..4_*.md` y `DMSA/capturas/`.
- [ ] Construir lo que falta (plan abajo), probar, recolectar evidencias y redactar el DMSA.

## Recursos del M11
| Recurso | ID |
|---|---|
| Manager `AI Automation Avanzado - M11` | `zLiXJWDV3i8OGJCK` (inactivo) |
| Supervisor `SUPERVISOR_Judge (M11)` | `x0qFeyPW15wSX0hD` |
| Tool RAG `Tool_ConsultarConocimiento (M11)` | `Ukqb3UUpTZhgnULF` |
| Workers 1–4 (M11) | `NQW5Mkmm0zJc6UJQ` · `8kgru7BieMefNVvz` · `CJKVcfkXPu6oNk8D` · `wT9rHHVpMreJFqwO` |
| Agenda_Turnos (11) | `19rWr4cy1pVmiDi5iv3Nkr3gZn4ExF12Ep5OkMrxxaWk` |
| QA_Veredictos (11) | `1IYqouMdEh8s0ecJEdDMWjtObglgDA1Nd8E84nWdSEQk` (la pestaña "Untitled" no se renombra: n8n la busca por nombre) |
| Memoria_M11 (Airtable, base `Memoria_Agente`) | `tblaIZxUOLY1T8g40` |
| Drive `Entregas/Trabajo Final` | `15y6JMd_aVrDFc_hL_yMcVolUFcXkUcV7` (subcarpeta `Del Profe`) |
| Base de conocimiento (Qdrant) | `kb_lodetincho_m5` (compartida, sin cambios) |

> Las planillas (11) se copiaron con los datos del M9. Antes de las pruebas finales conviene vaciar las filas de prueba (dejar los encabezados), así la auditoría del DMSA muestra solo casos del M11.
>
> El M11 existe solo en el n8n de **LOBO**. `activar_aqui.ps1` usa el último módulo que encuentre en el n8n local, así que en WOLVERINE sigue con el M9 hasta que se copie la base de n8n.

## Diagnóstico: qué tiene el M9 frente a los criterios del final
| Criterio de aceptación | Situación del M9 (revisada en los JSON el 14/10/2026) |
|---|---|
| 1. Webhook que responde de inmediato + proceso asincrónico | ✘ No hay nodo Webhook. Los disparadores son chat de n8n (sincrónico), Gmail Trigger y Telegram Trigger |
| 2. Juez **antes** de consolidar datos o registrar en el CRM | ✘ Parcial. El Juez evalúa solo las respuestas informativas. El alta y la modificación de turnos (Workers 1 y 4), el contacto en HubSpot y el guardado de memoria se ejecutan sin pasar por el Juez |
| 3. Despacho a un canal externo | ✔ Telegram, Gmail y Slack conectados |
| 4. Modular, sin monolitos | ~ Manager + 4 Workers + Tool RAG + Juez, pero el Manager tiene 99 nodos e incluye la ingesta de la base de conocimiento y el manejo de los tres canales |
| 5. RAG con citas y "No sé" | ✔ Top-K 5, Min Score 0,60, cita la fuente y el prompt instruye "No sé" |
| 6. Reintentos y fallas sin duplicados | ✘ Parcial. Telegram filtra los `update_id` repetidos y HubSpot busca antes de crear, pero el Worker 1 hace *append* (un reintento duplica el turno). Solo el modelo RAG tiene *Retry on Fail* |
| Ramas de error que alerten al equipo | ✘ No hay *Error Workflow* ni ramas de error en las APIs externas. Además, el Manager tiene `saveDataErrorExecution: none`: **las ejecuciones con error no se guardan** |
| Sin secretos en prompts ni textos | ✔ Las claves están en las credenciales de n8n y en `.env` (fuera de git) |

## Plan: lo que hay que construir
La consigna pide que el final **implemente lo que en las pre-entregas quedó solo diseñado**. Todo lo que sigue es una **propuesta, sin confirmar**, ordenada por prioridad.

**Prioridad 1: criterios de aceptación (35 % de la nota)**
1. **Webhook asincrónico:** `POST /agendabot` que responde enseguida con `202 {estado: "recibido", traceId}` y procesa en segundo plano. El resultado sale por un canal: Telegram, borrador de Gmail o Slack.
2. **Juez antes de consolidar:** ampliar el Supervisor para que también evalúe las **acciones** (alta y cambio de turno, contacto en el CRM, guardado de memoria): datos completos, coherencia con el pedido, que no sea un duplicado y que respete el semáforo. Con `exactitud_factual < 4` o una acción dudosa, la acción **se congela** y va a la cola de aprobación en Slack (*Send and Wait*). Solo después se escribe.
3. **Idempotencia:** una clave por pedido (canal + id del mensaje o de la petición). Antes de procesar se busca en un registro de pedidos procesados, el Worker 1 pasa a *append or update* por ID, y los envíos (Gmail, Telegram, Slack) se marcan como hechos para no repetirlos.
4. **Ramas de error y reintentos:** un workflow `Errores (M11)` con *Error Trigger* que avise a Slack con el traceId y mande un aviso al paciente, configurado como *Error Workflow* de todos los workflows. Además, *Retry on Fail* en las APIs externas (Sheets, HubSpot, Airtable, Gmail, Slack, Telegram, Cohere, Qdrant y los modelos), salida de error en los nodos críticos y guardar las ejecuciones con error.
5. **Modularidad:** sacar la ingesta de la base de conocimiento a su propio workflow y evaluar Workers para el CRM y para el despacho (Manager más chico).
6. **Email con HITL** (devolución de la P4): el envío directo solo después de un veredicto ACEPTADO; en cualquier otro caso, borrador.

**Prioridad 2: lo diseñado en M7, M9 y M10 que todavía no está construido**
7. **Triaje de señales rojas antes del Router** (M7, Pieza 3 y Scorecard B): palabras y patrones de urgencia, dinero, temas legales e historia clínica → respuesta fija (con la guardia 24 h si es una urgencia) → Slack con botones *Tomar el caso / Responder con plantilla / Descartar* y espera de 15 minutos.
8. **Metadatos en el CRM** (M10 y slide de trazabilidad del profe): `Origen = AgendaBot`, traceId, canal, última interacción, versión del workflow, resultado del Juez y escalado. Hay que crear las propiedades en HubSpot.
9. **Agenda:** columna `Asistencia`; el código de seguimiento (traceId) ya existe.
10. **Freno de mano** (M10): una bandera que se cambia desde Slack o la planilla. Si está activa, todo pasa a la atención humana.
11. **Respaldo ante demoras del modelo** (M10): un reintento y después el mensaje "Estamos con demoras…" más el aviso a Slack. **Dos fallas de comprensión seguidas** → humano (M7).
12. **Pendientes de privacidad** (M8/M9): enmascarar el nombre del paciente en el log y anonimizar la razón social real en la base (`Datos impositivos`).

**Prioridad 3: evidencias y DMSA (25 % + 12 % + 8 %)**
13. Batería de pruebas de punta a punta (incluido un reintento forzado para mostrar que no duplica y una API caída para mostrar la alerta) y métricas de precisión del Juez.
14. **3 veredictos reales del Juez en JSON plano**, capturas nítidas del lienzo (las saca el usuario: el lienzo grande congela Chrome), resultados visibles (mensaje despachado, fila en la agenda, contacto en el CRM, panel de KPIs).
15. ROI con modelos económicos: el M9 ya calculó el costo con el agente en Haiku (US$ 52,99/mes en tokens). Variables de entorno y estructuras de tablas, sin valores secretos. Video opcional de 3 minutos.

## Próximo paso
Confirmar el plan (o ajustarlo) y empezar por la Prioridad 1, en orden: Error Workflow (para ver las fallas desde el principio), idempotencia, Juez sobre las acciones y webhook asincrónico.
