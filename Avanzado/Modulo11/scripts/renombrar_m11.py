# -*- coding: utf-8 -*-
"""Proyecto Final (M11) — nombres de producción, sin sufijos de los módulos del curso (pedido del usuario, 16/10/2026).

- Workflows: "AI Automation Avanzado - M11" → "AgendaBot · Manager", "Receptor (M11)" → "AgendaBot · Receptor", etc.
- Webhooks: /webhook/agendabot → /webhook/agendabot · /webhook/freno-de-mano → /webhook/freno-de-mano ·
  /webhook/simulacro-de-falla → /webhook/simulacro-de-falla.
- Data Tables: pedidos_procesados_m11 → pedidos_procesados (y escalados, control, sesiones, pendientes).
- Base de conocimiento: copia de los fragmentos de kb_lodetincho_m5 (con sus vectores) a kb_lodetincho; la vieja queda
  como respaldo.
- Credenciales creadas en el M11 (la API de n8n no permite renombrar): se crean "n8n API (alertas)" y "Freno de mano"
  con los mismos valores del .env y los workflows pasan a usarlas.
- Referencias internas (cachedResultName, notas): Memoria_M11 → Memoria_Pacientes, "Agenda_Turnos (11)" → Agenda_Turnos,
  "QA_Veredictos (11)" → QA_Veredictos. Los ids no cambian: los workflows se conectan por id.

Uso:  python renombrar_m11.py      # idempotente
"""
import json, os, sys, urllib.error
sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
MOD11 = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "..", "..", "Modulo5", "scripts"))
sys.path.insert(0, HERE)
import _config as C  # noqa: E402
import seguridad_p2_m11 as S  # noqa: E402

IDS, AUX = S.IDS, S.AUX
ENV = os.path.join(HERE, "..", "..", "Modulo5", "scripts", ".env")

NOMBRES = {"manager": "AgendaBot · Manager", "receptor": "AgendaBot · Receptor", "canal_telegram": "AgendaBot · Canal Telegram",
           "worker1": "AgendaBot · Worker 1 · Registrar turno", "worker2": "AgendaBot · Worker 2 · Confirmación",
           "worker3": "AgendaBot · Worker 3 · Consultar turnos", "worker4": "AgendaBot · Worker 4 · Modificar turno",
           "tool_rag": "AgendaBot · Herramienta RAG", "supervisor": "AgendaBot · Juez (supervisor)",
           "escalado_humano": "AgendaBot · Escalado humano", "respuesta_voz": "AgendaBot · Respuesta de voz",
           "errores": "AgendaBot · Errores", "freno_de_mano": "AgendaBot · Freno de mano",
           "simulacro": "AgendaBot · Simulacro de falla", "ingesta_kb": "AgendaBot · Ingesta KB"}
VIEJOS = {"manager": "AI Automation Avanzado - M11", "receptor": "Receptor (M11)", "canal_telegram": "Canal Telegram (M11)",
          "worker1": "Worker1_RegistrarTurno (M11)", "worker2": "Worker2_Confirmacion (M11)",
          "worker3": "Worker3_ConsultarTurno (M11)", "worker4": "Worker4_ModificarTurno (M11)",
          "tool_rag": "Tool_ConsultarConocimiento (M11)", "supervisor": "SUPERVISOR_Judge (M11)",
          "escalado_humano": "Escalado humano (M11)", "respuesta_voz": "Respuesta de voz (M11)",
          "errores": "Errores (M11)", "freno_de_mano": "Freno de mano (M11)",
          "simulacro": "Simulacro de falla (M11)", "ingesta_kb": "Ingesta KB (M11)"}
TABLAS = {"dt_pedidos_procesados_m11": "pedidos_procesados", "dt_escalados_m11": "escalados", "dt_control_m11": "control",
          "dt_sesiones_m11": "sesiones", "dt_pendientes_m11": "pendientes"}
TEXTO = [  # reemplazos dentro de los workflows (orden importa: lo más largo primero)
    ("/webhook/agendabot", "/webhook/agendabot"), ('"path": "agendabot"', '"path": "agendabot"'),
    ("/webhook/freno-de-mano", "/webhook/freno-de-mano"), ('"path": "freno-de-mano"', '"path": "freno-de-mano"'),
    ('"path": "simulacro-de-falla"', '"path": "simulacro-de-falla"'),
    ("kb_lodetincho_m5", "kb_lodetincho"),
    ("pedidos_procesados_m11", "pedidos_procesados"), ("escalados_m11", "escalados"), ("control_m11", "control"),
    ("sesiones_m11", "sesiones"), ("pendientes_m11", "pendientes"),
    ("Memoria_M11", "Memoria_Pacientes"), ("Agenda_Turnos (11)", "Agenda_Turnos"), ("QA_Veredictos (11)", "QA_Veredictos"),
]


def qdrant_copia():
    try:
        C.qdrant("GET", "/collections/kb_lodetincho")
        print("Qdrant: kb_lodetincho ya existe")
        return
    except urllib.error.HTTPError:
        pass
    cfg = C.qdrant("GET", "/collections/kb_lodetincho_m5")["result"]["config"]["params"]["vectors"]
    C.qdrant("PUT", "/collections/kb_lodetincho", {"vectors": cfg})
    pts, off = [], None
    while True:
        body = {"limit": 256, "with_payload": True, "with_vector": True}
        if off is not None:
            body["offset"] = off
        r = C.qdrant("POST", "/collections/kb_lodetincho_m5/points/scroll", body)["result"]
        pts += r["points"]
        off = r.get("next_page_offset")
        if off is None:
            break
    for i in range(0, len(pts), 64):
        C.qdrant("PUT", "/collections/kb_lodetincho/points?wait=true",
                 {"points": [{"id": p["id"], "vector": p["vector"], "payload": p["payload"]} for p in pts[i:i + 64]]})
    n = C.qdrant("POST", "/collections/kb_lodetincho/points/count", {"exact": True})["result"]["count"]
    print(f"Qdrant: kb_lodetincho creada con {n} fragmentos (copia de kb_lodetincho_m5)")


def tablas():
    for clave, nombre in TABLAS.items():
        try:
            C.n8n("PATCH", f"/data-tables/{AUX[clave]}", {"name": nombre})
            print(f"Data Table {clave[3:]} → {nombre}")
        except urllib.error.HTTPError as e:
            print(f"AVISO Data Table {clave}: {e.code} {e.read().decode()[:150]}")


def env():
    return {l.split("=", 1)[0]: l.split("=", 1)[1].strip() for l in open(ENV, encoding="utf-8") if "=" in l and not l.startswith("#")}


def credenciales():
    e = env()
    nuevas = {}
    for clave, nombre, header, valor in (("cred_n8n_api_v2", "n8n API (alertas)", "X-N8N-API-KEY", C.N8N_KEY),
                                          ("cred_freno_v2", "Freno de mano", "X-Freno-Token",
                                           e.get("FRENO_TOKEN") or e.get("FRENO_TOKEN"))):
        if not AUX.get(clave):
            r = C.n8n("POST", "/credentials", {"name": nombre, "type": "httpHeaderAuth", "data": {"name": header, "value": valor}})
            AUX[clave] = r["id"]
            json.dump(AUX, open(S.AUX_PATH, "w"), indent=1)
        nuevas[clave] = (AUX[clave], nombre)
    return [(f'{{"id": "{AUX["cred_n8n_api"]}", "name": "n8n API local (M11 errores)"}}',
             f'{{"id": "{nuevas["cred_n8n_api_v2"][0]}", "name": "n8n API (alertas)"}}'),
            (f'{{"id": "{AUX["cred_freno"]}", "name": "Freno de mano (M11)"}}',
             f'{{"id": "{nuevas["cred_freno_v2"][0]}", "name": "Freno de mano"}}')]


def workflows(cred_reemplazos):
    todos = {**IDS, "ingesta_kb": AUX["ingesta_kb"]}
    nombres = [(VIEJOS[k], NOMBRES[k]) for k in sorted(VIEJOS, key=lambda k: -len(VIEJOS[k]))]
    orden = [k for k in todos if k not in ("receptor", "canal_telegram", "freno_de_mano", "simulacro", "manager")] + \
            ["manager", "receptor", "canal_telegram", "freno_de_mano", "simulacro"]
    for clave in orden:
        wid = todos[clave]
        w = C.n8n("GET", f"/workflows/{wid}")
        s = json.dumps({"nodes": w["nodes"], "connections": w["connections"]}, ensure_ascii=False)
        for a, b in cred_reemplazos + TEXTO + nombres:
            s = s.replace(a, b)
        s = s.replace(" (M11)", "")
        d = json.loads(s)
        C.n8n("PUT", f"/workflows/{wid}", {"name": NOMBRES[clave], "nodes": d["nodes"], "connections": d["connections"],
                                            "settings": {k: v for k, v in w["settings"].items() if k in S.SETTINGS_OK}})
        if w.get("active"):
            S.republicar(wid)
        quedan = [m for m in ("M11", "_m11", "_m5", "(11)") if m in s]
        print(f"{NOMBRES[clave]:40s} {'publicado' if w.get('active') else 'guardado'}"
              + (f"  · quedan menciones: {quedan}" if quedan else ""))


def main():
    qdrant_copia()
    tablas()
    workflows(credenciales())


if __name__ == "__main__":
    main()
