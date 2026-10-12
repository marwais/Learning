# Módulo 7 — Agentes Especializados por Industria

**Curso:** AI Automation Avanzado (Coderhouse) · **Clase en vivo:** 01/10/2026, 2h 16m (136 min) — "Nueva unidad: Agentes Especializados por Industria"
**Material de la unidad:** documento "Módulo 7" en Drive (unidades 1–3) + en la plataforma una unidad 4, "Patrones rápidos para Real Estate, e-commerce y…", y el Podcast EP 7.

> Barrido por cuadros: cada 4 minutos y **cada 1 minuto en las zonas donde cambió algo** (10–30, 58–62, 78–82, 98–104, 129–135); la demo, cada 2 minutos. Claude ve slides y demos, **no el audio**.

---

## Resumen

El M7 pasa de "un agente que sabe usar herramientas" a un **sistema especializado por vertical** que opera bajo una **política de negocio**: especialistas "quirúrgicos" con alcance acotado, un triaje de señales **antes** del agente (Switch/Filter), scorecards con evidencia y un **semáforo de riesgo** que fija qué es autónomo y qué exige un humano (HITL). La pre-entrega es un **informe de diseño**, no un workflow nuevo.

---

## Recorrido de la clase

| Min | Tema | Tipo |
|----:|------|------|
| 00–12 | Apertura (cámara apagada) | — |
| 13 | Docente en cámara | — |
| 14 | Ficha de la sesión en la plataforma: "Consolidación de Agentes Especializados por Industria" | plataforma |
| 15–16 | **Consigna de la Pre-entrega 7** en la plataforma (objetivos e instrucciones paso a paso) | plataforma |
| 17 | Unidad Sales Ops/CS; infografía del M6 "Matriz de Salida UX (¿Audio o Texto?)" | plataforma |
| 18 | Unidad RRHH: infografía "El Pipeline de Talento Agéntico" (cribado con LlamaCloud → selección asistida con RAG + Vector DB → onboarding por webhooks) | plataforma |
| 19–20 | **Objetivos** | slide |
| 21–58 | **El ruido del CRM — de la tarea a la política de negocio** (problema: CRM con datos sucios; lo lineal falla; el agente como copiloto de infraestructura). A los 25 min, búsqueda de "qué es un lead" (MQL vs SQL) | slide + web |
| 61–80 | **Especialistas de Sales Ops — tres roles quirúrgicos** (enriquecer y calificar; higiene del pipeline; atribución de ingresos), con un dibujo: "clasifica clientes" → 3 ramas → producto/servicio | slide + pizarra |
| 81–98 | **Customer Success proactivo** (Onboarding Orchestrator; Health Score y churn; expansión y upsell) | slide |
| 99 | **Señales y priorización — el triaje antes del agente** (señales explícitas, implícitas y externas; un Switch o Filter hace el triaje; autónomo: actualizar metadatos; supervisado: cambiar un precio o marcar un deal perdido) | slide |
| 100–130 | **Demo n8n**: clasificador de clientes con triaje (ver abajo) | demo |
| 131–133 | **Ejemplo resuelto de la estructura de la pre-entrega (vertical RRHH)** | texto |
| 132 | Momentos de la clase — **Coder Tips** | slide |
| 134–136 | Demo y vuelta al slide del CRM | — |

### Objetivos (slide)
1. Diseñar sistemas agénticos especializados por vertical de negocio.
2. Adaptar arquitecturas de Sales Ops, RRHH y Legal bajo políticas corporativas.
3. Fragmentar cada proceso en especialistas quirúrgicos con alcance acotado.
4. Estructurar scorecards y reportes basados en evidencias.
5. Fijar el semáforo de riesgo y los puntos de control humano (HITL).

### Ficha de la sesión (plataforma)
- **Qué se aprende:** diferenciar un "chatbot con esteroides" de un agente especializado con lógica de dominio; diseño para sectores de alto riesgo (**Salud**, Legal, Finanzas); orquestación y escalado humano por industria; riesgos y métricas de éxito por vertical.
- **Temas clave:** anatomía de la especialización (más allá del system prompt); arquitecturas verticales (casos Harvey, Nuance DAX, Intercom); taller de diseño; debate: ¿agentes modulares o plataformas universales con adaptadores?
- **Preparación:** traer una problemática real de la propia industria y una herramienta de diagramación (Miro, LucidChart o papel).
- **Resultado esperado:** presentar una **ficha técnica de implementación** de un agente especializado: fuentes de datos, herramientas y protocolo de gestión de riesgos.

### Demo n8n (minutos 100–130)
```
On form submission (Nombre, Edad 18-25/26-40/+40, Servicio [dropdown], Presupuesto)
 → AI Clasificador (AI Agent + Cohere Chat Model): por presupuesto etiqueta BÁSICO (200.000–350.000),
   MEDIUM (350.000–500.000) o PREMIUM (> 500.000); "Solo devolver la etiqueta"
 → TRIAGE (Switch, mode Rules, sobre {{ $json.output }}) → 3 salidas
 → Merge
 → AI RAG (AI Agent + Cohere): "Analizá el perfil {{ $json.output }} y recomendá el producto: BÁSICO → producto 1, MEDIUM → 2, PREMIUM → 3"
```
Resultado: "Para el cliente con perfil PREMIUM se recomienda el producto 3…". La idea: **el triaje (clasificación + Switch) ocurre antes del agente que redacta**.

### Ejemplo resuelto de la pre-entrega (vertical RRHH, minuto 131)
- **Baseline manual:** 40 horas/mes × $/h = $…/mes; tasa de error alta.
- **Arquitectura multi-agente (coreografía):** Manager recibe el webhook del ATS → Worker 1 (Parser): LlamaCloud extrae datos y normaliza skills → Worker 2 (Evaluator): compara contra el Scorecard RAG (Manual de Perfil) → Worker 3 (Comms): redacta el email de rechazo o avance (HITL).
- **Scorecard (cribado):** experiencia core 40 % (evidencia en el PDF); certificaciones 30 % (vigencia validada); fit cultural 30 % (análisis semántico de la cover letter).
- **Semáforo (HITL):** verde, autónomo = registro en Airtable y notificación interna; rojo, HITL = descarte definitivo u oferta económica, **requiere clic en Slack**.

### Coder Tips (slide)
Dos guardrails de RRHH que no se pueden saltear: **nunca automatizar un rechazo total sin validación humana** (riesgo legal y de marca) y **auditar los logs del agente para detectar sesgos**. La IA propone; el humano decide lo delicado.

---

## Cómo se aplica a AgendaBot (vertical salud)
- Es el mismo patrón de la demo: el **Router** ya clasifica (CREAR/MODIFICAR/CONSULTAR/INFO/FUERA_DE_ALCANCE) y un **Switch** deriva a especialistas: la pre-entrega lo documenta como coreografía.
- El ejemplo de RRHH da el **formato**: baseline con horas × costo, coreografía Manager + workers, scorecard con pesos y evidencia, semáforo verde/rojo con clic en Slack.
- Salud es una vertical de **alto riesgo** (lo dice la ficha): urgencias médicas, datos sensibles y consentimiento son candidatos naturales a HITL.
