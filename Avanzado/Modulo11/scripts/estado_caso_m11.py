# -*- coding: utf-8 -*-
"""Proyecto Final — Estado del Caso en la memoria (Airtable) y filtro de correos propios / rebotes.

Hallazgos de la revisión de capturas (16/10/2026):
1. Memoria_Pacientes tiene el campo "Estado del Caso" (En Progreso / Pendiente / En Revisión / Cerrado), pero el
   Manager siempre escribía "En Progreso". Ahora "Actualizar contador" y "Guardar memoria (upsert)" lo calculan
   según cómo terminó el pedido:
     En Revisión  → la acción quedó congelada sin aprobación humana, o se derivó por incomprensión
     Pendiente    → faltan datos del paciente
     Cerrado      → resuelto (turno registrado/modificado, consulta respondida, turno existente, fuera de alcance)
2. El filtro anti auto-reply dejaba pasar el propio aviso "Clínica LoDeTincho — estamos con demoras" y los rebotes
   de mailer-daemon (avisos a direcciones de prueba inexistentes), que entraban como pacientes. Se agregan
   condiciones al mismo IF (sin código): remitente mailer-daemon/postmaster, asunto "Delivery Status Notification"
   / "Mail Delivery" y asuntos que EMPIEZAN con "Clínica LoDeTincho — " (los correos del propio sistema; una
   respuesta del paciente empieza con "Re:" y sí pasa).

Uso:  python estado_caso_m11.py      # idempotente
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
ESTADO = ("={{ (() => { const corrio = n => { try { return $(n).isExecuted } catch (e) { return false } }; "
          "if (corrio('Acción en revisión (aviso)') || corrio('Escalar por incomprensión (sub-workflow)')) return 'En Revisión'; "
          "if (corrio('Resolver accion') && $('Resolver accion').first().json.accion === 'faltan_datos') return 'Pendiente'; "
          "return 'Cerrado'; })() }}")
FILTROS = [("={{ $json.From }}", "contains", "mailer-daemon"), ("={{ $json.From }}", "contains", "postmaster@"),
           ("={{ $json.Subject }}", "contains", "Delivery Status Notification"),
           ("={{ $json.Subject }}", "contains", "Mail Delivery"),
           ("={{ $json.Subject }}", "startsWith", "Clínica LoDeTincho — ")]


def main():
    w = C.n8n("GET", f"/workflows/{IDS['manager']}")
    N = {n["name"]: n for n in w["nodes"]}
    cambios = 0
    for nm in ("Actualizar contador", "Guardar memoria (upsert)"):
        v = N[nm]["parameters"]["columns"]["value"]
        if v.get("Estado del Caso") != ESTADO:
            v["Estado del Caso"] = ESTADO
            cambios += 1
    conds = N["IF anti auto-reply"]["parameters"]["conditions"]["conditions"]
    ya = {(c["leftValue"], c["rightValue"]) for c in conds}
    for izq, op, val in FILTROS:
        if (izq, val) not in ya:
            conds.append({"id": str(uuid.uuid4()), "leftValue": izq, "rightValue": val,
                          "operator": {"type": "string", "operation": op}})
            cambios += 1
    # 3) La ruta INFO (consultas) terminaba sin actualizar la memoria (0 mensajes, siempre "En Progreso"). En serie,
    #    después de "Aplicar validación": upsert en Airtable y se retoma la respuesta para el resto de la cadena.
    if "Actualizar memoria (consulta)" not in N:
        ax, ay = N["Aplicar validación"]["position"]
        base = N["Actualizar contador"]
        mem = json.loads(json.dumps(base))
        mem.update({"id": str(uuid.uuid4()), "name": "Actualizar memoria (consulta)", "position": [ax + 60, ay + 200],
                    "onError": "continueRegularOutput"})
        mem.pop("webhookId", None)
        mem["parameters"]["columns"]["value"] = {
            "Session_ID": "={{ $('Preparar contexto').first().json.session_id }}",
            "Estado del Caso": "={{ String($('Aplicar validación').first().json.validacion || '').startsWith('ESCALADO') "
                               "? 'En Revisión' : 'Cerrado' }}",
            "Fecha de Actualización": "={{ $now.toISO() }}",
            "Mensajes": "={{ $('Preparar contexto').first().json.mensajes }}",
            "Ultimo_traceId": "={{ $('Generar traceId').first().json.traceId }}"}
        w["nodes"] += [mem, S.set_json("Retomar respuesta (consulta)", [ax + 180, ay + 200],
                                       "={{ JSON.stringify($('Aplicar validación').first().json) }}")]
        con = w["connections"]
        con["Aplicar validación"] = {"main": [[{"node": "Actualizar memoria (consulta)", "type": "main", "index": 0}]]}
        S.conectar(con, "Actualizar memoria (consulta)", "Retomar respuesta (consulta)", 0)
        S.conectar(con, "Retomar respuesta (consulta)", "¿Email? (INFO)", 0)
        cambios += 1
    if not cambios:
        print("Manager: ya aplicado")
        return
    C.n8n("PUT", f"/workflows/{IDS['manager']}", {"name": w["name"], "nodes": w["nodes"], "connections": w["connections"],
                                                  "settings": {k: v for k, v in w["settings"].items() if k in S.SETTINGS_OK}})
    S.republicar(IDS["manager"])
    x = C.n8n("GET", f"/workflows/{IDS['manager']}")
    x = {k: x[k] for k in ("name", "nodes", "connections", "settings")}
    json.dump(x, open(os.path.join(MOD11, "AI Automation Avanzado - M11.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(f"Manager: {cambios} cambios (Estado del Caso + filtro de correos), publicado")


if __name__ == "__main__":
    main()
