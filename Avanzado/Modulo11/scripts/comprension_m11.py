# -*- coding: utf-8 -*-
"""Proyecto Final (M11) — "dos fallas de comprensión seguidas → una persona" (semáforo del M7, fallback del M10).

Falla de comprensión = la respuesta final es la de FUERA_DE_ALCANCE o el "No pude procesar tu pedido".
Si la misma sesión tuvo otra falla en los últimos 30 minutos, el pedido pasa a una persona: el paciente recibe
"No logro ayudarte…" y el caso entra a Escalado humano (M11). Todo con nodos visuales y la Data Table sesiones_m11.

  Responder al chat → ¿No se pudo ayudar? ─no→ Respuesta final → (despacho por el canal)
                                         └sí→ Buscar falla anterior → ¿Segunda falla seguida?
                                                ├sí→ Limpiar fallas → Derivar por incomprensión → Escalar a una persona + Respuesta final
                                                └no→ Registrar falla → Respuesta sin cambios → Respuesta final
Uso:  python comprension_m11.py      # idempotente
"""
import json, os, sys, uuid
sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
MOD11 = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "..", "..", "Modulo5", "scripts"))
sys.path.insert(0, HERE)
import _config as C  # noqa: E402
import seguridad_p2_m11 as S  # noqa: E402  (fábricas de nodos visuales)

IDS, AUX = S.IDS, S.AUX
MENSAJE = ("No logro ayudarte con tu pedido por este medio: ya le pasé tu consulta a una persona del equipo de la "
           "Central de Turnos, que te va a contactar a la brevedad.")


def tabla():
    if AUX.get("dt_sesiones_m11"):
        return
    r = C.n8n("POST", "/data-tables", {"name": "sesiones_m11",
                                       "columns": [{"name": "sesion", "type": "string"},
                                                   {"name": "ultima_falla", "type": "string"}]})
    AUX["dt_sesiones_m11"] = r["id"]
    json.dump(AUX, open(S.AUX_PATH, "w"), indent=1)
    print("Data Table sesiones_m11:", r["id"])


def main():
    tabla()
    w = C.n8n("GET", f"/workflows/{IDS['manager']}")
    N = {n["name"]: n for n in w["nodes"]}
    con = w["connections"]
    if "¿No se pudo ayudar?" in N:
        print("Manager: ya instalado")
        return
    x, y = N["Responder al chat"]["position"]
    for n in w["nodes"]:
        if n["position"][0] > x:
            n["position"] = [n["position"][0] + 1540, n["position"][1]]
    ses = "={{ $('Normalizar entrada').first().json.sessionId }}"
    w["nodes"] += [
        S.si("¿No se pudo ayudar?", [x + 220, y],
             "={{ ($('Contrato de datos').isExecuted && $('Contrato de datos').first().json.intent === 'FUERA_DE_ALCANCE') "
             "|| String($json.output || '').startsWith('No pude procesar') }}"),
        S.dt("Buscar falla anterior", [x + 440, y + 200], "get", "sesiones_m11", filtro={"sesion": ses},
             alwaysOutputData=True),
        S.si("¿Segunda falla seguida?", [x + 660, y + 200],
             "={{ !!$json.ultima_falla && DateTime.fromISO($json.ultima_falla) > $now.minus({ minutes: 30 }) }}"),
        S.dt("Limpiar fallas", [x + 880, y + 100], "upsert", "sesiones_m11", filtro={"sesion": ses},
             cols={"sesion": ses, "ultima_falla": ""}),
        S.set_json("Derivar por incomprensión", [x + 1100, y + 100],
                   "={{ JSON.stringify({ ...$('Pedido validado').first().json, categoria: 'no se entiende el pedido (2 veces)', "
                   "protocolo: '" + S.PROTOCOLO + "', respuesta_fija: " + json.dumps(MENSAJE, ensure_ascii=False)
                   + ", output: " + json.dumps(MENSAJE, ensure_ascii=False) + " }) }}"),
        S.dt("Registrar falla", [x + 880, y + 300], "upsert", "sesiones_m11", filtro={"sesion": ses},
             cols={"sesion": ses, "ultima_falla": "={{ $now.toUTC().toISO() }}"}),
        S.set_json("Respuesta sin cambios", [x + 1100, y + 300], "={{ JSON.stringify($('Responder al chat').first().json) }}"),
        S.nodo("Respuesta final", "n8n-nodes-base.noOp", 1, [x + 1320, y], {}),
    ]
    N = {n["name"]: n for n in w["nodes"]}
    destino = con["Responder al chat"]["main"][0]          # hoy: ¿Vino por Telegram?
    con["Responder al chat"] = {"main": [[{"node": "¿No se pudo ayudar?", "type": "main", "index": 0}]]}
    con["Respuesta final"] = {"main": [destino]}
    for a, b, o in [("¿No se pudo ayudar?", "Buscar falla anterior", 0), ("¿No se pudo ayudar?", "Respuesta final", 1),
                    ("Buscar falla anterior", "¿Segunda falla seguida?", 0),
                    ("¿Segunda falla seguida?", "Limpiar fallas", 0), ("¿Segunda falla seguida?", "Registrar falla", 1),
                    ("Limpiar fallas", "Derivar por incomprensión", 0),
                    ("Derivar por incomprensión", "Escalar a una persona (sub-workflow)", 0),
                    ("Derivar por incomprensión", "Respuesta final", 0),
                    ("Registrar falla", "Respuesta sin cambios", 0), ("Respuesta sin cambios", "Respuesta final", 0)]:
        S.conectar(con, a, b, o)
    for k in ("Borrador del resultado (Gmail)", "Enviar resultado (Telegram)"):
        p = N[k]["parameters"]
        for campo in ("text", "message"):
            if campo in p:
                p[campo] = p[campo].replace("$('Responder al chat').first().json.output", "$('Respuesta final').first().json.output")
    settings = {k: v for k, v in (w.get("settings") or {}).items() if k in S.SETTINGS_OK}
    C.n8n("PUT", f"/workflows/{IDS['manager']}", {"name": w["name"], "nodes": w["nodes"], "connections": con,
                                                  "settings": settings})
    S.republicar(IDS["manager"])
    x2 = C.n8n("GET", f"/workflows/{IDS['manager']}")
    x2 = {k: x2[k] for k in ("name", "nodes", "connections", "settings") if k in x2}
    json.dump(x2, open(os.path.join(MOD11, "AI Automation Avanzado - M11.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(f"Manager: control de comprensión instalado — {len(x2['nodes'])} nodos, publicado")


if __name__ == "__main__":
    main()
