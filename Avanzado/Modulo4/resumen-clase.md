# Módulo 4 — Ecosistema de Herramientas e Integraciones

**Curso:** AI Automation Avanzado (Coderhouse) · **Clase en vivo:** 2h 23m
**Deck:** "Maestría en el Ecosistema de Herramientas e Integraciones — LIVE_SESSION" (Coderhouse 2026)
**Guía visual:** artifact "Ecosistema e Integraciones" (recorrido minutado + diagramas + sección de entrega).

---

## Resumen

El módulo cierra la columna de integraciones del curso: hasta acá el agente **pensaba** (M2) y **recordaba** (M3); ahora **actúa sobre el mundo real** leyendo y escribiendo en las apps que la empresa ya usa. La clase alterna teoría del deck, explicaciones a mano (Paint) y una demo larga en n8n construyendo un agente de atención conectado a **Gmail** y a una **Data Table**, con foco en **OAuth2** y en los **guardrails** que evitan romper la casilla o la base del cliente.

Idea que ordena el módulo: un conector nativo **encapsula** una API en menús/checkboxes. El valor del asesor no es arrastrar el nodo, sino decidir **qué** conectar, **con qué permisos** (mínimo privilegio) y **con qué controles**.

---

## Recorrido minutado (barrido completo)

Marcas: `slide` = deck · `n8n` = demo en vivo · `pizarra` = Paint.

| Min | Tema | Tipo |
|----:|------|------|
| 00–15 | Apertura y encuadre (de conectar nodos a diseñar el ecosistema) | — |
| ~18 | **Conectores nativos** — catálogo visual n8n: Workspace (Sheets/Gmail/Notion), Canales (Slack/Telegram/WhatsApp), Sistemas de registro (HubSpot/Salesforce) | slide |
| ~24 | Code node "Build HTML Signature" (preparar datos antes de un conector) | n8n |
| ~35 | Form Trigger "CONTACTENOS" (puerta de entrada de una consulta) | n8n |
| ~40 | **El panel de credenciales** — API Keys/Tokens vs OAuth2; nunca exponés contraseñas | slide |
| ~45 | **¿Qué es una API?** — Cliente (n8n) solicita → Servidor (Gmail) disponibiliza; `api.n8n.com` ↔ `api.google.com/gmail` | pizarra |
| 50–77 | **Setup OAuth2 Google ↔ n8n** — n8n Docs + Google Cloud Console: crear proyecto, habilitar APIs, pantalla de consentimiento, usuarios de prueba, crear **ID de cliente OAuth** (Aplicación web) con redirect URI `http://localhost:5678/rest/oauth2-credential/callback` | n8n |
| ~81 | Analogía de red (WiFi): localhost vs URL pública (túnel para webhooks) | pizarra |
| ~86 | Nodo **Webhook** — Test/Production URL; evento real con headers (Cloudflare, IP, user-agent) | n8n |
| ~91 | **Triage & Delegate** — Webhook → Router de triaje → Switch → Workers; taxonomía cerrada (BILLING/TECH_SUPPORT/SALES/OTHERS); salida JSON; fallback | slide |
| ~96 | **El CRM: fuente de verdad comercial** — Leer / Escribir / Mínimo privilegio | slide |
| 101–116 | Demo: **Form → AI Agent → Create draft in Gmail**; tool **Consulta** a Data Table "pedidos" (Get Row, condición definida por el modelo); se resuelve un error de credencial OAuth | n8n |
| ~121 | **FLUJO EJEMPLO** integrado — Chat Trigger → AI Agent (OpenAI + Simple Memory) con tools **Consulta** y **Escalar** | n8n |
| ~126 | **Modelo de 4 capas** — Herramientas → Integración → Proceso → Gobernanza | slide |
| 131–138 | **"Tu misión"** (pre-entrega): 3 conectores OAuth2 + IF anti auto-reply + lookup antes de crear + Create Draft HITL → `checkpoint4_nombre_apellido.json` | slide |
| ~142 | **Puente al Módulo 5** — RAG (conocimiento no estructurado) | slide |

---

## Conceptos clave (6 unidades)

1. **Conectores nativos** — nodos que encapsulan APIs; mantenibilidad (cambiar Slack por Teams = editar un nodo).
2. **Webhooks & Triage** — webhook como "timbre" en tiempo real (mejor que polling); router con taxonomía cerrada + Switch + fallback.
3. **CRM** — fuente de verdad comercial; **409** = duplicado (lookup antes de crear), **400** = payload mal formado (Set + validación).
4. **Email / HITL** — Email Trigger → triaje → especialista → **Create Draft**; la IA nunca envía sola.
5. **Canales directos** — WhatsApp/Telegram/Email; UX por canal + protocolo de escalado humano.
6. **Ecosistema** — 4 capas; Build/Buy/**Integrate** (Integrate primero); Observabilidad + Resiliencia + Fuente Única de Verdad; matriz de priorización.

### Errores de API (regla del docente)
- **400 Bad Request** → se previene **limpiando y validando** el payload (nodo **Set**).
- **409 Conflict** → se previene **consultando antes de escribir** (nodo **Look up**).
- Juntos son el criterio "Contención de Bucles y Mitigación de Errores" del Checkpoint 4 (**35% de la nota**).

---

## La demo en vivo

`Trigger (Form/Chat/Webhook) → AI Agent (OpenAI + Simple Memory)` con tres tools:
- **Consulta** → lookup en Data Table "pedidos" (leer).
- **Escalar** → derivar a humano.
- **Create Draft (Gmail)** → responder por borrador (HITL).

---

## Puente al Módulo 5

El agente quedó conectado a apps/canales/CRM y sabe leer/escribir **datos estructurados**. El M5 agrega el "cerebro documental" (**RAG**) para leer conocimiento **no estructurado**. Para llevar: *el 80% del valor no es cómo conectar, sino qué conectar y por qué.*
