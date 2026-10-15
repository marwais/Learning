# -*- coding: utf-8 -*-
"""Proyecto Final (M11) — tareas de mantenimiento que necesitan credenciales que solo existen dentro de n8n
(Cohere, HubSpot, Google Sheets). Crea un workflow TEMPORAL con un webhook, ejecuta la tarea y lo borra.

Tareas:
  reindexar     anonimiza (Modulo11/kb/anonimizacion.json) los fragmentos de Qdrant que mencionan la razón social
                real y los vuelve a indexar con embeddings nuevos de Cohere (mismo id y metadatos).
  hubspot       crea en HubSpot las propiedades de contacto de AgendaBot (origen, código de seguimiento, canal,
                última interacción, turno, resultado del Supervisor, aprobado por, versión).
  encabezado    lee la fila de encabezados de Agenda_Turnos (11).
  celda <A1> <texto>  escribe un encabezado en Agenda_Turnos (11) (ej.: celda I1 Asistencia).

Uso:  python mantenimiento_m11.py reindexar | hubspot | encabezado | celda I1 Asistencia
"""
import json, os, sys, uuid, time, urllib.request, urllib.error
sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
MOD11 = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "..", "..", "Modulo5", "scripts"))
import _config as C  # noqa: E402

AGENDA = "19rWr4cy1pVmiDi5iv3Nkr3gZn4ExF12Ep5OkMrxxaWk"
COHERE = {"cohereApi": {"id": "GIJyTK4Omxo0Qr5x", "name": "Cohere n8n"}}
HUBSPOT = {"hubspotAppToken": {"id": "hPGs8x3WWMPWG5Sk", "name": "HubSpot AgendaBot (App Token)"}}
SHEETS = {"googleSheetsOAuth2Api": {"id": "GZLtSYc1x6IEDIsF", "name": "Google Sheets account"}}
PROPIEDADES = [
    ("agendabot_origen", "Origen (AgendaBot)", "string", "text"),
    ("agendabot_trace_id", "Código de seguimiento (AgendaBot)", "string", "text"),
    ("agendabot_canal", "Canal (AgendaBot)", "string", "text"),
    ("agendabot_ultima_interaccion", "Última interacción (AgendaBot)", "datetime", "date"),
    ("agendabot_turno", "Turno gestionado (AgendaBot)", "string", "text"),
    ("agendabot_veredicto_juez", "Resultado del Supervisor (AgendaBot)", "string", "text"),
    ("agendabot_aprobado_por", "Aprobado por (AgendaBot)", "string", "text"),
    ("agendabot_version", "Versión del sistema (AgendaBot)", "string", "text"),
]


def http(name, pos, metodo, url, cuerpo, cred=None, tipo=None):
    p = {"method": metodo, "url": url, "sendBody": cuerpo is not None, "options": {}}
    if cuerpo is not None:
        p.update({"specifyBody": "json", "jsonBody": cuerpo})
    n = {"id": str(uuid.uuid4()), "name": name, "type": "n8n-nodes-base.httpRequest", "typeVersion": 4.2,
         "position": pos, "parameters": p, "onError": "continueRegularOutput"}
    if cred:
        p.update({"authentication": "predefinedCredentialType", "nodeCredentialType": tipo})
        n["credentials"] = cred
    return n


def correr(nodos, cuerpo):
    path = "mantenimiento-m11-" + uuid.uuid4().hex[:8]
    wh = {"id": str(uuid.uuid4()), "name": "Webhook", "type": "n8n-nodes-base.webhook", "typeVersion": 2,
          "position": [0, 0], "webhookId": str(uuid.uuid4()),
          "parameters": {"httpMethod": "POST", "path": path, "responseMode": "lastNode",
                         "options": {"responseData": "allEntries"}}}
    todos = [wh] + nodos
    con = {}
    for a, b in zip(todos, todos[1:]):
        con[a["name"]] = {"main": [[{"node": b["name"], "type": "main", "index": 0}]]}
    w = C.n8n("POST", "/workflows", {"name": "Mantenimiento (M11, temporal)", "nodes": todos, "connections": con,
                                     "settings": {"executionOrder": "v1"}})
    try:
        C.n8n("POST", f"/workflows/{w['id']}/activate")
        req = urllib.request.Request(C.N8N_BASE + "/webhook/" + path, method="POST",
                                     data=json.dumps(cuerpo, ensure_ascii=False).encode("utf-8"),
                                     headers={"Content-Type": "application/json"})
        try:
            return json.loads(urllib.request.urlopen(req, timeout=300).read().decode("utf-8") or "null")
        except urllib.error.HTTPError as e:
            return {"error_http": e.code, "detalle": e.read().decode()[:800]}
    finally:
        try:
            C.n8n("POST", f"/workflows/{w['id']}/deactivate")
        except Exception:
            pass
        C.n8n("DELETE", f"/workflows/{w['id']}")


def reindexar():
    reemplazos = json.load(open(os.path.join(MOD11, "kb", "anonimizacion.json"), encoding="utf-8"))
    pts = C.qdrant("POST", f"/collections/{C.COLLECTION}/points/scroll",
                   {"limit": 1000, "with_payload": True, "with_vector": False})["result"]["points"]
    puntos = []
    for p in pts:
        s = json.dumps(p["payload"], ensure_ascii=False)
        s2 = s
        for a, b in reemplazos:
            s2 = s2.replace(a, b)
        if s2 != s:
            puntos.append({"id": p["id"], "payload": json.loads(s2)})
    print(f"Fragmentos a reindexar: {len(puntos)}")
    if not puntos:
        return
    nodos = [
        {"id": str(uuid.uuid4()), "name": "Separar", "type": "n8n-nodes-base.code", "typeVersion": 2, "position": [200, 0],
         "parameters": {"jsCode": "return $json.body.puntos.map(p => ({ json: p }));"}},
        http("Embedding (Cohere)", [400, 0], "POST", "https://api.cohere.com/v2/embed",
             "={{ JSON.stringify({ model: 'embed-multilingual-v3.0', input_type: 'search_document', "
             "embedding_types: ['float'], texts: [$json.payload.content] }) }}", COHERE, "cohereApi"),
        http("Guardar en Qdrant", [600, 0], "PUT", f"=http://host.docker.internal:6333/collections/{C.COLLECTION}/points?wait=true",
             "={{ JSON.stringify({ points: [{ id: $('Separar').item.json.id, vector: $json.embeddings.float[0], "
             "payload: $('Separar').item.json.payload }] }) }}"),
    ]
    r = correr(nodos, {"puntos": puntos})
    # verificación directa en Qdrant (la respuesta del webhook no siempre trae todos los ítems)
    vivos = C.qdrant("POST", f"/collections/{C.COLLECTION}/points", {"ids": [p["id"] for p in puntos], "with_payload": True})
    ok = [x for x in vivos["result"] if not any(a in json.dumps(x["payload"], ensure_ascii=False) for a, _ in reemplazos)]
    print(f"Qdrant: {len(ok)}/{len(puntos)} fragmentos anonimizados y reindexados")


def hubspot():
    cuerpo = {"inputs": [{"name": n, "label": l, "type": t, "fieldType": f, "groupName": "contactinformation",
                          "description": "Metadato de trazabilidad de AgendaBot (fuente de verdad para facturar)."}
                         for n, l, t, f in PROPIEDADES]}
    nodos = [http("Crear propiedades (HubSpot)", [200, 0], "POST",
                  "https://api.hubapi.com/crm/v3/properties/contacts/batch/create",
                  "={{ JSON.stringify($json.body) }}", HUBSPOT, "hubspotAppToken")]
    r = correr(nodos, cuerpo)
    print(json.dumps(r, ensure_ascii=False)[:1500])


def encabezado():
    nodos = [http("Leer encabezado", [200, 0], "GET",
                  f"https://sheets.googleapis.com/v4/spreadsheets/{AGENDA}/values/Hoja%201!1:1", None,
                  SHEETS, "googleSheetsOAuth2Api")]
    print(json.dumps(correr(nodos, {}), ensure_ascii=False)[:800])


def celda(a1, texto):
    nodos = [http("Escribir celda", [200, 0], "PUT",
                  f"https://sheets.googleapis.com/v4/spreadsheets/{AGENDA}/values/Hoja%201!{a1}?valueInputOption=RAW",
                  "={{ JSON.stringify({ values: [[$json.body.texto]] }) }}", SHEETS, "googleSheetsOAuth2Api")]
    print(json.dumps(correr(nodos, {"texto": texto}), ensure_ascii=False)[:800])


if __name__ == "__main__":
    t = sys.argv[1] if len(sys.argv) > 1 else ""
    {"reindexar": reindexar, "hubspot": hubspot, "encabezado": encabezado}.get(t, lambda: None)() if t != "celda" \
        else celda(sys.argv[2], sys.argv[3])
    if t not in ("reindexar", "hubspot", "encabezado", "celda"):
        print(__doc__)
