# -*- coding: utf-8 -*-
"""Proyecto Final (M11) — mensaje de datos faltantes y pedido del email por escrito (pedido del usuario, 15/10/2026).

1. "Resolver accion": el aviso pasa a "Faltan datos que son necesarios para poder agendar turnos: fecha, hora y email."
   (o "…para poder modificar el turno: …"), con la lista unida por "y". Si falta el email, agrega "El email
   escribímelo por texto, por favor." y marca falta_email = true.
2. Manager, después de "Aviso (no se puede)": si falta el email y el paciente está en Telegram, se guarda el pedido
   en la Data Table pendientes_m11 (el mismo mecanismo del Canal Telegram): cuando escriba el email, el canal lo une
   con el pedido original. Si el paciente habló (nota de voz), la respuesta sale por voz y debajo va la aclaración
   por texto "Para evitar errores, el email te lo pido por escrito, por favor."
3. Canal Telegram: el texto que completa el pedido se agrega como "datos que el paciente agregó por texto" (puede
   traer el email y también la fecha u hora que faltaban).

Uso:  python faltan_datos_m11.py      # idempotente
"""
import json, os, sys
sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
MOD11 = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "..", "..", "Modulo5", "scripts"))
sys.path.insert(0, HERE)
import _config as C  # noqa: E402
import seguridad_p2_m11 as S  # noqa: E402

IDS = S.IDS
LISTA = ("// Etiquetas y orden de los datos faltantes en el aviso al paciente.\n"
         "const ETIQ={fecha:'Fecha',hora:'Hora','la nueva fecha u hora':'la nueva Fecha u Hora',motivo:'Motivo del turno',"
         "nombre:'su Nombre y Apellido',email:'su Email'};\n"
         "const ORDEN=['fecha','hora','la nueva fecha u hora','motivo','nombre','email'];\n"
         "const lista=a=>{const b=[...a].sort((x,y)=>ORDEN.indexOf(x)-ORDEN.indexOf(y)).map(x=>ETIQ[x]||x);"
         "return b.length>1?b.slice(0,-1).join(', ')+' y '+b[b.length-1]:b[0];};\n")
MOD_VIEJO = "  if(falta.length){ out={accion:'faltan_datos',mensaje:'Para modificar el turno faltan datos: '+falta.join(', ')+'.'}; }"
MOD_NUEVO = ("  if(falta.length){ out={accion:'faltan_datos',faltan:falta,falta_email:false,"
             "mensaje:'Faltan datos que son necesarios para poder modificar el turno: '+lista(falta)+'.'}; }")
ALTA_VIEJO = ("  if(falta.length){ out={accion:'faltan_datos',mensaje:'No se puede agendar la cita: faltan datos obligatorios ('"
              "+falta.join(', ')+').'}; }")
ALTA_NUEVO = ("  if(falta.length){ out={accion:'faltan_datos',faltan:falta,falta_email:falta.includes('email'),"
              "mensaje:'Faltan datos que son necesarios para poder agendar turnos: '+lista(falta)+'.'"
              "+(falta.includes('email')?' El email escribímelo por texto, por favor.':'')}; }")
ACLARACION = "Para evitar errores, el email te lo pido por escrito, por favor."
FALTA_EMAIL = "$('Resolver accion').isExecuted && $('Resolver accion').first().json.falta_email === true"


def manager():
    w = C.n8n("GET", f"/workflows/{IDS['manager']}")
    N = {n["name"]: n for n in w["nodes"]}
    con = w["connections"]
    rc = N["Resolver accion"]["parameters"]
    if "lista(falta)" not in rc["jsCode"]:
        assert MOD_VIEJO in rc["jsCode"] and ALTA_VIEJO in rc["jsCode"], "cambió el código de Resolver accion"
        rc["jsCode"] = rc["jsCode"].replace("let out; const falta=[];", LISTA + "let out; const falta=[];", 1)
        rc["jsCode"] = rc["jsCode"].replace(MOD_VIEJO, MOD_NUEVO).replace(ALTA_VIEJO, ALTA_NUEVO)
    ra = N["Responder al paciente (email)"]["parameters"]
    ra["message"] = ra["message"].replace("$('Aviso (no se puede)').item.json", "$('Aviso (no se puede)').first().json")
    if "¿Falta el email? (Telegram)" not in N:
        ax, ay = N["Aviso (no se puede)"]["position"]
        tg = "$('Normalizar entrada').first().json.tg_chat_id"
        ses = "={{ 'tg-' + " + tg + " }}"
        w["nodes"] += [
            S.si("¿Falta el email? (Telegram)", [ax, ay + 220], "={{ " + FALTA_EMAIL + " && !!" + tg + " }}"),
            S.dt("Guardar pedido pendiente", [ax + 220, ay + 320], "upsert", "pendientes_m11", filtro={"sesion": ses},
                 cols={"sesion": ses, "texto": "={{ $('Normalizar entrada').first().json.mensaje }}",
                       "creado": "={{ $now.toUTC().toISO() }}"}),
        ]
        con["Aviso (no se puede)"] = {"main": [[{"node": "¿Falta el email? (Telegram)", "type": "main", "index": 0}]]}
        S.conectar(con, "¿Falta el email? (Telegram)", "Guardar pedido pendiente", 0)
        S.conectar(con, "¿Falta el email? (Telegram)", "¿Vino por email?", 1)
        S.conectar(con, "Guardar pedido pendiente", "¿Vino por email?", 0)
        vx, vy = N["Responder con voz (sub-workflow)"]["position"]
        tgsend = S.nodo("Aclarar: email por escrito (Telegram)", "n8n-nodes-base.telegram", 1.2, [vx + 440, vy],
                        {"chatId": "={{ " + tg + " }}", "text": ACLARACION, "additionalFields": {"appendAttribution": False}},
                        credentials={"telegramApi": {"id": "x7iGZ1Z1LuKEKu80", "name": "Telegram account"}},
                        webhookId=__import__("uuid").uuid4().__str__(), **S.RETRY)
        w["nodes"] += [S.si("¿Aclarar email por texto?", [vx + 220, vy], "={{ " + FALTA_EMAIL + " }}"), tgsend]
        S.conectar(con, "Responder con voz (sub-workflow)", "¿Aclarar email por texto?", 0)
        S.conectar(con, "¿Aclarar email por texto?", tgsend["name"], 0)
    C.n8n("PUT", f"/workflows/{IDS['manager']}", {"name": w["name"], "nodes": w["nodes"], "connections": con,
                                                  "settings": {k: v for k, v in w["settings"].items() if k in S.SETTINGS_OK}})
    S.republicar(IDS["manager"])
    x = C.n8n("GET", f"/workflows/{IDS['manager']}")
    x = {k: x[k] for k in ("name", "nodes", "connections", "settings")}
    json.dump(x, open(os.path.join(MOD11, "AI Automation Avanzado - M11.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"Manager: mensaje de datos faltantes + pedido del email por escrito — {len(x['nodes'])} nodos, publicado")


def canal():
    w = C.n8n("GET", f"/workflows/{IDS['canal_telegram']}")
    n = next(x for x in w["nodes"] if x["name"] == "Pedido completado")
    n["parameters"]["jsonOutput"] = (
        "={{ JSON.stringify({ ...$('Entrada Telegram').first().json, mensaje: $('Buscar pedido pendiente').first().json.texto "
        "+ ' (Datos que el paciente agregó por texto: ' + $('Entrada Telegram').first().json.mensaje.trim() + '. Si incluye un "
        "email, ese es el correcto: ignorá cualquier email dictado en el audio.)' }) }}")
    C.n8n("PUT", f"/workflows/{IDS['canal_telegram']}", {"name": w["name"], "nodes": w["nodes"], "connections": w["connections"],
                                                         "settings": {k: v for k, v in w["settings"].items() if k in S.SETTINGS_OK}})
    S.republicar(IDS["canal_telegram"])
    x = C.n8n("GET", f"/workflows/{IDS['canal_telegram']}")
    x = {k: x[k] for k in ("name", "nodes", "connections", "settings")}
    json.dump(x, open(os.path.join(MOD11, "Canal Telegram (M11).json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Canal Telegram: el texto que completa el pedido se agrega como datos del paciente; publicado")


if __name__ == "__main__":
    manager()
    canal()
