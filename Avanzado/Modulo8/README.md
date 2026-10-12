# Módulo 8 — Evaluación Automática y Mejora Continua de Agentes

Octava etapa del proyecto integrador **AgendaBot**. Parte del M6 (multi-agente + memoria + integraciones + RAG + voz) y le suma la **capa de supervisión AI-as-a-Judge**, un **experimento A/B** de arquitecturas y el **dashboard** de precisión, HITL y coste.

> Resumen de la clase 8 (06/10, barrido cada 1 minuto) → [`resumen-clase.md`](resumen-clase.md).

## Estado
- [x] Recursos 08: carpeta Drive `Entregas/08`, `Agenda_Turnos (08)`, tabla Airtable `Memoria_M8`, planilla `QA_Veredictos (08)` (`1O1894tGkQFttThtInYEBC9kb0AvHudRfPL60u4fZyEs`, compartida con la cuenta de la credencial de Sheets). M6 duplicado a M8 (`_ids_m8.json`).
- [x] **SUPERVISOR_Judge (M8)**: Juez = Basic LLM Chain + Claude Sonnet 4.6 (temp 0) + Structured Output Parser (JSON Schema: `exactitud_factual` 1–5, `estado_veredicto`, `critica`); normaliza umbrales; registra cada veredicto en Sheets; JSON inválido → RECHAZADO.
- [x] **Manager M8**: en la ruta INFO el validador del M5 se reemplazó por el Juez + Switch: Aceptar (≥ 4) · Corregir (reintento con la crítica, máx. 2) · Escalar (aviso al paciente + Slack Send and Wait con Aprobar / Editar). Regla nueva en el Router: síntomas y urgencias → INFO (antes caían en FUERA_DE_ALCANCE).
- [x] **AB_Test (M8)**: webhook `ab-test-m8` (A = Sonnet 4.6, B = Haiku 4.5, mismo Juez). [`scripts/ab_test.py`](scripts/ab_test.py) corre los 5 casos × 2 y arma `ab_resultados.json/.csv`.
- [x] Checkpoint: [`Checkpoint/Checkpoint_Modulo8_Waisburd_JulioMartin.pdf`](Checkpoint/Checkpoint_Modulo8_Waisburd_JulioMartin.pdf) (3 bloques), con `Checkpoint/build_pdf.py`.
- [x] HITL probado con Slack: Aprobar y Editar (formulario de n8n) funcionan; después de cualquier decisión se publica una **derivación a operador** en `#soporte` y el paciente recibe "Un operador de la clínica ya fue avisado…". Capturas en el Bloque 1.

Todo lo arma [`scripts/agregar_supervisor.py`](scripts/agregar_supervisor.py) (idempotente; `--keep-executions` guarda ejecuciones para medir; el Manager queda con compliance = no guardar ejecuciones).

## Resultado del A/B (ronda final, 10 corridas)
| | Precisión | HITL | Coste × 1.000 | Latencia mediana |
|---|---|---|---|---|
| A — Sonnet 4.6 | 100 % | 20 % | US$ 21,84 | 11,6 s |
| B — Haiku 4.5 | 100 % | 20 % | US$ 10,84 | 7,3 s |

Recomendación: agente en Haiku 4.5, Juez en Sonnet 4.6. Rondas previas guardadas: `ab_resultados_ronda1.json` (casos demasiado fáciles: 10/10 aceptadas, sin errores) y `ab_resultados_ronda2_sin_log.json` (antes de arreglar el registro en Sheets).

## Hallazgos
- **Hueco de seguridad del Router**: "dolor de pecho" se clasificaba FUERA_DE_ALCANCE y el paciente recibía "solo puedo ayudarte con turnos". Corregido en el M8.
- **Base documental**: `Datos impositivos` conserva la razón social real de la empresa de origen; el Juez lo detectó (CORREGIR) al pedir el CUIT. Pendiente de anonimizar en la base.
- **Chat + espera humana**: mientras la ejecución espera en Slack, el chat devolvía el JSON del Juez; ahora devuelve un aviso al paciente.

## Consigna oficial (Checkpoint: QA automatizado con AI-as-a-Judge)
PDF único `Checkpoint_Modulo8_Apellido_Nombre.pdf` con: (1) supervisor + rúbrica del Juez en JSON (captura con el Switch de 3 rutas, prompt y esquema) — 60 %; (2) matriz A/B de 5 + 5 corridas con precisión y coste — 20 %; (3) dashboard (precisión media, categorías de error, coste proyectado a 1.000) + 1 recomendación — 20 %. Plazo: **13/10/2026 21:00**.
