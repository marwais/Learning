# -*- coding: utf-8 -*-
"""Proyecto Final (M11) — Prioridad 2: triaje de señales rojas, escalado humano, freno de mano e idempotencia
con Data Tables. Todo con nodos visuales de n8n (Set, IF, Switch, Data Table, Slack), sin nodos Code: es lo que
el M7 diseñó "con nodos IF y Switch (sin código)" (decisión del usuario del 15/10/2026 tras la devolución de la P7).

Data Tables (n8n): pedidos_procesados_m11 (idempotencia), escalados_m11 (registro de casos rojos y su decisión),
control_m11 (freno_de_mano = si/no). Sus ids están en _aux_m11.json.

Receptor (M11), ahora sin nodos Code:
  Webhook → Entrada webhook (Set) → ¿Petición válida? (IF) → 400 | Generar traceId (Set) → Buscar pedido (Data Table)
  → ¿Pedido nuevo? → Registrar pedido (Data Table) → Responder 202 → Pedido para el Manager (Set) → Manager (sin esperar)
                    └→ Responder 200 duplicado.
Manager M11:
  Generar traceId (Set) → Clave de idempotencia (Set) → Buscar pedido procesado (Data Table) → ¿Pedido nuevo? (IF)
  → Registrar pedido (Data Table, upsert) → Pedido validado (Set) → Triaje de señales rojas (Switch, protocolo triaje-v1)
      ├ urgencia / dinero / reclamo legal / historia clínica → Set con la respuesta fija → Caso rojo
      └ sin señales → Leer freno de mano (Data Table) → ¿Freno de mano activo? → sí: Freno activo (Set) → Caso rojo
                                                                              → no: Pedido en curso (Set) → Buscar memoria…
  Caso rojo → Escalar a una persona (sub-workflow "Escalado humano (M11)", sin esperar)
            → ¿Email? (caso rojo) → Responder caso rojo (email) → Responder al chat (despacho por el canal)
Escalado humano (M11): registra el caso en escalados_m11 → Slack con botones "Tomo el caso" / "Falso positivo"
  (espera máx. 15 min) → registra la decisión → si nadie respondió, recordatorio en Slack.
Freno de mano (M11): POST /webhook/freno-m11 (header X-Freno-Token; el valor está en Modulo5/scripts/.env como
  FRENO_TOKEN_M11) con {"activo": true|false, "quien": "..."} → actualiza control_m11 → avisa en Slack.

Uso:  python seguridad_p2_m11.py      # idempotente
"""
import json, os, sys, uuid, copy, secrets
sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
MOD11 = os.path.abspath(os.path.join(HERE, ".."))
ENV = os.path.join(HERE, "..", "..", "Modulo5", "scripts", ".env")
sys.path.insert(0, os.path.join(HERE, "..", "..", "Modulo5", "scripts"))
import _config as C  # noqa: E402

IDS_PATH, AUX_PATH = os.path.join(MOD11, "_ids_m11.json"), os.path.join(MOD11, "_aux_m11.json")
IDS, AUX = json.load(open(IDS_PATH)), json.load(open(AUX_PATH))
SETTINGS_OK = {"executionOrder", "saveDataSuccessExecution", "saveDataErrorExecution", "saveManualExecutions",
               "saveExecutionProgress", "executionTimeout", "errorWorkflow", "timezone", "callerPolicy"}
SLACK_CRED = {"slackOAuth2Api": {"id": "M9PprPoqQvpvY6pT", "name": "Slack account"}}
GMAIL_CRED = {"gmailOAuth2": {"id": "LCpAQRDOeUUC99pU", "name": "Gmail account"}}
SOPORTE = {"__rl": True, "value": "C0C4YCJ2M60", "mode": "list", "cachedResultName": "soporte"}
RETRY = {"retryOnFail": True, "maxTries": 3, "waitBetweenTries": 2000}
BASE_SETTINGS = {"executionOrder": "v1", "saveDataErrorExecution": "all", "saveDataSuccessExecution": "all"}
PROTOCOLO = "triaje-v1 (15/10/2026)"

# ------------------------------------------------------------------ protocolo de triaje (versionado)
NORMALIZADO = "={{ String($json.mensaje || '').toLowerCase().normalize('NFD').replace(/[\\u0300-\\u036f]/g, '') }}"
SENALES = [  # (salida, nombre del Set, regex sobre el texto en minúsculas y sin acentos, respuesta fija)
    ("urgencia médica", "Rojo: urgencia médica",
     r"(dolor (muy )?(fuerte )?(en el|de|del) pecho|me duele (mucho )?el pecho|no puedo respirar|me falta el aire|"
     r"falta de aire|me ahogo|desmay|convulsi|sangr(ado|o) (mucho|abundante)|hemorragia|infarto|\bacv\b|"
     r"perdi el conocimiento|perdida de conocimiento|intoxica|sobredosis|quiero morir|suicid|me quiero matar|"
     r"paralisis|no siento (el brazo|la pierna|la cara)|cara torcida)",
     "Si es una urgencia, no esperes una respuesta por este medio: llamá ya al 107 (SAME) o acercate a la guardia "
     "24 h de la clínica. Ya avisé al equipo para que te contacte."),
    ("dinero", "Rojo: dinero",
     r"(reintegro|reembols|devolucion (del|de mi) dinero|me devuelvan (la plata|el dinero)|me cobraron|"
     r"cobro indebido|cobraron de mas|doble cobro|me deben plata)",
     "Tu consulta la tiene que ver una persona del equipo de la Central de Turnos: ya le avisé y te va a contactar "
     "a la brevedad."),
    ("reclamo legal", "Rojo: reclamo legal",
     r"(abogad|denuncia|demandar|una demanda|carta documento|defensa del consumidor|mala praxis|negligencia|juicio)",
     "Tu consulta la tiene que ver una persona del equipo de la Central de Turnos: ya le avisé y te va a contactar "
     "a la brevedad."),
    ("historia clínica", "Rojo: historia clínica",
     r"(historia clinica|epicrisis|resumen de (mi )?historia|datos de otr[oa] paciente)",
     "Tu consulta la tiene que ver una persona del equipo de la Central de Turnos: ya le avisé y te va a contactar "
     "a la brevedad."),
]
RESPUESTA_FRENO = ("En este momento te atiende una persona del equipo de la Central de Turnos: ya le pasé tu mensaje "
                   "y te responde a la brevedad.")


# ------------------------------------------------------------------ fábricas de nodos
def nodo(name, typ, ver, pos, params, **extra):
    n = {"id": str(uuid.uuid4()), "name": name, "type": typ, "typeVersion": ver, "position": pos, "parameters": params}
    n.update(extra)
    return n


def set_campos(name, pos, campos, incluir=True):
    asg = [{"id": str(uuid.uuid4()), "name": k, "value": v, "type": "string"} for k, v in campos.items()]
    return nodo(name, "n8n-nodes-base.set", 3.4, pos,
                {"assignments": {"assignments": asg}, "includeOtherFields": incluir, "options": {}})


def set_json(name, pos, expr):
    return nodo(name, "n8n-nodes-base.set", 3.4, pos, {"mode": "raw", "jsonOutput": expr, "options": {}})


def si(name, pos, expr):
    """IF visual: verdadero si la expresión booleana da true."""
    return nodo(name, "n8n-nodes-base.if", 2.2, pos, {
        "conditions": {"options": {"caseSensitive": True, "leftValue": "", "typeValidation": "loose", "version": 2},
                       "conditions": [{"id": str(uuid.uuid4()), "leftValue": expr, "rightValue": "",
                                       "operator": {"type": "boolean", "operation": "true", "singleValue": True}}],
                       "combinator": "and"}, "looseTypeValidation": True, "options": {}})


def dt_ref(clave):
    return {"__rl": True, "mode": "id", "value": AUX["dt_" + clave]}


def dt_cols(vals):
    return {"mappingMode": "defineBelow", "value": vals, "matchingColumns": [],
            "schema": [{"id": k, "displayName": k, "required": False, "defaultMatch": False, "display": True,
                        "type": "string", "canBeUsedToMatch": True} for k in vals]}


def dt(name, pos, op, tabla, filtro=None, cols=None, **extra):
    p = {"resource": "row", "operation": op, "dataTableId": dt_ref(tabla)}
    if filtro:
        p["matchType"] = "allConditions"
        p["filters"] = {"conditions": [{"keyName": k, "condition": "eq", "keyValue": v} for k, v in filtro.items()]}
    if cols:
        p["columns"] = dt_cols(cols)
    return nodo(name, "n8n-nodes-base.dataTable", 1.1, pos, p, **extra)


def slack_post(name, pos, texto):
    return nodo(name, "n8n-nodes-base.slack", 2.3, pos,
                {"authentication": "oAuth2", "resource": "message", "operation": "post", "select": "channel",
                 "channelId": SOPORTE, "text": texto, "otherOptions": {"includeLinkToWorkflow": False}},
                credentials=SLACK_CRED, webhookId=str(uuid.uuid4()), **RETRY)


def responder(name, pos, cuerpo, codigo):
    return nodo(name, "n8n-nodes-base.respondToWebhook", 1.1, pos,
                {"respondWith": "json", "responseBody": cuerpo, "options": {"responseCode": codigo}})


def exec_wf(name, pos, wid, nombre, esperar):
    return nodo(name, "n8n-nodes-base.executeWorkflow", 1.2, pos,
                {"workflowId": {"__rl": True, "value": wid, "mode": "list", "cachedResultName": nombre},
                 "workflowInputs": {"mappingMode": "defineBelow", "value": {}, "matchingColumns": [], "schema": [],
                                    "attemptToConvertTypes": False, "convertFieldsToString": True},
                 "options": {"waitForSubWorkflow": esperar}})


def nota(pos, w, h, texto):
    return nodo("Nota " + str(uuid.uuid4())[:4], "n8n-nodes-base.stickyNote", 1, pos,
                {"width": w, "height": h, "content": texto})


def conectar(con, a, b, out=0):
    m = con.setdefault(a, {"main": []})["main"]
    while len(m) <= out:
        m.append([])
    if not any(x["node"] == b for x in m[out]):
        m[out].append({"node": b, "type": "main", "index": 0})


def republicar(wid):
    try:
        C.n8n("POST", f"/workflows/{wid}/deactivate")
    except Exception:
        pass
    C.n8n("POST", f"/workflows/{wid}/activate")


def guardar(clave, body, en_ids=True):
    store, path = (IDS, IDS_PATH) if en_ids else (AUX, AUX_PATH)
    if store.get(clave):
        r = C.n8n("PUT", f"/workflows/{store[clave]}", body)
    else:
        r = C.n8n("POST", "/workflows", body)
        if en_ids:
            man = IDS.pop("manager"); IDS[clave] = r["id"]; IDS["manager"] = man
        else:
            AUX[clave] = r["id"]
        json.dump(store, open(path, "w"), indent=1)
    return r


TRACE_EXPR = ("={{ $json.traceId || ('trc-' + $now.toUTC().toFormat('yyyyMMddHHmmss') + '-' + $execution.id + '-' "
              "+ Math.random().toString(36).slice(2, 6)) }}")


# ------------------------------------------------------------------ 1. Escalado humano (M11)
def escalado():
    caso = "$('Recibir caso').first().json"
    msg = ("=:rotating_light: *AgendaBot — caso para una persona: {{ " + caso + ".categoria }}*\n"
           "*Mensaje del paciente:* {{ " + caso + ".mensaje }}\n"
           "*Canal:* {{ " + caso + ".canal }} · *Sesión:* {{ " + caso + ".sessionId }}"
           "{{ " + caso + ".email_entrada ? ' · ' + " + caso + ".email_entrada : '' }}\n"
           "*Ya se le respondió:* {{ " + caso + ".respuesta_fija }}\n"
           "*traceId:* {{ " + caso + ".traceId }} · protocolo {{ " + caso + ".protocolo }}\n"
           "Tocá *Tomo el caso* y contactá al paciente, o *Falso positivo* si no hacía falta. Si nadie responde en "
           "15 minutos, se repite el aviso.")
    estado = ("={{ $('Avisar al equipo (Slack)').first().json.data?.approved === true ? 'tomado' : "
              "$('Avisar al equipo (Slack)').first().json.data?.approved === false ? 'falso_positivo' : 'sin_respuesta' }}")
    nodes = [
        nodo("Recibir caso", "n8n-nodes-base.executeWorkflowTrigger", 1.1, [0, 300], {"inputSource": "passthrough"}),
        dt("Registrar escalado", [220, 300], "insert", "escalados_m11",
           cols={"traceId": "={{ $json.traceId }}", "categoria": "={{ $json.categoria }}", "canal": "={{ $json.canal }}",
                 "sesion": "={{ $json.sessionId }}", "mensaje": "={{ $json.mensaje }}", "estado": "pendiente",
                 "decision": "={{ 'escalado ' + $now.setZone('America/Argentina/Buenos_Aires').toFormat('dd/MM HH:mm') }}"}),
        nodo("Avisar al equipo (Slack)", "n8n-nodes-base.slack", 2.3, [440, 300],
             {"authentication": "oAuth2", "resource": "message", "operation": "sendAndWait", "select": "channel",
              "channelId": SOPORTE, "message": msg, "responseType": "approval",
              "approvalOptions": {"values": {"approvalType": "double", "approveLabel": "Tomo el caso",
                                             "disapproveLabel": "Falso positivo"}},
              "options": {"limitWaitTime": {"values": {"limitType": "afterTimeInterval", "resumeAmount": 15,
                                                       "resumeUnit": "minutes"}}}},
             credentials=SLACK_CRED, webhookId=str(uuid.uuid4())),
        dt("Registrar decisión", [660, 300], "update", "escalados_m11",
           filtro={"traceId": "={{ $('Recibir caso').first().json.traceId }}"},
           cols={"estado": estado,
                 "decision": "={{ 'decidido ' + $now.setZone('America/Argentina/Buenos_Aires').toFormat('dd/MM HH:mm') }}"}),
        si("¿Nadie lo tomó?", [880, 300], "={{ $json.estado === 'sin_respuesta' }}"),
        slack_post("Recordatorio (Slack)", [1100, 220],
                   "=:warning: <!here> *Caso sin tomar hace 15 minutos* ({{ " + caso + ".categoria }}) — traceId "
                   "{{ " + caso + ".traceId }}. Mensaje: {{ " + caso + ".mensaje }}"),
        nota([-40, -20], 1240, 260,
             "## Escalado humano (M11): casos rojos y freno de mano\nLo llama el Manager **sin esperar**: el paciente ya "
             "recibió su respuesta fija. Registra el caso en la Data Table `escalados_m11` (traceId, categoría, canal, "
             "sesión, mensaje, estado), avisa en #soporte con los botones **Tomo el caso / Falso positivo** (espera máx. "
             "15 min), guarda la decisión y, si nadie respondió, repite el aviso. Es el protocolo de escalado forzado "
             "del M7 (semáforo rojo), armado sin código."),
    ]
    con = {}
    for a, b, o in [("Recibir caso", "Registrar escalado", 0), ("Registrar escalado", "Avisar al equipo (Slack)", 0),
                    ("Avisar al equipo (Slack)", "Registrar decisión", 0), ("Registrar decisión", "¿Nadie lo tomó?", 0),
                    ("¿Nadie lo tomó?", "Recordatorio (Slack)", 0)]:
        conectar(con, a, b, o)
    r = guardar("escalado_humano", {"name": "Escalado humano (M11)", "nodes": nodes, "connections": con,
                                    "settings": {**BASE_SETTINGS, "errorWorkflow": IDS["errores"]}})
    republicar(r["id"])
    print(f"Escalado humano: {r['id']} — publicado")
    return r["id"]


# ------------------------------------------------------------------ 2. Freno de mano (M11)
def credencial_freno():
    if AUX.get("cred_freno"):
        return AUX["cred_freno"]
    token = secrets.token_urlsafe(24)
    r = C.n8n("POST", "/credentials", {"name": "Freno de mano (M11)", "type": "httpHeaderAuth",
                                       "data": {"name": "X-Freno-Token", "value": token}})
    AUX["cred_freno"] = r["id"]
    json.dump(AUX, open(AUX_PATH, "w"), indent=1)
    with open(ENV, "a", encoding="utf-8") as f:  # .env está fuera de git
        f.write(f"\nFRENO_TOKEN_M11={token}\n")
    return r["id"]


def freno(cred):
    nodes = [
        nodo("Webhook freno de mano", "n8n-nodes-base.webhook", 2, [0, 300],
             {"httpMethod": "POST", "path": "freno-m11", "authentication": "headerAuth", "responseMode": "responseNode",
              "options": {}},
             credentials={"httpHeaderAuth": {"id": cred, "name": "Freno de mano (M11)"}}, webhookId=str(uuid.uuid4())),
        set_campos("Nuevo estado", [220, 300],
                   {"valor": "={{ [true, 'true', 'si', 'sí'].includes($json.body.activo) ? 'si' : 'no' }}",
                    "quien": "={{ $json.body.quien || 'sin nombre' }}"}, incluir=False),
        dt("Actualizar freno", [440, 300], "update", "control_m11", filtro={"clave": "freno_de_mano"},
           cols={"valor": "={{ $json.valor }}",
                 "actualizado_por": "={{ $json.quien + ' · ' + $now.setZone('America/Argentina/Buenos_Aires').toFormat('dd/MM/yyyy HH:mm') }}"}),
        slack_post("Avisar cambio (Slack)", [660, 300],
                   "={{ $json.valor === 'si' ? ':octagonal_sign: *Freno de mano ACTIVADO*: todos los pedidos pasan a "
                   "atención humana.' : ':white_check_mark: *Freno de mano desactivado*: AgendaBot vuelve a atender.' }} "
                   "({{ $json.actualizado_por }})"),
        responder("Responder estado", [880, 300],
                  "={{ JSON.stringify({ freno_de_mano: $('Actualizar freno').first().json.valor, "
                  "actualizado_por: $('Actualizar freno').first().json.actualizado_por }) }}", 200),
        nota([-40, -20], 1060, 260,
             "## Freno de mano (M11)\nPausa a AgendaBot: con `freno_de_mano = si` en la Data Table `control_m11`, el "
             "Manager deriva todos los pedidos a una persona (respuesta fija + escalado en Slack). Se activa con "
             "`POST /webhook/freno-m11` y el header `X-Freno-Token` (credencial de n8n; el valor no está en el workflow), "
             "body `{\"activo\": true, \"quien\": \"Coordinadora\"}`, o editando la tabla en n8n."),
    ]
    con = {}
    for a, b in [("Webhook freno de mano", "Nuevo estado"), ("Nuevo estado", "Actualizar freno"),
                 ("Actualizar freno", "Avisar cambio (Slack)"), ("Avisar cambio (Slack)", "Responder estado")]:
        conectar(con, a, b)
    r = guardar("freno_de_mano", {"name": "Freno de mano (M11)", "nodes": nodes, "connections": con,
                                  "settings": {**BASE_SETTINGS, "errorWorkflow": IDS["errores"]}})
    republicar(r["id"])
    print(f"Freno de mano: {r['id']} — publicado en POST /webhook/freno-m11")


# ------------------------------------------------------------------ 3. Receptor sin nodos Code
def receptor():
    w = C.n8n("GET", f"/workflows/{IDS['receptor']}")
    N = {n["name"]: n for n in w["nodes"]}
    if N["Entrada webhook"]["type"].endswith(".set"):
        print("Receptor: ya estaba sin nodos Code")
        return
    webhook = N["Webhook (petición asincrónica)"]
    gt = "$('Generar traceId').first().json"
    nodes = [
        webhook,
        set_campos("Entrada webhook", [220, 300], {
            "canal": "webhook",
            "request_id": "={{ String($json.body.request_id || $json.headers['idempotency-key'] || '').trim() }}",
            "mensaje": "={{ String($json.body.mensaje || '').trim() }}",
            "email": "={{ String($json.body.email || '').trim() }}",
            "tg_chat_id": "={{ String($json.body.tg_chat_id || '').trim() }}",
            "nombre": "={{ String($json.body.nombre || '').trim() }}",
            "sessionId": "={{ $json.body.email || ($json.body.tg_chat_id ? 'tg-' + $json.body.tg_chat_id : 'wh-' + $json.body.request_id) }}",
        }, incluir=False),
        si("¿Petición válida?", [440, 300], "={{ !!$json.request_id && !!$json.mensaje && (!!$json.email || !!$json.tg_chat_id) }}"),
        responder("Rechazar petición (400)", [660, 480],
                  "={{ JSON.stringify({ estado: 'rechazado', faltan: [!$json.request_id && 'request_id', "
                  "!$json.mensaje && 'mensaje', (!$json.email && !$json.tg_chat_id) && 'email o tg_chat_id (canal de respuesta)']"
                  ".filter(Boolean) }) }}", 400),
        set_campos("Generar traceId", [660, 280], {"traceId": TRACE_EXPR,
                                                   "trace_inicio": "={{ $now.toUTC().toISO() }}",
                                                   "idemKey": "={{ 'wh-' + $json.request_id }}"}),
        dt("Buscar pedido", [880, 280], "get", "pedidos_procesados_m11", filtro={"clave": "={{ $json.idemKey }}"},
           alwaysOutputData=True),
        si("¿Pedido nuevo?", [1100, 280], "={{ !$json.clave }}"),
        dt("Registrar pedido", [1320, 200], "insert", "pedidos_procesados_m11",
           cols={"clave": "={{ " + gt + ".idemKey }}", "traceId": "={{ " + gt + ".traceId }}", "canal": "webhook"}),
        responder("Responder 202 (recibido)", [1540, 200],
                  "={{ JSON.stringify({ estado: 'recibido', traceId: " + gt + ".traceId, request_id: " + gt + ".request_id, "
                  "detalle: 'Pedido recibido. La respuesta llega por ' + (" + gt + ".tg_chat_id ? 'Telegram' : 'email') + '.' }) }}",
                  202),
        set_json("Pedido para el Manager", [1760, 200], "={{ JSON.stringify(" + gt + ") }}"),
        exec_wf("Procesar en segundo plano (Manager)", [1980, 200], IDS["manager"], "AI Automation Avanzado - M11", False),
        responder("Responder 200 (duplicado)", [1320, 400],
                  "={{ JSON.stringify({ estado: 'duplicado', traceId: $json.traceId, request_id: " + gt + ".request_id, "
                  "detalle: 'Este pedido ya se había recibido: no se procesa de nuevo.' }) }}", 200),
        nota([-40, -20], 2200, 240,
             "## Receptor (M11): petición asincrónica e idempotente\nUn sistema externo (web de turnos, app, CRM) manda "
             "`POST /webhook/agendabot-m11` con `request_id`, `mensaje`, `nombre` y `email` y/o `tg_chat_id`. El Receptor "
             "**responde al instante** (202 con el traceId; 400 si falta un dato; 200 \"duplicado\" si el request_id ya "
             "está en la Data Table `pedidos_procesados_m11`) y le pasa el pedido al **Manager** sin esperarlo: el "
             "análisis, el Juez y el registro ocurren en segundo plano. Todo con nodos visuales, sin código."),
    ]
    webhook["position"] = [0, 300]
    con = {}
    for a, b, o in [("Webhook (petición asincrónica)", "Entrada webhook", 0), ("Entrada webhook", "¿Petición válida?", 0),
                    ("¿Petición válida?", "Generar traceId", 0), ("¿Petición válida?", "Rechazar petición (400)", 1),
                    ("Generar traceId", "Buscar pedido", 0), ("Buscar pedido", "¿Pedido nuevo?", 0),
                    ("¿Pedido nuevo?", "Registrar pedido", 0), ("¿Pedido nuevo?", "Responder 200 (duplicado)", 1),
                    ("Registrar pedido", "Responder 202 (recibido)", 0),
                    ("Responder 202 (recibido)", "Pedido para el Manager", 0),
                    ("Pedido para el Manager", "Procesar en segundo plano (Manager)", 0)]:
        conectar(con, a, b, o)
    C.n8n("PUT", f"/workflows/{IDS['receptor']}", {"name": w["name"], "nodes": nodes, "connections": con,
                                                   "settings": {**BASE_SETTINGS, "errorWorkflow": IDS["errores"]}})
    republicar(IDS["receptor"])
    print("Receptor: sin nodos Code, idempotencia en Data Table; publicado")


# ------------------------------------------------------------------ 4. Manager
def manager(escalado_id):
    w = C.n8n("GET", f"/workflows/{IDS['manager']}")
    N = {n["name"]: n for n in w["nodes"]}
    con = w["connections"]
    if "Triaje de señales rojas" in N:
        print("Manager: el triaje ya estaba instalado")
        return
    for n in w["nodes"]:
        if n["position"][0] >= -500:
            n["position"] = [n["position"][0] + 1500, n["position"][1]]
    # Generar traceId: Code -> Set (mismo nombre: las referencias $('Generar traceId') siguen valiendo)
    gpos = N["Generar traceId"]["position"]
    w["nodes"] = [n for n in w["nodes"] if n["name"] not in ("Generar traceId", "Control de idempotencia")]
    con.pop("Control de idempotencia", None)
    ck = "$('Clave de idempotencia').first().json"
    pv = "$('Pedido validado').first().json"
    nuevos = [
        set_campos("Generar traceId", gpos, {"traceId": TRACE_EXPR,
                                             "trace_inicio": "={{ $json.trace_inicio || $now.toUTC().toISO() }}"}),
        set_campos("Clave de idempotencia", [-660, 470], {"idemKey":
            "={{ $json.canal.startsWith('telegram') ? 'tg-' + $json.update_id : $json.canal === 'email' ? 'gm-' + "
            "$('Email entrante (Gmail Trigger)').first().json.id : $json.canal === 'webhook' ? 'wh-' + $json.request_id "
            ": 'chat-' + $execution.id }}"}),
        dt("Buscar pedido procesado", [-440, 470], "get", "pedidos_procesados_m11",
           filtro={"clave": "={{ $json.idemKey }}"}, alwaysOutputData=True),
        dt("Registrar pedido", [0, 470], "upsert", "pedidos_procesados_m11", filtro={"clave": "={{ " + ck + ".idemKey }}"},
           cols={"clave": "={{ " + ck + ".idemKey }}", "traceId": "={{ " + ck + ".traceId }}",
                 "canal": "={{ " + ck + ".canal }}"}),
        set_json("Pedido validado", [220, 470], "={{ JSON.stringify(" + ck + ") }}"),
    ]
    # Switch del triaje (sin código): una salida por señal roja + "sin señales"
    base_sw = copy.deepcopy(N["Crear o modificar"])
    reglas = []
    for salida, _, regex, _ in SENALES:
        reglas.append({"conditions": {"options": {"caseSensitive": True, "leftValue": "", "typeValidation": "loose",
                                                  "version": 2},
                                      "conditions": [{"id": str(uuid.uuid4()), "leftValue": NORMALIZADO,
                                                      "rightValue": regex,
                                                      "operator": {"type": "string", "operation": "regex"}}],
                                      "combinator": "and"},
                       "renameOutput": True, "outputKey": salida})
    base_sw.update({"id": str(uuid.uuid4()), "name": "Triaje de señales rojas", "position": [440, 470]})
    base_sw["parameters"] = {"rules": {"values": reglas},
                             "options": {"fallbackOutput": "extra", "renameFallbackOutput": "sin señales rojas"}}
    nuevos.append(base_sw)
    for i, (salida, nombre, _, respuesta) in enumerate(SENALES):
        nuevos.append(set_json(nombre, [700, 620 + 150 * i],
                               "={{ JSON.stringify({ ..." + pv + ", categoria: '" + salida + "', protocolo: '" + PROTOCOLO
                               + "', respuesta_fija: " + json.dumps(respuesta, ensure_ascii=False) + " }) }}"))
    nuevos += [
        dt("Leer freno de mano", [700, 300], "get", "control_m11", filtro={"clave": "freno_de_mano"},
           alwaysOutputData=True),
        si("¿Freno de mano activo?", [920, 300], "={{ $json.valor === 'si' }}"),
        set_json("Freno activo", [1140, 480],
                 "={{ JSON.stringify({ ..." + pv + ", categoria: 'freno de mano (atención humana)', protocolo: '"
                 + PROTOCOLO + "', respuesta_fija: " + json.dumps(RESPUESTA_FRENO, ensure_ascii=False) + " }) }}"),
        set_json("Pedido en curso", [1140, 300], "={{ JSON.stringify(" + pv + ") }}"),
        nodo("Caso rojo", "n8n-nodes-base.noOp", 1, [1360, 760], {}),
        exec_wf("Escalar a una persona (sub-workflow)", [1580, 680], escalado_id, "Escalado humano (M11)", False),
        si("¿Email? (caso rojo)", [1580, 860], "={{ $('Caso rojo').first().json.canal === 'email' }}"),
        nodo("Responder caso rojo (email)", "n8n-nodes-base.gmail", 2.1, [1800, 860],
             {"operation": "reply", "messageId": "={{ $('Email entrante (Gmail Trigger)').first().json.id }}",
              "emailType": "text",
              "message": "=Hola,\n\n{{ $('Caso rojo').first().json.respuesta_fija }}\n\n(Mensaje automático del "
                         "asistente de agenda de la Clínica LoDeTincho.)", "options": {}},
             credentials=GMAIL_CRED, webhookId=str(uuid.uuid4()), **RETRY),
        nota([360, 1240], 1700, 300,
             "## Triaje de señales rojas (protocolo " + PROTOCOLO + ")\nAntes del Router y sin código: el **Switch** "
             "busca en el mensaje (en minúsculas y sin acentos) las señales del semáforo rojo del M7: **urgencia médica**, "
             "**dinero** (reintegros, cobros), **reclamo legal** e **historia clínica**. Un caso rojo no lo resuelve la IA: "
             "el paciente recibe una respuesta fija (en una urgencia, el 107 y la guardia 24 h) y el caso pasa a una "
             "persona por **Escalado humano (M11)**. Si no hay señales, se consulta el **freno de mano** (Data Table "
             "`control_m11`): activo = todo a atención humana. Las listas de palabras son el protocolo versionado que "
             "aprueba la dirección médica y administrativa."),
    ]
    w["nodes"] += nuevos
    N = {n["name"]: n for n in w["nodes"]}
    pn = N["¿Pedido nuevo?"]
    pn["position"] = [-220, 470]
    N["Pedido repetido (descartado)"]["position"] = [-220, 680]
    pn["parameters"]["conditions"]["conditions"] = [{
        "id": str(uuid.uuid4()), "leftValue": "={{ " + ck + ".canal === 'webhook' || !$json.clave }}", "rightValue": "",
        "operator": {"type": "boolean", "operation": "true", "singleValue": True}}]
    for k in ("traceId → Worker 1", "traceId → Worker 2", "traceId → Worker 3", "traceId → Worker 4"):
        for a in N[k]["parameters"]["assignments"]["assignments"]:
            a["value"] = a["value"].replace("$('Control de idempotencia')", "$('Clave de idempotencia')")
    rc = N["Responder al chat"]["parameters"]
    if "Caso rojo" not in rc["jsCode"]:
        rc["jsCode"] = rc["jsCode"].replace("let m = grab('Aplicar validación','output')",
                                            "let m = grab('Caso rojo','respuesta_fija')\n     || grab('Aplicar validación','output')")
        assert "Caso rojo" in rc["jsCode"]
    # conexiones
    con["Generar traceId"] = {"main": [[{"node": "Clave de idempotencia", "type": "main", "index": 0}]]}
    con["Clave de idempotencia"] = {"main": [[{"node": "Buscar pedido procesado", "type": "main", "index": 0}]]}
    con["Buscar pedido procesado"] = {"main": [[{"node": "¿Pedido nuevo?", "type": "main", "index": 0}]]}
    con["¿Pedido nuevo?"] = {"main": [[{"node": "Registrar pedido", "type": "main", "index": 0}],
                                      [{"node": "Pedido repetido (descartado)", "type": "main", "index": 0}]]}
    conectar(con, "Registrar pedido", "Pedido validado")
    conectar(con, "Pedido validado", "Triaje de señales rojas")
    for i, (_, nombre, _, _) in enumerate(SENALES):
        conectar(con, "Triaje de señales rojas", nombre, i)
        conectar(con, nombre, "Caso rojo")
    conectar(con, "Triaje de señales rojas", "Leer freno de mano", len(SENALES))
    conectar(con, "Leer freno de mano", "¿Freno de mano activo?")
    conectar(con, "¿Freno de mano activo?", "Freno activo", 0)
    conectar(con, "¿Freno de mano activo?", "Pedido en curso", 1)
    conectar(con, "Freno activo", "Caso rojo")
    conectar(con, "Pedido en curso", "Buscar memoria (Airtable)")
    conectar(con, "Caso rojo", "Escalar a una persona (sub-workflow)")
    conectar(con, "Caso rojo", "¿Email? (caso rojo)")
    conectar(con, "¿Email? (caso rojo)", "Responder caso rojo (email)", 0)
    conectar(con, "¿Email? (caso rojo)", "Responder al chat", 1)
    conectar(con, "Responder caso rojo (email)", "Responder al chat")
    settings = {k: v for k, v in (w.get("settings") or {}).items() if k in SETTINGS_OK}
    C.n8n("PUT", f"/workflows/{IDS['manager']}", {"name": w["name"], "nodes": w["nodes"], "connections": con,
                                                  "settings": settings})
    republicar(IDS["manager"])
    print(f"Manager: triaje + freno + idempotencia en Data Table — {len(w['nodes'])} nodos, publicado")


def exportar():
    pares = [(IDS["manager"], "AI Automation Avanzado - M11.json"), (IDS["receptor"], "Receptor (M11).json"),
             (IDS["escalado_humano"], "Escalado humano (M11).json"), (IDS["freno_de_mano"], "Freno de mano (M11).json")]
    for wid, archivo in pares:
        x = C.n8n("GET", f"/workflows/{wid}")
        x = {k: x[k] for k in ("name", "nodes", "connections", "settings") if k in x}
        json.dump(x, open(os.path.join(MOD11, archivo), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Exportado")


def main():
    esc = escalado()
    freno(credencial_freno())
    receptor()
    manager(esc)
    exportar()


if __name__ == "__main__":
    main()
