# Módulo 10 — De Sistema Agéntico a Propuesta de Valor

Décima etapa del proyecto integrador **AgendaBot** (curso AI Automation Avanzado, Coderhouse). Como el M7, **la Pre-entrega 10 es un documento**: un brochure técnico-comercial que presenta el sistema construido hasta el M9 en lenguaje de negocio. No se construye un agente nuevo: el sistema que se vende es el **M9** (Manager `PmVOscqplghfUYzU`, activo en n8n). Por eso este módulo **no duplica workflows, planillas ni tablas**; si en algún momento hiciera falta, se sigue la convención (M9 → M10 con `Modulo9/scripts/duplicar_m8_a_m9.py` como modelo).

> Material: documentos "Módulo 10" (teoría, unidades 1–3) y "Módulo 10 - Pre Entrega" en Drive (`IA/AI Automation/Avanzado`). La unidad 4 (cuantificación del ROI) es un cuestionario (completado, 100 %). Clase en vivo: 13/10/2026 (1 h 51 min, con grabación) → [`resumen-clase.md`](resumen-clase.md).

## Estado
- [x] Consigna, teoría y grabación de la clase relevadas ([`resumen-clase.md`](resumen-clase.md), barrido general cada 4 min + cada 1 min en la zona de slides).
- [x] Carpeta Drive `Entregas/10` (`1rH6TuOBtEoIMNQpzwy-4z4z0lcCk7xG5`).
- [x] Esqueleto de la pre-entrega: `PreEntrega/build_pdf.py` (arma el PDF desde `Seccion1..4_*.md`).
- [ ] Redactar las 4 secciones del brochure.
- [ ] Diagrama de arquitectura de valor (capa de orquestación, sin capturas de n8n).
- [ ] Generar el PDF, revisión del usuario y entrega.

## Consigna oficial (Pre-entrega 10: Brochure Técnico-Comercial y Defensa ante Comité)
Entregable: **un único PDF** `PreEntrega_Modulo10_NombreApellido.pdf`, en lenguaje de negocio (sin "embeddings", "nodos", "tool-calling", "LLM"), de **6 a 10 páginas**, con cuatro secciones:

1. **Narrativa ejecutiva y arquitectura de valor** — problema y promesa (proceso, dolor actual, resultado medible); **diagrama de arquitectura de valor** como capa de orquestación (manager, workers, herramientas e interacciones; **no** captura del lienzo de n8n); traducción **Función → Beneficio**; **business case**: reutilizar baseline y ROI del M9 (actualizar si cambió algún dato) y sumar el **payback**.
2. **Roadmap de despliegue por horizontes** — Fase 0 modo sombra, Fase 1 piloto de solo lectura, Fase 2 escritura controlada con HITL, Fase 3 autonomía supervisada: qué puede hacer el agente, qué tiene prohibido y quién valida en cada una; **criterio de salida** de cada fase; **estrategia de fallback** ante errores o timeouts del modelo.
3. **Modelo comercial e incentivos** — pricing híbrido: **setup fee**, **retainer** mensual y **success fee** (qué cubre cada uno); **KPI de facturación** atribuible y auditable; **ventana de conversión** en días; **alcance del retainer** (prompt tuning, actualización de la base de conocimiento, gestión de modelos, revisión de métricas).
4. **Plan de implementación y control de metadatos** — **hitos a 30 días** con fecha y **responsable (rol)** por hito; **trazabilidad de metadatos** en el CRM como única fuente de verdad para facturar; **defensa ante comité**: tres objeciones ("esto ya lo hace mi CRM", "¿y si el agente alucina y borra datos?", "es caro para el ahorro que genera") con respuesta apoyada en guardrails, fases y números.

Checklist de la consigna: se entiende sin saber qué es n8n · el diagrama muestra la capa de orquestación · ROI contra baseline explícito · las 4 fases dicen qué puede y qué no · pricing con 3 componentes y ventana en días · cada hito con responsable por rol.

**Plazo: 20/10/2026 21:00.**

## Insumos que ya existen
| Pieza del brochure | Base en el proyecto |
|---|---|
| Arquitectura de valor | Manager/Router + Worker1 Registrar, Worker2 Confirmación, Worker3 Consultar, Worker4 Modificar + Agente RAG + Supervisor AI-as-a-Judge (M2 → M9). Canales: chat, Gmail, Telegram (voz, M6). Herramientas: Google Sheets (agenda), Airtable (memoria), Qdrant (base de conocimiento), HubSpot (CRM), Slack (escalado), ElevenLabs/Whisper (voz). |
| Función → Beneficio | RAG con cita y "No sé" (M5), Juez + HITL en Slack (M8), traceId y log JSON de auditoría (M9), memoria del paciente (M3/M5). |
| Roadmap por fases | Semáforo de autonomía y protocolo de escalado del M7 (`Modulo7/PreEntrega/Pieza3_Valor_HITL.md`). |
| Business case | M9 (`Modulo9/finanzas.json`): 183,3 h/mes evitadas = $ 1.832.600; TCO US$ 136,90 + mantenimiento = $ 351.660/mes; neto $ 1.480.940; ROI mensual 4,2×; setup $ 1.600.000 → **payback 1,08 meses**; resolución autónoma medida (QA) 70,6 %. Supuestos: hora administrativa $ 10.000, US$ 1 = $ 1.400. |
| KPI y trazabilidad | traceId por interacción (M9), columna `traceId` en la agenda, contacto en HubSpot (M4), veredictos en `QA_Veredictos (09)`. |

## Adelanto: Proyecto Final (vence 13/11/2026 20:59)
Consigna completa en [`consigna-proyecto-final.md`](consigna-proyecto-final.md). En síntesis: sistema en n8n asincrónico (webhook o chat que responde de inmediato y procesa en segundo plano), Manager-Worker, Juez obligatorio antes de registrar (umbral → HITL), despacho por un canal externo, RAG con "No sé", idempotencia y ramas de error; más el PDF `Apellido_Nombre_ProyectoFinal_AI_Experto.pdf` (DMSA) con 4 secciones.
