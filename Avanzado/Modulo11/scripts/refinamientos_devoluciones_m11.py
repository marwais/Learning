# -*- coding: utf-8 -*-
"""Proyecto Final (M11) — refinamientos pedidos en las devoluciones de las pre-entregas 5 y 6.

P5 (82 %): «Usá exactamente la frase "No sé" como escape cuando la información no figure en los fragmentos».
  - Agente RAG: la respuesta fija pasa a "No sé: ese dato no figura en la documentación de la clínica." y la regla
    de seguridad dice "No sé" literal. Juez: la rúbrica de respuestas reconoce "No sé" como 5.
P6 (94 %): «documentá y verificá la purga inmediata de ambos binarios» (nota de voz del paciente y audio sintetizado),
  sin depender de que la ejecución no se guarde.
  - La síntesis (ElevenLabs), el envío de la nota de voz y el descarte del audio salen del Manager a
    "Respuesta de voz (M11)", que NUNCA guarda ejecuciones (ni con éxito ni con error) y devuelve solo metadatos.
  - "Canal Telegram (M11)" (descarga + Whisper) tampoco guarda ejecuciones; al Manager le pasa solo texto.
  - Así el Manager puede guardar sus ejecuciones como evidencia sin que quede ningún audio persistido.

Uso:  python refinamientos_devoluciones_m11.py      # idempotente
"""
import json, os, sys, uuid, copy, hashlib, re
sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
MOD11 = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "..", "..", "Modulo5", "scripts"))
import _config as C  # noqa: E402

IDS_PATH = os.path.join(MOD11, "_ids_m11.json")
IDS = json.load(open(IDS_PATH))
SETTINGS_OK = {"executionOrder", "saveDataSuccessExecution", "saveDataErrorExecution", "saveManualExecutions",
               "saveExecutionProgress", "executionTimeout", "errorWorkflow", "timezone", "callerPolicy"}
SIN_GUARDAR = {"saveDataSuccessExecution": "none", "saveDataErrorExecution": "none", "saveManualExecutions": False,
               "saveExecutionProgress": False}
VOZ = ["Sintetizar voz (ElevenLabs)", "Enviar nota de voz (Telegram)", "Descartar audio (compliance)"]

NO_SE = [  # (texto viejo, texto nuevo) en el System Message del Agente RAG
    ('"No cuento con ese dato en la documentación de la clínica."',
     '"No sé: ese dato no figura en la documentación de la clínica."'),
    ('decilo ("No cuento con ese dato")', 'respondé "No sé"'),
]


def put(wid, w, extra=None):
    s = {k: v for k, v in (w.get("settings") or {}).items() if k in SETTINGS_OK}
    s.update(extra or {})
    return C.n8n("PUT", f"/workflows/{wid}", {"name": w["name"], "nodes": w["nodes"],
                                              "connections": w["connections"], "settings": s})


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

    # ---- P5: "No sé" literal
    sm = N["Agente RAG (Consultas)"]["parameters"]["options"]
    for viejo, nuevo in NO_SE:
        sm["systemMessage"] = sm["systemMessage"].replace(viejo, nuevo)
    assert "No sé: ese dato no figura" in sm["systemMessage"]

    # ---- P6: voz en un sub-workflow que no guarda ejecuciones
    if VOZ[0] in N:
        nodos = [copy.deepcopy(N[k]) for k in VOZ]
        x0, y0 = nodos[0]["position"]
        for n in nodos:
            n["position"] = [n["position"][0] - x0 + 240, n["position"][1] - y0 + 300]
            if n["name"] == "Enviar nota de voz (Telegram)":
                n["parameters"]["chatId"] = "={{ $('Recibir respuesta').first().json.tg_chat_id }}"
        nodos.insert(0, {"id": str(uuid.uuid4()), "name": "Recibir respuesta", "type": "n8n-nodes-base.executeWorkflowTrigger",
                         "typeVersion": 1.1, "position": [0, 300], "parameters": {"inputSource": "passthrough"}})
        nodos.append({"id": str(uuid.uuid4()), "name": "Nota", "type": "n8n-nodes-base.stickyNote", "typeVersion": 1,
                      "position": [-40, 0], "parameters": {"width": 920, "height": 240, "content":
                      "## Respuesta de voz (M11): privacidad de los audios\nSintetiza la respuesta (máx. 200 caracteres) con "
                      "ElevenLabs, la manda como nota de voz y **descarta el binario**: devuelve solo metadatos. Este workflow "
                      "**no guarda ninguna ejecución** (ni con éxito ni con error), así que el audio solo existe en memoria "
                      "durante el envío. Lo mismo hace el Canal Telegram con la nota de voz del paciente (devolución de la P6)."}})
        cw = {"Recibir respuesta": {"main": [[{"node": VOZ[0], "type": "main", "index": 0}]]},
              VOZ[0]: {"main": [[{"node": VOZ[1], "type": "main", "index": 0}]]},
              VOZ[1]: {"main": [[{"node": VOZ[2], "type": "main", "index": 0}]]}}
        body = {"name": "Respuesta de voz (M11)", "nodes": nodos, "connections": cw,
                "settings": {"executionOrder": "v1", **SIN_GUARDAR, "errorWorkflow": IDS["errores"]}}
        r = C.n8n("PUT", f"/workflows/{IDS['respuesta_voz']}", body) if IDS.get("respuesta_voz") \
            else C.n8n("POST", "/workflows", body)
        if not IDS.get("respuesta_voz"):
            man = IDS.pop("manager"); IDS["respuesta_voz"] = r["id"]; IDS["manager"] = man
            json.dump(IDS, open(IDS_PATH, "w"), indent=1)
        republicar(r["id"])
        print(f"Respuesta de voz: {r['name']} ({r['id']}) — publicado, sin guardar ejecuciones")
        llamada = {"id": str(uuid.uuid4()), "name": "Responder con voz (sub-workflow)", "type": "n8n-nodes-base.executeWorkflow",
                   "typeVersion": 1.2, "position": N[VOZ[0]]["position"],
                   "parameters": {"workflowId": {"__rl": True, "value": r["id"], "mode": "list",
                                                 "cachedResultName": "Respuesta de voz (M11)"},
                                  "workflowInputs": {"mappingMode": "defineBelow", "value": {}, "matchingColumns": [],
                                                     "schema": [], "attemptToConvertTypes": False,
                                                     "convertFieldsToString": True},
                                  "options": {"waitForSubWorkflow": True}}}
        w["nodes"] = [n for n in w["nodes"] if n["name"] not in VOZ] + [llamada]
        for k in VOZ:
            con.pop(k, None)
        con["¿Responder con voz?"]["main"][0] = [{"node": llamada["name"], "type": "main", "index": 0}]
    put(IDS["manager"], w)
    republicar(IDS["manager"])
    print("Manager: «No sé» literal; la voz sale por 'Responder con voz (sub-workflow)'; publicado")

    # ---- Canal Telegram: no guarda ejecuciones (nota de voz del paciente)
    t = C.n8n("GET", f"/workflows/{IDS['canal_telegram']}")
    put(IDS["canal_telegram"], t, SIN_GUARDAR)
    try:
        republicar(IDS["canal_telegram"])
        print("Canal Telegram: sin guardar ejecuciones; publicado")
    except Exception as ex:
        print("AVISO: Canal Telegram actualizado pero no se pudo publicar (¿túnel caído?):", ex)

    # ---- Juez: "No sé" en la rúbrica de respuestas
    j = C.n8n("GET", f"/workflows/{IDS['supervisor']}")
    msg = next(n for n in j["nodes"] if n["name"] == "Juez (LLM con JSON Schema)")["parameters"]["messages"]["messageValues"][0]
    msg["message"] = msg["message"].replace('y la respuesta lo reconoce ("no cuento con ese dato")',
                                            'y la respuesta lo reconoce con "No sé"')
    sha = hashlib.sha256(msg["message"].encode("utf-8")).hexdigest()[:12]  # versión del prompt en el log de auditoría
    lg = next(n for n in j["nodes"] if n["name"] == "Armar log de auditoría")["parameters"]
    lg["jsCode"] = re.sub(r"systemPromptSnapshot: \{ version: '[^']*', sha256: '[0-9a-f]*' \}",
                          f"systemPromptSnapshot: {{ version: 'juez-rubrica-v3.1 (M11: acciones + «No sé»)', sha256: '{sha}' }}",
                          lg["jsCode"])
    print("Juez: sha256 del prompt", sha)
    put(IDS["supervisor"], j)
    republicar(IDS["supervisor"])
    print("Juez: rúbrica reconoce «No sé»")

    for wid, archivo in [(IDS["manager"], "AI Automation Avanzado - M11.json"), (IDS["respuesta_voz"], "Respuesta de voz (M11).json"),
                         (IDS["canal_telegram"], "Canal Telegram (M11).json"), (IDS["supervisor"], "SUPERVISOR_Judge (M11).json")]:
        x = C.n8n("GET", f"/workflows/{wid}")
        x = {k: x[k] for k in ("name", "nodes", "connections", "settings") if k in x}
        json.dump(x, open(os.path.join(MOD11, archivo), "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
