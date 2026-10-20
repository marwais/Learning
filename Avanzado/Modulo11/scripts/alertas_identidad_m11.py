# -*- coding: utf-8 -*-
"""Proyecto Final (M11) — alertas que una persona del equipo pueda usar (pedido del usuario, 15/10/2026).

1. Identidad del paciente: el Canal Telegram guarda también el @usuario de Telegram (tg_username) y el Manager lo
   pasa junto con el nombre. Las alertas muestran nombre, cómo contactarlo (link t.me/@usuario, o el email) y lo
   que la memoria (Airtable) sabe del paciente.
2. Errores (M11): la alerta sale en castellano (traducción de los errores típicos de las APIs: sin saldo,
   credencial vencida, sin permisos, saturación, sin conexión…) con el detalle técnico original entre paréntesis,
   e incluye el mensaje del paciente que originó el caso.
3. Escalado humano (M11): el aviso con botones suma la identidad y la memoria del paciente.

Uso:  python alertas_identidad_m11.py      # idempotente
"""
import json, os, sys, copy, uuid
sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
MOD11 = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "..", "..", "Modulo5", "scripts"))
sys.path.insert(0, HERE)
import _config as C  # noqa: E402
import seguridad_p2_m11 as S  # noqa: E402

IDS = S.IDS

ARMAR_ALERTA = r"""// Arma la alerta para el equipo humano (en castellano) y, si se puede, el aviso al paciente.
const e = $('Error Trigger').first().json;
const ex = e.execution || {}, wf = e.workflow || {};
const rd = (($json.data || {}).resultData || {}).runData || {};
const salida = n => { try { return rd[n][0].data.main[0][0].json; } catch (_) { return {}; } };
// Manager: 'Normalizar entrada'; Canal Telegram: 'Entrada Telegram'
const norm = Object.keys(salida('Normalizar entrada')).length ? salida('Normalizar entrada') : salida('Entrada Telegram');
const traceId = salida('Generar traceId').traceId || '(sin traceId: falló antes de generarlo)';
const err = ex.error || {};
const original = [err.message, err.description].filter(Boolean).join(' — ');
// Traducción de los errores típicos de las APIs externas
const REGLAS = [
  [/credit balance|billing|insufficient.?(funds|quota)|quota exceeded/i, 'Sin saldo en la API del proveedor de IA: hay que cargar crédito'],
  [/needs to be reconnected|refresh token|revoked|invalid_grant/i, 'La credencial venció: hay que reconectarla en n8n'],
  [/unauthori[sz]ed|401|invalid api key|authentication/i, 'Credencial inválida o vencida'],
  [/forbidden|403|scope|permission/i, 'El servicio externo negó el permiso (credencial o permisos insuficientes)'],
  [/rate.?limit|429|too many requests|overloaded|529/i, 'El servicio externo está saturado (demasiadas solicitudes)'],
  [/timed? ?out|timeout|ETIMEDOUT/i, 'El servicio externo no respondió a tiempo'],
  [/ENOTFOUND|ECONNREFUSED|ECONNRESET|connection cannot be established|getaddrinfo|network/i, 'No hay conexión con el servicio externo'],
  [/not found|404/i, 'El recurso del servicio externo no existe (404)'],
  [/bad request|400|invalid/i, 'El servicio externo rechazó la solicitud (datos inválidos)'],
  [/simulacro/i, 'Simulacro de falla (prueba de la rama de error)'],
];
const regla = REGLAS.find(([re]) => re.test(original));
const errorEs = regla ? regla[1] : 'Error técnico inesperado';
const tgUser = norm.tg_username ? '@' + norm.tg_username : '';
const contacto = String(norm.canal || '').startsWith('telegram') || norm.tg_chat_id
  ? (norm.tg_username ? `Telegram <https://t.me/${norm.tg_username}|${tgUser}>` : `Telegram (sin usuario público; chat ${norm.tg_chat_id || '?'})`)
  : (norm.email_entrada ? 'Email ' + norm.email_entrada : 'chat de la web');
const texto = [
  ':rotating_light: *AgendaBot — falla en producción*',
  `*Qué pasó:* ${errorEs} (detalle técnico: ${String(original || 'sin mensaje').slice(0, 220)})`,
  `*Dónde:* ${wf.name || '?'} · nodo ${ex.lastNodeExecuted || (err.node || {}).name || '?'}`,
  `*Paciente:* ${norm.nombre_remitente || 'sin nombre'}${tgUser ? ' (' + tgUser + ')' : ''} · contacto: ${contacto}`,
  `*Mensaje del paciente:* ${norm.mensaje ? '"' + String(norm.mensaje).slice(0, 400) + '"' : '(no llegó a leerse)'}`,
  `*traceId:* ${traceId} · *Ejecución:* ${ex.id || '?'}`,
  '*Acción:* tomar el caso y contactar al paciente; revisar la ejecución en n8n.'
].join('\n');
return [{ json: {
  texto, traceId, canal: norm.canal || '', tg_chat_id: norm.tg_chat_id || '',
  email_entrada: norm.email_entrada || '',
  aviso_paciente: 'Estamos con demoras: una persona del equipo te va a responder en unos minutos. Disculpá la espera.'
} }];"""


def canal():
    w = C.n8n("GET", f"/workflows/{IDS['canal_telegram']}")
    n = next(x for x in w["nodes"] if x["name"] == "Entrada Telegram")
    c = n["parameters"]["jsCode"]
    if "tg_username" not in c:
        c = c.replace("  tg_chat_id: t.chat.id,", "  tg_chat_id: t.chat.id,\n  tg_username: t.from?.username || '',  // para que el equipo pueda abrir el chat")
        assert "tg_username" in c
        n["parameters"]["jsCode"] = c
    C.n8n("PUT", f"/workflows/{IDS['canal_telegram']}", {"name": w["name"], "nodes": w["nodes"], "connections": w["connections"],
                                                         "settings": {k: v for k, v in w["settings"].items() if k in S.SETTINGS_OK}})
    S.republicar(IDS["canal_telegram"])
    return w


def manager():
    w = C.n8n("GET", f"/workflows/{IDS['manager']}")
    n = next(x for x in w["nodes"] if x["name"] == "Normalizar entrada")
    c = n["parameters"]["jsCode"]
    if "tg_username" not in c:
        c = c.replace("tg_chat_id: j.tg_chat_id, update_id: j.update_id } }];",
                      "tg_chat_id: j.tg_chat_id, tg_username: j.tg_username || '', update_id: j.update_id } }];")
        assert "tg_username" in c
        n["parameters"]["jsCode"] = c
    C.n8n("PUT", f"/workflows/{IDS['manager']}", {"name": w["name"], "nodes": w["nodes"], "connections": w["connections"],
                                                  "settings": {k: v for k, v in w["settings"].items() if k in S.SETTINGS_OK}})
    S.republicar(IDS["manager"])
    return w


def errores():
    w = C.n8n("GET", f"/workflows/{IDS['errores']}")
    next(x for x in w["nodes"] if x["name"] == "Armar alerta")["parameters"]["jsCode"] = ARMAR_ALERTA
    C.n8n("PUT", f"/workflows/{IDS['errores']}", {"name": w["name"], "nodes": w["nodes"], "connections": w["connections"],
                                                  "settings": {k: v for k, v in w["settings"].items() if k in S.SETTINGS_OK}})
    S.republicar(IDS["errores"])
    return w


def escalado(manager_w):
    w = C.n8n("GET", f"/workflows/{IDS['escalado_humano']}")
    N = {n["name"]: n for n in w["nodes"]}
    con = w["connections"]
    if "Buscar memoria del paciente" not in N:
        mem = copy.deepcopy(next(x for x in manager_w["nodes"] if x["name"] == "Buscar memoria (Airtable)"))
        mem.update({"id": str(uuid.uuid4()), "name": "Buscar memoria del paciente", "alwaysOutputData": True,
                    "onError": "continueRegularOutput"})
        mem["parameters"]["filterByFormula"] = ("={{ '{Session_ID} = \"' + String($('Recibir caso').first().json.sessionId)"
                                                ".replace(/\"/g,'') + '\"' }}")
        rx, ry = N["Registrar escalado"]["position"]
        for n in w["nodes"]:
            if n["position"][0] > rx:
                n["position"] = [n["position"][0] + 220, n["position"][1]]
        mem["position"] = [rx + 220, ry]
        w["nodes"].append(mem)
        con["Registrar escalado"] = {"main": [[{"node": mem["name"], "type": "main", "index": 0}]]}
        con[mem["name"]] = {"main": [[{"node": "Avisar al equipo (Slack)", "type": "main", "index": 0}]]}
    caso = "$('Recibir caso').first().json"
    memf = "($('Buscar memoria del paciente').first().json.fields || {})"
    N = {n["name"]: n for n in w["nodes"]}
    N["Avisar al equipo (Slack)"]["parameters"]["message"] = (
        "=:rotating_light: *AgendaBot — caso para una persona: {{ " + caso + ".categoria }}*\n"
        "*Paciente:* {{ " + caso + ".nombre_remitente || " + memf + "['Datos Clave'] && (" + memf + "['Datos Clave'].match(/Paciente:\\s*([^|]+)/) || [])[1] || 'sin nombre' }}"
        "{{ " + caso + ".tg_username ? ' (@' + " + caso + ".tg_username + ')' : '' }}\n"
        "*Cómo contactarlo:* {{ String(" + caso + ".canal).startsWith('telegram') || " + caso + ".tg_chat_id ? "
        "(" + caso + ".tg_username ? 'Telegram <https://t.me/' + " + caso + ".tg_username + '|abrir chat con @' + " + caso + ".tg_username + '>' "
        ": 'Telegram (sin usuario público, chat ' + " + caso + ".tg_chat_id + '): pedile un teléfono o email por el bot') "
        ": (" + caso + ".email_entrada ? 'Email ' + " + caso + ".email_entrada : 'chat de la web') }}\n"
        "*Mensaje del paciente:* {{ " + caso + ".mensaje }}\n"
        "*Lo que sabemos (memoria):* {{ " + memf + "['Datos Clave'] || 'sin datos previos' }}"
        "{{ " + memf + "['Resumen Consolidado'] ? ' · ' + " + memf + "['Resumen Consolidado'] : '' }}\n"
        "*Ya se le respondió:* {{ " + caso + ".respuesta_fija }}\n"
        "*traceId:* {{ " + caso + ".traceId }} · protocolo {{ " + caso + ".protocolo }}\n"
        "Tocá *Tomo el caso* y contactá al paciente, o *Falso positivo* si no hacía falta. Si nadie responde en "
        "15 minutos, se repite el aviso.")
    C.n8n("PUT", f"/workflows/{IDS['escalado_humano']}", {"name": w["name"], "nodes": w["nodes"], "connections": con,
                                                          "settings": {k: v for k, v in w["settings"].items() if k in S.SETTINGS_OK}})
    S.republicar(IDS["escalado_humano"])


def exportar():
    for clave, archivo in [("manager", "workflows/AgendaBot · Manager.json"), ("canal_telegram", "workflows/AgendaBot · Canal Telegram.json"),
                           ("errores", "workflows/AgendaBot · Errores.json"), ("escalado_humano", "workflows/AgendaBot · Escalado humano.json")]:
        x = C.n8n("GET", f"/workflows/{IDS[clave]}")
        x = {k: x[k] for k in ("name", "nodes", "connections", "settings")}
        json.dump(x, open(os.path.join(MOD11, archivo), "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def main():
    canal()
    m = manager()
    errores()
    escalado(m)
    exportar()
    print("Alertas: identidad del paciente, memoria y errores en castellano; publicado")


if __name__ == "__main__":
    main()
