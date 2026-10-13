# Módulo 9 — Gobernanza, FinOps y Observabilidad

Novena etapa del proyecto integrador **AgendaBot**. Parte del M8 (multi-agente + memoria + integraciones + RAG + voz + Juez AI-as-a-Judge) y le suma **trazabilidad con traceId**, **logs JSON de auditoría**, **contención de costes** (Prompt Caching, model routing, límites) y los **controles de objetividad** en los prompts.

> Resumen de la clase 9 (barrido cada 1 minuto) → [`resumen-clase.md`](resumen-clase.md).

## Estado
- [x] Recursos 09: carpeta Drive `Entregas/09`, `Agenda_Turnos (09)` (+ columna `traceId`), `QA_Veredictos (09)` (+ 7 columnas de log y pestaña **KPIs**), ambas compartidas con la cuenta de la credencial de Sheets; tabla Airtable `Memoria_M9` (+ `Ultimo_traceId`). M8 duplicado a M9 con [`scripts/duplicar_m8_a_m9.py`](scripts/duplicar_m8_a_m9.py) (`_ids_m9.json`); el Manager M8 quedó desactivado (comparte Telegram y Gmail).
- [x] [`scripts/agregar_trazabilidad.py`](scripts/agregar_trazabilidad.py) (idempotente; `--keep-executions` solo para pruebas):
  - **Generar traceId** después de *Normalizar entrada*; Sets **traceId → Worker N**, input `traceId` en la Tool RAG y en el caso del Juez; los Workers lo devuelven (W1/W4 lo graban en la agenda).
  - **Armar log de auditoría** en el Juez: `timestamp, traceId, parentExecutionId, nodeName, toolOutput, systemPromptSnapshot (versión + sha256), confidenceScore, decision`, con enmascarado de email/DNI/teléfono.
  - FinOps: Prompt Caching 5 min en el Agente RAG (bloque fijo primero, memoria al final), *Max Iterations* 5, resumen de memoria con Haiku 4.5; el Juez **sin** caché (1 llamada por caso, rúbrica < 1.024 tokens).
  - Objetividad: bloque en Router y Agente RAG + criterio en la rúbrica del Juez (v2, sha `d121785de282`).
- [x] [`scripts/medir_prompt_caching.py`](scripts/medir_prompt_caching.py): medición real con la API (workflow temporal, ya borrado) → `finops_cache.json`.
- [x] [`scripts/finanzas.py`](scripts/finanzas.py): KPIs, ROI y TCO → `finanzas.json`.
- [x] Pre-entrega: [`PreEntrega/PreEntrega_Modulo9_JulioMartinWaisburd.pdf`](PreEntrega/PreEntrega_Modulo9_JulioMartinWaisburd.pdf) (10 págs., 3 dimensiones) con `PreEntrega/build_pdf.py`.

## Números clave
| | |
|---|---|
| Resolución autónoma (QA) | 70,6 % |
| Horas evitadas (proyección) | 183 h/mes → $ 1.832.600 |
| TCO mensual | US$ 136,90 + mantenimiento = $ 351.660 |
| ROI mensual / payback | 4,2× / 1,1 meses |
| Tokens/mes | US$ 79,36 (M8) → 68,90 (M9) → 52,99 con agente Haiku |

## Pruebas (13/10, chat de n8n)
INFO (Juez ACEPTADO), CREAR_TURNO (W1+W2, traceId en la agenda), CONSULTAR_TURNO (W3), prompt injection (FUERA_DE_ALCANCE), INFO doble con CUIT (CORREGIR → ACEPTADO), dolor de pecho (RECHAZADO → Slack, ejecución 494 en espera). Detalle en `pruebas_m9.json`.

## Pendientes
- Separar las API keys en las consolas (workspace `agendabot-dev` con tope US$ 10/mes, etc.): lo configura el usuario.
- La KB (`Datos impositivos`) sigue con la razón social real sin anonimizar.
- El nombre del paciente no se enmascara en el log (sí email, DNI y teléfono).

## Consigna oficial (Pre-entrega 9)
PDF `PreEntrega_Modulo9_NombreApellido.pdf`: dashboard con KPIs, matriz de costos de tokens con retorno esperado, mapa de riesgos éticos y de ciberseguridad, y esquema de logs JSON correlacionados con traceId. Tres dimensiones: Finanzas 35 %, Trazabilidad 35 %, Ética y compliance 30 %.
