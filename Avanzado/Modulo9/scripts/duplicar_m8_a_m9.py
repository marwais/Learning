# -*- coding: utf-8 -*-
"""Duplica el sistema del Módulo 8 en el Módulo 9 (convención: cada módulo parte del anterior).

Lee los workflows vivos del M8 por la API de n8n y crea sus copias M9 remapeando:
  - ids de sub-workflows (Tool RAG, Workers 1-4, Supervisor) a sus copias M9,
  - planillas Agenda_Turnos (08) y QA_Veredictos (08) a sus copias (09),
  - tabla de Airtable Memoria_M8 a Memoria_M9 y la carpeta Entregas/08 a Entregas/09,
  - webhookId nuevos (chat, Telegram, esperas de Slack) para no chocar con el M8.
El AB_Test (M8) no se duplica: el A/B ya se cerró en el M8.

Al final desactiva el Manager M8 (comparten bot de Telegram y casilla de Gmail) y activa el M9.

Uso:  python duplicar_m8_a_m9.py          # idempotente: si ya existe la copia, la actualiza (PUT)
"""
import json, os, sys, uuid
sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "Modulo5", "scripts"))
import _config as C  # noqa: E402

M8 = json.load(open(os.path.join(HERE, "..", "..", "Modulo8", "_ids_m8.json")))
IDS_PATH = os.path.join(HERE, "..", "_ids_m9.json")
IDS = json.load(open(IDS_PATH)) if os.path.exists(IDS_PATH) else {}

# Recursos 09 (creados en Drive / Airtable antes de correr este script)
REMAP = {
    "1rsbwlKjYOln3QcH0drwmSunNUdY17GQmdWX8d6eR-18": "18iDnwiUt6kEU_bXB2UHsOaYP0RVLD4ERWGFVgR8LGYo",  # Agenda_Turnos
    "1O1894tGkQFttThtInYEBC9kb0AvHudRfPL60u4fZyEs": "1ras982C-ZORHtRIIBQ96PwPQVy9m0Op5CgZwVea-DLY",  # QA_Veredictos
    "tbl9Jmni1XpwXnONw": "tblNsEBHTVb0oLK1n",                                                      # Memoria_M9
    "1_oljK2VbrHo0-FmsQmEY4nMSSOdbqv1I": "15PZwmfrNUmO2r-2xTp4bK6sLteXEhn1s",                      # Entregas/09
    "Memoria_M8": "Memoria_M9",
    "(M8)": "(M9)",
    "Agenda_Turnos (08)": "Agenda_Turnos (09)",
    "QA_Veredictos (08)": "QA_Veredictos (09)",
}
SETTINGS_OK = {"executionOrder", "saveDataSuccessExecution", "saveDataErrorExecution", "saveManualExecutions",
               "saveExecutionProgress", "executionTimeout", "errorWorkflow", "timezone", "callerPolicy"}

# (clave en _ids_m8, clave en _ids_m9) en orden de dependencia: primero lo que otros llaman
ORDEN = [("aEnYAA9K1l7YAwRj", "tool_rag"), ("OhqlaD9owJHhZ0Xp", "worker1"), ("Ft8psvxAlilfFKuw", "worker2"),
         ("mC0rTN5ylCLiu6gX", "worker3"), ("47lULDxTZa8YGKjj", "worker4"), ("supervisor", "supervisor"),
         ("manager", "manager")]


def remap(texto, ids_wf):
    for a, b in {**REMAP, **ids_wf}.items():
        texto = texto.replace(a, b)
    return texto.replace("AI Automation Avanzado - M8", "AI Automation Avanzado - M9")


def copiar(m8_id, clave, ids_wf):
    w = C.n8n("GET", f"/workflows/{m8_id}")
    nodes = json.loads(remap(json.dumps(w["nodes"], ensure_ascii=False), ids_wf))
    for n in nodes:
        if "webhookId" in n:
            n["webhookId"] = str(uuid.uuid4())
    body = {"name": remap(w["name"], ids_wf), "nodes": nodes,
            "connections": json.loads(remap(json.dumps(w["connections"], ensure_ascii=False), ids_wf)),
            "settings": {k: v for k, v in (w.get("settings") or {}).items() if k in SETTINGS_OK}}
    if IDS.get(clave):
        r = C.n8n("PUT", f"/workflows/{IDS[clave]}", body)
    else:
        r = C.n8n("POST", "/workflows", body)
        IDS[clave] = r["id"]
        json.dump(IDS, open(IDS_PATH, "w"), indent=1)
    ids_wf[m8_id] = r["id"]
    print(f"OK: {r['name']} ({r['id']}) — {len(r['nodes'])} nodos")
    return r["id"]


def activar(wid):
    try:
        C.n8n("POST", f"/workflows/{wid}/deactivate")
    except Exception:
        pass
    C.n8n("POST", f"/workflows/{wid}/activate")


def main():
    ids_wf = {}
    for k8, k9 in ORDEN:
        copiar(M8[k8], k9, ids_wf)
    for k in ("tool_rag", "worker1", "worker2", "worker3", "worker4", "supervisor"):
        activar(IDS[k])
    try:
        C.n8n("POST", f"/workflows/{M8['manager']}/deactivate")
        print("Manager M8 desactivado (comparte Telegram y Gmail con el M9)")
    except Exception as e:
        print("Aviso: no se pudo desactivar el Manager M8:", e)
    activar(IDS["manager"])
    print("Manager M9 activo:", IDS["manager"])


if __name__ == "__main__":
    main()
