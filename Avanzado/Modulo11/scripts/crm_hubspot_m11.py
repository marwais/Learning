# -*- coding: utf-8 -*-
"""Proyecto Final (M11) — el CRM como fuente de verdad: contacto en HubSpot con los metadatos de AgendaBot.

Bug heredado del M4: "Crear contacto (HubSpot)" y "Actualizar contacto (HubSpot)" tenían las operaciones
`create` y `update`, que el nodo HubSpot v2.1 no tiene (sus operaciones de contacto son upsert/search/get/
getAll/delete). n8n no daba error: devolvía un ítem vacío, así que el contacto NUNCA se escribía en el CRM.

Ahora los dos nodos hacen `upsert` (crear o actualizar por email; un reintento no duplica) con nombre y las
propiedades de trazabilidad que creó mantenimiento_m11.py (M10, Sección 4; slide de trazabilidad del profe):
origen = AgendaBot, código de seguimiento (traceId), canal, última interacción, turno gestionado,
resultado del Supervisor, aprobado por (Juez o persona) y versión del sistema.

Uso:  python crm_hubspot_m11.py      # idempotente
"""
import json, os, sys
sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
MOD11 = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "..", "..", "Modulo5", "scripts"))
sys.path.insert(0, HERE)
import _config as C  # noqa: E402
import seguridad_p2_m11 as S  # noqa: E402

VERSION = "AgendaBot 1.0 · juez-rubrica-v3.1"
ACC = "$('Recuperar acción aprobada')"


def propiedades():
    turno = ("={{ " + ACC + ".isExecuted ? (" + ACC + ".first().json.accion === 'crear' ? 'Alta' : 'Cambio') + ': ' + "
             + ACC + ".first().json.motivo + ' · ' + " + ACC + ".first().json.fecha + ' ' + " + ACC + ".first().json.hora : '' }}")
    veredicto = ("={{ " + ACC + ".isExecuted ? " + ACC + ".first().json.veredicto_juez + ' (exactitud ' + "
                 + ACC + ".first().json.exactitud_factual + '/5)' : '' }}")
    return [
        ("agendabot_origen", "AgendaBot"),
        ("agendabot_trace_id", "={{ $('Generar traceId').first().json.traceId }}"),
        ("agendabot_canal", "={{ $('Normalizar entrada').first().json.canal }}"),
        ("agendabot_ultima_interaccion", "={{ $now.toMillis() }}"),
        ("agendabot_turno", turno),
        ("agendabot_veredicto_juez", veredicto),
        ("agendabot_aprobado_por", "={{ " + ACC + ".isExecuted ? " + ACC + ".first().json.aprobado_por : '' }}"),
        ("agendabot_version", VERSION),
    ]


def main():
    w = C.n8n("GET", f"/workflows/{S.IDS['manager']}")
    N = {n["name"]: n for n in w["nodes"]}
    for k in ("Crear contacto (HubSpot)", "Actualizar contacto (HubSpot)"):
        N[k]["parameters"] = {
            "authentication": "appToken", "resource": "contact", "operation": "upsert",
            "email": "={{ $('Validar contacto (Set)').first().json.email }}",
            "additionalFields": {
                "firstName": "={{ $('Validar contacto (Set)').first().json.firstname }}",
                "customPropertiesUi": {"customPropertiesValues": [{"property": p, "value": v} for p, v in propiedades()]},
            },
        }
        N[k].update(S.RETRY)
    C.n8n("PUT", f"/workflows/{S.IDS['manager']}", {"name": w["name"], "nodes": w["nodes"], "connections": w["connections"],
                                                    "settings": {k: v for k, v in w["settings"].items() if k in S.SETTINGS_OK}})
    S.republicar(S.IDS["manager"])
    x = C.n8n("GET", f"/workflows/{S.IDS['manager']}")
    x = {k: x[k] for k in ("name", "nodes", "connections", "settings")}
    json.dump(x, open(os.path.join(MOD11, "AI Automation Avanzado - M11.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("HubSpot: contacto con upsert + metadatos de AgendaBot; Manager publicado")


if __name__ == "__main__":
    main()
