# Learning — curso "AI Automation Avanzado" (Coderhouse)

Proyecto integrador **AgendaBot**: el coordinador de agenda de la Clínica LoDeTincho, hecho con n8n.
El proyecto crece módulo a módulo y no se rehace.
- M1 a M10 entregados.
- **M11 = Proyecto Final**, vence el **13/11/2026 a las 20:59**.

El estado y los pendientes están en el contexto vivo:

@docs/contexto.md

## Estructura del repo
- `Avanzado/ModuloN/`: cada módulo tiene su README (estado, pruebas y pendientes), consigna, resumen de la clase, scripts y exportaciones de los workflows.
- `Avanzado/Modulo5/scripts/_config.py`: cliente de la API de n8n que usan todos los scripts (`C.n8n(method, path, body)`). Lee `Avanzado/Modulo5/scripts/.env`, que está fuera de git.
- `Avanzado/scripts/`:
  - `activar_aqui.ps1` / `desactivar_aqui.ps1`: cambian de PC.
  - `levantar_ngrok.ps1`: levanta el túnel.
  - `maquinas.json`: datos de las dos PCs.
- `Avanzado/Modulo11/`:
  - `scripts/`: construcción y pruebas.
  - `evaluacion/`: batería y finanzas.
  - `DMSA/`: el documento final y `build_pdf.py`.
  - `_ids_m11.json`: ids de los workflows.
  - `_aux_m11.json`: ids de las Data Tables y las credenciales.

## Entorno
- **Dos PCs: LOBO** (repo en `C:\MW\...\Learning`) **y WOLVERINE** (repo en `G:\Trabajos\MW\IA\SessionLocal\Learning`). Solo una puede tener n8n activo, porque comparten el bot de Telegram y Gmail. Para cambiar, se corre `Avanzado\scripts\activar_aqui.ps1` en la que se va a usar.
- **n8n**:
  - Versión 2.39.5 en Docker, en `http://localhost:5678`, con un bind mount de `C:\Users\mwais\.n8n`.
  - API en `/api/v1` con el header `X-N8N-API-KEY`. La key está en `.env`.
- **Variables de n8n**:
  - `WEBHOOK_URL`: el dominio fijo de ngrok.
  - `N8N_EDITOR_BASE_URL=http://localhost:5678/`: sin esto, el OAuth de Google da `redirect_uri_mismatch`.
- **Túnel**: ngrok con dominio fijo; el token y el dominio están en `.env`. Cloudflare quick tunnel queda solo de respaldo, porque la red pública bloquea el puerto 7844.
- **Google**:
  - Gmail y Sheets se autorizan con **mwquiero@gmail.com**. El cliente OAuth está en modo Testing, así que el token vence cada 7 días.
  - Las planillas tienen que estar compartidas como editor con esa cuenta; si no, Sheets da 403.
- **Datos**:
  - Qdrant local, colección `kb_lodetincho`, con embeddings de Cohere `embed-multilingual-v3.0`.
  - Airtable: base Memoria_Agente.
  - HubSpot: propiedades `agendabot_*`.
- **Repo**: github.com/marwais/Learning, push con git local. Los entregables van a Google Drive `IA/AI Automation/Avanzado/Entregas/0N`.

## Convenciones
- Al arrancar un módulo, se duplica el anterior con recursos propios: carpeta de Drive, planilla, tabla de Airtable, `moduloN.config.json` y `_ids_mN.json`.
  - Excepción del Proyecto Final: va con **nombres de producción sin sufijos del curso** ("AgendaBot · Manager", `/webhook/agendabot`, `pedidos_procesados`, etc.).
- **Los workflows se construyen por la API de n8n con scripts Python idempotentes.** El flujo es:
  1. GET del workflow;
  2. modificar los nodos y las conexiones;
  3. PUT con `settings` filtrados;
  4. republicar;
  5. exportar el JSON.

  Las fábricas de nodos están en `Modulo11/scripts/seguridad_p2_m11.py` (`si`, `dt`, `set_json`, `set_campos`, `slack_post`, `exec_wf`, `conectar`, `republicar`).
- **No-Code híbrido** (decisión del usuario): los nodos Code heredados no se migran. Todo lo nuevo se hace con nodos visuales (IF, Set, Switch, Data Table, Slack, etc.).
- Para probar, se usan `Modulo11/scripts/probar_webhook.py` (manda UTF-8; curl desde Git Bash no lo hace) y `ver_ejecucion.py <clave> [n] [--nodo X]`.
- Las entregas son PDFs generados por un script (markdown → HTML → Edge headless) y se verifican con `pdftotext` contra la consigna.
- La documentación y los mensajes al paciente van en castellano rioplatense, con voseo.
- Los commits son `feat(MN): …` / `docs(MN): …`, en castellano.

## Reglas de seguridad (del usuario)
- Nunca pegar claves en el chat ni guardarlas en git o en Drive: van en `Avanzado/Modulo5/scripts/.env`.
- En el DMSA nunca se exponen valores de claves; exponer una API key puede reprobar.
- No copiar el `client_secret_*.json` de "Del Profe".
- Los cambios de seguridad los hace el usuario: firewall, OAuth, scopes de HubSpot, reconexión de credenciales.
- No tocar otros proyectos de Docker.
- En Google Docs, nunca usar Ctrl+A: usar Buscar y reemplazar.

## Gotchas de n8n que costaron tiempo
- **Guardado y publicación**:
  - El `staticData` se guarda recién al **terminar** la ejecución. Por eso la idempotencia vive en el Receptor (dura menos de 1 s) y en las Data Tables.
  - Los sub-workflows y el Error Workflow tienen que estar **publicados**.
  - **Antes de editar por la API, recargar las pestañas abiertas de n8n.** Una pestaña vieja guardó sola y revirtió cambios: los modelos volvieron a Sonnet.
- **Nodos**:
  - Execution order v1: las ramas se recorren por posición. Lo que tiene que correr sí o sí (por ejemplo, el escalado) va **en serie**, no en una rama paralela.
  - HubSpot v2.1: las operaciones de contacto son `upsert`, `search`, `get`, `getAll` y `delete`. `create` y `update` no existen; los nodos heredados del M4 nunca escribían.
  - Data Tables: nodo `n8n-nodes-base.dataTable` v1.1. En la API, `/data-tables` y `/data-tables/{id}/rows`.
- **Credenciales**:
  - La API no permite renombrarlas: hay que crear una nueva.
- **Base de conocimiento**: el workflow Ingesta KB lleva el markdown embebido en un nodo Code. Para reindexar se usa `scripts/mantenimiento_m11.py` (workflow temporal), no se edita a mano.
- **Proveedores**: si se agota el saldo de Anthropic, se paran el Router, el RAG y el Juez. Las alertas de Slack lo traducen al castellano.
