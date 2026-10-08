# -*- coding: utf-8 -*-
"""Muestra las últimas ejecuciones del Manager M5 (pregunta, intent, respuesta del RAG)
y de la herramienta de búsqueda (consulta, Top-K/Min Score y scores). Uso: python ver_ejecuciones.py [N]"""

import sys,json; sys.stdout.reconfigure(encoding='utf-8')
import _config as C
n=int(sys.argv[1]) if len(sys.argv)>1 else 3
r=C.n8n("GET",f"/executions?limit={n}&workflowId={C.WORKFLOW_ID}&includeData=true")
for e in r["data"]:
    rd=e["data"]["resultData"]["runData"]
    g=lambda node,k: rd.get(node,[{}])[0].get("data",{}).get("main",[[{}]])[0][0].get("json",{}).get(k)
    print(f"\n#{e['id']} {e['status']} {e['startedAt'][11:19]} | {g('Normalizar entrada','mensaje')} | intent={g('Contrato de datos','intent')}\n{g('Agente RAG (Consultas)','output')}")
r=C.n8n("GET",f"/executions?limit={n*2}&workflowId=aEnYAA9K1l7YAwRj&includeData=true")
for e in r["data"]:
    rd=e["data"]["resultData"]["runData"]
    q=rd["Parámetros RAG"][0]["data"]["main"][0][0]["json"]
    hits=rd["Buscar en Qdrant (Top-K + Min Score)"][0]["data"]["main"][0][0]["json"].get("result",[])
    print(f"  tool#{e['id']} [{q['top_k']}/{q['min_score']}] {q['consulta']} -> {[(round(h['score'],3),h['payload']['metadata']['section'][:40]) for h in hits]}")
