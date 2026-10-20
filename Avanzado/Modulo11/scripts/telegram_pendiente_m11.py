# -*- coding: utf-8 -*-
"""Proyecto Final (M11) — Canal Telegram: no perder el pedido cuando se pide el email por escrito.

Hueco de diseño del M6 (encontrado en la prueba del usuario del 15/10): si la nota de voz dictaba un email, el canal
pedía "escribímelo por texto" pero DESCARTABA el pedido del audio; el email llegaba después como un mensaje suelto
y el sistema respondía "¿En qué te puedo ayudar?".

Ahora, con nodos visuales y la Data Table pendientes_m11 (sesion, texto, creado):
  ¿Dictó un email? ─sí→ Guardar pedido pendiente → Pedir email por escrito
  Entrada Telegram → Buscar pedido pendiente → ¿Completa un pedido pendiente? (hay pendiente de < 30 min y el texto trae @)
      ├sí→ Limpiar pendiente → Pedido completado (transcripción + "el email correcto es …") → Pasar al Manager
      └no→ Pedido tal cual → Pasar al Manager
La transcripción pendiente es solo texto (el audio ya se descartó) y se borra al usarse.

Uso:  python telegram_pendiente_m11.py      # idempotente
"""
import json, os, sys
sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
MOD11 = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "..", "..", "Modulo5", "scripts"))
sys.path.insert(0, HERE)
import _config as C  # noqa: E402
import seguridad_p2_m11 as S  # noqa: E402

IDS, AUX = S.IDS, S.AUX
SES = "={{ 'tg-' + $('Mensaje de Telegram').first().json.message.chat.id }}"
ET = "$('Entrada Telegram').first().json"


def tabla():
    if AUX.get("dt_pendientes_m11"):
        return
    r = C.n8n("POST", "/data-tables", {"name": "pendientes_m11", "columns": [
        {"name": "sesion", "type": "string"}, {"name": "texto", "type": "string"}, {"name": "creado", "type": "string"}]})
    AUX["dt_pendientes_m11"] = r["id"]
    json.dump(AUX, open(S.AUX_PATH, "w"), indent=1)
    print("Data Table pendientes_m11:", r["id"])


def main():
    tabla()
    w = C.n8n("GET", f"/workflows/{IDS['canal_telegram']}")
    N = {n["name"]: n for n in w["nodes"]}
    con = w["connections"]
    if "Guardar pedido pendiente" in N:
        print("Canal Telegram: ya instalado")
        return
    ex, ey = N["Entrada Telegram"]["position"]
    N["Pasar al Manager"]["position"] = [ex + 1320, ey]
    px, py = N["Pedir email por escrito"]["position"]
    N["Pedir email por escrito"]["position"] = [px + 220, py]
    N["Pedir email por escrito"]["parameters"]["text"] = ("Anoté tu pedido. Para no anotar mal tu email, ¿me lo escribís por "
                                                          "texto? Por audio se confunden letras.")
    w["nodes"] += [
        S.dt("Guardar pedido pendiente", [px, py], "upsert", "pendientes_m11", filtro={"sesion": SES},
             cols={"sesion": SES, "texto": "={{ $('Transcribir (Whisper)').first().json.text }}",
                   "creado": "={{ $now.toUTC().toISO() }}"}),
        S.dt("Buscar pedido pendiente", [ex + 220, ey], "get", "pendientes_m11",
             filtro={"sesion": "={{ $json.sessionId }}"}, alwaysOutputData=True),
        S.si("¿Completa un pedido pendiente?", [ex + 440, ey],
             "={{ !!$json.texto && DateTime.fromISO($json.creado) > $now.minus({ minutes: 30 }) && "
             + ET + ".mensaje.includes('@') }}"),
        S.dt("Limpiar pendiente", [ex + 660, ey - 120], "update", "pendientes_m11",
             filtro={"sesion": "={{ " + ET + ".sessionId }}"}, cols={"texto": "", "creado": ""}),
        S.set_json("Pedido completado", [ex + 880, ey - 120],
                   "={{ JSON.stringify({ ..." + ET + ", mensaje: $('Buscar pedido pendiente').first().json.texto + "
                   "' (Corrección del paciente por texto: su email correcto es ' + " + ET + ".mensaje.trim() + "
                   "'; ignorá cualquier email dictado en el audio.)' }) }}"),
        S.set_json("Pedido tal cual", [ex + 880, ey + 120], "={{ JSON.stringify(" + ET + ") }}"),
        S.nota([ex - 40, ey + 260], 1140, 200,
               "## Pedido pendiente (email dictado)\nSi la nota de voz dicta un email, se guarda la transcripción en la "
               "Data Table `pendientes_m11` y se le pide el email por texto. Cuando llega un texto con @ (dentro de "
               "30 min), se une con el pedido guardado y recién ahí pasa al Manager: el pedido no se pierde y el email "
               "es el escrito. La transcripción (solo texto) se borra al usarse."),
    ]
    con["¿Dictó un email?"]["main"][0] = [{"node": "Guardar pedido pendiente", "type": "main", "index": 0}]
    con["Entrada Telegram"] = {"main": [[{"node": "Buscar pedido pendiente", "type": "main", "index": 0}]]}
    for a, b, o in [("Guardar pedido pendiente", "Pedir email por escrito", 0),
                    ("Buscar pedido pendiente", "¿Completa un pedido pendiente?", 0),
                    ("¿Completa un pedido pendiente?", "Limpiar pendiente", 0),
                    ("¿Completa un pedido pendiente?", "Pedido tal cual", 1),
                    ("Limpiar pendiente", "Pedido completado", 0),
                    ("Pedido completado", "Pasar al Manager", 0), ("Pedido tal cual", "Pasar al Manager", 0)]:
        S.conectar(con, a, b, o)
    C.n8n("PUT", f"/workflows/{IDS['canal_telegram']}", {"name": w["name"], "nodes": w["nodes"], "connections": con,
                                                         "settings": {k: v for k, v in w["settings"].items() if k in S.SETTINGS_OK}})
    S.republicar(IDS["canal_telegram"])
    x = C.n8n("GET", f"/workflows/{IDS['canal_telegram']}")
    x = {k: x[k] for k in ("name", "nodes", "connections", "settings")}
    json.dump(x, open(os.path.join(MOD11, "workflows/AgendaBot · Canal Telegram.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"Canal Telegram: pedido pendiente instalado — {len(x['nodes'])} nodos, publicado")


if __name__ == "__main__":
    main()
