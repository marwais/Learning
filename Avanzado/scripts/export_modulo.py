#!/usr/bin/env python3
"""
Exporta todos los artefactos de un modulo del proyecto AgendaBot al repo.
Por modulo: workflows (JSON) + por cada tabla {esquema, recrear, registros [+create_base payload en Airtable]}.

Uso:
    export N8N_API_KEY="..."           # API key de n8n (Settings -> n8n API)
    export AIRTABLE_TOKEN="pat..."     # PAT de Airtable (si el modulo usa Airtable)
    export GOOGLE_SA_JSON="/ruta/sa.json"   # cuenta de servicio Google (opcional, para exportar Sheets)
    python export_modulo.py moduloN.config.json

El .docx/.pdf de la entrega los genera el usuario a mano; este script NO los toca.
Ver la convencion completa en el README de esta carpeta.
"""
import json, os, sys, csv, io, urllib.request, urllib.parse

def http_get(url, headers):
    return urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=60).read()

def save_text(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text)
    print("  guardado:", os.path.basename(path))

def export_workflows(cfg, out):
    key = os.environ["N8N_API_KEY"]; base = cfg.get("n8n_base", "http://localhost:5678")
    print("== Workflows ==")
    for wid, fname in cfg.get("workflows", {}).items():
        d = json.loads(http_get(base + "/api/v1/workflows/" + wid, {"X-N8N-API-KEY": key}))
        clean = {"name": d["name"], "nodes": d["nodes"], "connections": d["connections"],
                 "settings": d.get("settings", {"executionOrder": "v1"})}
        save_text(os.path.join(out, fname), json.dumps(clean, ensure_ascii=False, indent=2))

def _airtable_field_to_create(f):
    t = f["type"]; o = f.get("options") or {}
    if t in ("singleSelect", "multipleSelects"):
        return {"name": f["name"], "type": t, "options": {"choices": [{"name": c["name"]} for c in o.get("choices", [])]}}
    if t in ("number", "percent", "currency", "duration", "date", "dateTime", "rating"):
        return {"name": f["name"], "type": t, "options": o}
    return {"name": f["name"], "type": t}

def export_airtable(cfg, out):
    tables = cfg.get("airtable_tables", [])
    if not tables: return
    tok = os.environ["AIRTABLE_TOKEN"]; H = {"Authorization": "Bearer " + tok}
    print("== Airtable ==")
    for t in tables:
        base, tid, bname = t["base"], t["table"], t["base_name"]
        meta = json.loads(http_get("https://api.airtable.com/v0/meta/bases/%s/tables" % base, H))
        tbl = next(x for x in meta["tables"] if x["id"] == tid)
        cols = [f["name"] for f in tbl["fields"]]
        # esquema
        esquema = {"base": {"id": base, "name": bname}, "table": {"id": tid, "name": tbl["name"]},
                   "fields": [{"name": f["name"], "type": f["type"], "options": f.get("options"), "description": f.get("description")} for f in tbl["fields"]]}
        save_text(os.path.join(out, "%s (esquema).json" % bname), json.dumps(esquema, ensure_ascii=False, indent=2))
        # create_base payload
        payload = {"workspaceId": "REEMPLAZAR_wspXXXXXXXXXXXXXX", "name": bname,
                   "tables": [{"name": tbl["name"], "fields": [_airtable_field_to_create(f) for f in tbl["fields"]]}]}
        save_text(os.path.join(out, "%s (create_base payload).json" % bname), json.dumps(payload, ensure_ascii=False, indent=2))
        # recrear.py
        recrear = ('"""Recrea la base/tabla en Airtable. Uso:\n'
                   '  export AIRTABLE_TOKEN=pat... ; export AIRTABLE_WORKSPACE_ID=wsp...\n'
                   '  python "%s (recrear).py"\n"""\n' % bname +
                   "import json, os, urllib.request\n"
                   "payload = " + json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
                   'payload["workspaceId"] = os.environ["AIRTABLE_WORKSPACE_ID"]\n'
                   'req = urllib.request.Request("https://api.airtable.com/v0/meta/bases", data=json.dumps(payload).encode(), method="POST",\n'
                   '    headers={"Authorization": "Bearer " + os.environ["AIRTABLE_TOKEN"], "Content-Type": "application/json"})\n'
                   'print(json.loads(urllib.request.urlopen(req).read()).get("id"))\n')
        save_text(os.path.join(out, "%s (recrear).py" % bname), recrear)
        # registros
        recs = []; offset = None
        while True:
            q = {"pageSize": 100}
            if offset: q["offset"] = offset
            d = json.loads(http_get("https://api.airtable.com/v0/%s/%s?%s" % (base, tid, urllib.parse.urlencode(q)), H))
            recs += d.get("records", []); offset = d.get("offset")
            if not offset: break
        buf = io.StringIO(); w = csv.writer(buf); w.writerow(cols)
        for r in recs:
            fdict = r.get("fields", {}); w.writerow([fdict.get(c, "") for c in cols])
        save_text(os.path.join(out, "%s (registros).csv" % bname), buf.getvalue())
        print("   registros:", len(recs))

def export_sheets(cfg, out):
    sheets = cfg.get("google_sheets", [])
    if not sheets: return
    sa = os.environ.get("GOOGLE_SA_JSON")
    if not sa:
        print("== Google Sheets == (omitido: falta GOOGLE_SA_JSON)")
        return
    import gspread
    gc = gspread.service_account(filename=sa)
    print("== Google Sheets ==")
    for s in sheets:
        sh = gc.open_by_key(s["id"]); ws = sh.sheet1
        rows = ws.get_all_values()
        buf = io.StringIO(); csv.writer(buf).writerows(rows)
        save_text(os.path.join(out, "%s.csv" % s["base_name"]), buf.getvalue())
        headers = rows[0] if rows else []
        esquema = {"fuente": "Google Sheets", "id": s["id"], "columnas": [{"nombre": h, "tipo": "texto"} for h in headers]}
        save_text(os.path.join(out, "%s (esquema).json" % s["base_name"]), json.dumps(esquema, ensure_ascii=False, indent=2))

def main():
    if len(sys.argv) < 2:
        print("uso: python export_modulo.py <config.json>"); sys.exit(1)
    cfg_path = sys.argv[1]
    cfg = json.load(open(cfg_path, encoding="utf-8"))
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(cfg_path)), cfg["out_dir"]))
    print("Modulo", cfg.get("modulo"), "-> ", out)
    export_workflows(cfg, out)
    export_airtable(cfg, out)
    export_sheets(cfg, out)
    print("Listo.")

if __name__ == "__main__":
    main()
