# -*- coding: utf-8 -*-
"""Parsea los documentos de /documentacion con LlamaParse (API v2, tier agentic)
y guarda un .md por documento en ../kb_md/ (respetando las subcarpetas).

Requiere LLAMA_CLOUD_API_KEY en scripts/.env (se crea en cloud.llamaindex.ai -> API Keys).

Uso:  python parse_kb.py            # parsea solo los que no tienen .md
      python parse_kb.py --force    # re-parsea todos
"""
import os, glob, json, sys, time, uuid, urllib.request
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
import _config as C

API = "https://api.cloud.llamaindex.ai/api/v2"
KEY = os.environ.get("LLAMA_CLOUD_API_KEY", "")
EXCLUDE = {"00_Indice.docx", "Documentacion_Completa_LoDeTincho.docx"}
CONFIG = {"tier": "agentic", "version": "latest"}

def _req(method, path, data=None, ctype=None):
    h = {"Authorization": "Bearer " + KEY, "Accept": "application/json"}
    if ctype:
        h["Content-Type"] = ctype
    r = urllib.request.Request(API + path, data=data, method=method, headers=h)
    return json.loads(urllib.request.urlopen(r, timeout=120).read())

def upload(path):
    """POST multipart: file + configuration (JSON)."""
    b = uuid.uuid4().hex
    name = os.path.basename(path)
    parts = [
        f'--{b}\r\nContent-Disposition: form-data; name="configuration"\r\n\r\n{json.dumps(CONFIG)}\r\n'.encode(),
        f'--{b}\r\nContent-Disposition: form-data; name="file"; filename="{name}"\r\n'
        f'Content-Type: application/octet-stream\r\n\r\n'.encode() + open(path, "rb").read() + b"\r\n",
        f"--{b}--\r\n".encode(),
    ]
    return _req("POST", "/parse/upload", b"".join(parts), f"multipart/form-data; boundary={b}")["id"]

def wait_markdown(job_id, timeout=600):
    t0 = time.time()
    while time.time() - t0 < timeout:
        j = _req("GET", f"/parse/{job_id}")["job"]
        if j["status"] == "COMPLETED":
            r = _req("GET", f"/parse/{job_id}?expand=markdown_full")
            return r.get("markdown_full") or r["job"].get("markdown_full") or ""
        if j["status"] in ("FAILED", "CANCELLED"):
            raise RuntimeError(f"job {job_id}: {j['status']} {j.get('error_message')}")
        time.sleep(3)
    raise TimeoutError(job_id)

def main(force=False):
    if not KEY:
        raise SystemExit("Falta LLAMA_CLOUD_API_KEY en scripts/.env")
    files = [f for f in sorted(glob.glob(os.path.join(C.DOCDIR, "**", "*.doc*"), recursive=True))
             if os.path.basename(f) not in EXCLUDE and not os.path.basename(f).startswith("~$")]
    for f in files:
        rel = os.path.relpath(f, C.DOCDIR)
        out = os.path.join(C.KBMD, os.path.splitext(rel)[0] + ".md")
        if os.path.exists(out) and not force:
            print("  (ya está)", rel)
            continue
        print("  parseando", rel, "...", end=" ", flush=True)
        md = wait_markdown(upload(f))
        os.makedirs(os.path.dirname(out), exist_ok=True)
        open(out, "w", encoding="utf-8").write(md)
        print(f"{len(md)} chars")
    print(f"Listo: {len(files)} documentos en {C.KBMD}")

if __name__ == "__main__":
    main(force="--force" in sys.argv)
