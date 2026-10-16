# -*- coding: utf-8 -*-
"""Proyecto Final (M11) — petición asincrónica en un workflow propio: "Receptor (M11)".

Por qué: n8n guarda la memoria del workflow (staticData) recién al terminar la ejecución. Si el control de
idempotencia del webhook vive en el Manager (que tarda ~20 s), un reintento que llega mientras tanto no ve
la clave y se procesa dos veces. El Receptor termina en menos de un segundo, así que su memoria queda
guardada antes de que llegue cualquier reintento.

Receptor (M11): Webhook POST /webhook/agendabot -> Entrada webhook (valida) -> ¿Petición válida?
  -> 400 | Generar traceId -> Control de idempotencia -> Responder (202 recibido / 200 duplicado)
  -> ¿Pedido nuevo? -> "Procesar en segundo plano (Manager)" (Execute Workflow sin esperar).
Manager M11: se quitan los nodos del webhook que instaló webhook_m11.py y se agrega el disparador
  "Llamada de un canal (Receptor / Telegram)" -> Normalizar entrada. "Generar traceId" reutiliza el traceId del Receptor y
  "Control de idempotencia" no vuelve a controlar los pedidos del webhook. El despacho final queda igual.

Uso:  python receptor_m11.py      # idempotente
"""
import json, os, sys, uuid, copy
sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
MOD11 = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "..", "..", "Modulo5", "scripts"))
sys.path.insert(0, HERE)
import _config as C  # noqa: E402
import webhook_m11 as W  # noqa: E402  (código de los nodos de entrada y la respuesta 202)

IDS_PATH = os.path.join(MOD11, "_ids_m11.json")
IDS = json.load(open(IDS_PATH))
SETTINGS_OK = W.SETTINGS_OK

GENERAR_TRACEID_RECEPTOR = r"""// traceId único por pedido: el Receptor lo genera y lo devuelve en la respuesta 202; el Manager lo reutiliza.
// Formato: trc-<fecha>-<executionId del Receptor>-<sufijo aleatorio>
const ahora = new Date();
const fecha = ahora.toISOString().slice(0, 19).replace(/[-:T]/g, '');
const traceId = 'trc-' + fecha + '-' + $execution.id + '-' + Math.random().toString(36).slice(2, 6);
return [{ json: { ...$json, traceId, trace_inicio: ahora.toISOString() } }];"""

CONTROL_RECEPTOR = r"""// Idempotencia del webhook: la clave es el request_id que manda el sistema externo (o el header
// Idempotency-Key). Si ya se recibió en los últimos 7 días, se responde "duplicado" con el traceId
// original y el pedido NO se vuelve a procesar. Las claves se guardan en la memoria del Receptor, que
// termina en menos de un segundo (así un reintento inmediato ya encuentra la clave).
const j = $json;
const idemKey = 'wh-' + j.request_id;
const s = $getWorkflowStaticData('global');
s.procesados = s.procesados || {};
const ahora = Date.now(), TTL = 7 * 24 * 3600 * 1000;
for (const [k, v] of Object.entries(s.procesados)) if (ahora - (v.t || v) > TTL) delete s.procesados[k];
const previo = s.procesados[idemKey];
if (previo) return [{ json: { ...j, idemKey, duplicado: true, traceId_original: previo.traceId || '' } }];
s.procesados[idemKey] = { t: ahora, traceId: j.traceId };
return [{ json: { ...j, idemKey, duplicado: false } }];"""

GENERAR_TRACEID_MANAGER = r"""// traceId único por mensaje entrante: viaja a TODOS los sub-workflows y queda en cada log.
// Si el pedido vino por el Receptor (webhook), se reutiliza el traceId que ya se le devolvió al que llamó.
// Formato: trc-<fecha>-<executionId>-<sufijo aleatorio>
const j = $json;
const ahora = new Date();
const fecha = ahora.toISOString().slice(0, 19).replace(/[-:T]/g, '');
const traceId = j.traceId || ('trc-' + fecha + '-' + $execution.id + '-' + Math.random().toString(36).slice(2, 6));
return [{ json: { ...j, traceId, trace_inicio: j.trace_inicio || ahora.toISOString() } }];"""

CONTROL_MANAGER = r"""// Idempotencia: cada pedido tiene una clave única según su canal (tg-<update_id>, gm-<id del mail>,
// chat-<ejecución>). Si la clave ya se procesó en los últimos 7 días, el pedido se marca como repetido y
// no se registra ni se responde dos veces. Los pedidos del webhook ya los controló el Receptor (M11).
const j = $json;
const canal = String(j.canal || '');
if (canal === 'webhook') return [{ json: { ...j, idemKey: 'wh-' + j.request_id, duplicado: false } }];
let idemKey;
if (canal.startsWith('telegram')) idemKey = 'tg-' + j.update_id;  // lo manda el Canal Telegram (M11)
else if (canal === 'email') idemKey = 'gm-' + $('Email entrante (Gmail Trigger)').first().json.id;
else idemKey = 'chat-' + $execution.id;
const s = $getWorkflowStaticData('global');
s.procesados = s.procesados || {};
const ahora = Date.now(), TTL = 7 * 24 * 3600 * 1000;
for (const [k, v] of Object.entries(s.procesados)) if (ahora - (v.t || v) > TTL) delete s.procesados[k];
const previo = s.procesados[idemKey];
if (previo) return [{ json: { ...j, idemKey, duplicado: true, traceId_original: previo.traceId || '' } }];
s.procesados[idemKey] = { t: ahora, traceId: j.traceId };
return [{ json: { ...j, idemKey, duplicado: false } }];"""

WEBHOOK_NODOS = {"Webhook (petición asincrónica)", "Entrada webhook", "¿Petición válida?", "Rechazar petición (400)",
                 "¿Vino por webhook?", "Responder recibido (202)"}


def receptor(manager_id, if_base):
    n, c = W.nodo, W.cond_if
    nodes = [
        n("Webhook (petición asincrónica)", "n8n-nodes-base.webhook", 2, [0, 300],
          {"httpMethod": "POST", "path": "agendabot", "responseMode": "responseNode", "options": {}},
          webhookId=str(uuid.uuid4())),
        n("Entrada webhook", "n8n-nodes-base.code", 2, [220, 300], {"jsCode": W.ENTRADA_WEBHOOK}),
        c(if_base, "¿Petición válida?", [440, 300], "={{ $json.valido }}",
          {"type": "boolean", "operation": "true", "singleValue": True}),
        n("Rechazar petición (400)", "n8n-nodes-base.respondToWebhook", 1.1, [660, 480],
          {"respondWith": "json",
           "responseBody": "={{ JSON.stringify({ estado: 'rechazado', faltan: $json.faltan }) }}",
           "options": {"responseCode": 400}}),
        n("Generar traceId", "n8n-nodes-base.code", 2, [660, 280], {"jsCode": GENERAR_TRACEID_RECEPTOR}),
        n("Control de idempotencia", "n8n-nodes-base.code", 2, [880, 280], {"jsCode": CONTROL_RECEPTOR}),
        n("Responder (202 recibido / 200 duplicado)", "n8n-nodes-base.respondToWebhook", 1.1, [1100, 280],
          {"respondWith": "json", "responseBody": W.RESPUESTA_202,
           "options": {"responseCode": "={{ $json.duplicado ? 200 : 202 }}"}}),
        c(if_base, "¿Pedido nuevo?", [1320, 280], "={{ $json.duplicado }}",
          {"type": "boolean", "operation": "false", "singleValue": True}),
        n("Procesar en segundo plano (Manager)", "n8n-nodes-base.executeWorkflow", 1.2, [1540, 200],
          {"workflowId": {"__rl": True, "value": manager_id, "mode": "list",
                          "cachedResultName": "AI Automation Avanzado - M11"},
           "workflowInputs": {"mappingMode": "defineBelow", "value": {}, "matchingColumns": [], "schema": [],
                              "attemptToConvertTypes": False, "convertFieldsToString": True},
           "options": {"waitForSubWorkflow": False}}),
        n("Pedido repetido (descartado)", "n8n-nodes-base.noOp", 1, [1540, 380], {}),
        n("Nota", "n8n-nodes-base.stickyNote", 1, [-40, -20],
          {"width": 1760, "height": 240, "content":
           "## Receptor (M11): petición asincrónica e idempotente\n"
           "Un sistema externo (web de turnos, app, CRM) manda `POST /webhook/agendabot` con "
           "`request_id`, `mensaje`, `nombre` y `email` y/o `tg_chat_id`. El Receptor **responde al instante** "
           "(202 con el traceId; 400 si falta un dato; 200 \"duplicado\" si el request_id ya se recibió) y le "
           "pasa el pedido al **Manager** sin esperarlo: el análisis, el Juez y el registro ocurren en segundo "
           "plano y el resultado sale por Telegram o como borrador de Gmail. La idempotencia vive acá porque "
           "esta ejecución dura menos de un segundo y su memoria queda guardada antes de cualquier reintento."}),
    ]
    con = {}
    for a, b, o in [("Webhook (petición asincrónica)", "Entrada webhook", 0), ("Entrada webhook", "¿Petición válida?", 0),
                    ("¿Petición válida?", "Generar traceId", 0), ("¿Petición válida?", "Rechazar petición (400)", 1),
                    ("Generar traceId", "Control de idempotencia", 0),
                    ("Control de idempotencia", "Responder (202 recibido / 200 duplicado)", 0),
                    ("Responder (202 recibido / 200 duplicado)", "¿Pedido nuevo?", 0),
                    ("¿Pedido nuevo?", "Procesar en segundo plano (Manager)", 0),
                    ("¿Pedido nuevo?", "Pedido repetido (descartado)", 1)]:
        W.link(con, a, b, o)
    return {"name": "Receptor (M11)", "nodes": nodes, "connections": con,
            "settings": {"executionOrder": "v1", "saveDataErrorExecution": "all", "saveDataSuccessExecution": "all"}}


def republicar(wid):
    try:
        C.n8n("POST", f"/workflows/{wid}/deactivate")
    except Exception:
        pass
    C.n8n("POST", f"/workflows/{wid}/activate")


def main():
    w = C.n8n("GET", f"/workflows/{IDS['manager']}")
    N = {n["name"]: n for n in w["nodes"]}
    con = w["connections"]
    if_base = N["¿Vino por Telegram?"]
    # 1. Manager: sacar los nodos del webhook y poner el disparador "Llamada de un canal (Receptor / Telegram)"
    w["nodes"] = [n for n in w["nodes"] if n["name"] not in WEBHOOK_NODOS]
    for k in WEBHOOK_NODOS:
        con.pop(k, None)
    if "Llamada de un canal (Receptor / Telegram)" not in N:
        w["nodes"].append(W.nodo("Llamada de un canal (Receptor / Telegram)", "n8n-nodes-base.executeWorkflowTrigger", 1.1, [-1760, -150],
                                 {"inputSource": "passthrough"}))
    con["Llamada de un canal (Receptor / Telegram)"] = {"main": [[{"node": "Normalizar entrada", "type": "main", "index": 0}]]}
    con["Control de idempotencia"] = {"main": [[{"node": "¿Pedido nuevo?", "type": "main", "index": 0}]]}
    N = {n["name"]: n for n in w["nodes"]}
    N["Generar traceId"]["parameters"]["jsCode"] = GENERAR_TRACEID_MANAGER
    nz = N["Normalizar entrada"]["parameters"]
    nz["jsCode"] = nz["jsCode"].replace("request_id: j.request_id } }];",
                                        "request_id: j.request_id, traceId: j.traceId, trace_inicio: j.trace_inicio } }];")
    N["Control de idempotencia"]["parameters"]["jsCode"] = CONTROL_MANAGER
    N["¿Pedido nuevo?"]["position"] = [-440, 470]
    N["Pedido repetido (descartado)"]["position"] = [-440, 680]
    settings = {k: v for k, v in (w.get("settings") or {}).items() if k in SETTINGS_OK}
    C.n8n("PUT", f"/workflows/{IDS['manager']}",
          {"name": w["name"], "nodes": w["nodes"], "connections": con, "settings": settings})
    republicar(IDS["manager"])
    print("Manager: nodos del webhook quitados; disparador 'Llamada del Receptor' agregado; publicado")
    # 2. Receptor
    body = receptor(IDS["manager"], if_base)
    if IDS.get("receptor"):
        r = C.n8n("PUT", f"/workflows/{IDS['receptor']}", body)
    else:
        r = C.n8n("POST", "/workflows", body)
        man = IDS.pop("manager")
        IDS["receptor"] = r["id"]
        IDS["manager"] = man  # el Manager queda último (activar_aqui lo activa al final)
        json.dump(IDS, open(IDS_PATH, "w"), indent=1)
    w2 = C.n8n("GET", f"/workflows/{r['id']}")
    C.n8n("PUT", f"/workflows/{r['id']}", {"name": w2["name"], "nodes": w2["nodes"], "connections": w2["connections"],
                                           "settings": {**body["settings"], "errorWorkflow": IDS["errores"]}})
    republicar(r["id"])
    print(f"Receptor: {r['name']} ({r['id']}) — publicado en POST /webhook/agendabot")
    for wid, archivo in [(IDS["manager"], "AI Automation Avanzado - M11.json"), (r["id"], "Receptor (M11).json")]:
        x = C.n8n("GET", f"/workflows/{wid}")
        x = {k: x[k] for k in ("name", "nodes", "connections", "settings") if k in x}
        json.dump(x, open(os.path.join(MOD11, archivo), "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
