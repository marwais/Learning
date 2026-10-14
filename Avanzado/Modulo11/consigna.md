# Proyecto Final Integrador — Sistema Agéntico Empresarial

Fuentes: plataforma Coderhouse (14/10/2026) y documento "Trabajo Final - Consigna" en Drive (`IA/AI Automation/Avanzado`). **Plazo: 13/11/2026 20:59.** Se entrega por la plataforma (Ticher) en .pdf, .doc o .docx (máx. 10 MB).

## Objetivo
Ensamblar todos los componentes construidos en las pre-entregas en un sistema agéntico funcional, **asincrónico, idempotente y supervisado**, acompañado de un informe de consultoría ejecutiva. Se presenta ante un Comité de Innovación (C-Suite) demostrando viabilidad técnica, gobernanza de datos e impacto económico, usando solo capas de software y conexiones **gratuitas o freemium**.

## Qué entregar
PDF **`Apellido_Nombre_ProyectoFinal_AI_Experto.pdf`** → para nosotros `Waisburd_JulioMartin_ProyectoFinal_AI_Experto.pdf` ("Documentación Maestra del Sistema Agéntico", DMSA) con:
- Diagrama de la arquitectura (sub-workflows, Manager-Worker, correlación de traceId).
- Gobernanza y auditoría: cómo funciona el supervisor, umbrales configurados y métricas de precisión obtenidas en pruebas.
- ROI: horas humanas evitadas y TCO de las APIs vs. operación manual.
- Video (opcional): enlace público de máx. 3 minutos mostrando el flujo activo, incluido en el PDF o en comentarios.

## Criterios de aceptación
1. El sistema captura la petición **vía webhook y responde de inmediato**; el procesamiento ocurre de forma asincrónica.
2. La respuesta del agente pasa **obligatoriamente por el supervisor AI-as-a-Judge antes de consolidar datos o registrar en el CRM**.
3. El resultado validado se despacha a al menos **un canal externo** (Slack, WhatsApp, Gmail/Outlook).
4. Arquitectura modular: **sub-workflows independientes** bajo patrón Manager-Worker (sin flujos monolíticos).
5. El agente responde solo con información del **RAG indexado**, **cita fuentes con metadatos reales** y responde **"No sé"** ante consultas sin cobertura documental.
6. El sistema maneja **reintentos y fallas sin duplicar registros ni envíos**.

## Qué evitar
- Exponer API keys o tokens reales en prompts o textos.
- No trazar **ramas de error** ante caídas de APIs externas (el sistema de grado industrial debe **alertar al Manager o al equipo humano**).
- Informe con lenguaje técnico de nodos dirigido a un comité ejecutivo: traducir todo a impacto de negocio (tiempo, riesgo, valor).

## Componente A — El ecosistema técnico (workflows en n8n)
n8n comunitario o nube (prueba/freemium), patrón Manager-Worker:
1. **Petición asincrónica:** disparador (Webhook o Chat Trigger) que recibe la solicitud, **responde de inmediato al servidor externo con un código de recepción rápida** y procesa la lógica analítica en segundo plano.
2. **Auditoría activa (QA automatizado):** la propuesta de respuesta pasa obligatoriamente por el sub-workflow supervisor AI-as-a-Judge **antes de consolidar datos o registrar acciones comerciales**. Si la nota es inferior al umbral (ej. `exactitud_factual < 4` en la rúbrica JSON Schema), **se congela la autonomía** y se desvía a revisión humana mediante una **cola de aprobación (HITL)**.
3. **Notificación final:** despacho del resultado validado por un canal con API freemium o gratuita (borradores de Gmail, bot oficial de Telegram, canales de Slack).

## Componente B — La documentación de defensa (DMSA), 4 secciones fijas
1. **Portada y resumen ejecutivo:** título del proyecto, autor, **cohorte (2026)** y descripción del problema real de negocio resuelto.
2. **Diagrama de arquitectura de n8n:** **capturas nítidas del lienzo general** explicando la interconexión modular distributiva, el flujo de datos, la base de memoria persistente de largo plazo y el acople contextual. *(Acá sí van capturas del lienzo, a diferencia del brochure del M10.)*
3. **Reporte de auditoría y rúbricas:** **3 ejemplos reales** de respuestas de la IA evaluadas, criticadas y puntuadas **en formato JSON plano** por el supervisor.
4. **Justificación financiera (ROI):** coste mensual estimado en tokens (optimizando la ventana de contexto con **modelos económicos** como GPT-4o-mini o Claude Haiku) vs. coste de labor humana evitado, demostrando la rentabilidad.

**Gobernanza de datos:** la documentación técnica describe **variables de entorno, estructuras de tablas y parámetros de conexión**, sin exponer API keys ni tokens privados reales.

## Rúbrica (presentación "Proyecto final - Trabajo Final V2", sobre 100, se aprueba con 70)
| Criterio | Peso | Qué se mira |
|---|---:|---|
| Consolidación técnica | 35 % | Flujo asincrónico con el supervisor conectado y funcionando |
| Calidad del DMSA | 25 % | Secciones completas, ordenadas y de nivel ejecutivo |
| Arquitectura y persistencia | 20 % | Sub-workflows, memoria e integración coherente |
| Auditoría | 12 % | Los 3 ejemplos del Juez |
| ROI | 8 % | Justificación financiera plausible |

Advertencia de la presentación: **exponer API keys o tokens reales puede reprobar la entrega** ("la ciberseguridad también se evalúa").

## Pasos que propone la clase (clínica de integración)
1. **Flujo asincrónico:** webhook (o Chat Trigger) que responde de inmediato; lógica en segundo plano; todo bajo Manager-Worker.
2. **Conectar el supervisor:** Juez antes de consolidar datos; umbral (`exactitud_factual < 4`); lo dudoso a una cola de aprobación humana.
3. **Blindar la robustez:** idempotencia (sin duplicar registros ni envíos), reintentos y ramas de error que alerten al equipo, RAG que cita fuentes y dice "No sé".
4. **Redactar el DMSA:** 4 secciones, 3 ejemplos reales del Juez en JSON, todo traducido a impacto de negocio.
5. **Ensayar la defensa:** revisar que no haya API keys ni tokens expuestos; narrativa de impacto, riesgo y control; PDF final.

Mostrar resultados, no solo el lienzo: el mensaje despachado, el registro actualizado, el panel de control. Defender decisiones: por qué el supervisor, por qué el despliegue por fases, por qué ese stack.
