# Proyecto Final Integrador — Sistema Agéntico Empresarial

Relevado de la plataforma Coderhouse el 14/10/2026 (unidad "Entrega final: sistema agéntico empresarial desplegado y defendido"). **Plazo: 13/11/2026 20:59.** Se entrega por la plataforma (Ticher) en .pdf, .doc o .docx (máx. 10 MB).

## Objetivo
Ensamblar todos los componentes construidos en las pre-entregas en un sistema agéntico funcional, asincrónico y supervisado, acompañado de un informe de consultoría ejecutiva. Presentarlo ante un Comité de Innovación (C-Suite) demostrando viabilidad técnica, gobernanza de datos e impacto económico, usando solo capas de software y conexiones gratuitas o freemium.

## Qué entregar
PDF `Apellido_Nombre_ProyectoFinal_AI_Experto.pdf` ("Documentación Maestra del Sistema Agéntico", DMSA) con:
- Diagrama de la arquitectura (sub-workflows, Manager-Worker, correlación de traceId).
- Gobernanza y auditoría: cómo funciona el supervisor, umbrales configurados y métricas de precisión obtenidas en pruebas.
- ROI: horas humanas evitadas y TCO de las APIs vs. operación manual.
- Video (opcional): enlace público de máx. 3 minutos mostrando el flujo activo, incluido en el PDF o en comentarios.

## Criterios de aceptación
- El sistema captura la petición vía webhook y responde de inmediato; el procesamiento ocurre de forma asincrónica.
- La respuesta del agente pasa obligatoriamente por el supervisor AI-as-a-Judge antes de consolidar datos o registrar en el CRM.
- El resultado validado se despacha a al menos un canal externo (Slack, WhatsApp, Gmail/Outlook).
- Arquitectura modular: sub-workflows independientes bajo patrón Manager-Worker (sin flujos monolíticos).
- El agente responde solo con información del RAG indexado, cita fuentes con metadatos reales y responde "No sé" ante consultas sin cobertura documental.
- El sistema maneja reintentos y fallas sin duplicar registros ni envíos.

## Qué evitar
- Exponer API keys o tokens reales en prompts o textos.
- No trazar ramas de error ante caídas de APIs externas (debe alertar al Manager o al equipo humano).
- Informe con lenguaje técnico de nodos dirigido a un comité ejecutivo: traducir todo a impacto de negocio (tiempo, riesgo, valor).

## Componente A — El ecosistema técnico (workflows en n8n)
n8n comunitario o nube (prueba/freemium), patrón Manager-Worker:
- **Petición asincrónica:** disparador (Webhook o Chat Trigger) que responde de inmediato con un código de recepción y procesa en segundo plano.
- **Auditoría activa (QA automatizado):** la propuesta de respuesta pasa obligatoriamente por el sub-workflow supervisor AI-as-a-Judge antes de consolidar datos o registrar acciones comerciales. Si la nota es inferior al umbral (ej. `exactitud_factual < 4` en la rúbrica JSON Schema), se congela la autonomía y se desvía a revisión humana (cola de aprobación HITL).
- **Notificación final:** despacho del resultado validado por un canal con API freemium o gratuita (borradores de Gmail, bot de Telegram, canales de Slack).

## Componente B — La documentación de defensa (DMSA), 4 secciones fijas
1. **Portada y resumen ejecutivo:** título, autor, cohorte (2026) y problema real de negocio resuelto.
2. **Diagrama de arquitectura de n8n:** capturas nítidas del lienzo general explicando la interconexión modular, el flujo de datos, la memoria persistente de largo plazo y el acople contextual.
3. **Reporte de auditoría y rúbricas:** 3 ejemplos reales de respuestas evaluadas, criticadas y puntuadas en JSON plano por el supervisor.
4. **Justificación financiera (ROI):** coste mensual estimado en tokens (con modelos económicos como GPT-4o-mini o Claude Haiku) vs. coste de labor humana evitado.

**Gobernanza de datos:** describir variables de entorno, estructuras de tablas y parámetros de conexión, sin exponer API keys ni tokens reales.

## Estado del sistema frente a los criterios (a revisar al arrancar el M11)
| Criterio | Situación en el M9 |
|---|---|
| Webhook que responde de inmediato + proceso asincrónico | Hoy los disparadores son chat, Gmail y Telegram; falta un webhook con respuesta inmediata explícita. |
| Juez antes de registrar en el CRM | El Juez evalúa la ruta INFO; revisar que también gobierne las acciones comerciales (HubSpot, agenda). |
| Despacho a canal externo | Slack, Gmail y Telegram ya conectados. |
| Manager-Worker modular | Sí (Router + 4 workers + Tool RAG + Juez). |
| RAG con citas y "No sé" | Sí (M5, Min Score 0.60). |
| Reintentos sin duplicados | Parcial (filtro de `update_id` de Telegram en el M6; revisar idempotencia de registros). |
