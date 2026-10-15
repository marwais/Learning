# -*- coding: utf-8 -*-
"""Proyecto Final (M11) — "Responder al paciente" desde Slack después de "Tomo el caso" (botón "Responder con
plantilla" del protocolo de escalado del M7; pedido del usuario del 15/10/2026).

Escalado humano (M11), con nodos visuales:
  Registrar decisión → ¿Lo tomó una persona? → Respuesta para el paciente (Slack, texto libre, espera máx. 10 min)
  → Mensaje para el paciente (lo escrito; si está vacío, es "." o venció la espera: "Nos estaremos comunicando en
    breve para continuar.") → Registrar respuesta (escalados_m11)
  → ¿Paciente en Telegram? ─sí→ ¿Mandó audio? ─sí→ Respuesta de voz (M11) (misma voz del bot, máx. 200 caracteres)
                          │                  └no→ Responder por texto (Telegram)
                          └no→ ¿Hay email y una respuesta escrita? ─sí→ Responder por email (Gmail)
El texto por defecto se usa solo para Telegram (por email se envía únicamente lo que escribió la persona).

Uso:  python responder_paciente_m11.py      # idempotente
"""
import json, os, sys, uuid
sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
MOD11 = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "..", "..", "Modulo5", "scripts"))
sys.path.insert(0, HERE)
import _config as C  # noqa: E402
import seguridad_p2_m11 as S  # noqa: E402

IDS = S.IDS
DEFECTO = "Nos estaremos comunicando en breve para continuar."
CASO = "$('Recibir caso').first().json"
MSG = "$('Mensaje para el paciente').first().json"
TG_CRED = {"telegramApi": {"id": "x7iGZ1Z1LuKEKu80", "name": "Telegram account"}}


def main():
    w = C.n8n("GET", f"/workflows/{IDS['escalado_humano']}")
    N = {n["name"]: n for n in w["nodes"]}
    con = w["connections"]
    if "¿Lo tomó una persona?" in N:
        print("Escalado humano: ya instalado")
        return
    dx, dy = N["Registrar decisión"]["position"]
    y = dy + 260
    w["nodes"] += [
        S.si("¿Lo tomó una persona?", [dx + 220, y], "={{ $json.estado === 'tomado' }}"),
        S.nodo("Respuesta para el paciente (Slack)", "n8n-nodes-base.slack", 2.3, [dx + 440, y],
               {"authentication": "oAuth2", "resource": "message", "operation": "sendAndWait", "select": "channel",
                "channelId": S.SOPORTE, "responseType": "freeText",
                "message": "=:writing_hand: *Respuesta para {{ " + CASO + ".nombre_remitente || 'el paciente' }}* "
                           "({{ " + CASO + ".categoria }} · traceId {{ " + CASO + ".traceId }})\n"
                           "Escribí lo que AgendaBot le tiene que mandar por su canal ({{ " + CASO + ".canal }}). "
                           "Si no escribís nada en 10 minutos, o escribís un punto, "
                           "{{ String(" + CASO + ".canal).startsWith('telegram') || " + CASO + ".tg_chat_id ? "
                           "'se le envía: _" + DEFECTO + "_' : 'no se le envía nada (contactalo vos)' }}",
                "options": {"limitWaitTime": {"values": {"limitType": "afterTimeInterval", "resumeAmount": 10,
                                                         "resumeUnit": "minutes"}}}},
               credentials=S.SLACK_CRED, webhookId=str(uuid.uuid4())),
        S.set_campos("Mensaje para el paciente", [dx + 660, y], {
            "personalizado": "={{ !!String($json.data?.text || '').trim() && String($json.data?.text || '').trim() !== '.' }}",
            "texto": "={{ (String($json.data?.text || '').trim() && String($json.data?.text || '').trim() !== '.') "
                     "? String($json.data.text).trim() : " + json.dumps(DEFECTO, ensure_ascii=False) + " }}",
        }, incluir=False),
        S.dt("Registrar respuesta", [dx + 880, y], "update", "escalados_m11",
             filtro={"traceId": "={{ " + CASO + ".traceId }}"},
             cols={"decision": "={{ 'tomado; respuesta al paciente: ' + $json.texto }}"}),
        S.si("¿Paciente en Telegram?", [dx + 1100, y], "={{ !!" + CASO + ".tg_chat_id }}"),
        S.si("¿Mandó audio?", [dx + 1320, y - 100],
             "={{ " + CASO + ".canal === 'telegram_voz' && " + MSG + ".texto.length <= 200 }}"),
        S.set_campos("Armar respuesta de voz", [dx + 1540, y - 200],
                     {"texto_voz": "={{ " + MSG + ".texto }}", "tg_chat_id": "={{ " + CASO + ".tg_chat_id }}"}, incluir=False),
        S.exec_wf("Responder por voz (Respuesta de voz)", [dx + 1760, y - 200], IDS["respuesta_voz"],
                  "Respuesta de voz (M11)", True),
        S.nodo("Responder por texto (Telegram)", "n8n-nodes-base.telegram", 1.2, [dx + 1540, y],
               {"chatId": "={{ " + CASO + ".tg_chat_id }}", "text": "={{ " + MSG + ".texto }}",
                "additionalFields": {"appendAttribution": False}},
               credentials=TG_CRED, webhookId=str(uuid.uuid4()), **S.RETRY),
        S.si("¿Hay email y una respuesta escrita?", [dx + 1320, y + 160],
             "={{ !!" + CASO + ".email_entrada && " + MSG + ".personalizado }}"),
        S.nodo("Responder por email (Gmail)", "n8n-nodes-base.gmail", 2.1, [dx + 1540, y + 160],
               {"sendTo": "={{ " + CASO + ".email_entrada }}", "subject": "Clínica LoDeTincho — sobre tu consulta",
                "emailType": "text",
                "message": "=Hola,\n\n{{ " + MSG + ".texto }}\n\n— Central de Turnos, Clínica LoDeTincho",
                "options": {"appendAttribution": False}},
               credentials=S.GMAIL_CRED, webhookId=str(uuid.uuid4()), **S.RETRY),
    ]
    for a, b, o in [("Registrar decisión", "¿Lo tomó una persona?", 0),
                    ("¿Lo tomó una persona?", "Respuesta para el paciente (Slack)", 0),
                    ("Respuesta para el paciente (Slack)", "Mensaje para el paciente", 0),
                    ("Mensaje para el paciente", "Registrar respuesta", 0),
                    ("Registrar respuesta", "¿Paciente en Telegram?", 0),
                    ("¿Paciente en Telegram?", "¿Mandó audio?", 0),
                    ("¿Paciente en Telegram?", "¿Hay email y una respuesta escrita?", 1),
                    ("¿Mandó audio?", "Armar respuesta de voz", 0),
                    ("¿Mandó audio?", "Responder por texto (Telegram)", 1),
                    ("Armar respuesta de voz", "Responder por voz (Respuesta de voz)", 0),
                    ("¿Hay email y una respuesta escrita?", "Responder por email (Gmail)", 0)]:
        S.conectar(con, a, b, o)
    nota = next((n for n in w["nodes"] if "stickyNote" in n["type"]), None)
    if nota:
        nota["parameters"]["content"] += ("\n\n**Responder al paciente**: con *Tomo el caso*, Slack pide la respuesta (texto "
                                          "libre, 10 min). AgendaBot la envía por el canal del paciente (por Telegram, en "
                                          "audio si habló o en texto si escribió; por email, solo si hay respuesta escrita). "
                                          "Por defecto, en Telegram: \"" + DEFECTO + "\"")
        nota["parameters"]["height"] = max(nota["parameters"].get("height", 260), 330)
    C.n8n("PUT", f"/workflows/{IDS['escalado_humano']}", {"name": w["name"], "nodes": w["nodes"], "connections": con,
                                                          "settings": {k: v for k, v in w["settings"].items() if k in S.SETTINGS_OK}})
    S.republicar(IDS["escalado_humano"])
    x = C.n8n("GET", f"/workflows/{IDS['escalado_humano']}")
    x = {k: x[k] for k in ("name", "nodes", "connections", "settings")}
    json.dump(x, open(os.path.join(MOD11, "Escalado humano (M11).json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"Escalado humano: responder al paciente instalado — {len(x['nodes'])} nodos, publicado")


if __name__ == "__main__":
    main()
