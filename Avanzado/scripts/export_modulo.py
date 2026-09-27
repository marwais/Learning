#!/usr/bin/env python3
"""
Exporta todos los artefactos de un modulo del proyecto AgendaBot al repo.
Por modulo: workflows (JSON) + por cada tabla {esquema, recrear, registros [+create_table payload en Airtable]}.

Convencion de datos:
- Airtable: UNA sola base ("Memoria_Agente") con UNA tabla por modulo ("Memoria_M3", "Memoria_M4", ...).
  Asi se otorga el permiso del token una sola vez.
- Google Sheets: una planilla Agenda_Turnos por carpeta 0N.

Uso:
    export N8N_API_KEY="..."                 # Settings -> n8n API
    export AIRTABLE_TOKEN="pat..."           # si el modulo usa Airtable
    export GOOGLE_SA_JSON="/ruta/sa.json"    # opcional: cuenta de servicio Google para exportar Sheets
    python export_modulo.py moduloN.config.json

El .docx/.pdf de la entrega los genera el usuario a mano; este script NO los toca.
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
    key = os.environ.get("N8N_API_KEY")
    if not key:
        print("== Workflows == (omitido: falta N8N_API_KEY)"); return
    base = cfg.get("n8n_base", "http://localhost:5678")
    print("== Workflows ==")
    for wid, fname in cfg.get("workflows", {}).items():
        try:
            d = json.loads(http_get(base + "/api/v1/workflows/" + wid, {"X-N8N-API-KEY": key}))
            clean = {"name": d["name"], "nodes": d["nodes"], "connections": d["connections"],
                     "settings": d.get("settings", {"executionOrder": "v1"})}
            save_text(os.path.join(out, fname), json.dumps(clean, ensure_ascii=False, indent=2))
        except Exception as e:
            print("  [WARN] %s: %s" % (fname, e))

def _fields_from_meta(tbl):
    out = []
    for f in tbl["fields"]:
        t = f["type"]; o = f.get("options") or {}
        if t in ("singleSelect", "multipleSelects"):
            out.append({"name": f["name"], "type": t, "options": {"choices": [{"name": c["name"]} for c in o.get("choices", [])]}})
        elif t in ("number", "percent", "currency", "duration", "date", "dateTime", "rating"):
            out.append({"name": f["name"], "type": t, "options": o})
        else:
            out.append({"name": f["name"], "type": t})
    return out

def export_airtable(cfg, out):
    tables = cfg.get("airtable_tables", [])
    if not tables: return
    tok = os.environ.get("AIRTABLE_TOKEN")
    if not tok:
        print("== Airtable == (omitido: falta AIRTABLE_TOKEN)"); return
    H = {"Authorization": "Bearer " + tok}
    print("== Airtable ==")
    for t in tables:
        base, tid, name = t["base"], t["table"], t["base_name"]
        try:
            meta = json.loads(http_get("https://api.airtable.com/v0/meta/bases/%s/tables" % base, H))
            tbl = next(x for x in meta["tables"] if x["id"] == tid)
            cols = [f["name"] for f in tbl["fields"]]
            # esquema
            save_text(os.path.join(out, "%s (esquema).json" % name), json.dumps(
                {"base": {"id": base}, "table": {"id": tid, "name": tbl["name"]},
                 "fields": [{"name": f["name"], "type": f["type"], "options": f.get("options"), "description": f.get("description")} for f in tbl["fields"]]},
                ensure_ascii=False, indent=2))
            # create_table payload
            fields = _fields_from_meta(tbl)
            save_text(os.path.join(out, "%s (create_table payload).json" % name),
                      json.dumps({"baseId": base, "name": tbl["name"], "fields": fields}, ensure_ascii=False, indent=2))
            # recrear.py (crea la tabla en la base existente)
            recrear = ('"""Recrea esta tabla en la base existente (una base por proyecto, una tabla por modulo).\n'
                       '  export AIRTABLE_TOKEN=pat...\n'
                       '  export AIRTABLE_BASE_ID=%s\n'
                       '  python "%s (recrear).py"\n"""\n' % (base, name) +
                       "import json, os, urllib.request\n"
                       "fields = " + json.dumps(fields, ensure_ascii=False, indent=2) + "\n"
                       'payload = {"name": %s, "fields": fields}\n' % json.dumps(tbl["name"], ensure_ascii=False) +
                       'req = urllib.request.Request("https://api.airtable.com/v0/meta/bases/" + os.environ["AIRTABLE_BASE_ID"] + "/tables",\n'
                       '    data=json.dumps(payload).encode(), method="POST",\n'
                       '    headers={"Authorization": "Bearer " + os.environ["AIRTABLE_TOKEN"], "Content-Type": "application/json"})\n'
                       'print(json.loads(urllib.request.urlopen(req).read()).get("id"))\n')
            save_text(os.path.join(out, "%s (recrear).py" % name), recrear)
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
                fd = r.get("fields", {}); w.writerow([fd.get(c, "") for c in cols])
            save_text(os.path.join(out, "%s (registros).csv" % name), buf.getvalue())
            print("   %s: %d registros" % (name, len(recs)))
        except Exception as e:
            print("   [WARN] %s no exportada: %s" % (name, e))

def export_sheets(cfg, out):
    sheets = cfg.get("google_sheets", [])
    if not sheets: return
    sa = os.environ.get("GOOGLE_SA_JSON")
    if not sa:
        print("== Google Sheets == (omitido: falta GOOGLE_SA_JSON)"); return
    import gspread
    gc = gspread.service_account(filename=sa)
    print("== Google Sheets ==")
    for s in sheets:
        try:
            rows = gc.open_by_key(s["id"]).sheet1.get_all_values()
            buf = io.StringIO(); csv.writer(buf).writerows(rows)
            save_text(os.path.join(out, "%s.csv" % s["base_name"]), buf.getvalue())
            headers = rows[0] if rows else []
            save_text(os.path.join(out, "%s (esquema).json" % s["base_name"]),
                      json.dumps({"fuente": "Google Sheets", "id": s["id"], "columnas": [{"nombre": h, "tipo": "texto"} for h in headers]}, ensure_ascii=False, indent=2))
        except Exception as e:
            print("   [WARN] %s: %s" % (s.get("base_name"), e))

def main():
    if len(sys.argv) < 2:
        print("uso: python export_modulo.py <config.json>"); sys.exit(1)
    cfg = json.load(open(sys.argv[1], encoding="utf-8"))
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(sys.argv[1])), cfg["out_dir"]))
    print("Modulo", cfg.get("modulo"), "-> ", out)
    export_workflows(cfg, out)
    export_airtable(cfg, out)
    export_sheets(cfg, out)
    print("Listo.")

if __name__ == "__main__":
    main()
