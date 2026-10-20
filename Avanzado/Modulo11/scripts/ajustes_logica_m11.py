# -*- coding: utf-8 -*-
"""Proyecto Final (M11) — ajustes de lógica de negocio encontrados en las pruebas.

1. "Resolver accion": si el paciente pide un turno que ya tiene (mismo motivo, misma fecha y hora), antes se
   trataba como una reprogramación al mismo horario ("quedó Reprogramado" sin cambios y una escritura inútil
   en la agenda). Ahora responde "Ya tenés ese turno… no hice cambios" y no toca la agenda.

Uso:  python ajustes_logica_m11.py      # idempotente
"""
import json, os, sys
sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
MOD11 = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "..", "..", "Modulo5", "scripts"))
import _config as C  # noqa: E402

IDS = json.load(open(os.path.join(MOD11, "_ids_m11.json")))
SETTINGS_OK = {"executionOrder", "saveDataSuccessExecution", "saveDataErrorExecution", "saveManualExecutions",
               "saveExecutionProgress", "executionTimeout", "errorWorkflow", "timezone", "callerPolicy"}

VIEJO = ("  else { const choque=mine.find(r=>r.ID!==target.ID&&sameF(r.Fecha,nf)&&n(r.Hora)===n(nh));")
NUEVO = ("  else if(sameF(target.Fecha,nf)&&n(target.Hora)===n(nh)){ out={accion:'rechazo',mensaje:'Ya tenés un turno de '"
         "+target.Motivo+' el '+target.Fecha+' a las '+target.Hora+': no hice cambios.'}; }\n"
         "  else { const choque=mine.find(r=>r.ID!==target.ID&&sameF(r.Fecha,nf)&&n(r.Hora)===n(nh));")


def main():
    w = C.n8n("GET", f"/workflows/{IDS['manager']}")
    nodo = next(n for n in w["nodes"] if n["name"] == "Resolver accion")
    code = nodo["parameters"]["jsCode"]
    if "no hice cambios" in code:
        print("Resolver accion: ya ajustado")
        exportar()
        return
    assert VIEJO in code, "Cambió el código de 'Resolver accion': revisar el ajuste"
    nodo["parameters"]["jsCode"] = code.replace(VIEJO, NUEVO)
    settings = {k: v for k, v in (w.get("settings") or {}).items() if k in SETTINGS_OK}
    C.n8n("PUT", f"/workflows/{IDS['manager']}",
          {"name": w["name"], "nodes": w["nodes"], "connections": w["connections"], "settings": settings})
    try:
        C.n8n("POST", f"/workflows/{IDS['manager']}/deactivate")
    except Exception:
        pass
    C.n8n("POST", f"/workflows/{IDS['manager']}/activate")
    exportar()
    print("Resolver accion: ajustado y Manager publicado")


def exportar():
    x = C.n8n("GET", f"/workflows/{IDS['manager']}")
    x = {k: x[k] for k in ("name", "nodes", "connections", "settings") if k in x}
    json.dump(x, open(os.path.join(MOD11, "workflows/AgendaBot · Manager.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
