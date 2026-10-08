# -*- coding: utf-8 -*-
"""Config compartida para los scripts de mantenimiento del RAG (Modulo 5).

Lee la configuracion de scripts/.env (o variables de entorno). Copiá
.env.example a .env y completá N8N_API_KEY (la creás en n8n -> Settings -> n8n API).
"""
import os, json, urllib.request

def _load_env():
    here = os.path.dirname(os.path.abspath(__file__))
    for p in (os.path.join(here, ".env"), os.path.join(here, "..", ".env")):
        if os.path.exists(p):
            for line in open(p, encoding="utf-8"):
                s = line.strip()
                if s and not s.startswith("#") and "=" in s:
                    k, v = s.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip())
            break
_load_env()

N8N_BASE    = os.environ.get("N8N_BASE", "http://localhost:5678").rstrip("/")
N8N_KEY     = os.environ.get("N8N_API_KEY", "")
WORKFLOW_ID = os.environ.get("N8N_WORKFLOW_ID", "ciy1C6pB26Urfmlj")
QDRANT_URL  = os.environ.get("QDRANT_URL", "http://localhost:6333").rstrip("/")
COLLECTION  = os.environ.get("QDRANT_COLLECTION", "kb_lodetincho_m5")
EMBED_DIM   = int(os.environ.get("EMBED_DIM", "1024"))  # Cohere embed-multilingual-v3.0

# Workers del M5 (para export_workflows.py)
WORKERS = {
    "OhqlaD9owJHhZ0Xp": "Worker1_RegistrarTurno (M5).json",
    "Ft8psvxAlilfFKuw": "Worker2_Confirmacion (M5).json",
    "mC0rTN5ylCLiu6gX": "Worker3_ConsultarTurno (M5).json",
    "47lULDxTZa8YGKjj": "Worker4_ModificarTurno (M5).json",
    "aEnYAA9K1l7YAwRj": "Tool_ConsultarConocimiento (M5).json",
}

HERE   = os.path.dirname(os.path.abspath(__file__))
MOD5   = os.path.abspath(os.path.join(HERE, ".."))
DOCDIR = os.path.join(MOD5, "documentacion")
KBMD   = os.path.join(MOD5, "kb_md")  # markdown de LlamaParse (uno por documento)

def n8n(method, path, body=None):
    if not N8N_KEY:
        raise SystemExit("Falta N8N_API_KEY. Poné el valor en scripts/.env "
                         "(creá la key en n8n -> Settings -> n8n API).")
    data = json.dumps(body, ensure_ascii=False).encode("utf-8") if body is not None else None
    req = urllib.request.Request(
        N8N_BASE + "/api/v1" + path, data=data, method=method,
        headers={"X-N8N-API-KEY": N8N_KEY, "Content-Type": "application/json",
                 "Accept": "application/json"})
    return json.loads(urllib.request.urlopen(req, timeout=120).read())

def qdrant(method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(QDRANT_URL + path, data=data, method=method,
                                 headers={"Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(req, timeout=60).read())
