# -*- coding: utf-8 -*-
"""Proyecto Final (M11) — justificación financiera reproducible (DMSA, Sección 4).

Combina lo MEDIDO en las pruebas del M11 (costo por pedido de la corrida C de la batería, con los tokens que registra
n8n) con los volúmenes y supuestos del M9 (baseline manual). Todas las cifras se guardan sin redondear en
Modulo11/evaluacion/finanzas_m11.json (devolución de la P8: fórmulas y valores reproducibles; P9: separar medido
de proyectado).

Fórmulas:
  costo de una llamada (US$) = (tokens_entrada × precio_entrada + tokens_salida × precio_salida) / 1.000.000
  costo de un pedido         = suma de sus llamadas (Router + Agente/Workers + Juez), medido por pedido en la batería
  tokens por mes             = consultas × costo_consulta × (1 + reintentos del Juez) + gestiones × (acción + 1 mensaje
                               complementario) + resúmenes de memoria
  costo total de operación   = tokens + otros servicios (US$) × tipo de cambio + mantenimiento (pesos)
  beneficio                  = horas evitadas × valor de la hora administrativa
  retorno = (beneficio − costo total) / costo total · recupero = implementación / (beneficio − costo total)

Uso:  python finanzas_m11.py
"""
import json, os, sys
sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
MOD11 = os.path.abspath(os.path.join(HERE, ".."))
M9 = json.load(open(os.path.join(MOD11, "..", "Modulo9", "finanzas.json"), encoding="utf-8"))
BAT = json.load(open(os.path.join(MOD11, "evaluacion", "bateria_C.json"), encoding="utf-8"))
BAT_A = json.load(open(os.path.join(MOD11, "evaluacion", "bateria_A.json"), encoding="utf-8"))
S = M9["supuestos"]


def prom(d, cond):
    v = [r["costo_usd"] for r in d["resultados"] if "costo_usd" in r and cond(r)]
    return sum(v) / len(v), len(v)


def main():
    medido = {}
    for nombre, d in (("C (Router y Agente en Haiku 4.5, Juez en Sonnet 4.6)", BAT), ("A (todo Sonnet 4.6)", BAT_A)):
        info, n_info = prom(d, lambda r: r["esperado_ruta"].startswith("info"))
        accion, n_acc = prom(d, lambda r: r["esperado_ruta"].startswith("accion"))
        compl, n_c = prom(d, lambda r: r["esperado_ruta"] in ("faltan_datos", "consulta_turnos", "turno_existente"))
        medido[nombre] = {"consulta_informativa": info, "accion_con_juez": accion, "mensaje_complementario": compl,
                          "casos": {"info": n_info, "accion": n_acc, "complementario": n_c}}
    c = medido["C (Router y Agente en Haiku 4.5, Juez en Sonnet 4.6)"]
    consultas = M9["info_mes"]                                   # 1.584 consultas informativas por mes
    gestiones = sum(t["volumen_mes"] for t in M9["roi"][:2])    # 1.540 altas + 836 cambios o cancelaciones
    resumen = M9["escenarios"]["M9 actual: Sonnet + caché + resumen Haiku"]["resumen"]
    tok_info = consultas * c["consulta_informativa"] * (1 + S["tasa_reintento_juez"])
    tok_gestion = gestiones * (c["accion_con_juez"] + c["mensaje_complementario"])
    tokens = tok_info + tok_gestion + resumen
    otros = [(k, v, nota) for k, v, nota in M9["tco_usd"] if not k.startswith("Tokens")]
    otros.append(("Túnel público (ngrok, plan gratuito; en un VPS con dominio propio no hace falta)", 0.0, "medido M11"))
    tco_usd = tokens + sum(v for _, v, _ in otros)
    tc = S["tipo_cambio"]
    mant = M9["mantenimiento"]
    tco_pesos = tco_usd * tc + mant
    escenarios = {}
    for nombre, autonomia_factor in (("Conservador (60 % de autonomía)", 0.60 / 0.78), ("Base (78 %)", 1.0),
                                     ("Optimista (90 %)", 0.90 / 0.78)):
        beneficio = M9["beneficio"] * autonomia_factor
        neto = beneficio - tco_pesos
        escenarios[nombre] = {"horas_evitadas": M9["horas_evitadas"] * autonomia_factor, "beneficio": beneficio,
                              "costo_total": tco_pesos, "neto": neto, "retorno": neto / tco_pesos,
                              "recupero_meses": M9["setup"] / neto}
    out = {
        "medido_en_pruebas": medido,
        "volumenes_proyectados": {"consultas_informativas_mes": consultas, "gestiones_mes": gestiones,
                                  "reintentos_juez": S["tasa_reintento_juez"]},
        "tokens_mes_usd": {"consultas": tok_info, "gestiones": tok_gestion, "resumenes": resumen, "total": tokens,
                           "M9_sin_juez_de_acciones": M9["escenarios"]["M9 actual: Sonnet + caché + resumen Haiku"]["total"]},
        "otros_servicios_usd": otros, "costo_total_usd_mes": tco_usd, "tipo_cambio": tc, "mantenimiento_pesos": mant,
        "costo_total_pesos_mes": tco_pesos, "baseline": M9["roi"], "escenarios": escenarios,
        "implementacion_pesos": M9["setup"], "costo_por_1000_consultas_usd": c["consulta_informativa"] * 1000,
        "costo_por_1000_acciones_usd": c["accion_con_juez"] * 1000,
    }
    json.dump(out, open(os.path.join(MOD11, "evaluacion", "finanzas_m11.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print("Medido (C):", {k: round(v, 6) if isinstance(v, float) else v for k, v in c.items()})
    print(f"Tokens/mes US$ {tokens:.4f} (consultas {tok_info:.4f} + gestiones {tok_gestion:.4f} + resúmenes {resumen}) "
          f"· M9 {out['tokens_mes_usd']['M9_sin_juez_de_acciones']}")
    print(f"Costo total US$ {tco_usd:.4f}/mes = $ {tco_usd * tc:,.2f} + mantenimiento $ {mant:,} = $ {tco_pesos:,.2f}")
    for k, v in escenarios.items():
        print(f"  {k}: beneficio $ {v['beneficio']:,.2f} · neto $ {v['neto']:,.2f} · retorno {v['retorno']:.4f} · "
              f"recupero {v['recupero_meses']:.4f} meses")


if __name__ == "__main__":
    main()
