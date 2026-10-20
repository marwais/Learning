# -*- coding: utf-8 -*-
"""Proyecto Final — Juez: el enmascarado del log no debe tocar el CUIT de la clínica.

Hallazgo (QA_Veredictos, 20/10/2026): la regla del DNI (\\b\\d{7,8}\\b) tomaba el bloque del medio del CUIT
"30-71234567-0" (el guion es límite de palabra) y el log quedaba "30-[DNI]-0". El CUIT de una empresa es dato
público; el CUIL de una persona contiene su DNI y sí es dato personal. Ahora, en "Armar log de auditoría":
  - CUIT de persona jurídica (prefijo 30, 33 o 34): se conserva tal cual (no pasa por ninguna regla);
  - CUIL/CUIT de persona humana (prefijo 20, 23, 24 o 27): [CUIL];
  - los códigos de turno (T-tg-…, T-wh-…) se conservan: la regla del teléfono los confundía;
  - el resto de las reglas (nombre, email, DNI, teléfono) sin cambios.

Uso:  python enmascarado_cuit_m11.py      # idempotente
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
VIEJO = """const enmascarar = s => nombres.reduce((t, nm) => t.replace(new RegExp(esc(nm), 'gi'), '[NOMBRE]'), String(s || ''))
  .replace(/\\b(soy|me llamo|mi nombre es)\\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(\\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)?/g, '$1 [NOMBRE]')
  .replace(/[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}/g, '[EMAIL]')
  .replace(/\\b\\d{1,2}\\.\\d{3}\\.\\d{3}\\b|\\b\\d{7,8}\\b/g, '[DNI]')
  .replace(/\\+?\\d[\\d\\s-]{8,}\\d/g, '[TEL]');"""
NUEVO = """// El CUIT de una empresa (30/33/34) es dato público: se separa y no pasa por las reglas.
// El CUIL/CUIT de una persona (20/23/24/27) contiene su DNI: se enmascara como [CUIL].
const reglas = s => nombres.reduce((t, nm) => t.replace(new RegExp(esc(nm), 'gi'), '[NOMBRE]'), s)
  .replace(/\\b(soy|me llamo|mi nombre es)\\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(\\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)?/g, '$1 [NOMBRE]')
  .replace(/[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}/g, '[EMAIL]')
  .replace(/\\b(20|23|24|27)-?\\d{8}-?\\d\\b/g, '[CUIL]')
  .replace(/\\b\\d{1,2}\\.\\d{3}\\.\\d{3}\\b|\\b\\d{7,8}\\b/g, '[DNI]')
  .replace(/\\+?\\d[\\d\\s-]{8,}\\d/g, '[TEL]');
const enmascarar = s => String(s || '').split(PROTEGIDOS)
  .map((parte, i) => i % 2 ? parte : reglas(parte)).join('');"""
# Lo que no es dato personal y no pasa por las reglas: CUIT de empresa y códigos de turno (T-tg-…, T-wh-…),
# que la regla del teléfono confundía.
PROTEGIDOS_VIEJO = "const enmascarar = s => String(s || '').split(/(\\b(?:30|33|34)-\\d{8}-\\d\\b)/)"
PROTEGIDOS = "const PROTEGIDOS = /(\\b(?:30|33|34)-\\d{8}-\\d\\b|\\bT-(?:tg|wh)-[\\w-]+)/;\n"
NUEVO = NUEVO.replace("const reglas", PROTEGIDOS + "const reglas", 1)


def main():
    w = C.n8n("GET", f"/workflows/{IDS['supervisor']}")
    n = next(x for x in w["nodes"] if x["name"] == "Armar log de auditoría")
    code = n["parameters"]["jsCode"]
    if "PROTEGIDOS" in code:
        print("Juez: ya aplicado")
        return
    if PROTEGIDOS_VIEJO in code:  # primera versión (solo CUIT): se agregan los códigos de turno
        code = code.replace(PROTEGIDOS_VIEJO, "const enmascarar = s => String(s || '').split(PROTEGIDOS)")
        code = code.replace("const reglas", PROTEGIDOS + "const reglas", 1)
    else:
        assert VIEJO in code, "el enmascarado no coincide con lo esperado"
        code = code.replace(VIEJO, NUEVO)
    n["parameters"]["jsCode"] = code
    C.n8n("PUT", f"/workflows/{IDS['supervisor']}", {"name": w["name"], "nodes": w["nodes"], "connections": w["connections"],
                                                     "settings": {k: v for k, v in w["settings"].items() if k in S.SETTINGS_OK}})
    S.republicar(IDS["supervisor"])
    x = C.n8n("GET", f"/workflows/{IDS['supervisor']}")
    x = {k: x[k] for k in ("name", "nodes", "connections", "settings")}
    json.dump(x, open(os.path.join(MOD11, "SUPERVISOR_Judge (M11).json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Juez: enmascarado con CUIT de empresa preservado y [CUIL] para personas, publicado")


if __name__ == "__main__":
    main()
