# -*- coding: utf-8 -*-
"""Ciclo completo de actualización del conocimiento del RAG.

Hace: parsear los documentos nuevos/cambiados con LlamaParse (-> kb_md/) ->
cargar el markdown en el nodo de ingesta de n8n. Después SOLO falta correr
"▶ Ingerir KB (RAG)" en n8n, que recrea la colección de Qdrant y la vuelve a llenar.

Uso:  python update_kb.py            # parsea solo lo que no tiene .md
      python update_kb.py --force    # re-parsea todo
"""
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
import parse_kb, update_codenode

print("1) Parseando con LlamaParse ...")
parse_kb.main(force="--force" in sys.argv)
print("\n2) Cargando el markdown en el nodo de ingesta de n8n ...")
update_codenode.main()
print("\n==> LISTO. Ahora en n8n: abrí el workflow M5, desplegá el botón")
print("    'Execute workflow' -> 'from ▶ Ingerir KB (RAG)' y ejecutalo.")
print("    Verificá con: python verify_qdrant.py")
