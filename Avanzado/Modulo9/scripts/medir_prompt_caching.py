# -*- coding: utf-8 -*-
"""Mide el Prompt Caching de Anthropic con bloques fijos reales del proyecto (Módulo 9).

Crea un workflow temporal "FinOps_CacheProbe (M9)" (webhook -> HTTP Request a /v1/messages con la credencial
Anthropic de n8n, así la API key nunca sale de n8n), manda dos pedidos seguidos por escenario con el bloque fijo
marcado con cache_control y guarda el `usage` que devuelve la API. Al final borra el workflow.

Escenarios:
  A. Prompt de sistema fijo del Agente RAG (~3.500 caracteres)
  B. "Manual completo": toda la base documental (16 documentos markdown) como bloque fijo

Uso:  python medir_prompt_caching.py      -> ../finops_cache.json
"""
import glob, json, os, sys, time, urllib.request, uuid
sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "Modulo5", "scripts"))
import _config as C  # noqa: E402

MODELO = "claude-sonnet-4-6"
PATH = "finops-cache-probe-m9"
CRED = {"anthropicApi": {"id": "qyqhv8Oy5wq4bqNd", "name": "Anthropic account"}}
PRECIO_IN, PRECIO_OUT = 3.00, 15.00  # US$/MTok Sonnet 4.6; escritura 5 min = 1,25x · lectura = 0,1x


def crear_probe():
    nodes = [
        {"id": "w", "name": "Webhook", "type": "n8n-nodes-base.webhook", "typeVersion": 2, "position": [0, 0],
         "webhookId": str(uuid.uuid4()),
         "parameters": {"httpMethod": "POST", "path": PATH, "responseMode": "lastNode", "options": {}}},
        {"id": "h", "name": "Claude /v1/messages", "type": "n8n-nodes-base.httpRequest", "typeVersion": 4.2,
         "position": [260, 0], "credentials": CRED,
         "parameters": {"method": "POST", "url": "https://api.anthropic.com/v1/messages",
                        "authentication": "predefinedCredentialType", "nodeCredentialType": "anthropicApi",
                        "sendHeaders": True, "headerParameters": {"parameters": [
                            {"name": "anthropic-version", "value": "2023-06-01"}]},
                        "sendBody": True, "specifyBody": "json",
                        "jsonBody": "={{ JSON.stringify($json.body.req) }}", "options": {}}},
    ]
    conns = {"Webhook": {"main": [[{"node": "Claude /v1/messages", "type": "main", "index": 0}]]}}
    r = C.n8n("POST", "/workflows", {"name": "FinOps_CacheProbe (M9)", "nodes": nodes, "connections": conns,
                                     "settings": {"executionOrder": "v1", "saveDataSuccessExecution": "none"}})
    C.n8n("POST", f"/workflows/{r['id']}/activate")
    return r["id"]


def pedir(sistema, pregunta):
    req = {"model": MODELO, "max_tokens": 60,
           "system": [{"type": "text", "text": sistema, "cache_control": {"type": "ephemeral"}}],
           "messages": [{"role": "user", "content": pregunta}]}
    data = json.dumps({"req": req}).encode("utf-8")
    r = urllib.request.Request(f"http://localhost:5678/webhook/{PATH}", data=data,
                               headers={"Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(r, timeout=120).read())["usage"]


def coste(u):
    return (u.get("input_tokens", 0) * PRECIO_IN + u.get("cache_creation_input_tokens", 0) * PRECIO_IN * 1.25
            + u.get("cache_read_input_tokens", 0) * PRECIO_IN * 0.1 + u.get("output_tokens", 0) * PRECIO_OUT) / 1e6


def main():
    rag = open(os.path.join(HERE, "_rag_static.txt"), encoding="utf-8").read()
    kb_files = sorted(glob.glob(os.path.join(HERE, "..", "..", "Modulo5", "kb_md", "**", "*.md"), recursive=True))
    kb = "Sos el asistente de la Clínica LoDeTincho. Respondé solo con este manual:\n\n" + "\n\n".join(
        open(f, encoding="utf-8").read() for f in kb_files)
    wid = crear_probe()
    out = {"modelo": MODELO, "fecha": time.strftime("%Y-%m-%d %H:%M"), "escenarios": {}}
    try:
        for nombre, sistema in (("A_prompt_sistema_RAG", rag), ("B_manual_completo_KB", kb)):
            filas = []
            for i, q in enumerate(("¿Qué profesionales atienden Cardiología?",
                                   "¿En qué horario hacen tomografías sin contraste los domingos?")):
                u = pedir(sistema, q)
                filas.append({"pedido": i + 1, "usage": u, "coste_usd": round(coste(u), 6)})
                print(nombre, i + 1, u)
                time.sleep(2)
            sin_cache = (sum(f["usage"].get("input_tokens", 0) + f["usage"].get("cache_creation_input_tokens", 0)
                             + f["usage"].get("cache_read_input_tokens", 0) for f in filas) * PRECIO_IN
                         + sum(f["usage"]["output_tokens"] for f in filas) * PRECIO_OUT) / 1e6
            out["escenarios"][nombre] = {"caracteres_bloque_fijo": len(sistema), "pedidos": filas,
                                         "coste_2_pedidos_con_cache": round(sum(f["coste_usd"] for f in filas), 6),
                                         "coste_2_pedidos_sin_cache": round(sin_cache, 6)}
    finally:
        C.n8n("POST", f"/workflows/{wid}/deactivate")
        C.n8n("DELETE", f"/workflows/{wid}")
        print("workflow temporal borrado")
    json.dump(out, open(os.path.join(HERE, "..", "finops_cache.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
