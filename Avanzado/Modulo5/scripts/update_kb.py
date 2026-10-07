# -*- coding: utf-8 -*-
"""Ciclo completo de actualizacion del conocimiento del RAG.

Hace: extraer texto de los .docx -> actualizar el nodo de ingesta en n8n ->
recrear la coleccion Qdrant limpia. Despues SOLO falta correr el trigger
"▶ Ingerir KB (RAG)" en n8n (Execute workflow).

Uso:  python update_kb.py
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import extract_kb, update_codenode, recreate_qdrant

print("1) Extrayendo texto de los .docx ...")
extract_kb.main()
print("\n2) Actualizando el nodo de ingesta en n8n ...")
update_codenode.main()
print("\n3) Recreando la coleccion Qdrant (limpia) ...")
recreate_qdrant.main()
print("\n==> LISTO. Ahora en n8n: abri el workflow, desplega el boton")
print("    'Execute workflow' -> 'from ▶ Ingerir KB (RAG)' y ejecutalo.")
print("    Verifica con: python verify_qdrant.py")
