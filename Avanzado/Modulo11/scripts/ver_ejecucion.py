# -*- coding: utf-8 -*-
"""Muestra las últimas ejecuciones de un workflow M11: estado, nodos recorridos y datos clave.

Uso:  python ver_ejecucion.py [clave] [n]     # clave de _ids_m11.json (default: manager), n ejecuciones (default: 1)
      python ver_ejecucion.py manager 1 --nodo "Aplicar validación"   # además imprime la salida de ese nodo
"""
import json, os, sys
sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "Modulo5", "scripts"))
import _config as C  # noqa: E402

IDS = json.load(open(os.path.join(HERE, "..", "_ids_m11.json")))
args = [a for a in sys.argv[1:] if not a.startswith("--")]
clave = args[0] if args else "manager"
n = int(args[1]) if len(args) > 1 else 1
nodo = sys.argv[sys.argv.index("--nodo") + 1] if "--nodo" in sys.argv else None
if nodo in args:
    args.remove(nodo)


def salida(runs):
    try:
        return runs[-1]["data"]["main"][0][0]["json"]
    except Exception:
        return None


r = C.n8n("GET", f"/executions?workflowId={IDS.get(clave, clave)}&limit={n}&includeData=true")
for e in r["data"]:
    rd = e.get("data", {}).get("resultData", {})
    run = rd.get("runData", {})
    err = (rd.get("error") or {}).get("message")
    print(f"== ejecución {e['id']} · {e['status']} · {e['mode']} · {e.get('startedAt')} → {e.get('stoppedAt')}"
          + (f" · ERROR: {err}" if err else ""))
    trc = salida(run.get("Generar traceId", [])) or {}
    if trc:
        print("   traceId:", trc.get("traceId"), "· canal:", trc.get("canal"), "· mensaje:", str(trc.get("mensaje"))[:80])
    print("   nodos:", " → ".join(f"{k}{' ✘' if v[-1].get('error') else ''}" for k, v in run.items()))
    for k in ("Contrato de datos", "Normalizar veredicto", "Supervisor (Juez)", "Responder al chat"):
        if k in run:
            print(f"   {k}:", json.dumps(salida(run[k]), ensure_ascii=False)[:400])
    if nodo and nodo in run:
        print(f"   {nodo}:", json.dumps(salida(run[nodo]), ensure_ascii=False)[:1500])
