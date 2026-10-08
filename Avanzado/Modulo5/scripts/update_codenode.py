# -*- coding: utf-8 -*-
"""Carga los .md de ../kb_md/ (salida de LlamaParse) en el nodo Code
"Cargar KB (markdown LlamaParse)" del workflow M5, como una lista legible
de {source, file, markdown}. Después solo falta correr "▶ Ingerir KB (RAG)" en n8n."""
import os, glob, json, re, sys
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
import _config as C

NODE = "Cargar KB (markdown LlamaParse)"

def docs():
    items = []
    for f in sorted(glob.glob(os.path.join(C.KBMD, "**", "*.md"), recursive=True)):
        md = open(f, encoding="utf-8").read().strip()
        m = re.search(r"^#{1,6}\s+(.+)$", md, re.M)  # LlamaParse suele usar "##" para el título
        rel = os.path.relpath(f, C.KBMD).replace("\\", "/")
        source = m.group(1).replace("**", "").strip() if m else os.path.splitext(os.path.basename(f))[0]
        items.append({"source": source, "file": rel, "markdown": md})
    return items

def main():
    items = docs()
    if not items:
        raise SystemExit("No hay .md en kb_md/. Corré primero: python parse_kb.py")
    js = ("// Documentos de la base de conocimiento, parseados con LlamaParse (tier agentic).\n"
          "// Generado por scripts/update_codenode.py a partir de Avanzado/Modulo5/kb_md/*.md. No editar a mano.\n"
          "const DOCS = " + json.dumps(items, ensure_ascii=False, indent=1) + ";\n"
          "return DOCS.map(d => ({ json: d }));\n")
    wf = C.n8n("GET", "/workflows/" + C.WORKFLOW_ID)
    node = next((n for n in wf["nodes"] if n["name"] == NODE), None)
    if node is None:
        raise SystemExit(f"No encontré el nodo '{NODE}' en el workflow {C.WORKFLOW_ID}")
    node["parameters"]["jsCode"] = js
    C.n8n("PUT", "/workflows/" + C.WORKFLOW_ID,
          {"name": wf["name"], "nodes": wf["nodes"], "connections": wf["connections"],
           "settings": {"executionOrder": "v1"}})
    print(f"Nodo '{NODE}' actualizado: {len(items)} documentos, {sum(len(i['markdown']) for i in items)} chars.")
    for i in items:
        print(f"  - {i['source']}  ({i['file']})")

if __name__ == "__main__":
    main()
