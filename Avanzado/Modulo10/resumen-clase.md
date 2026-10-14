# Módulo 10 — Resumen de la clase y de la teoría

Clase en vivo 10 "De Sistema Agéntico a Propuesta de Valor" (13/10/2026, grabación de 1 h 51 min). Barrido del 14/10: pasada general cada 4 minutos y cada 1 minuto en la zona de slides (Claude ve los cuadros, no escucha el audio). Teoría: documento "Módulo 10" en Drive (unidades 1–3); la unidad 4 (ROI) es un cuestionario.

## Recorrido de la clase

| Min | Contenido |
|---:|---|
| 00–13 | Apertura con cámara apagada. |
| 14–18 | Dónde desplegar n8n: búsqueda de opciones de n8n en la nube vs. autoalojado (VPS) y acceso a n8n Cloud. |
| 22–26 | Slide de apertura: **"Última clase: de agentes a negocio"**. Temas: modelos comerciales · storytelling ejecutivo · despliegue por fases · ROI · brochure final. Objetivo: *que el sistema agéntico deje de verse como "un flujo en n8n" y se entienda como una propuesta de valor financiable.* |
| 30–34 | Recorrido por la plataforma: unidad 1 y **consigna del Proyecto Final** (ver [`consigna-proyecto-final.md`](consigna-proyecto-final.md)). |
| 38–42 | Revisión de un workflow de un alumno (entrega final en curso, error en un nodo HTTP). |
| 46–78 | **Deck de 18 slides** (detalle abajo). Diagrama de arquitectura armado en Excalidraw en el minuto 64. |
| 82–97 | Demo: workflow **"Clase Final - Oferta IA Agéntica por Telegram + ROI + Juez + HITL"** (detalle abajo). |
| 102 | Repositorio público de plantillas de n8n en GitHub (awesome-n8n-templates). |
| 106–111 | Cierre con el workflow del alumno (lienzo vacío). |

## El deck (slides 1–18)
1. **Última clase: de agentes a negocio** — ver arriba.
2. **El problema de vender "solo desarrollo"** — semana 1: el cliente está feliz (el agente responde leads, consulta el CRM, agenda y reporta a Slack); semana 3: cambió una API, el modelo se actualizó, el CRM cambió campos y el prompt empieza a fallar; pregunta incómoda: ¿quién paga las horas de ajuste si cobraste solo por "entregar el flujo"? → *Una automatización agéntica no se entrega y se olvida: se opera, se mide y se mejora.*
3. *(Cambio de paradigma, sin detalle legible.)*
4. **Por qué fallan los modelos tradicionales** — precio fijo (alcance inflado: casos borde, cambios de API, datos malos, mantenimiento no presupuestado); por hora (penaliza tu eficiencia); soporte reactivo (la IA se percibe inestable). → *La propuesta debe alinear incentivos, riesgo y mantenimiento.*
5. **Modelo 1: Success Fee** — sirve cuando el KPI es atribuible, auditable y escalable (ej.: cobrar por cada visita calificada agendada por el agente); necesitás metadatos en el CRM para demostrar que la IA participó. Riesgo: atribución discutible (¿si el cliente compra a los 6 meses?) → ventana de conversión contractual. → *Nunca dejes el éxito sin definición: KPI + fuente de verdad + ventana temporal.*
6. **Modelo 2: Retainer Experto** — prompt tuning (ajuste basado en logs para reducir alucinaciones), knowledge refresh (actualizar la base de conocimiento cuando cambian documentos), model management (testear modelos por costo, calidad y latencia), observabilidad (métricas, juez y precisión técnica). → *No vendés "horas de arreglo": vendés seguridad operativa y evolución mensual.*
7. **Modelo 3: Híbrido — el más defendible** — setup fee (descubrimiento, diseño, implementación inicial, pruebas y documentación); retainer (mantenimiento, observabilidad, tuning, cambios de modelos y base de conocimiento); success fee (upside por resultados atribuibles: citas, leads, tickets resueltos). → *Regla sana: el retainer debe cubrir tu costo operativo. El success fee es upside, no supervivencia.*
8. **ROI: números que entiende un CFO** — ejemplo: baseline 1.200 leads/mes × 8 min a USD 12/h = 160 h/mes = USD 1.920 de costo manual; TCO mensual USD 2.130 (retainer 750 + infra/LLM 180 + success fee 1.200), setup USD 3.000; si el valor mensual neto justifica el costo, el proyecto es defendible. → *No vendas "horas ahorradas" como despidos: vendé capacidad liberada para absorber demanda.*
9. **Análisis de sensibilidad** — conservador (800/mes, 45 % éxito, costo IA alto: ¿sigue siendo viable?), base (1.200/mes, 60 %, medio: caso esperado), optimista (1.800/mes, 75 %, bajo: upside). → *Un solo número de ROI es frágil. Tres escenarios muestran madurez y anticipan objeciones.*
10. **Storytelling técnico para no técnicos** — Impacto (¿cuánto ahorra, genera o libera? No "procesa tickets": "libera capacidad para cuentas VIP"), Riesgo (alucinaciones, datos incorrectos, acciones sensibles), Control (¿quién tiene la mano en el freno? guardrails, logs, HITL, AI-as-a-Judge).
11. *(Matriz de stakeholders y qué le importa a cada uno; pasó sin detenerse.)*
12. **Traducción Función → Beneficio** — RAG multi-fuente → información corporativa verificada en segundos, sin silos; AI-as-a-Judge → control de calidad automático antes de impactar al cliente; HITL → el humano aprueba acciones sensibles con contexto listo; Logs + CRM metadata → atribución auditable para ROI y facturación sin disputas; Manager-Worker → cada tarea va al especialista correcto, menos errores y mantenimiento más simple.
13. **Arquitectura como capa de orquestación** — Agente Manager arriba; Worker Leads, Worker Agenda, Worker Soporte y Supervisor QA; herramientas WhatsApp, CRM, Calendar y Slack. → *No mostrar "nodos": mostrar roles, herramientas, flujos de decisión y control.*
14. **Despliegue por fases: autonomía con seguridad** — escalera de 4 fases (imagen; pasó sin detenerse).
15. **Qué permite y qué prohíbe cada fase** — F0 modo sombra: lee y sugiere / no responde solo; F1 solo lectura: responde FAQs/RAG / no escribe en el CRM; F2 escritura controlada: propone acciones / no ejecuta sin HITL; F3 autonomía supervisada: opera con guardrails / no sale de políticas. Criterio de avance en todas: precisión, logs y fallback bajo control.
16. **Trazabilidad: fuente de verdad del Success Fee** — cadena de 4 pasos hasta el CRM y "metadatos mínimos" (pasó sin detenerse).
17. **Defensa ante comité: objeciones típicas** — "Esto ya lo hace mi CRM" → el CRM registra; el agente opera sobre el proceso: prioriza, responde, agenda y escala con trazabilidad. "¿Y si alucina?" → despliegue por fases, AI-as-a-Judge, HITL y límites de escritura según criticidad. "Es caro" → comparamos contra baseline, TCO y payback; no se vende costo: se vende capacidad y reducción de fricción.
18. **Cierre de camada** — *"Dejen de vender el motor. Empiecen a vender el destino."* El cliente no compra nodos: compra más ventas, menos fricción, menor riesgo y una forma segura de escalar. *Arquitecto técnico + estrategia de negocio = Asesor de IA experto.*

## La demo: "Clase Final - Oferta IA Agéntica por Telegram + ROI + Juez + HITL"
Workflow que genera el brochure automáticamente a partir de un mensaje de Telegram. Lógica de negocio (nota del lienzo):
1. Discovery libre → JSON estructurado (Basic LLM Chain "Discovery IA": extrae solo lo que está explícito o se puede calcular — cliente, industria, proceso actual, dolor operativo, volumen mensual…; no inventa números).
2. Validación de faltantes (si faltan datos, pide por Telegram).
3. ROI/TCO determinístico (nodo de código, no lo calcula la IA).
4. Sensibilidad: conservador / base / optimista.
5. Pricing híbrido.
6. Roadmap por fases.
7. Storytelling por stakeholder.
8. Brochure Writer IA (modelo en Groq).
9. AI-as-a-Judge sobre el brochure (Structured Output).
10. Switch del veredicto: APROBADO / CORREGIR (máximo 2 correcciones) / HITL (revisión por Telegram).
11. Salida por Telegram.

## Teoría (documento "Módulo 10")
**Unidad 1 · Modelos comerciales.** Tu producto no es una automatización que "se entrega y se olvida", sino la continuidad operativa. Precio fijo, por hora y soporte reactivo fallan en sistemas probabilísticos. *Success fee*: solo con KPI atribuible, auditable y escalable, con el origen marcado en el CRM y una **ventana de conversión** contractual (X días desde la última interacción del agente). *Retainer "Experto Lux"*: prompt tuning, knowledge refresh, model management y observabilidad activa (que la precisión no baje del 95 %). *Híbrido*: el estándar (nunca 100 % success fee: APIs y datos del cliente no se controlan). Errores: ignorar el drift del modelo (el soporte incluye adaptarse a cambios del proveedor), no definir el baseline (la auditoría de procesos es el primer paso remunerado), el cliente que "juega el sistema" (logs y metadatos del CRM como única fuente de verdad para facturar).

**Unidad 2 · Storytelling para no técnicos.** La sofisticación técnica no genera confianza. El agente es un **"Analista Virtual Especializado"** (un rol en el organigrama), no un prompt. Tres preguntas silenciosas del ejecutivo: **impacto** (conectar con KPIs de negocio, no "horas ahorradas"), **riesgo** (alucinación como "probabilidad gestionada" con un supervisor), **control** (HITL, *kill-switch*, analogía del copiloto). Analogías: Manager-Worker = director de orquesta; RAG = biblioteca corporativa privada que el agente consulta y cita, sin inventar. Errores: caja negra, sobre-prometer autonomía ("niveles de autonomía"), demos técnicas en vez de demos de valor (mostrar el resultado y el panel de supervisión, no el editor).

**Unidad 3 · Oferta técnica y despliegue por fases.** El stack se justifica pieza por pieza (persistencia, varios modelos según la tarea, n8n self-hosted en sectores regulados). Despliegue: Fase 0 *shadowing* (propone, un humano valida), Fase 1 solo lectura/FAQs, Fase 2 escritura controlada con HITL (botón en Slack), Fase 3 autonomía supervisada con AI-as-a-Judge. La oferta habla de **SLA**, punto de control (en qué fase deja de intervenir el humano) y **estrategia de fallback** (qué pasa ante un timeout del modelo).

**Unidad 4 · Cuantificación del ROI.** Cuestionario (resuelto con 100 %). El contenido de ROI está en las slides 8 y 9.

## Para el brochure de AgendaBot (aplicación directa)
- Slide 13 → diagrama: Manager (Router) + Worker Registrar / Confirmar / Consultar / Modificar + Asistente de conocimiento (RAG) + Supervisor QA (Juez); herramientas: chat/Telegram/Gmail, agenda (Sheets), CRM (HubSpot), memoria (Airtable), Slack.
- Slide 12 → la tabla Función → Beneficio ya está casi escrita para nuestro sistema.
- Slides 8–9 → baseline y ROI del M9 + payback 1,08 meses; sumar tres escenarios de sensibilidad.
- Slides 15–17 → fases con el semáforo del M7; objeciones con guardrails reales (Juez, HITL en Slack, validación, traceId).
