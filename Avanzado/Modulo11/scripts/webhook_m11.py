# -*- coding: utf-8 -*-
"""Proyecto Final (M11) — Prioridad 1, paso 1: petición asincrónica por webhook.

Manager M11:
  - POST /webhook/agendabot-m11 -> "Entrada webhook" (valida: request_id, mensaje y un canal de respuesta)
    -> si falta algo, responde 400 al instante; si no, entra al flujo común por "Normalizar entrada".
  - Orden nuevo al inicio: Normalizar entrada -> Generar traceId -> Control de idempotencia (marca los
    repetidos y recuerda su traceId) -> ¿Vino por webhook? -> "Responder recibido (202)" con el traceId
    (el que llamó no espera el proceso) -> ¿Pedido nuevo? -> resto del flujo. Un repetido no se procesa.
  - Al final, si el pedido vino por webhook, el resultado validado se despacha por Telegram (si mandó
    tg_chat_id) o queda como borrador de Gmail para revisión humana (HITL, devolución de la P4).
  - Para hacer lugar, los nodos del lienzo con x >= -800 se corren 900 px a la derecha (una sola vez).

Uso:  python webhook_m11.py      # (histórico) ya aplicado; lo reemplaza receptor_m11.py, que mueve el webhook
                                  # a "Receptor (M11)" y conserva el despacho final y los nodos de entrada
"""
import json, os, sys, uuid, copy
sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
MOD11 = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "..", "..", "Modulo5", "scripts"))
import _config as C  # noqa: E402

IDS = json.load(open(os.path.join(MOD11, "_ids_m11.json")))
TG_CRED = {"telegramApi": {"id": "x7iGZ1Z1LuKEKu80", "name": "Telegram account"}}
GMAIL_CRED = {"gmailOAuth2": {"id": "LCpAQRDOeUUC99pU", "name": "Gmail account"}}
RETRY = {"retryOnFail": True, "maxTries": 3, "waitBetweenTries": 2000}
SETTINGS_OK = {"executionOrder", "saveDataSuccessExecution", "saveDataErrorExecution", "saveManualExecutions",
               "saveExecutionProgress", "executionTimeout", "errorWorkflow", "timezone", "callerPolicy"}

ENTRADA_WEBHOOK = r"""// Petición asincrónica: un sistema externo (web de turnos, app, CRM) manda el pedido del paciente por POST.
// Campos: request_id (clave de idempotencia del que llama; también vale el header Idempotency-Key),
// mensaje (obligatorio), nombre, email y/o tg_chat_id (por dónde se le manda el resultado).
const b = $json.body || {};
const h = $json.headers || {};
const mensaje = String(b.mensaje || '').trim();
const email = String(b.email || '').trim();
const tg_chat_id = String(b.tg_chat_id || '').trim();
const request_id = String(b.request_id || h['idempotency-key'] || '').trim();
const faltan = [];
if (!request_id) faltan.push('request_id');
if (!mensaje) faltan.push('mensaje');
if (!email && !tg_chat_id) faltan.push('email o tg_chat_id (canal de respuesta)');
return [{ json: {
  valido: faltan.length === 0, faltan,
  canal: 'webhook', request_id, mensaje, email, tg_chat_id, nombre: String(b.nombre || '').trim(),
  sessionId: email || (tg_chat_id ? 'tg-' + tg_chat_id : 'wh-' + request_id)
} }];"""

BLOQUE_WEBHOOK = """// Webhook (petición asincrónica): llega ya validado por "Entrada webhook"
if (j.canal === 'webhook') {
  return [{ json: { sessionId: j.sessionId, mensaje: j.mensaje, email_entrada: j.email || '', nombre_remitente: j.nombre || '', canal: 'webhook', tg_chat_id: j.tg_chat_id || '', request_id: j.request_id } }];
}
"""

CONTROL_IDEMPOTENCIA = r"""// Idempotencia: cada pedido tiene una clave única según su canal (tg-<update_id>, gm-<id del mail>,
// wh-<request_id>, chat-<ejecución>). Si la clave ya se procesó en los últimos 7 días, el pedido se marca
// como repetido: no se registra ni se responde dos veces (al webhook se le devuelve el traceId original).
// Las claves se guardan en la memoria del workflow publicado.
const j = $json;
const canal = String(j.canal || '');
let idemKey;
if (canal.startsWith('telegram')) idemKey = 'tg-' + $('Mensaje de Telegram').first().json.update_id;
else if (canal === 'email') idemKey = 'gm-' + $('Email entrante (Gmail Trigger)').first().json.id;
else if (canal === 'webhook') idemKey = 'wh-' + j.request_id;
else idemKey = 'chat-' + $execution.id;
const s = $getWorkflowStaticData('global');
s.procesados = s.procesados || {};
const ahora = Date.now(), TTL = 7 * 24 * 3600 * 1000;
for (const [k, v] of Object.entries(s.procesados)) if (ahora - (v.t || v) > TTL) delete s.procesados[k];
const previo = s.procesados[idemKey];
if (previo) return [{ json: { ...j, idemKey, duplicado: true, traceId_original: previo.traceId || '' } }];
s.procesados[idemKey] = { t: ahora, traceId: j.traceId };
return [{ json: { ...j, idemKey, duplicado: false } }];"""

RESPUESTA_202 = ("={{ JSON.stringify({ estado: $json.duplicado ? 'duplicado' : 'recibido', "
                 "traceId: $json.duplicado ? $json.traceId_original : $json.traceId, request_id: $json.request_id, "
                 "detalle: $json.duplicado ? 'Este pedido ya se había recibido: no se procesa de nuevo.' "
                 ": 'Pedido recibido. La respuesta llega por ' + ($json.tg_chat_id ? 'Telegram' : 'email') + '.' }) }}")


def nodo(name, typ, ver, pos, params, **extra):
    n = {"id": str(uuid.uuid4()), "name": name, "type": typ, "typeVersion": ver, "position": pos,
         "parameters": params}
    n.update(extra)
    return n


def cond_if(base, name, pos, left, op, right=""):
    n = copy.deepcopy(base)
    n.update({"id": str(uuid.uuid4()), "name": name, "position": pos})
    c = n["parameters"]["conditions"]["conditions"][0]
    c.update({"id": str(uuid.uuid4()), "leftValue": left, "rightValue": right, "operator": op})
    n["parameters"]["conditions"]["conditions"] = [c]
    return n


def link(con, a, b, out=0):
    m = con.setdefault(a, {"main": []})["main"]
    while len(m) <= out:
        m.append([])
    if not any(x["node"] == b for x in m[out]):
        m[out].append({"node": b, "type": "main", "index": 0})


def main():
    w = C.n8n("GET", f"/workflows/{IDS['manager']}")
    N = {n["name"]: n for n in w["nodes"]}
    con = w["connections"]
    if "Llamada de un canal (Receptor / Telegram)" in N:
        raise SystemExit("Superado por receptor_m11.py: el webhook vive en 'Receptor (M11)'. No se toca el Manager.")
    if "Webhook (petición asincrónica)" in N:
        N["Control de idempotencia"]["parameters"]["jsCode"] = CONTROL_IDEMPOTENCIA
        N["Entrada webhook"]["parameters"]["jsCode"] = ENTRADA_WEBHOOK
        print("Webhook ya instalado: actualizo el código de los nodos")
    else:
        for n in w["nodes"]:  # hacer lugar
            if n["position"][0] >= -800:
                n["position"] = [n["position"][0] + 900, n["position"][1]]
        si_tg = N["¿Vino por Telegram?"]
        eq = {"type": "string", "operation": "equals"}
        nuevos = [
            nodo("Webhook (petición asincrónica)", "n8n-nodes-base.webhook", 2, [-1760, -150],
                 {"httpMethod": "POST", "path": "agendabot-m11", "responseMode": "responseNode", "options": {}},
                 webhookId=str(uuid.uuid4())),
            nodo("Entrada webhook", "n8n-nodes-base.code", 2, [-1540, -150], {"jsCode": ENTRADA_WEBHOOK}),
            cond_if(si_tg, "¿Petición válida?", [-1320, -150], "={{ $json.valido }}",
                    {"type": "boolean", "operation": "true", "singleValue": True}),
            nodo("Rechazar petición (400)", "n8n-nodes-base.respondToWebhook", 1.1, [-1100, -300],
                 {"respondWith": "json",
                  "responseBody": "={{ JSON.stringify({ estado: 'rechazado', faltan: $json.faltan }) }}",
                  "options": {"responseCode": 400}}),
            nodo("Control de idempotencia", "n8n-nodes-base.code", 2, [-660, 470],
                 {"jsCode": CONTROL_IDEMPOTENCIA}),
            cond_if(si_tg, "¿Vino por webhook?", [-440, 470], "={{ $json.canal }}", eq, "webhook"),
            nodo("Responder recibido (202)", "n8n-nodes-base.respondToWebhook", 1.1, [-220, 330],
                 {"respondWith": "json", "responseBody": RESPUESTA_202,
                  "options": {"responseCode": "={{ $json.duplicado ? 200 : 202 }}"}}),
            cond_if(si_tg, "¿Pedido nuevo?", [0, 470], "={{ $json.duplicado }}",
                    {"type": "boolean", "operation": "false", "singleValue": True}),
            nodo("Pedido repetido (descartado)", "n8n-nodes-base.noOp", 1, [0, 680], {}),
        ]
        # el nodo de idempotencia de robustez_m11.py se reemplaza por el nuevo (mismo nombre, nueva posición)
        w["nodes"] = [n for n in w["nodes"] if n["name"] != "Control de idempotencia"] + nuevos
        N = {n["name"]: n for n in w["nodes"]}
        N["Generar traceId"]["position"] = [-880, 470]
        # despacho final para el webhook
        x, y = N["Respuesta (chat / email)"]["position"]
        N["Respuesta (chat / email)"]["position"] = [x + 440, y + 170]
        canal = "={{ $('Normalizar entrada').first().json.canal }}"
        w["nodes"] += [
            cond_if(si_tg, "¿Respuesta por webhook?", [x, y], canal, eq, "webhook"),
            cond_if(si_tg, "¿Pidió Telegram?", [x + 220, y - 80], "={{ $('Normalizar entrada').first().json.tg_chat_id }}",
                    {"type": "string", "operation": "notEmpty", "singleValue": True}),
            nodo("Enviar resultado (Telegram)", "n8n-nodes-base.telegram", 1.2, [x + 440, y - 170],
                 {"chatId": "={{ $('Normalizar entrada').first().json.tg_chat_id }}",
                  "text": "={{ $('Responder al chat').first().json.output }}",
                  "additionalFields": {"appendAttribution": False}},
                 credentials=TG_CRED, webhookId=str(uuid.uuid4()), **RETRY),
            nodo("Borrador del resultado (Gmail)", "n8n-nodes-base.gmail", 2.1, [x + 440, y - 20],
                 {"resource": "draft",
                  "subject": "=AgendaBot — respuesta a tu pedido ({{ $('Generar traceId').first().json.traceId }})",
                  "message": "=Hola {{ $('Normalizar entrada').first().json.nombre_remitente || '' }},\n\n"
                             "{{ $('Responder al chat').first().json.output }}\n\n"
                             "— Central de Turnos, Clínica LoDeTincho\n"
                             "(Borrador generado por AgendaBot para revisión humana antes de enviar.)",
                  "options": {"sendTo": "={{ $('Normalizar entrada').first().json.email_entrada }}"}},
                 credentials=GMAIL_CRED, webhookId=str(uuid.uuid4()), **RETRY),
        ]
        # conexiones
        con["Webhook (petición asincrónica)"] = {"main": [[{"node": "Entrada webhook", "type": "main", "index": 0}]]}
        con["Entrada webhook"] = {"main": [[{"node": "¿Petición válida?", "type": "main", "index": 0}]]}
        con["¿Petición válida?"] = {"main": [[{"node": "Normalizar entrada", "type": "main", "index": 0}],
                                             [{"node": "Rechazar petición (400)", "type": "main", "index": 0}]]}
        con["Normalizar entrada"] = {"main": [[{"node": "Generar traceId", "type": "main", "index": 0}]]}
        con["Generar traceId"] = {"main": [[{"node": "Control de idempotencia", "type": "main", "index": 0}]]}
        con["Control de idempotencia"] = {"main": [[{"node": "¿Vino por webhook?", "type": "main", "index": 0}]]}
        con["¿Vino por webhook?"] = {"main": [[{"node": "Responder recibido (202)", "type": "main", "index": 0}],
                                              [{"node": "¿Pedido nuevo?", "type": "main", "index": 0}]]}
        con["Responder recibido (202)"] = {"main": [[{"node": "¿Pedido nuevo?", "type": "main", "index": 0}]]}
        con["¿Pedido nuevo?"] = {"main": [[{"node": "Buscar memoria (Airtable)", "type": "main", "index": 0}],
                                          [{"node": "Pedido repetido (descartado)", "type": "main", "index": 0}]]}
        con["¿Vino por Telegram?"]["main"][1] = [{"node": "¿Respuesta por webhook?", "type": "main", "index": 0}]
        con["¿Respuesta por webhook?"] = {"main": [[{"node": "¿Pidió Telegram?", "type": "main", "index": 0}],
                                                   [{"node": "Respuesta (chat / email)", "type": "main", "index": 0}]]}
        con["¿Pidió Telegram?"] = {"main": [[{"node": "Enviar resultado (Telegram)", "type": "main", "index": 0}],
                                            [{"node": "Borrador del resultado (Gmail)", "type": "main", "index": 0}]]}
    # Normalizar entrada acepta el canal webhook
    nz = N["Normalizar entrada"]["parameters"]
    if "j.canal === 'webhook'" not in nz["jsCode"]:
        a, b = nz["jsCode"].split("\n", 1)
        nz["jsCode"] = a + "\n" + BLOQUE_WEBHOOK + b
    # chequeo de superposiciones (nodos a menos de 60 px)
    pos = [(n["name"], n["position"]) for n in w["nodes"] if "stickyNote" not in n["type"]]
    for i, (a, pa) in enumerate(pos):
        for b, pb in pos[i + 1:]:
            if abs(pa[0] - pb[0]) < 60 and abs(pa[1] - pb[1]) < 60:
                print(f"  aviso: '{a}' y '{b}' quedan superpuestos ({pa} / {pb})")
    settings = {k: v for k, v in (w.get("settings") or {}).items() if k in SETTINGS_OK}
    r = C.n8n("PUT", f"/workflows/{IDS['manager']}",
              {"name": w["name"], "nodes": w["nodes"], "connections": con, "settings": settings})
    try:
        C.n8n("POST", f"/workflows/{IDS['manager']}/deactivate")
    except Exception:
        pass
    C.n8n("POST", f"/workflows/{IDS['manager']}/activate")
    print(f"Manager: {r['name']} — {len(r['nodes'])} nodos, publicado. POST /webhook/agendabot-m11")
    w = C.n8n("GET", f"/workflows/{IDS['manager']}")
    w = {k: w[k] for k in ("name", "nodes", "connections", "settings") if k in w}
    json.dump(w, open(os.path.join(MOD11, "AI Automation Avanzado - M11.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
