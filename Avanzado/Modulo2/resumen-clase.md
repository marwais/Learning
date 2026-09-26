# Resumen de la clase — Módulo 2: Arquitectura Multi-Agente

**Curso:** AI Automation Avanzado · **Clase en vivo:** 15 sep 2026 · **Duración:** 2 h 23 min
**Tema:** *De agente único a organigrama* — pasar del workflow "mono-bloque" a una red modular Manager-Worker.

> Nota: el resumen se basa en las **slides** de la clase (transcritas) y en el material escrito del módulo.
> La grabación **no tiene subtítulos**, por lo que los comentarios hablados que no estén en pantalla no están recogidos.

---

## Recorrido de la clase (minutado)

| Minuto | Tramo | Contenido |
|--------|-------|-----------|
| 00:00–12:00 | Intro / espera | Placa de Coderhouse. |
| 12:00–20:00 | Título + Agenda | Manager-Worker · Patrones de orquestación · Robustez · Break · Práctica en vivo · Pre-entrega 2. |
| 21:00–44:00 | **Teoría** | Modularización, contrato de datos, Planner-Executor, checkpoints, especialistas, enrutamiento, guardrails. |
| 45:00–89:00 | **Práctica en vivo (1)** | AI Agents encadenados (`Detector_Productos → Admin_Datos`), Structured Output Parser, Data tables. |
| 92:00–108:00 | ☕ Break | — |
| 108:00–114:00 | Ejemplo en vivo | Actividad colaborativa: un reto, tres arquitecturas + "Break the Agent" (leer una traza fallida). |
| 114:00–134:00 | **Práctica en vivo (2)** | Execute Workflow Trigger, Workers (Validador), Manager con "Call Worker", Code/Set/Google Sheets. |
| 135:00 | Slide "Tu misión" | La consigna de la Pre-entrega 2. |
| 138:00–143:00 | Cierre | Canvas del Manager de ejemplo + puente al Módulo 3 (Memoria y Persistencia). |

---

## Los conceptos, destacados

### 1. El patrón Manager-Worker
- **Manager**: el director de orquesta. Recibe el trigger, decide a qué especialista llamar y consolida la respuesta. No hace el trabajo pesado.
- **Worker**: un sub-workflow que hace **una sola cosa** excepcionalmente bien.
- **Agnóstico**: el Worker no sabe quién lo llamó; recibe una entrada y devuelve un resultado.

### 2. ¿Por qué modularizar?
- **Testabilidad**: probás cada Worker aislado; si falla, sabés exactamente dónde.
- **Reutilización**: un buen Worker lo llamás desde Ventas, Soporte y Éxito del Cliente.
- **Menos ruido**: pasás solo lo necesario → mejor precisión del LLM y menos costo de tokens.

### 3. El contrato de datos
- **Execute Workflow**: el nodo con que el Manager llama al Worker y le pasa datos.
- **Wait for child to finish**: el Manager se pausa hasta que el Worker termina y devuelve su resultado.
- **Set antes de delegar**: limpiá el payload y mandá solo el mínimo producto viable.

### 4. Planner-Executor (separar el pensar del hacer)
- **Planner**: el cerebro estratégico. Desglosa un pedido complejo en un plan y tiene **prohibido** usar conectores.
- **Executor**: las extremidades. Cumple una orden atómica con sus conectores y devuelve el resultado.
- **El plan es dato, no texto**: ID de paso, acción, herramienta y criterio de éxito.

### 5. El loop con checkpoints
- **El bucle** itera el plan e invoca al Executor paso por paso.
- **Plan B dinámico**: si un paso falla, el error vuelve al Planner para replanificar.
- **Checkpoint HITL**: un nodo `Wait` congela el plan hasta que un humano hace clic en "Autorizar".

### 6. Los especialistas (una red de roles acotados)
- **Researcher**: extrae información de fuentes autorizadas.
- **Writer**: transforma datos técnicos en lenguaje humano claro.
- **Executor**: tiene credenciales para modificar sistemas (CRM, planillas).
- **Critic**: valida que la salida cumpla las normas antes de enviarla.

### 7. Enrutamiento: intención, confianza y riesgo
- **Intención**: qué quiere el usuario; un mensaje puede esconder dos pedidos a la vez.
- **Confianza** (0–1): alta (>0.85) ejecuta sola; media (0.50–0.84) ejecuta pero marca revisión; baja va a un humano.
- **Riesgo**: bajo (lectura) libre; medio validado; **alto** (reembolsos, borrados) exige aprobación humana obligatoria.

### 8. Guardrails por infraestructura
- **El error**: confiar la seguridad a un "no borres datos" en el prompt. La IA es probabilística.
- **La práctica**: límites físicos en el lienzo. Un conector en modo **Solo Lectura** es inviolable para la IA.
- **Límite de iteraciones**: 5–10 máximo en el AI Agent para cortar bucles y proteger el presupuesto de tokens.
- **Salida de error**: conectá Slack/Gmail a la rama de error para que el fallo no muera en silencio.

### 9. Herramientas del agente (Tools)
- Las Tools son los **ojos y manos** del agente: se arrastran al nodo AI Agent.
- **Instrucción huérfana**: una descripción vaga ("Google Sheets") hace que el modelo ignore o alucine la tool.
- Escribí descripciones operativas: el **cuándo, por qué y para qué** de cada conector.

### 10. Fallas en cascada
- **Alucinación heredada**: el error de A se propaga como verdad a B.
- **Bucle infinito**: dos especialistas se rebotan la tarea entre sí y agotan créditos.
- **Contexto en el handoff**: mandá siempre `original_input`, `intent` y `confidence` entre sub-workflows.

---

## Práctica en vivo (lo que se armó en n8n)

- **Parte 1:** un asistente de catálogo/ventas con AI Agents encadenados —
  `When chat message received → Detector_Productos (AI Agent + Structured Output Parser + modelo) → Admin_Datos (AI Agent + modelo)` — escribiendo en **Data tables** de n8n (CATALOGO_PROD, LEADS, SOLICITUDES, COMPRAS).
- **Parte 2:** los sub-workflows —
  - **Worker** con `Execute Workflow Trigger` (*Input data mode: Define using fields below* → Workflow Input Schema).
  - **Manager** de ejemplo: `INICIO → Obtener datos del sheet → Pasarlo a JSON → Call "Worker1_ValidadorDatos"` (nodo Execute Workflow).
  - Nodos de apoyo: `Code` (JS), `Set` / `Edit Fields`, `Google Sheets`.
- Durante la demo aparecieron errores reales de nodo (p. ej. el "Call Worker" fallando por leer un dato inexistente) — refuerzan la importancia de testear cada Worker aislado y de devolver JSON de contingencia.

---

## Cierre — puente al Módulo 3

El Módulo 3 (**Memoria, Contexto y Persistencia**) le suma a esta red la capacidad de recordar
estado entre ejecuciones. Idea final de la clase: *orquestar no es acumular agentes, es coordinar los justos.*

> Para la consigna y el checklist de la Pre-entrega 2, ver [`README.md`](./README.md).
