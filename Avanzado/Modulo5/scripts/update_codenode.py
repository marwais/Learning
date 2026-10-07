# -*- coding: utf-8 -*-
"""Mete el contenido de kb_b64.txt en el nodo Code "Cargar documentos LoDeTincho"
del workflow de n8n (para que la ingesta use el texto actualizado)."""
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
import _config as C

NODE = "Cargar documentos LoDeTincho"

def main():
    b64 = open(C.B64, "r", encoding="ascii").read().strip()
    js = ('const b64="' + b64 + '";'
          'const items=JSON.parse(Buffer.from(b64,"base64").toString("utf8"));'
          'return items.map(i=>({json:i}));')
    wf = C.n8n("GET", "/workflows/" + C.WORKFLOW_ID)
    found = False
    for n in wf["nodes"]:
        if n["name"] == NODE:
            n["parameters"]["jsCode"] = js; found = True
    if not found:
        raise SystemExit(f"No encontre el nodo '{NODE}' en el workflow {C.WORKFLOW_ID}")
    C.n8n("PUT", "/workflows/" + C.WORKFLOW_ID,
          {"name": wf["name"], "nodes": wf["nodes"], "connections": wf["connections"],
           "settings": wf.get("settings", {"executionOrder": "v1"})})
    print(f"Nodo '{NODE}' actualizado (base64 len {len(b64)}).")

if __name__ == "__main__":
    main()
