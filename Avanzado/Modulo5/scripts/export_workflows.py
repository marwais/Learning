# -*- coding: utf-8 -*-
"""Exporta los workflows de n8n (Manager M5 + 4 workers) a /Avanzado/Modulo5
como JSON, para versionarlos en el repo."""
import os, json, sys
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
import _config as C

def save(name, wf):
    out = os.path.join(C.MOD5, name)
    data = {"name": wf["name"], "nodes": wf["nodes"],
            "connections": wf["connections"],
            "settings": wf.get("settings", {"executionOrder": "v1"})}
    open(out, "w", encoding="utf-8", newline="").write(json.dumps(data, ensure_ascii=False, indent=2))
    print("  guardado:", name)

def main():
    save("AI Automation Avanzado - M5.json", C.n8n("GET", "/workflows/" + C.WORKFLOW_ID))
    for wid, fn in C.WORKERS.items():
        try:
            save(fn, C.n8n("GET", "/workflows/" + wid))
        except Exception as e:
            print("  (omito", fn, "->", e, ")")

if __name__ == "__main__":
    main()
