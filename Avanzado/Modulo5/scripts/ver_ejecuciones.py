# -*- coding: utf-8 -*-
"""Muestra las últimas ejecuciones del Manager M5 (pregunta, intent, respuesta final y resultado
del validador) y de la herramienta de búsqueda (consulta, Top-K/Min Score y scores).
Uso: python ver_ejecuciones.py [N]"""
import sys
sys.stdout.reconfigure(encoding="utf-8")
import _config as C

n = int(sys.argv[1]) if len(sys.argv) > 1 else 3

def salida(rd, nodo):
    r = rd.get(nodo)
    if not r or not r[0].get("data"):
        return {}
    return r[0]["data"].get("main", [[{}]])[0][0].get("json", {})

r = C.n8n("GET", f"/executions?limit={n}&workflowId={C.WORKFLOW_ID}&includeData=true")
for e in reversed(r["data"]):
    rd = e["data"]["resultData"]["runData"]
    print(f"\n#{e['id']} {e['status']} {e['startedAt'][11:19]} | {salida(rd, 'Normalizar entrada').get('mensaje')} "
          f"| intent={salida(rd, 'Contrato de datos').get('intent')}")
    v = salida(rd, "Aplicar validación")
    if v:
        print(f"  validación: {v.get('validacion')} | búsquedas: {v.get('busquedas')} | {v.get('motivo')}")
        if v.get("validacion") == "rechazada":
            print("  respuesta ORIGINAL (bloqueada):\n" + v.get("respuesta_original", ""))
        print("  respuesta enviada:\n" + v.get("output", ""))
    else:
        print("  respuesta:", salida(rd, "Responder al chat").get("output"))

r = C.n8n("GET", f"/executions?limit={n * 2}&workflowId=aEnYAA9K1l7YAwRj&includeData=true")
for e in r["data"]:
    rd = e["data"]["resultData"]["runData"]
    q = salida(rd, "Parámetros RAG")
    hits = salida(rd, "Buscar en Qdrant (Top-K + Min Score)").get("result", [])
    print(f"  tool#{e['id']} [{q.get('top_k')}/{q.get('min_score')}] {q.get('consulta')} -> "
          f"{[(round(h['score'], 3), h['payload']['metadata']['section'][:40]) for h in hits]}")
