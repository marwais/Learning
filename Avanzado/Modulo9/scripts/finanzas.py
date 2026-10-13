# -*- coding: utf-8 -*-
"""Modelo financiero del Módulo 9: KPIs de negocio, ROI contra el baseline manual y TCO mensual.

Toma como dato medido:
  - el coste por ejecución del M8 (A/B: agente + Juez) y el del Router medido en las pruebas del M9,
  - el ahorro de Prompt Caching medido con la API (../finops_cache.json).
Todo lo demás son SUPUESTOS explícitos (volumen, mezcla, tipo de cambio, planes de terceros), en SUPUESTOS.

Uso:  python finanzas.py   -> ../finanzas.json (lo leen las piezas del PDF)
"""
import json, os, sys
sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = json.load(open(os.path.join(HERE, "..", "finops_cache.json"), encoding="utf-8"))

SUPUESTOS = {
    "dias_habiles_mes": 22,
    "valor_hora_admin": 10_000,           # $ por hora (mismo supuesto del M7)
    "valor_hora_tecnico": 20_000,         # $ por hora de mantenimiento del flujo
    "horas_mantenimiento_mes": 8,
    "tipo_cambio": 1_400,                 # $ por US$ (supuesto de referencia, a actualizar)
    "mensajes_por_gestion": 2,            # el paciente suele mandar 2 mensajes (pedido + dato que faltaba)
    "tasa_reintento_juez": 0.15,          # INFO que pasan por CORREGIR una vez
    "porcentaje_voz": 0.10,               # mensajes que llegan como nota de voz
    "min_por_audio": 0.5,
    "setup_horas": 80,                    # horas de implementación (una vez)
}

# Baseline manual del M7 (Pieza 1): tarea -> (volumen diario, minutos por gestión, % autónomo esperado)
TAREAS = [
    ("Sacar un turno nuevo", 70, 4.0, 0.80),
    ("Modificar o cancelar un turno", 38, 3.0, 0.70),
    ("Consulta informativa (RAG)", 72, 2.5, 0.70),   # 70 %: medido en QA_Veredictos (ACEPTADO sin humano)
    ("Confirmación o recordatorio", 70, 1.0, 1.00),
]

# US$ por ejecución, MEDIDOS
ROUTER = (1_216 * 3 + 74 * 15) / 1e6                  # Sonnet 4.6, promedio de 4 ejecuciones M9
INFO_A = 0.0218                                       # agente Sonnet 4.6 + Juez (M8, A/B)
INFO_B = 0.0108                                       # agente Haiku 4.5 + Juez (M8, A/B)
AGENTE_A_INPUT = 0.0102                               # parte de entrada del agente A (70 % de 0,0146)
RESUMEN_SONNET, RESUMEN_HAIKU = 0.0090 / 6, 0.0030 / 6  # 1 resumen cada 6 mensajes
WHISPER_MIN = 0.006


def ahorro_cache_loop():
    """Ahorro del caché automático dentro del loop del agente (llamada 1 escribe, llamada 2 lee).
    Prompts medidos en la ejecución 473: llamada 1 = 2.965 tokens, llamada 2 = 4.260 tokens."""
    p1, p2 = 2_965, 4_260
    sin = p1 + p2
    con = p1 * 1.25 + p1 * 0.10 + (p2 - p1) * 1.25
    return 1 - con / sin


def main():
    s = SUPUESTOS
    d = s["dias_habiles_mes"]
    # --- ROI: horas evitadas por tarea
    filas_roi, horas_tot = [], 0
    for t, vol, mins, aut in TAREAS:
        horas_base = vol * d * mins / 60
        horas_evit = horas_base * aut
        horas_tot += horas_evit
        filas_roi.append({"tarea": t, "volumen_mes": vol * d, "min": mins, "horas_base": round(horas_base, 1),
                          "autonomia": aut, "horas_evitadas": round(horas_evit, 1),
                          "ahorro": round(horas_evit * s["valor_hora_admin"])})
    beneficio = horas_tot * s["valor_hora_admin"]

    # --- Volumen de ejecuciones del Manager
    info_mes = 72 * d
    gestion_mes = (70 + 38) * d * s["mensajes_por_gestion"]
    ejec_mes = info_mes + gestion_mes

    cache = ahorro_cache_loop()
    escenarios = {}
    for nombre, info, resumen, cache_on in (
            ("Sin optimizar (M8)", INFO_A, RESUMEN_SONNET, False),
            ("M9 actual: Sonnet + caché + resumen Haiku", INFO_A - AGENTE_A_INPUT * cache, RESUMEN_HAIKU, True),
            ("Recomendado: agente Haiku 4.5", INFO_B, RESUMEN_HAIKU, False)):
        coste_info = info_mes * (ROUTER + info * (1 + s["tasa_reintento_juez"]))
        coste_gest = gestion_mes * ROUTER
        coste_res = ejec_mes * resumen
        escenarios[nombre] = {"info": round(coste_info, 2), "gestion": round(coste_gest, 2),
                              "resumen": round(coste_res, 2), "total": round(coste_info + coste_gest + coste_res, 2),
                              "por_ejecucion": round((coste_info + coste_gest + coste_res) / ejec_mes, 5)}

    # Tres escenarios de una consulta INFO (U2: optimista / realista / fat loop)
    por_consulta = {"Optimista (1 intento, sin herramienta extra)": round(ROUTER + INFO_A * 0.8, 4),
                    "Realista (1 intento + Juez)": round(ROUTER + INFO_A, 4),
                    "Fat loop (3 intentos: tope de 2 reintentos)": round(ROUTER + INFO_A * 3, 4)}

    # --- TCO mensual (US$ salvo indicación)
    voz = ejec_mes * s["porcentaje_voz"]
    tok = escenarios["M9 actual: Sonnet + caché + resumen Haiku"]["total"]
    tco_usd = [
        ("Tokens Claude (Router, Agente RAG, Juez, resumen)", tok, "medido M8/M9 × volumen"),
        ("Whisper (transcripción de notas de voz)", round(voz * s["min_por_audio"] * WHISPER_MIN, 2), "supuesto 10 % voz"),
        ("ElevenLabs (respuesta por voz, plan Creator)", 22.0, "supuesto: respuestas ≤ 200 caracteres"),
        ("Embeddings Cohere (búsquedas RAG)", 0.10, "~2 búsquedas × 20 tokens por consulta"),
        ("Qdrant Cloud (195 fragmentos)", 0.0, "plan gratuito 1 GB"),
        ("n8n self-hosted (VPS 2 vCPU / 4 GB)", 24.0, "supuesto"),
        ("Airtable Team (1 editor)", 20.0, "supuesto; hoy plan gratuito"),
        ("Gmail, Sheets, Slack, HubSpot CRM, Telegram", 0.0, "planes ya existentes o gratuitos"),
    ]
    total_usd = sum(x[1] for x in tco_usd)
    mant = s["horas_mantenimiento_mes"] * s["valor_hora_tecnico"]
    tco_pesos = total_usd * s["tipo_cambio"] + mant
    neto = beneficio - tco_pesos
    setup = s["setup_horas"] * s["valor_hora_tecnico"]

    # Picos: duplicar la demanda un día
    pico_extra = 250 * (ROUTER + INFO_A * 0.3)          # 250 gestiones extra, ~30 % INFO

    out = {"supuestos": s, "roi": filas_roi, "horas_evitadas": round(horas_tot, 1), "beneficio": round(beneficio),
           "ejecuciones_mes": ejec_mes, "info_mes": info_mes, "gestion_mes": gestion_mes,
           "router": round(ROUTER, 5), "escenarios": escenarios, "por_consulta": por_consulta,
           "ahorro_cache_loop": round(cache, 3), "tco_usd": tco_usd, "tco_total_usd": round(total_usd, 2),
           "mantenimiento": mant, "tco_pesos": round(tco_pesos), "neto": round(neto),
           "roi_mensual": round(neto / tco_pesos, 2), "setup": setup, "payback_meses": round(setup / neto, 2),
           "pico_extra_usd": round(pico_extra, 2), "cache_api": CACHE}
    json.dump(out, open(os.path.join(HERE, "..", "finanzas.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps({k: v for k, v in out.items() if k not in ("cache_api", "roi", "tco_usd")}, ensure_ascii=False, indent=1))
    for r in filas_roi:
        print(r)
    for t in tco_usd:
        print(t)


if __name__ == "__main__":
    main()
