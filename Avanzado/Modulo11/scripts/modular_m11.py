# -*- coding: utf-8 -*-
"""Proyecto Final (M11) — Prioridad 1, paso 5: modularidad (sin flujos monolíticos).

1. "Canal Telegram (M11)": el disparador de Telegram y su procesamiento de entrada (filtro de repetidos, nota de
   voz → Whisper, audio ilegible, email dictado) salen del Manager a un workflow propio que termina en
   "Pasar al Manager" (Execute Workflow sin esperar). Así el Manager ya no depende del túnel para publicarse
   (Telegram exige registrar su webhook en una URL pública viva) y cada canal es un adaptador independiente.
   Las respuestas por Telegram (texto o voz) siguen en el Manager: no usan webhook.
2. "Ingesta KB (M11)": la carga manual de la base de conocimiento (LlamaParse → chunking → Cohere → Qdrant) sale
   del Manager a su propio workflow (disparo manual; queda en _aux_m11.json porque no se activa).
3. Manager: el disparador "Llamada del Receptor" pasa a llamarse "Llamada de un canal (Receptor / Telegram)";
   la clave de idempotencia de Telegram llega como update_id.
4. Errores (M11): si la falla es en el Canal Telegram, toma los datos del paciente de "Entrada Telegram".

Uso:  python modular_m11.py      # idempotente
"""
import json, os, sys, uuid, copy
sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
MOD11 = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "..", "..", "Modulo5", "scripts"))
import _config as C  # noqa: E402

IDS_PATH = os.path.join(MOD11, "_ids_m11.json")
AUX_PATH = os.path.join(MOD11, "_aux_m11.json")
IDS = json.load(open(IDS_PATH))
AUX = json.load(open(AUX_PATH))
SETTINGS_OK = {"executionOrder", "saveDataSuccessExecution", "saveDataErrorExecution", "saveManualExecutions",
               "saveExecutionProgress", "executionTimeout", "errorWorkflow", "timezone", "callerPolicy"}
TRIGGER_VIEJO = "Llamada del Receptor"
TRIGGER = "Llamada de un canal (Receptor / Telegram)"

TG = {"Mensaje de Telegram", "Filtrar repetidos", "¿Nota de voz?", "Descargar nota de voz", "Transcribir (Whisper)",
      "Evaluar transcripción", "¿Audio vacío o ilegible?", "Avisar: no se escuchó", "¿Dictó un email?",
      "Pedir email por escrito", "Entrada Telegram"}
KB = {"▶ Ingerir KB (RAG)", "Borrar colección (Qdrant)", "Crear colección (Qdrant)", "Cargar KB (markdown LlamaParse)",
      "Chunking por secciones", "Vector Store Qdrant (insert)", "Data Loader", "Splitter (red de seguridad)",
      "Embeddings Cohere (insert)"}

CONTROL_MANAGER = r"""// Idempotencia: cada pedido tiene una clave única según su canal (tg-<update_id>, gm-<id del mail>,
// chat-<ejecución>). Si la clave ya se procesó en los últimos 7 días, el pedido se marca como repetido y
// no se registra ni se responde dos veces. Los pedidos del webhook ya los controló el Receptor (M11).
const j = $json;
const canal = String(j.canal || '');
if (canal === 'webhook') return [{ json: { ...j, idemKey: 'wh-' + j.request_id, duplicado: false } }];
let idemKey;
if (canal.startsWith('telegram')) idemKey = 'tg-' + j.update_id;
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


def mover(w, S, notas):
    """Saca de w los nodos de S (y las notas indicadas); devuelve (nodos, conexiones internas, aristas salientes)."""
    nodos = [n for n in w["nodes"] if n["name"] in S or n["name"] in notas]
    con = w["connections"]
    internas, salientes = {}, []
    for a in list(con):
        if a not in S:
            continue
        for typ, outs in con[a].items():
            nuevo = []
            for i, o in enumerate(outs):
                dentro = [x for x in (o or []) if x["node"] in S]
                salientes += [(a, i, x["node"]) for x in (o or []) if x["node"] not in S]
                nuevo.append(dentro)
            internas.setdefault(a, {})[typ] = nuevo
        del con[a]
    for a, v in con.items():  # aristas desde afuera hacia S
        for typ, outs in v.items():
            for i, o in enumerate(outs):
                outs[i] = [x for x in (o or []) if x["node"] not in S]
    w["nodes"] = [n for n in w["nodes"] if n not in nodos]
    return nodos, internas, salientes


def normalizar_posiciones(nodos):
    x0 = min(n["position"][0] for n in nodos)
    y0 = min(n["position"][1] for n in nodos)
    for n in nodos:
        n["position"] = [n["position"][0] - x0, n["position"][1] - y0 + 300]


def republicar(wid):
    try:
        C.n8n("POST", f"/workflows/{wid}/deactivate")
    except Exception:
        pass
    C.n8n("POST", f"/workflows/{wid}/activate")


def put(wid, w):
    settings = {k: v for k, v in (w.get("settings") or {}).items() if k in SETTINGS_OK}
    return C.n8n("PUT", f"/workflows/{wid}", {"name": w["name"], "nodes": w["nodes"],
                                              "connections": w["connections"], "settings": settings})


def main():
    w = C.n8n("GET", f"/workflows/{IDS['manager']}")
    N = {n["name"]: n for n in w["nodes"]}
    base = {"executionOrder": "v1", "saveDataErrorExecution": "all", "saveDataSuccessExecution": "all"}

    # ---- 1. Canal Telegram
    if "Mensaje de Telegram" in N:
        nota_voz = [n["name"] for n in w["nodes"] if "stickyNote" in n["type"]
                    and n["parameters"].get("content", "").startswith("## Capa de voz") and "entrada" in n["parameters"]["content"][:60]]
        nodos, internas, _ = mover(w, TG, set(nota_voz))
        ent = next(n for n in nodos if n["name"] == "Entrada Telegram")
        ent["parameters"]["jsCode"] = ent["parameters"]["jsCode"].replace(
            "  canal: esVoz ? 'telegram_voz' : 'telegram_texto',",
            "  canal: esVoz ? 'telegram_voz' : 'telegram_texto',\n"
            "  update_id: $('Mensaje de Telegram').first().json.update_id,  // clave de idempotencia")
        nodos.append({"id": str(uuid.uuid4()), "name": "Pasar al Manager", "type": "n8n-nodes-base.executeWorkflow",
                      "typeVersion": 1.2, "position": [ent["position"][0] + 240, ent["position"][1]],
                      "parameters": {"workflowId": {"__rl": True, "value": IDS["manager"], "mode": "list",
                                                    "cachedResultName": "AI Automation Avanzado - M11"},
                                     "workflowInputs": {"mappingMode": "defineBelow", "value": {}, "matchingColumns": [],
                                                        "schema": [], "attemptToConvertTypes": False,
                                                        "convertFieldsToString": True},
                                     "options": {"waitForSubWorkflow": False}}})
        internas["Entrada Telegram"] = {"main": [[{"node": "Pasar al Manager", "type": "main", "index": 0}]]}
        for n in nodos:
            if n["name"] == "Mensaje de Telegram":
                n["webhookId"] = str(uuid.uuid4())
        normalizar_posiciones(nodos)
        body = {"name": "Canal Telegram (M11)", "nodes": nodos, "connections": internas,
                "settings": {**base, "errorWorkflow": IDS["errores"]}}
        r = C.n8n("PUT", f"/workflows/{IDS['canal_telegram']}", body) if IDS.get("canal_telegram") \
            else C.n8n("POST", "/workflows", body)
        if not IDS.get("canal_telegram"):
            man = IDS.pop("manager"); IDS["canal_telegram"] = r["id"]; IDS["manager"] = man
            json.dump(IDS, open(IDS_PATH, "w"), indent=1)
        print(f"Canal Telegram: {r['name']} ({r['id']}) — {len(nodos)} nodos")
    else:
        print("Canal Telegram: ya separado")

    # ---- 2. Ingesta KB
    if "▶ Ingerir KB (RAG)" in N:
        nodos, internas, _ = mover(w, KB, set())
        normalizar_posiciones(nodos)
        nodos.append({"id": str(uuid.uuid4()), "name": "Nota", "type": "n8n-nodes-base.stickyNote", "typeVersion": 1,
                      "position": [-40, 0], "parameters": {"width": 1300, "height": 240, "content":
                      "## Ingesta KB (M11): carga de la base de conocimiento\nSe corre a mano cuando cambian los "
                      "documentos oficiales: lee el markdown que generó LlamaParse, lo divide por secciones (con la ruta "
                      "de títulos como metadato para las citas), calcula los embeddings con Cohere y reemplaza la "
                      "colección `kb_lodetincho_m5` en Qdrant. La consulta en producción la hace "
                      "`Tool_ConsultarConocimiento (M11)` (Top-K 5, Min Score 0,60)."}})
        body = {"name": "Ingesta KB (M11)", "nodes": nodos, "connections": internas, "settings": base}
        r = C.n8n("PUT", f"/workflows/{AUX['ingesta_kb']}", body) if AUX.get("ingesta_kb") \
            else C.n8n("POST", "/workflows", body)
        if not AUX.get("ingesta_kb"):
            AUX["ingesta_kb"] = r["id"]
            json.dump(AUX, open(AUX_PATH, "w"), indent=1)
        print(f"Ingesta KB: {r['name']} ({r['id']}) — {len(nodos)} nodos")
    else:
        print("Ingesta KB: ya separada")

    # ---- 3. Manager
    N = {n["name"]: n for n in w["nodes"]}
    con = w["connections"]
    if TRIGGER_VIEJO in N:
        N[TRIGGER_VIEJO]["name"] = TRIGGER
        con[TRIGGER] = con.pop(TRIGGER_VIEJO)
    N = {n["name"]: n for n in w["nodes"]}
    N["Control de idempotencia"]["parameters"]["jsCode"] = CONTROL_MANAGER
    nz = N["Normalizar entrada"]["parameters"]
    nz["jsCode"] = nz["jsCode"].replace("canal: j.canal, tg_chat_id: j.tg_chat_id } }];",
                                        "canal: j.canal, tg_chat_id: j.tg_chat_id, update_id: j.update_id } }];")
    assert "update_id: j.update_id" in nz["jsCode"], "no pude pasar update_id en Normalizar entrada"
    put(IDS["manager"], w)
    republicar(IDS["manager"])
    print(f"Manager: {len(w['nodes'])} nodos, publicado (sin disparador de Telegram)")

    # ---- 4. Errores: datos del paciente si falla el Canal Telegram
    e = C.n8n("GET", f"/workflows/{IDS['errores']}")
    a = next(n for n in e["nodes"] if n["name"] == "Armar alerta")
    viejo = "const norm = salida('Normalizar entrada');"
    if viejo in a["parameters"]["jsCode"]:
        a["parameters"]["jsCode"] = a["parameters"]["jsCode"].replace(viejo,
            "// Manager: 'Normalizar entrada'; Canal Telegram: 'Entrada Telegram'\n"
            "const norm = Object.keys(salida('Normalizar entrada')).length ? salida('Normalizar entrada') : salida('Entrada Telegram');")
        put(IDS["errores"], e)
        republicar(IDS["errores"])
        print("Errores: también reconoce fallas del Canal Telegram")

    # ---- activar el canal (necesita el túnel vivo)
    try:
        republicar(IDS["canal_telegram"])
        print("Canal Telegram: activo")
    except Exception as ex:
        print("AVISO: no se pudo activar el Canal Telegram (¿túnel caído? correr Modulo6/scripts/levantar_tunel.ps1):", ex)

    # ---- exportar
    for wid, archivo in [(IDS["manager"], "workflows/AgendaBot · Manager.json"), (IDS["canal_telegram"], "workflows/AgendaBot · Canal Telegram.json"),
                         (AUX["ingesta_kb"], "workflows/AgendaBot · Ingesta KB.json"), (IDS["errores"], "workflows/AgendaBot · Errores.json")]:
        x = C.n8n("GET", f"/workflows/{wid}")
        x = {k: x[k] for k in ("name", "nodes", "connections", "settings") if k in x}
        json.dump(x, open(os.path.join(MOD11, archivo), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Exportado")


if __name__ == "__main__":
    main()
