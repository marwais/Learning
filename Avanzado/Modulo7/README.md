# Módulo 7 — Agentes Especializados por Industria

Séptima etapa del proyecto integrador **AgendaBot** (curso AI Automation Avanzado, Coderhouse). A diferencia de los módulos anteriores, **la Pre-entrega 7 es un documento de diseño**: no se construye un agente nuevo en n8n, sino que se diseña cómo se especializa el que ya existe (Manager M6) para su vertical. La vertical de AgendaBot es **salud: coordinación de turnos y atención al paciente de una clínica** (Clínica LoDeTincho).

> Material: documento "Módulo 7" en Drive (unidades 1–3: Sales Ops/CS, RRHH, Finanzas y Legal). Clase en vivo: 01/10/2026 (con grabación) → [`resumen-clase.md`](resumen-clase.md).

## Estado
- [x] Consigna y material de las unidades relevados.
- [x] Barrido de la grabación de la clase 7 (01/10) → [`resumen-clase.md`](resumen-clase.md). Incluye un **ejemplo resuelto de la estructura de la pre-entrega** (vertical RRHH) que sirve de modelo.
- [x] Informe de consultoría, **V3** (V2: corrige la V1 tras revisar la consigna punto por punto: framework con los 5 vectores — operación, ingresos, viabilidad no-code, accesos regulados y adopción — con fundamento; matriz de permisos por rol con L/E; semáforo taxativo; churn nombrado; triaje con IF/Switch sin código; Scorecard B coherente con el semáforo). Baseline y KPIs con **supuestos declarados** ($ 10.000 por hora); escalado con botones de Slack **propuesto**, no implementado. V3: portafolio sin la falsa afirmación "sin código propio" (es low-code), ficha del Resumidor de memoria, W2 y Router coherentes con la matriz de permisos, `riesgo` en el JSON del Router, "reclamo" en las palabras clave, protocolo versionado como evidencia del Scorecard B y meta de tiempo de respuesta ≤ 20 s.
  - Versión corta (4 hojas, una por componente): [`PreEntrega/PreEntrega_Modulo7_JulioMartinWaisburd_versión_corta_V3.pdf`](PreEntrega/PreEntrega_Modulo7_JulioMartinWaisburd_versión_corta_V3.pdf) — `build_pdf_corta.py` desde `corta/Pieza1..4.md`.
  - Versión extendida (10 págs.): [`PreEntrega/PreEntrega_Modulo7_JulioMartinWaisburd_versión_extendida_V3.pdf`](PreEntrega/PreEntrega_Modulo7_JulioMartinWaisburd_versión_extendida_V3.pdf) — `build_pdf.py` desde `Pieza1..4_*.md`.
  - Las V1 y V2 quedan en la misma carpeta como referencia.

## Consigna oficial (Pre-entrega 7: Diseño Arquitectónico de un Sistema Agéntico Vertical de Industria)
Entregable: **un único informe de consultoría en PDF**, enfoque 100 % no-code, con cuatro componentes obligatorios:

1. **Relevamiento y priorización** — problema operativo, industria y justificación de la solución agéntica; framework de priorización del asesor (impacto en las operaciones, viabilidad técnica no-code, adopción probable); **baseline** manual (qué se hace hoy, quién lo hace, cuánto tiempo consume).
2. **Arquitectura multi-agente y mapa de permisos** — diagrama de la coreografía (roles especializados, herramientas, delegación y comunicación); ficha de cada agente (máx. media página: misión, System Prompt constitutivo, herramientas, qué JSON entrega a quién); permisos de lectura/escritura por conector bajo **mínimo privilegio**.
3. **Propuesta de valor y semáforo de riesgo (HITL)** — propuesta en lenguaje comercial; **KPIs** medibles definidos antes de implementar (tasa de resolución autónoma, tiempo ahorrado…); semáforo: qué acciones son 100 % autónomas y cuáles exigen congelamiento y supervisión humana en Slack o Gmail; protocolo de escalado forzado con **botones interactivos en Slack** ante variables críticas.
4. **Scorecards y portafolio** — playbook/scorecard/rúbrica que usan los agentes para evaluar de forma unívoca con evidencia documental; **versión de portafolio** anonimizada (máx. media página).

Instrucciones adicionales: estrategia de **Context Engineering** (qué historiales y señales recibe cada sub-workflow).

Plazo: **13/10/2026 21:00**.

## Insumos que ya existen (del M1 al M6)
| Pieza de la consigna | Base en el proyecto |
|---|---|
| Red de especialistas | Manager/Router + Worker1 Registrar, Worker2 Confirmación, Worker3 Consultar, Worker4 Modificar + Agente RAG + Validador (Haiku) |
| Herramientas y permisos | Google Sheets (Agenda_Turnos), Airtable (Memoria), Qdrant (KB), Gmail, Slack, HubSpot, Telegram, Whisper, ElevenLabs |
| Context Engineering | Memoria de largo plazo (Airtable) + memoria de sesión + fragmentos RAG recuperados en el turno |
| HITL actual | Borrador de Gmail (no envío directo), notificación a Slack, validador que bloquea respuestas sin respaldo |
| Evidencia / métricas | Validación ciega del M5 (5/5), pruebas de voz del M6, latencia medida |

## Plan de trabajo
1. Barrer la clase 7 y completar `resumen-clase.md`.
2. Baseline de la clínica (supuestos explícitos: volumen de turnos, quién atiende, minutos por gestión).
3. Diagrama de la coreografía (desde el Manager M6) + fichas de agente + matriz de permisos.
4. Semáforo HITL y escalado con botones de Slack (diseño; opcional: un prototipo con *Send and Wait* en el M6).
5. Scorecard (p. ej. triage de urgencia / priorización de turnos) + versión portafolio.
6. PDF con `PreEntrega/build_pdf.py` (mismo esquema que M5 y M6).
