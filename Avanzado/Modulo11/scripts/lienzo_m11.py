# -*- coding: utf-8 -*-
"""Proyecto Final (M11) — lienzo legible del Manager (devolución de la P8: capturas con recortes cercanos y etiquetas
numeradas; DMSA Sección 2: capturas nítidas del lienzo).

Reubica los nodos del Manager en carriles de izquierda a derecha (sin tocar conexiones ni parámetros) y reemplaza las
notas viejas por 10 marcos numerados, uno por etapa del recorrido:
  1 Entrada · 2 Trazabilidad e idempotencia · 3 Seguridad (triaje y freno) · 4 Memoria y clasificación ·
  5 Gestión de turnos con Juez · 6 Consulta de turnos · 7 Consultas informativas con Juez · 8 Registro y memoria ·
  9 Respuesta y comprensión · 10 Despacho por el canal.
Cada nodo tiene una posición (columna, fila) en la grilla; si aparece un nodo nuevo sin posición, el script avisa.

Uso:  python lienzo_m11.py      # idempotente
"""
import json, os, sys, uuid
sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
MOD11 = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "..", "..", "Modulo5", "scripts"))
sys.path.insert(0, HERE)
import _config as C  # noqa: E402
import seguridad_p2_m11 as S  # noqa: E402

X0, Y0, CW, RH = -1800, 0, 240, 170

GRUPOS = [  # (número, título, color, descripción, {nodo: (columna, fila)})
    (1, "Entrada por canales", 7,
     "Llegan los pedidos: webhook (Receptor) y Telegram (Canal Telegram) por *Llamada de un canal*, email (con filtro "
     "de respuestas automáticas) y chat. Se normalizan a un formato común.",
     {"Llamada de un canal (Receptor / Telegram)": (0, 0), "Email entrante (Gmail Trigger)": (0, 1.5),
      "IF anti auto-reply": (1, 1.5), "Frenar auto-reply": (2, 0.9), "Limpiar payload (Set)": (2, 2.1),
      "When chat message received": (0, 3), "Normalizar entrada": (3, 1.5)}),
    (2, "Trazabilidad e idempotencia", 5,
     "Cada pedido recibe su `traceId` y una clave única. Si la clave ya está en la Data Table `pedidos_procesados_m11`, "
     "el pedido se descarta: no se procesa ni se responde dos veces.",
     {"Generar traceId": (4, 1.5), "Clave de idempotencia": (5, 1.5), "Buscar pedido procesado": (6, 1.5),
      "¿Pedido nuevo?": (7, 1.5), "Registrar pedido": (8, 1.5), "Pedido repetido (descartado)": (8, 2.7),
      "Pedido validado": (9, 1.5)}),
    (3, "Seguridad: triaje y freno de mano", 3,
     "Antes de la IA. El Switch busca señales rojas (protocolo `triaje-v1`): urgencia, dinero, reclamo legal, historia "
     "clínica. Si hay, responde con un texto fijo y escala a una persona. Con el freno de mano activo, todo va a "
     "atención humana.",
     {"Triaje de señales rojas": (10, 1.5), "Leer freno de mano": (11, 0.5), "¿Freno de mano activo?": (12, 0.5),
      "Pedido en curso": (13, 0.5), "Freno activo": (13, 1.6), "Rojo: urgencia médica": (11, 2.5),
      "Rojo: dinero": (11, 3.4), "Rojo: reclamo legal": (11, 4.3), "Rojo: historia clínica": (11, 5.2),
      "Caso rojo": (13, 3.4), "Escalar a una persona (sub-workflow)": (14, 3.4), "¿Email? (caso rojo)": (15, 3.4),
      "Responder caso rojo (email)": (15, 4.6)}),
    (4, "Memoria y clasificación", 4,
     "Se recupera la memoria del paciente (Airtable) y el Router clasifica el pedido (crear, modificar o consultar "
     "turno; información; fuera de alcance) y extrae los datos.",
     {"Buscar memoria (Airtable)": (16, 0.5), "¿Usuario recurrente?": (17, 0.5), "Crear registro inicial": (18, 1.4),
      "Preparar contexto": (19, 0.5), "Router (AI Agent)": (20, 0.5), "Anthropic Chat Model": (20, 1.6),
      "Memoria de sesion": (21, 1.6), "Contrato de datos": (22, 0.5), "Enrutar por intencion": (23, 0.5)}),
    (5, "Gestión de turnos con Juez", 6,
     "La acción se resuelve contra la agenda y el **Juez la audita antes de escribir**. Aceptada: Workers 1/4 registran, "
     "Worker 2 confirma, HubSpot (upsert con metadatos) y borrador de Gmail. Dudosa: se congela y se aprueba en Slack. "
     "Datos faltantes: aviso (el email se pide por escrito).",
     {"Buscar turnos de la persona": (24, -3), "Resolver accion": (25, -3), "Crear o modificar": (26, -3),
      "Preparar auditoría de acción": (27, -3.6), "Supervisor (Juez) — acción": (28, -3.6),
      "¿Acción aprobada por el Juez?": (29, -3.6), "Aprobar acción (Slack)": (30, -2.6),
      "¿Aprobó la acción el humano?": (31, -2.6), "Recuperar acción aprobada": (32, -3.6), "¿Es alta?": (33, -3.6),
      "traceId → Worker 1": (34, -4.3), "traceId → Worker 4": (34, -2.9), "Registrar turno (Worker 1)": (35, -4.3),
      "Modificar turno (Worker 4)": (35, -2.9), "traceId → Worker 2": (36, -3.6), "Confirmacion (Worker 2)": (37, -3.6),
      "¿Hay email?": (38, -3.6), "Validar contacto (Set)": (39, -4.3), "Buscar contacto (HubSpot)": (40, -4.3),
      "Contacto existe?": (41, -4.3), "Actualizar contacto (HubSpot)": (42, -5), "Crear contacto (HubSpot)": (42, -3.6),
      "Crear borrador (Gmail)": (43, -4.3),
      "Acción en revisión (aviso)": (32, -1.6), "Aviso (no se puede)": (33, -1.6), "¿Falta el email? (Telegram)": (34, -1.6),
      "Guardar pedido pendiente": (35, -0.95), "¿Vino por email?": (36, -1.6), "Responder al paciente (email)": (37, -1.6)}),
    (6, "Consulta de turnos", 2,
     "Worker 3 lista los turnos futuros de la persona (solo lectura).",
     {"traceId → Worker 3": (24, 0.6), "Consultar turno (Worker 3)": (25, 0.6)}),
    (7, "Consultas informativas con Juez", 6,
     "El Agente RAG responde solo con la biblioteca oficial (cita la fuente o dice **«No sé»**). El Juez evalúa cada "
     "respuesta: aceptar, corregir (máximo 2 veces) o escalar a una persona en Slack (aprobar o editar).",
     {"Agente RAG (Consultas)": (24, 3.1), "Modelo RAG (Anthropic)": (24, 4.2), "Memoria de sesión (RAG)": (25, 4.2),
      "consultar_conocimiento": (26, 4.2), "Preparar validación": (26, 3.1), "Supervisor (Juez)": (27, 3.1),
      "Switch del veredicto": (28, 3.1), "Respuesta aceptada": (29, 2.4), "¿Quedan reintentos?": (29, 3.5),
      "Preparar reintento": (30, 3.5), "Aviso al paciente (escalado)": (30, 4.7), "Escalar a humano (Slack)": (31, 4.7),
      "¿Aprobó el humano?": (32, 4.7), "Respuesta aprobada por humano": (33, 4.0), "Editar respuesta (Slack)": (33, 5.4),
      "Respuesta editada por humano": (34, 5.4), "Derivar a operador (Slack)": (35, 4.7), "Aplicar validación": (35, 3.1),
      "¿Email? (INFO)": (36, 3.1), "Responder INFO (email)": (37, 2.4)}),
    (8, "Registro y memoria", 5,
     "Log de trazabilidad (con rama de error a Slack), aviso a soporte y actualización de la memoria del paciente; "
     "cada 5 mensajes se resume la conversación.",
     {"Log de trazabilidad": (44, -1), "Alerta: log no enviado (Slack)": (45, 0.1), "Notificar a soporte (Slack)": (46, -1),
      "Consolidar datos": (47, -1), "¿Más de 5 mensajes?": (48, -1), "Resumir (LLM mini)": (49, -1.9),
      "Modelo mini (resumen)": (49, -0.8), "Parsear resumen": (51, -1.9), "Guardar memoria (upsert)": (52, -1.9),
      "Actualizar contador": (52, -0.5)}),
    (9, "Respuesta y comprensión", 4,
     "Se arma la respuesta final. Dos pedidos que no se pueden atender seguidos (30 min) pasan a una persona.",
     {"Responder al chat": (53, 0.5), "¿No se pudo ayudar?": (54, 0.5), "Buscar falla anterior": (55, 1.5),
      "¿Segunda falla seguida?": (56, 1.5), "Limpiar fallas": (57, 1), "Registrar falla": (57, 2.2),
      "Derivar por incomprensión": (58, 1), "Respuesta sin cambios": (58, 2.2),
      "Escalar por incomprensión (sub-workflow)": (59, 1), "Respuesta final": (60, 0.5)}),
    (10, "Despacho por el canal", 7,
     "La respuesta sale por donde llegó: Telegram en voz (sub-workflow *Respuesta de voz*) o en texto, webhook (Telegram "
     "o borrador de Gmail), chat o email.",
     {"¿Vino por Telegram?": (61, 0.5), "Preparar respuesta hablada": (62, -0.4), "¿Responder con voz?": (63, -0.4),
      "Responder con voz (sub-workflow)": (64, -1.2), "¿Aclarar email por texto?": (65, -1.2),
      "Aclarar: email por escrito (Telegram)": (66, -1.2), "Enviar texto (Telegram)": (64, 0.1),
      "¿Respuesta por webhook?": (62, 1.6), "¿Pidió Telegram?": (63, 1.6), "Enviar resultado (Telegram)": (64, 1.3),
      "Borrador del resultado (Gmail)": (64, 2.3), "Respuesta (chat / email)": (63, 3.0)}),
]


def main():
    w = C.n8n("GET", f"/workflows/{S.IDS['manager']}")
    posiciones = {}
    for _, _, _, _, nodos in GRUPOS:
        posiciones.update(nodos)
    reales = [n for n in w["nodes"] if "stickyNote" not in n["type"]]
    faltan = [n["name"] for n in reales if n["name"] not in posiciones]
    sobran = [k for k in posiciones if k not in {n["name"] for n in reales}]
    if faltan or sobran:
        raise SystemExit(f"Nodos sin posición: {faltan} · posiciones sin nodo: {sobran}")

    def marco(nodos, desc, dy=0.0):
        """Rectángulo (x, y, ancho, alto) en px; el margen superior crece con el largo de la descripción."""
        cs = [c for c, _ in nodos.values()]
        rs = [r + dy for _, r in nodos.values()]
        ancho = (max(cs) - min(cs) + 0.95) * CW
        lineas = 2 + -(-len(desc) * 7.5 // max(ancho - 40, 160))   # título + líneas de texto estimadas
        margen = 30 + 22 * lineas
        x = X0 + (min(cs) - 0.25) * CW
        y = Y0 + min(rs) * RH - margen
        return [x, y, ancho, (max(rs) - min(rs)) * RH + margen + 0.75 * RH]

    # los carriles 5, 6 y 7 comparten columnas: se bajan lo necesario para que sus marcos no se pisen
    dy = {g[0]: 0.0 for g in GRUPOS}
    G = {g[0]: g for g in GRUPOS}
    for arriba, abajo in ((5, 6), (6, 7)):
        a = marco(G[arriba][4], G[arriba][3], dy[arriba])
        b = marco(G[abajo][4], G[abajo][3], dy[abajo])
        solape = (a[1] + a[3] + 25) - b[1]
        if solape > 0:
            dy[abajo] += solape / RH
            if abajo == 6:
                dy[7] += solape / RH
    for num, _, _, _, nodos in GRUPOS:
        for nombre, (c, r) in nodos.items():
            posiciones[nombre] = (c, r + dy[num])
    for n in reales:
        c, r = posiciones[n["name"]]
        n["position"] = [round(X0 + c * CW), round(Y0 + r * RH)]
    w["nodes"] = reales  # se van las notas viejas
    for num, titulo, color, desc, nodos in GRUPOS:
        x, y, ancho, alto = marco(nodos, desc, dy[num])
        w["nodes"].append({"id": str(uuid.uuid4()), "name": f"Etapa {num}", "type": "n8n-nodes-base.stickyNote",
                           "typeVersion": 1, "position": [round(x), round(y)],
                           "parameters": {"content": f"## {num} · {titulo}\n{desc}", "color": color,
                                          "width": round(ancho), "height": round(alto)}})
    C.n8n("PUT", f"/workflows/{S.IDS['manager']}", {"name": w["name"], "nodes": w["nodes"], "connections": w["connections"],
                                                    "settings": {k: v for k, v in w["settings"].items() if k in S.SETTINGS_OK}})
    S.republicar(S.IDS["manager"])
    x = C.n8n("GET", f"/workflows/{S.IDS['manager']}")
    x = {k: x[k] for k in ("name", "nodes", "connections", "settings")}
    json.dump(x, open(os.path.join(MOD11, "AI Automation Avanzado - M11.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"Lienzo: {len(reales)} nodos reubicados y 10 marcos numerados (carriles bajados: {dy[6]:.2f}/{dy[7]:.2f} filas)")


if __name__ == "__main__":
    main()
