# Módulo 11 — Resumen de la clase y de la teoría

**Clase:** el Proyecto Final se explicó en la misma clase del Módulo 10 (13/10/2026, 1 h 51 min). El barrido de esa grabación está en [`../Modulo10/resumen-clase.md`](../Modulo10/resumen-clase.md); lo que aplica al final:

| Min | Contenido | Para el Proyecto Final |
|---:|---|---|
| 14–18 | Dónde desplegar n8n: nube vs. autoalojado (VPS), acceso a n8n Cloud | El sistema puede quedarse en n8n comunitario local (freemium); justificar el stack en el DMSA |
| 30–34 | Recorrido de la consigna del Proyecto Final en la plataforma | Ver [`consigna.md`](consigna.md) |
| 38–42 | Revisión del workflow de un alumno (entrega final en curso, error en un nodo HTTP) | Las ramas de error de los nodos HTTP son parte de la consigna |
| 82–97 | Demo "Clase Final - Oferta IA Agéntica por Telegram + ROI + Juez + HITL" | Patrón a reutilizar: Juez con salida estructurada → Switch APROBADO / CORREGIR (máx. 2) / HITL; cálculos de ROI en nodo de código (no los hace la IA) |
| 102 | Repositorio público de plantillas de n8n (awesome-n8n-templates) | Referencia |

**Material del profe** (Drive `Entregas/Trabajo Final/Del Profe`):
- `Clase_Final_Modelos_Comerciales_IA_Agentica_n8n.pptx`: es el mismo deck de 18 slides del M10, ya resumido en el resumen de esa clase. Lo nuevo y útil para el DMSA es la slide de **trazabilidad**, que en la grabación pasó rápido. Ahí aparecen los metadatos mínimos en el CRM: `origen = IA · timestamp · workflow_version · interaction_id · owner · estado · ventana_conversion_dias · kpi_atribuible`.
- `client_secret_….apps.googleusercontent.com.json`: **no es un workflow de ejemplo**. Es el archivo de credenciales OAuth de un cliente de Google, un secreto. No se copia al repo ni se usa. Si hace falta un ejemplo de workflow del profe, hay que pedírselo.

## Teoría: presentación "Proyecto final - Trabajo Final V2" (31 slides)
- **Objetivos:** ensamblar las pre-entregas en un sistema funcional y supervisado; conectar el AI-as-a-Judge para bloquear acciones de riesgo; robustez (idempotencia, reintentos, manejo de errores); ROI traducido a negocio; defensa ante un C-Suite.
- **El recorrido ensamblado:** M1–M3 agentes y memoria (Session_ID) · M4–M5 herramientas y RAG con citas · M6–M8 voz, especialización y Juez · M9–M10 gobernanza, costos y narrativa comercial. *"No entregás un flujo: entregás una solución de negocio, defendida."*
- **Componente A:** webhook que responde al toque y procesa en segundo plano → Juez obligatorio → despacho a Slack, Telegram o Gmail. Criterios: asincrónico, con supervisor ("nada se consolida en el CRM sin pasar por el Juez"), modular. **Robustez de grado industrial:** RAG con disciplina ("No sé"), idempotencia, ramas de error que alertan al Manager o al equipo.
- **Umbral (#FindTheBug):** si el Juez califica por debajo del umbral (ej. `exactitud_factual < 4`), se congela la autonomía y se desvía a una cola de aprobación humana: *"ese umbral es lo que hace que el sistema sea seguro para producción"*.
- **Componente B (DMSA):** portada y resumen; arquitectura (lienzo, flujo de datos, memoria persistente); auditoría (3 ejemplos reales en JSON); ROI (tokens vs. labor humana evitada). Hablar el idioma del comité: impacto, riesgo y valor; **mostrar el resultado** (mensaje despachado, registro actualizado, panel); defender decisiones (supervisor, fases, stack).
- **ROI que convence:** tokens mensuales optimizados con modelos económicos (GPT-4o-mini o Haiku) contra el costo de la labor evitada y el *lead time* antes/después. Pregunta del CFO: *"¿esto realmente nos ahorra plata o es un gasto nuevo?"*.
- **Clínica de integración (5 pasos)** y **rúbrica**: ver [`consigna.md`](consigna.md).
- **Seguridad:** exponer API keys o tokens reales puede reprobar; documentar variables de entorno y estructuras de tablas, nunca los valores.
