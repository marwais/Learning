# -*- coding: utf-8 -*-
"""Duplica el sistema del Módulo 9 en el Módulo 11 (Proyecto Final). Convención: cada módulo parte del anterior.

Lee los workflows vivos del M9 por la API de n8n y crea sus copias M11 remapeando:
  - ids de sub-workflows (Tool RAG, Workers 1-4, Supervisor) a sus copias M11,
  - planillas Agenda_Turnos (09) y QA_Veredictos (09) a sus copias (11),
  - tabla de Airtable Memoria_M9 a Memoria_M11 y la carpeta Entregas/09 a Entregas/Trabajo Final,
  - webhookId nuevos (chat, Telegram, esperas de Slack) para no chocar con el M9.

A diferencia de los módulos anteriores, NO desactiva el M9 ni activa el Manager M11: el M9 sigue
siendo el sistema en producción hasta que el M11 esté listo (comparten bot de Telegram y casilla
de Gmail). Solo publica los sub-workflows M11, que no tienen disparadores externos.
Al final exporta los JSON del M11 a Avanzado/Modulo11/.

Uso:  python duplicar_m9_a_m11.py          # idempotente: si ya existe la copia, la actualiza (PUT)
"""
import json, os, sys, uuid
sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
MOD11 = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "..", "..", "Modulo5", "scripts"))
import _config as C  # noqa: E402

M9 = json.load(open(os.path.join(HERE, "..", "..", "Modulo9", "_ids_m9.json")))
IDS_PATH = os.path.join(MOD11, "_ids_m11.json")
IDS = json.load(open(IDS_PATH)) if os.path.exists(IDS_PATH) else {}

# Recursos 11 (creados en Drive / Airtable antes de correr este script)
REMAP = {
    "18iDnwiUt6kEU_bXB2UHsOaYP0RVLD4ERWGFVgR8LGYo": "19rWr4cy1pVmiDi5iv3Nkr3gZn4ExF12Ep5OkMrxxaWk",  # Agenda_Turnos
    "1ras982C-ZORHtRIIBQ96PwPQVy9m0Op5CgZwVea-DLY": "1IYqouMdEh8s0ecJEdDMWjtObglgDA1Nd8E84nWdSEQk",  # QA_Veredictos
    "tblNsEBHTVb0oLK1n": "tblaIZxUOLY1T8g40",                                                      # Memoria_M11
    "15PZwmfrNUmO2r-2xTp4bK6sLteXEhn1s": "15y6JMd_aVrDFc_hL_yMcVolUFcXkUcV7",                      # Entregas/Trabajo Final
    "Memoria_M9": "Memoria_M11",
    "(M9)": "(M11)",
    "Agenda_Turnos (09)": "Agenda_Turnos (11)",
    "QA_Veredictos (09)": "QA_Veredictos (11)",
}
SETTINGS_OK = {"executionOrder", "saveDataSuccessExecution", "saveDataErrorExecution", "saveManualExecutions",
               "saveExecutionProgress", "executionTimeout", "errorWorkflow", "timezone", "callerPolicy"}

# clave (igual en _ids_m9 y _ids_m11) en orden de dependencia: primero lo que otros llaman
ORDEN = ["tool_rag", "worker1", "worker2", "worker3", "worker4", "supervisor", "manager"]
ARCHIVOS = {"tool_rag": "workflows/AgendaBot · Herramienta RAG.json", "worker1": "workflows/AgendaBot · Worker 1 · Registrar turno.json",
            "worker2": "workflows/AgendaBot · Worker 2 · Confirmación.json", "worker3": "workflows/AgendaBot · Worker 3 · Consultar turnos.json",
            "worker4": "workflows/AgendaBot · Worker 4 · Modificar turno.json", "supervisor": "workflows/AgendaBot · Juez (supervisor).json",
            "manager": "workflows/AgendaBot · Manager.json"}


def remap(texto, ids_wf):
    for a, b in {**REMAP, **ids_wf}.items():
        texto = texto.replace(a, b)
    return texto.replace("AI Automation Avanzado - M9", "AI Automation Avanzado - M11")


def copiar(clave, ids_wf):
    w = C.n8n("GET", f"/workflows/{M9[clave]}")
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
    ids_wf[M9[clave]] = r["id"]
    print(f"OK: {r['name']} ({r['id']}) — {len(r['nodes'])} nodos")
    return r["id"]


def activar(wid):
    try:
        C.n8n("POST", f"/workflows/{wid}/deactivate")
    except Exception:
        pass
    C.n8n("POST", f"/workflows/{wid}/activate")


def exportar():
    for clave, archivo in ARCHIVOS.items():
        w = C.n8n("GET", f"/workflows/{IDS[clave]}")
        w = {k: w[k] for k in ("name", "nodes", "connections", "settings") if k in w}
        json.dump(w, open(os.path.join(MOD11, archivo), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Exportados", len(ARCHIVOS), "workflows a", MOD11)


def main():
    ids_wf = {}
    for clave in ORDEN:
        copiar(clave, ids_wf)
    for k in ("tool_rag", "worker1", "worker2", "worker3", "worker4", "supervisor"):
        activar(IDS[k])
    print("Sub-workflows M11 publicados. Manager M11 inactivo (el M9 sigue en producción):", IDS["manager"])
    exportar()


if __name__ == "__main__":
    main()
