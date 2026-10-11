# -*- coding: utf-8 -*-
"""Agrega la capa de voz (Telegram + Whisper + ElevenLabs) al Manager M6.

Entrada:  Telegram Trigger -> ¿nota de voz? -> Descargar audio -> Whisper (es)
          -> ¿transcripción vacía? -> Entrada Telegram -> Normalizar entrada (como el chat y el email)
Salida:   Responder al chat -> ¿vino por Telegram? -> Preparar respuesta hablada (<=200 car.)
          -> ¿voz o texto? -> ElevenLabs (Multilingual v2) -> Telegram sendAudio -> Descartar audio
Además:   regla de 200 caracteres en el System Prompt del Agente RAG, nota de compliance en el lienzo
          y settings que no guardan las ejecuciones (los binarios de voz se borran al terminar).

Es idempotente: si los nodos de voz ya existen, los reemplaza.
Uso:  python agregar_voz.py            # aplica en n8n (lee la API key de Modulo5/scripts/.env)
      python agregar_voz.py --dry-run  # solo muestra qué haría
"""
import json, os, subprocess, sys, uuid
sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "Modulo5", "scripts"))
import _config as C  # noqa: E402

IDS = json.load(open(os.path.join(HERE, "..", "_ids_m6.json")))
MANAGER = IDS["manager"]
DRY = "--dry-run" in sys.argv
KEEP_EXECUTIONS = "--keep-executions" in sys.argv  # para depurar: guarda las ejecuciones
VOICE_ID = next((a.split("=", 1)[1] for a in sys.argv if a.startswith("--voice=")), "EXAVITQu4vr4xnSDxMaL")

VOICE_NODES = [
    "Mensaje de Telegram", "¿Nota de voz?", "Descargar nota de voz", "Transcribir (Whisper)",
    "¿Audio vacío o ilegible?", "Avisar: no se escuchó", "Entrada Telegram", "¿Vino por Telegram?",
    "Preparar respuesta hablada", "¿Responder con voz?", "Sintetizar voz (ElevenLabs)",
    "Enviar nota de voz (Telegram)", "Enviar texto (Telegram)", "Descartar audio (compliance)",
    "Nota: Compliance de voz", "Nota: Capa de voz", "Respuesta (chat / email)",
    "Filtrar repetidos", "Evaluar transcripción", "¿Dictó un email?", "Pedir email por escrito",
]

FILTRAR_JS = r"""// Telegram reintenta la entrega si el webhook tarda en responder: el mismo update llega varias veces.
// Se procesa cada update_id una sola vez (memoria del workflow; persiste con el workflow publicado).
const s = $getWorkflowStaticData('global');
s.vistos = s.vistos || [];
const id = $json.update_id;
if (s.vistos.includes(id)) return [];
s.vistos.push(id);
s.vistos = s.vistos.slice(-200);
return [$input.first()];"""

EVALUAR_JS = r"""// Contingencia de audio: Whisper no devuelve vacío ante silencio o ruido, ALUCINA frases de subtítulos
// (p. ej. "Subtítulos realizados por la comunidad de Amara.org"). Se marca como ilegible:
// texto vacío o < 3 letras, solo signos, o una frase alucinada conocida.
const texto = String($json.text || '').trim();
const letras = texto.replace(/[^\p{L}\p{N}]/gu, '');
const ALUCINACIONES = [
  /amara\.org/i, /subt[ií]tulos (realizados|hechos|por)/i, /gracias por ver/i, /suscr[ií]bete/i,
  /^\W*(m[uú]sica|aplausos|risas|silencio)\W*$/i, /^\W*gracias\.?\W*$/i, /www\.\S+/i
];
const alucinada = ALUCINACIONES.some(r => r.test(texto));
const ilegible = letras.length < 3 || alucinada;
// Un email dictado por voz se transcribe mal ("mwhisbord arroba gmail punto com"): se pide por escrito.
const dicta_email = !ilegible && (/\barroba\b/i.test(texto) || /@/.test(texto) || /punto\s*com\b/i.test(texto));
return [{ json: { ...$json, text: texto, ilegible, motivo_ilegible: ilegible ? (alucinada ? 'alucinación de Whisper' : 'audio vacío') : '', dicta_email } }];"""

RESPONDER_JS = r"""function grab(node,path){ try{ let o=$(node).first().json; for(const k of path.split('.')){ o=o[k]; } return o||''; }catch(e){ return ''; } }
let m = grab('Aplicar validación','output')
     || grab('Confirmacion (Worker 2)','data.mensaje')
     || grab('Aviso (no se puede)','data.mensaje')
     || grab('Consultar turno (Worker 3)','data.mensaje')
     || grab('Consultar turno (Worker 3)','mensaje');
// Sin respuesta de ninguna rama: FUERA_DE_ALCANCE (sale por el Fallback del Switch) o un caso no previsto.
// Antes caía en un "Listo." genérico.
if (!m) {
  const intent = grab('Contrato de datos','intent');
  m = intent === 'FUERA_DE_ALCANCE'
    ? 'Solo puedo ayudarte con turnos e información de la Clínica LoDeTincho. Esa consulta no la puedo responder.'
    : 'No pude procesar tu pedido. ¿Me lo repetís con otras palabras?';
}
return [{ json: { output: m } }];"""

REGLA_ROUTER = """

CANAL DE VOZ (Telegram) — CONTENCIÓN FINANCIERA: canal actual = {{ $('Normalizar entrada').first().json.canal }}. Si el canal es "telegram_voz", toda respuesta escrita que se le devuelva al paciente se convierte en audio con ElevenLabs (cobra por carácter): debe tener como MÁXIMO 200 CARACTERES, sin URLs, emojis ni listas. Si en un pedido por voz falta el email, no lo infieras del audio: el sistema se lo pide por escrito."""


def credenciales():
    """id/nombre de las credenciales por tipo (sin secretos: export sin --decrypted)."""
    out = subprocess.run(["docker", "exec", "n8n", "n8n", "export:credentials", "--all"],
                         capture_output=True, text=True, encoding="utf-8").stdout
    i = out.find("[")
    data = json.loads(out[i:]) if i >= 0 else []
    por_tipo = {}
    for c in data:
        por_tipo.setdefault(c["type"], []).append({"id": c["id"], "name": c["name"]})
    return por_tipo


def cred(por_tipo, tipo):
    lst = por_tipo.get(tipo) or []
    return {tipo: lst[0]} if lst else None


def nodo(name, type_, version, pos, params, creds=None, **extra):
    n = {"id": str(uuid.uuid4()), "name": name, "type": type_, "typeVersion": version,
         "position": pos, "parameters": params}
    if creds:
        n["credentials"] = creds
    n.update(extra)
    return n


def if_node(name, pos, left, op_type, operation, right=None, single=False):
    cond = {"id": str(uuid.uuid4()), "leftValue": left,
            "operator": {"type": op_type, "operation": operation}}
    if single:
        cond["operator"]["singleValue"] = True
    else:
        cond["rightValue"] = right
    return nodo(name, "n8n-nodes-base.if", 2, pos, {
        "conditions": {"options": {"caseSensitive": True, "leftValue": "", "typeValidation": "loose", "version": 1},
                       "conditions": [cond], "combinator": "and"},
        "options": {}})


NORMALIZAR_JS = r"""const j=$input.first().json||{};
// Telegram (voz o texto): llega ya preparado por "Entrada Telegram"
if (String(j.canal||'').startsWith('telegram')) {
  return [{ json: { sessionId: j.sessionId, mensaje: j.mensaje, email_entrada: '', nombre_remitente: j.nombre_remitente||'', canal: j.canal, tg_chat_id: j.tg_chat_id } }];
}
const isEmail=(j.From!==undefined)||(j.BodyText!==undefined);
const rawFrom=String(j.From||"");
const m=rawFrom.match(/[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}/);
const email=m?m[0]:"";
let disp = rawFrom.includes("<") ? rawFrom.split("<")[0] : "";
disp = disp.replace(/["']/g,"").trim();
if(disp.includes("@")) disp="";
const sessionId=isEmail ? (email||rawFrom.replace(/["']/g,"")) : String(j.sessionId||"");
const mensaje=j.chatInput||j.BodyText||j.Subject||"";
const email_entrada=isEmail?email:"";
const nombre_remitente=isEmail?disp:"";
const canal=isEmail?"email":"chat";
return [{ json: { sessionId, mensaje, email_entrada, nombre_remitente, canal } }];"""

ENTRADA_TG_JS = r"""// Une las dos ramas de Telegram (voz transcrita o texto) en el formato del Manager.
const t = $('Mensaje de Telegram').first().json.message || {};
const esVoz = !!(t.voice || t.audio);
const texto = esVoz ? String($json.text || '').trim() : String(t.text || '').trim();
return [{ json: {
  canal: esVoz ? 'telegram_voz' : 'telegram_texto',
  sessionId: 'tg-' + t.chat.id,
  tg_chat_id: t.chat.id,
  mensaje: texto,
  nombre_remitente: [t.from?.first_name, t.from?.last_name].filter(Boolean).join(' ')
} }];"""

HABLADA_JS = r"""// Respuesta para el canal de voz: sin citas, links, emojis ni markdown, y como máximo 200 caracteres
// (ElevenLabs cobra por carácter; la regla también está en el System Prompt del Agente RAG).
const MAX = 200;
const original = String($json.output || '');
let t = original
  .replace(/\[Fuente:[^\]]*\]/gi, '')          // citas de fuente (quedan en el texto, no en el audio)
  .replace(/https?:\/\/\S+/g, '')              // URLs
  .replace(/[*_`#>]/g, '')                     // markdown
  .replace(/^\s*[-•]\s+/gm, '')                // viñetas
  .replace(/[\u{1F300}-\u{1FAFF}\u{2600}-\u{27BF}\u{FE0F}]/gu, '') // emojis
  .split(/\s*\n+\s*/).map(s => s.trim()).filter(Boolean)
  // cada línea se une como frase: si no termina en signo, se le agrega un punto ("atienden:" -> "atienden:")
  .map(s => /[.?!:;,]$/.test(s) ? s : s + '.').join(' ')
  .replace(/\s{2,}/g, ' ').trim();
if (t.length > MAX) {
  // cortar en el último fin de oración (. ? !) que entre en 200; si no hay, en la última palabra
  const corte = t.slice(0, MAX + 1);
  // fines de oración reales: no cuentan las abreviaturas (Dr., Dra., Sr., Sra., Lic., etc.)
  let fin = -1;
  for (const m of corte.matchAll(/[.?!](?=\s|$)/g)) {
    const previa = corte.slice(0, m.index).split(/\s/).pop();
    if (m[0] === '.' && /^(Dr|Dra|Sr|Sra|Lic|Dres|Av|Nro|Ing)$/i.test(previa)) continue;
    fin = m.index;
  }
  t = (fin > 60 ? corte.slice(0, fin + 1) : corte.slice(0, corte.lastIndexOf(' ')) + '…').trim();
}
const n = $('Normalizar entrada').first().json;
return [{ json: { texto_voz: t, caracteres: t.length, texto_completo: original, canal: n.canal, tg_chat_id: n.tg_chat_id } }];"""

DESCARTAR_JS = r"""// Compliance: el audio del paciente y el sintetizado no se conservan.
// Se devuelve solo metadata (sin binario); además el workflow no guarda ejecuciones,
// así que n8n borra los archivos temporales de la ejecución al terminar.
return $input.all().map(i => ({ json: { enviado: true, chat_id: i.json.result?.chat?.id ?? null, audio_destruido: true } }));"""

REGLA_PROMPT = """

## 4. Canal de voz (Telegram) — CONTENCIÓN FINANCIERA
Canal de esta conversación: {{ $('Normalizar entrada').first().json.canal }}.
Si el canal es "telegram_voz", tu respuesta se convierte en audio con ElevenLabs, que cobra por carácter. En ese caso:
- LIMITÁ IMPERATIVAMENTE tu respuesta a un MÁXIMO DE 200 CARACTERES (contando espacios y signos).
- Frases cortas (sujeto + verbo + predicado) y puntos seguidos para marcar pausas.
- PROHIBIDO incluir URLs, viñetas, emojis, markdown o listas largas. Si el dato es una lista larga, nombrá los 2 o 3 primeros y ofrecé enviar el resto por escrito.
- Las citas [Fuente: ...] van igual al final: el sistema las saca del audio antes de sintetizar."""


def main():
    por_tipo = credenciales()
    c_tg = cred(por_tipo, "telegramApi")
    c_oa = cred(por_tipo, "openAiApi")
    c_el = cred(por_tipo, "elevenLabsApi")
    print("Credenciales:", {k: (v and list(v.values())[0]["name"]) for k, v in
                            {"telegram": c_tg, "openai": c_oa, "elevenlabs": c_el}.items()})

    w = C.n8n("GET", f"/workflows/{MANAGER}")
    # Respetar lo que se haya elegido a mano en n8n (voz de ElevenLabs y credenciales de los nodos de voz)
    previos = {n["name"]: n for n in w["nodes"] if n["name"] in VOICE_NODES}
    voz_previa = previos.get("Sintetizar voz (ElevenLabs)", {}).get("parameters", {}).get("voice")
    if voz_previa and voz_previa.get("value") and not any(a.startswith("--voice=") for a in sys.argv):
        global VOICE_ID
        VOICE_ID = voz_previa["value"]
    print("Voz ElevenLabs:", VOICE_ID)
    nodes = [n for n in w["nodes"] if n["name"] not in VOICE_NODES]
    conns = {k: v for k, v in w["connections"].items() if k not in VOICE_NODES}
    for src in conns.values():  # quitar conexiones hacia nodos de voz viejos
        for kind, outs in src.items():
            src[kind] = [[t for t in (o or []) if t["node"] not in VOICE_NODES] for o in outs]
    by = {n["name"]: n for n in nodes}

    by["Normalizar entrada"]["parameters"]["jsCode"] = NORMALIZAR_JS
    by["Responder al chat"]["parameters"]["jsCode"] = RESPONDER_JS
    rag = by["Agente RAG (Consultas)"]["parameters"]["options"]
    sm = rag["systemMessage"].split("\n\n## 4. Canal de voz")[0]
    rag["systemMessage"] = sm + REGLA_PROMPT
    rt = by["Router (AI Agent)"]["parameters"]["options"]
    rt["systemMessage"] = rt["systemMessage"].split("\n\nCANAL DE VOZ (Telegram)")[0] + REGLA_ROUTER
    # Heredado del M5: el System Message del Router no era expresión (sin "="), así que los {{ }}
    # (memoria de Airtable y ahora el canal) llegaban literales al modelo.
    if not rt["systemMessage"].startswith("="):
        rt["systemMessage"] = "=" + rt["systemMessage"]
    # cachedResultUrl de los sub-workflows: que apunten a los ids M6
    for n in nodes:
        wf = n["parameters"].get("workflowId")
        if isinstance(wf, dict) and wf.get("value"):
            wf["cachedResultUrl"] = f"/workflow/{wf['value']}"

    x0, y0 = -2400, 1500   # entrada de voz (abajo a la izquierda del Manager)
    xs, ys = 2700, 1250    # salida de voz (a la derecha de "Responder al chat")
    file_id = "={{ $json.message.voice ? $json.message.voice.file_id : $json.message.audio.file_id }}"
    nuevos = [
        nodo("Mensaje de Telegram", "n8n-nodes-base.telegramTrigger", 1.2, [x0, y0],
             {"updates": ["message"], "additionalFields": {}}, c_tg, webhookId=str(uuid.uuid4())),
        nodo("Filtrar repetidos", "n8n-nodes-base.code", 2, [x0 + 200, y0], {"jsCode": FILTRAR_JS}),
        if_node("¿Nota de voz?", [x0 + 400, y0],
                "={{ $json.message.voice || $json.message.audio ? 'si' : 'no' }}", "string", "equals", "si"),
        nodo("Descargar nota de voz", "n8n-nodes-base.telegram", 1.2, [x0 + 600, y0 - 100],
             {"resource": "file", "fileId": file_id, "additionalFields": {}}, c_tg),
        nodo("Transcribir (Whisper)", "@n8n/n8n-nodes-langchain.openAi", 2.3, [x0 + 800, y0 - 100],
             {"resource": "audio", "operation": "transcribe", "binaryPropertyName": "data",
              "options": {"language": "es", "temperature": 0}}, c_oa),
        nodo("Evaluar transcripción", "n8n-nodes-base.code", 2, [x0 + 1000, y0 - 100], {"jsCode": EVALUAR_JS}),
        if_node("¿Audio vacío o ilegible?", [x0 + 1200, y0 - 100],
                "={{ $json.ilegible }}", "boolean", "true", single=True),
        nodo("Avisar: no se escuchó", "n8n-nodes-base.telegram", 1.2, [x0 + 1420, y0 - 300],
             {"chatId": "={{ $('Mensaje de Telegram').first().json.message.chat.id }}",
              "text": "Perdón, no logré escuchar tu audio con claridad. ¿Podés grabarlo de nuevo en un lugar con menos ruido, o escribirme tu consulta?",
              "additionalFields": {"appendAttribution": False}}, c_tg),
        if_node("¿Dictó un email?", [x0 + 1420, y0 - 60],
                "={{ $json.dicta_email }}", "boolean", "true", single=True),
        nodo("Pedir email por escrito", "n8n-nodes-base.telegram", 1.2, [x0 + 1640, y0 - 200],
             {"chatId": "={{ $('Mensaje de Telegram').first().json.message.chat.id }}",
              "text": "Para no anotar mal tu email, ¿me lo escribís por texto? Por audio se confunden letras.",
              "additionalFields": {"appendAttribution": False}}, c_tg),
        nodo("Entrada Telegram", "n8n-nodes-base.code", 2, [x0 + 1640, y0 + 60],
             {"jsCode": ENTRADA_TG_JS}),
        if_node("¿Vino por Telegram?", [xs, ys],
                "={{ $('Normalizar entrada').first().json.canal }}", "string", "startsWith", "telegram"),
        # El Chat Trigger responde con el último nodo ejecutado: la rama "no Telegram" termina acá con el output.
        nodo("Respuesta (chat / email)", "n8n-nodes-base.noOp", 1, [xs + 220, ys + 160], {}),
        nodo("Preparar respuesta hablada", "n8n-nodes-base.code", 2, [xs + 220, ys - 100],
             {"jsCode": HABLADA_JS}),
        if_node("¿Responder con voz?", [xs + 440, ys - 100],
                "={{ $json.canal }}", "string", "equals", "telegram_voz"),
        nodo("Sintetizar voz (ElevenLabs)", "@elevenlabs/n8n-nodes-elevenlabs.elevenLabs", 1, [xs + 660, ys - 200],
             {"resource": "speech", "operation": "textToSpeech",
              # Voz prediseñada de ElevenLabs (multilingüe). Se puede cambiar desde la lista del nodo.
              "voice": {"__rl": True, "mode": "id", "value": VOICE_ID},
              "text": "={{ $json.texto_voz }}",
              "additionalOptions": {
                  "model": {"__rl": True, "mode": "list", "value": "eleven_multilingual_v2"},
                  "outputFormat": "mp3_44100_128", "languageCode": "es",
                  "voiceSettings": json.dumps({"stability": 0.55, "similarity_boost": 0.75, "style": 0,
                                               "use_speaker_boost": True, "speed": 1}, indent=2)}},
             c_el),
        nodo("Enviar nota de voz (Telegram)", "n8n-nodes-base.telegram", 1.2, [xs + 880, ys - 200],
             {"operation": "sendAudio", "chatId": "={{ $('Preparar respuesta hablada').first().json.tg_chat_id }}",
              "binaryData": True, "binaryPropertyName": "data",
              "additionalFields": {"title": "AgendaBot", "fileName": "respuesta.mp3"}}, c_tg),
        nodo("Descartar audio (compliance)", "n8n-nodes-base.code", 2, [xs + 1100, ys - 200],
             {"jsCode": DESCARTAR_JS}),
        nodo("Enviar texto (Telegram)", "n8n-nodes-base.telegram", 1.2, [xs + 660, ys + 20],
             {"chatId": "={{ $json.tg_chat_id }}", "text": "={{ $json.texto_completo }}",
              "additionalFields": {"appendAttribution": False}}, c_tg),
        nodo("Nota: Capa de voz", "n8n-nodes-base.stickyNote", 1, [x0 - 60, y0 - 520],
             {"width": 1960, "height": 760, "color": 4, "content": "## Capa de voz (M6) — entrada"}),
        nodo("Nota: Compliance de voz", "n8n-nodes-base.stickyNote", 1, [xs - 80, ys - 460],
             {"width": 1460, "height": 820, "color": 3, "content": "## Compliance: audios en memoria volátil"}),
    ]
    # n8n valida el workflow entero antes de ejecutar: un nodo sin credencial frena también al chat.
    # Mientras falte una credencial, sus nodos quedan desactivados (se reactivan al volver a correr el script).
    falta = {"telegramApi": not c_tg, "openAiApi": not c_oa, "elevenLabsApi": not c_el}
    tipo_cred = {"n8n-nodes-base.telegramTrigger": "telegramApi", "n8n-nodes-base.telegram": "telegramApi",
                 "@n8n/n8n-nodes-langchain.openAi": "openAiApi",
                 "@elevenlabs/n8n-nodes-elevenlabs.elevenLabs": "elevenLabsApi"}
    for n in nuevos:
        if falta.get(tipo_cred.get(n["type"], ""), False):
            n["disabled"] = True
    if any(falta.values()):
        print("Nodos desactivados por falta de credencial:", [n["name"] for n in nuevos if n.get("disabled")])
    nodes += nuevos

    def link(a, b, out=0):
        conns.setdefault(a, {}).setdefault("main", [])
        m = conns[a]["main"]
        while len(m) <= out:
            m.append([])
        m[out].append({"node": b, "type": "main", "index": 0})

    link("Mensaje de Telegram", "Filtrar repetidos")
    link("Filtrar repetidos", "¿Nota de voz?")
    link("¿Nota de voz?", "Descargar nota de voz", 0)
    link("¿Nota de voz?", "Entrada Telegram", 1)
    link("Descargar nota de voz", "Transcribir (Whisper)")
    link("Transcribir (Whisper)", "Evaluar transcripción")
    link("Evaluar transcripción", "¿Audio vacío o ilegible?")
    link("¿Audio vacío o ilegible?", "Avisar: no se escuchó", 0)
    link("¿Audio vacío o ilegible?", "¿Dictó un email?", 1)
    link("¿Dictó un email?", "Pedir email por escrito", 0)
    link("¿Dictó un email?", "Entrada Telegram", 1)
    link("Entrada Telegram", "Normalizar entrada")
    link("Responder al chat", "¿Vino por Telegram?")
    link("¿Vino por Telegram?", "Preparar respuesta hablada", 0)
    link("¿Vino por Telegram?", "Respuesta (chat / email)", 1)
    link("Preparar respuesta hablada", "¿Responder con voz?")
    link("¿Responder con voz?", "Sintetizar voz (ElevenLabs)", 0)
    link("¿Responder con voz?", "Enviar texto (Telegram)", 1)
    link("Sintetizar voz (ElevenLabs)", "Enviar nota de voz (Telegram)")
    link("Enviar nota de voz (Telegram)", "Descartar audio (compliance)")

    settings = {"executionOrder": "v1"}
    if not KEEP_EXECUTIONS:
        settings.update({"saveDataSuccessExecution": "none", "saveDataErrorExecution": "none",
                         "saveManualExecutions": False, "saveExecutionProgress": False})
    body = {"name": w["name"], "nodes": nodes, "connections": conns, "settings": settings}
    if DRY:
        print(f"[dry-run] nodos: {len(w['nodes'])} -> {len(nodes)}; settings: {settings}")
        return
    r = C.n8n("PUT", f"/workflows/{MANAGER}", body)
    print(f"OK: {r['name']} — {len(r['nodes'])} nodos; settings: {r.get('settings')}")


if __name__ == "__main__":
    main()
