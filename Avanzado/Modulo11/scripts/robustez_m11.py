# -*- coding: utf-8 -*-
"""Proyecto Final (M11) — Prioridad 1, pasos 3 y 4: ramas de error, reintentos e idempotencia.

1. Crea (o actualiza) el workflow "Errores (M11)": Error Trigger -> lee la ejecución fallida por la API
   de n8n -> alerta a Slack (#soporte) con workflow, nodo, error, traceId y paciente -> si el paciente
   escribió por Telegram, le avisa que hay demoras. Queda como Error Workflow del Manager M11.
2. Crea "Simulacro de falla (M11)": webhook que falla a propósito, para probar y mostrar la alerta.
3. Manager M11:
   - nodo "Control de idempotencia" entre "Normalizar entrada" y "Generar traceId": clave única por
     pedido (tg-<update_id>, gm-<id del mail>, wh-<request_id>, chat-<ejecución>); si la clave ya se
     procesó en los últimos 7 días, el pedido se descarta (no se registra ni se responde dos veces);
   - la clave viaja a los Workers junto con el traceId;
   - "Crear registro inicial" (Airtable) pasa de create a upsert por Session_ID;
   - Retry on Fail (3 intentos, 2 s) en las APIs externas (no en las esperas de Slack ni en la ingesta).
4. Worker 1: append -> appendOrUpdate por ID, con ID = "T-" + clave de idempotencia (un reintento
   actualiza la misma fila en vez de duplicar el turno).
5. Settings de todos los workflows M11: se guardan las ejecuciones con error y con éxito (evidencia).

Uso:  python robustez_m11.py      # idempotente: se puede correr varias veces
"""
import json, os, sys, uuid, copy
sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
MOD11 = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "..", "..", "Modulo5", "scripts"))
import _config as C  # noqa: E402

IDS_PATH = os.path.join(MOD11, "_ids_m11.json")
IDS = json.load(open(IDS_PATH))
AUX_PATH = os.path.join(MOD11, "_aux_m11.json")   # ids de credenciales auxiliares (sin secretos)
AUX = json.load(open(AUX_PATH)) if os.path.exists(AUX_PATH) else {}

SLACK_CRED = {"slackOAuth2Api": {"id": "M9PprPoqQvpvY6pT", "name": "Slack account"}}
TG_CRED = {"telegramApi": {"id": "x7iGZ1Z1LuKEKu80", "name": "Telegram account"}}
SOPORTE = {"__rl": True, "value": "C0C4YCJ2M60", "mode": "list", "cachedResultName": "soporte"}
SETTINGS_OK = {"executionOrder", "saveDataSuccessExecution", "saveDataErrorExecution", "saveManualExecutions",
               "saveExecutionProgress", "executionTimeout", "errorWorkflow", "timezone", "callerPolicy"}
RETRY = {"retryOnFail": True, "maxTries": 3, "waitBetweenTries": 2000}
SIN_REINTENTO = {"Borrar colección (Qdrant)", "Crear colección (Qdrant)", "Vector Store Qdrant (insert)",
                 "Embeddings Cohere (insert)"}  # ingesta manual de la base: se corre a mano


def guardar_aux():
    json.dump(AUX, open(AUX_PATH, "w"), indent=1)


def put(wid, w, settings_extra=None):
    settings = {k: v for k, v in (w.get("settings") or {}).items() if k in SETTINGS_OK}
    settings.update(settings_extra or {})
    body = {"name": w["name"], "nodes": w["nodes"], "connections": w["connections"], "settings": settings}
    return C.n8n("PUT", f"/workflows/{wid}", body)


def crear_o_actualizar(clave, body):
    # Los workflows nuevos van a _ids_m11.json: activar_aqui.ps1 los publica (el de errores debe estar activo).
    if IDS.get(clave):
        return C.n8n("PUT", f"/workflows/{IDS[clave]}", body)
    r = C.n8n("POST", "/workflows", body)
    IDS[clave] = r["id"]
    json.dump(IDS, open(IDS_PATH, "w"), indent=1)
    return r


def republicar(wid):
    try:
        C.n8n("POST", f"/workflows/{wid}/deactivate")
    except Exception:
        pass
    C.n8n("POST", f"/workflows/{wid}/activate")


# ---------------------------------------------------------------- 1. credencial para leer ejecuciones
def credencial_api():
    if AUX.get("cred_n8n_api"):
        return AUX["cred_n8n_api"]
    r = C.n8n("POST", "/credentials", {"name": "n8n API local (M11 errores)", "type": "httpHeaderAuth",
                                       "data": {"name": "X-N8N-API-KEY", "value": C.N8N_KEY}})
    AUX["cred_n8n_api"] = r["id"]
    guardar_aux()
    return r["id"]


ARMAR_ALERTA = r"""// Arma la alerta para el equipo humano y, si se puede, el aviso al paciente.
const e = $('Error Trigger').first().json;
const ex = e.execution || {}, wf = e.workflow || {};
const rd = (($json.data || {}).resultData || {}).runData || {};
const salida = n => { try { return rd[n][0].data.main[0][0].json; } catch (_) { return {}; } };
const norm = salida('Normalizar entrada');
const traceId = salida('Generar traceId').traceId || '(sin traceId: falló antes de generarlo)';
const err = ex.error || {};
const texto = [
  ':rotating_light: *AgendaBot — falla en producción*',
  `*Workflow:* ${wf.name || '?'} · *Nodo:* ${ex.lastNodeExecuted || (err.node || {}).name || '?'}`,
  `*Error:* ${String(err.message || 'sin mensaje').slice(0, 300)}`,
  `*traceId:* ${traceId} · *Ejecución:* ${ex.id || '?'}`,
  `*Paciente:* canal ${norm.canal || '?'} · sesión ${norm.sessionId || '?'}${norm.email_entrada ? ' · ' + norm.email_entrada : ''}`,
  '*Acción:* tomar el caso y contactar al paciente; revisar la ejecución en n8n.'
].join('\n');
return [{ json: {
  texto, traceId, canal: norm.canal || '', tg_chat_id: norm.tg_chat_id || '',
  aviso_paciente: 'Estamos con demoras: una persona del equipo te va a responder en unos minutos. Disculpá la espera.'
} }];"""


def workflow_errores(cred_id):
    nodes = [
        {"id": str(uuid.uuid4()), "name": "Error Trigger", "type": "n8n-nodes-base.errorTrigger", "typeVersion": 1,
         "position": [0, 300], "parameters": {}},
        {"id": str(uuid.uuid4()), "name": "Leer ejecución fallida", "type": "n8n-nodes-base.httpRequest",
         "typeVersion": 4.2, "position": [220, 300], "onError": "continueRegularOutput",
         "retryOnFail": True, "maxTries": 2, "waitBetweenTries": 1000,
         "parameters": {"url": "=http://localhost:5678/api/v1/executions/{{ $json.execution.id }}",
                        "authentication": "genericCredentialType", "genericAuthType": "httpHeaderAuth",
                        "sendQuery": True,
                        "queryParameters": {"parameters": [{"name": "includeData", "value": "true"}]},
                        "options": {"timeout": 15000}},
         "credentials": {"httpHeaderAuth": {"id": cred_id, "name": "n8n API local (M11 errores)"}}},
        {"id": str(uuid.uuid4()), "name": "Armar alerta", "type": "n8n-nodes-base.code", "typeVersion": 2,
         "position": [440, 300], "parameters": {"jsCode": ARMAR_ALERTA}},
        {"id": str(uuid.uuid4()), "name": "Alertar al equipo (Slack)", "type": "n8n-nodes-base.slack",
         "typeVersion": 2.3, "position": [680, 200], "webhookId": str(uuid.uuid4()), **RETRY,
         "parameters": {"authentication": "oAuth2", "resource": "message", "operation": "post", "select": "channel",
                        "channelId": SOPORTE, "text": "={{ $json.texto }}",
                        "otherOptions": {"includeLinkToWorkflow": False}},
         "credentials": SLACK_CRED},
        {"id": str(uuid.uuid4()), "name": "¿Paciente en Telegram?", "type": "n8n-nodes-base.if", "typeVersion": 2.2,
         "position": [680, 420],
         "parameters": {"conditions": {"options": {"caseSensitive": True, "leftValue": "", "typeValidation": "loose",
                                                   "version": 2},
                                       "conditions": [{"id": str(uuid.uuid4()),
                                                       "leftValue": "={{ $json.tg_chat_id }}", "rightValue": "",
                                                       "operator": {"type": "string", "operation": "notEmpty",
                                                                    "singleValue": True}}],
                                       "combinator": "and"},
                        "looseTypeValidation": True, "options": {}}},
        {"id": str(uuid.uuid4()), "name": "Avisar demora (Telegram)", "type": "n8n-nodes-base.telegram",
         "typeVersion": 1.2, "position": [900, 400], "webhookId": str(uuid.uuid4()), **RETRY,
         "parameters": {"chatId": "={{ $json.tg_chat_id }}", "text": "={{ $json.aviso_paciente }}",
                        "additionalFields": {"appendAttribution": False}},
         "credentials": TG_CRED},
        {"id": str(uuid.uuid4()), "name": "Nota", "type": "n8n-nodes-base.stickyNote", "typeVersion": 1,
         "position": [-40, 0],
         "parameters": {"width": 1000, "height": 220, "content":
                        "## Errores (M11): rama de error de grado industrial\n"
                        "Se dispara cuando falla una ejecución del Manager M11 (o del simulacro). Lee la ejecución "
                        "fallida por la API de n8n para recuperar el **traceId** y el canal del paciente, **alerta al "
                        "equipo humano en Slack** (#soporte) y, si el paciente escribió por Telegram, le avisa que hay "
                        "demoras. Credencial: encabezado `X-N8N-API-KEY` guardado en las credenciales de n8n "
                        "(el valor no está en el workflow)."}},
    ]
    con = {"Error Trigger": {"main": [[{"node": "Leer ejecución fallida", "type": "main", "index": 0}]]},
           "Leer ejecución fallida": {"main": [[{"node": "Armar alerta", "type": "main", "index": 0}]]},
           "Armar alerta": {"main": [[{"node": "Alertar al equipo (Slack)", "type": "main", "index": 0},
                                      {"node": "¿Paciente en Telegram?", "type": "main", "index": 0}]]},
           "¿Paciente en Telegram?": {"main": [[{"node": "Avisar demora (Telegram)", "type": "main", "index": 0}], []]}}
    return {"name": "Errores (M11)", "nodes": nodes, "connections": con,
            "settings": {"executionOrder": "v1", "saveDataErrorExecution": "all", "saveDataSuccessExecution": "all"}}


def workflow_simulacro(err_id):
    nodes = [
        {"id": str(uuid.uuid4()), "name": "Webhook simulacro", "type": "n8n-nodes-base.webhook", "typeVersion": 2,
         "position": [0, 300], "webhookId": str(uuid.uuid4()),
         "parameters": {"httpMethod": "POST", "path": "simulacro-falla-m11", "responseMode": "onReceived",
                        "options": {"responseCode": 202}}},
        {"id": str(uuid.uuid4()), "name": "API externa caída (simulada)", "type": "n8n-nodes-base.code",
         "typeVersion": 2, "position": [240, 300],
         "parameters": {"jsCode": "// Simula la caída de una API externa para probar la rama de error.\n"
                                  "throw new Error('Simulacro: la API externa no responde (HTTP 503)');"}},
    ]
    con = {"Webhook simulacro": {"main": [[{"node": "API externa caída (simulada)", "type": "main", "index": 0}]]}}
    return {"name": "Simulacro de falla (M11)", "nodes": nodes, "connections": con,
            "settings": {"executionOrder": "v1", "saveDataErrorExecution": "all", "saveDataSuccessExecution": "all",
                         "errorWorkflow": err_id}}


# ---------------------------------------------------------------- 3. Manager
CONTROL_IDEMPOTENCIA = r"""// Idempotencia: cada pedido tiene una clave única según su canal. Si la misma clave ya se procesó
// (reintento de Telegram o de Gmail, doble envío al webhook), el pedido se descarta: no se registra
// ni se responde dos veces. Las claves se guardan 7 días en la memoria del workflow publicado.
const j = $json;
const canal = String(j.canal || '');
let idemKey;
if (canal.startsWith('telegram')) idemKey = 'tg-' + $('Mensaje de Telegram').first().json.update_id;
else if (canal === 'email') idemKey = 'gm-' + $('Email entrante (Gmail Trigger)').first().json.id;
else if (canal === 'webhook') idemKey = 'wh-' + (j.request_id || $execution.id);
else idemKey = 'chat-' + $execution.id;
const s = $getWorkflowStaticData('global');
s.procesados = s.procesados || {};
const ahora = Date.now(), TTL = 7 * 24 * 3600 * 1000;
for (const [k, t] of Object.entries(s.procesados)) if (ahora - t > TTL) delete s.procesados[k];
if (s.procesados[idemKey]) return [];
s.procesados[idemKey] = ahora;
return [{ json: { ...j, idemKey } }];"""


def patch_manager(err_id):
    w = C.n8n("GET", f"/workflows/{IDS['manager']}")
    N = {n["name"]: n for n in w["nodes"]}
    con = w["connections"]
    if "Control de idempotencia" not in N:
        w["nodes"].append({"id": str(uuid.uuid4()), "name": "Control de idempotencia", "type": "n8n-nodes-base.code",
                           "typeVersion": 2, "position": [-1040, 470], "parameters": {"jsCode": CONTROL_IDEMPOTENCIA}})
        con["Normalizar entrada"] = {"main": [[{"node": "Control de idempotencia", "type": "main", "index": 0}]]}
        con["Control de idempotencia"] = {"main": [[{"node": "Generar traceId", "type": "main", "index": 0}]]}
        N["Generar traceId"]["position"] = [-900, 470]
    # (si ya existe, su código lo mantiene receptor_m11.py: no se pisa acá)
    for k in ("traceId → Worker 1", "traceId → Worker 2", "traceId → Worker 3", "traceId → Worker 4"):
        asg = N[k]["parameters"]["assignments"]["assignments"]
        if not any(a["name"] == "idemKey" for a in asg):
            asg.append({"id": str(uuid.uuid4()), "name": "idemKey",
                        "value": "={{ $('Control de idempotencia').first().json.idemKey }}", "type": "string"})
    p = N["Crear registro inicial"]["parameters"]
    p["operation"] = "upsert"
    p["columns"]["matchingColumns"] = ["Session_ID"]
    externos = ("googleSheets", "airtable", "hubspot", "httpRequest", "lmChat", "gmail", "slack", "telegram",
                "openAi", "elevenLabs")
    for n in w["nodes"]:
        t = n["type"]
        if ("Trigger" in t or n["name"] in SIN_REINTENTO or not any(x in t for x in externos)
                or n["parameters"].get("operation") == "sendAndWait"):
            continue
        n.update(RETRY)
    r = put(IDS["manager"], w, {"errorWorkflow": err_id, "saveDataErrorExecution": "all",
                                "saveDataSuccessExecution": "all", "saveManualExecutions": True})
    print(f"Manager: {r['name']} — {len(r['nodes'])} nodos")


# ---------------------------------------------------------------- 4/5. sub-workflows
def patch_sub(clave):
    w = C.n8n("GET", f"/workflows/{IDS[clave]}")
    for n in w["nodes"]:
        if any(x in n["type"] for x in ("googleSheets", "httpRequest", "lmChat")):
            n.update(RETRY)
        if clave == "worker1" and "googleSheets" in n["type"]:
            p = n["parameters"]
            p["operation"] = "appendOrUpdate"
            p["columns"]["matchingColumns"] = ["ID"]
            p["columns"]["value"]["ID"] = "={{ 'T-' + ($json.idemKey || $now.toMillis()) }}"
    r = put(IDS[clave], w, {"saveDataErrorExecution": "all", "saveDataSuccessExecution": "all"})
    republicar(IDS[clave])
    print(f"{clave}: {r['name']} — publicado")


def exportar():
    archivos = {"manager": "AI Automation Avanzado - M11.json", "supervisor": "SUPERVISOR_Judge (M11).json",
                "tool_rag": "Tool_ConsultarConocimiento (M11).json", "worker1": "Worker1_RegistrarTurno (M11).json",
                "worker2": "Worker2_Confirmacion (M11).json", "worker3": "Worker3_ConsultarTurno (M11).json",
                "worker4": "Worker4_ModificarTurno (M11).json"}
    todos = [(IDS[k], v) for k, v in archivos.items()] + [(IDS["errores"], "Errores (M11).json"),
                                                         (IDS["simulacro"], "Simulacro de falla (M11).json")]
    for wid, archivo in todos:
        w = C.n8n("GET", f"/workflows/{wid}")
        w = {k: w[k] for k in ("name", "nodes", "connections", "settings") if k in w}
        json.dump(w, open(os.path.join(MOD11, archivo), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Exportados", len(todos), "workflows")


def main():
    cred = credencial_api()
    err = crear_o_actualizar("errores", workflow_errores(cred))
    republicar(err["id"])  # n8n 2.x solo ejecuta un Error Workflow publicado
    print(f"Errores: {err['name']} ({err['id']}) — publicado")
    sim = crear_o_actualizar("simulacro", workflow_simulacro(err["id"]))
    republicar(sim["id"])
    print(f"Simulacro: {sim['name']} ({sim['id']}) — activo en POST /webhook/simulacro-falla-m11")
    patch_manager(err["id"])
    for k in ("tool_rag", "worker1", "worker2", "worker3", "worker4", "supervisor"):
        patch_sub(k)
    exportar()


if __name__ == "__main__":
    main()
