# -*- coding: utf-8 -*-
"""Cliente de prueba del Receptor (M11): manda un pedido por POST /webhook/agendabot-m11 (UTF-8) y mide la respuesta.

Uso:  python probar_webhook.py <request_id> "<mensaje>" [--email x@y] [--nombre "N"] [--tg 123] [--esperar]
      --esperar: espera a que termine la ejecución del Manager con ese traceId y muestra su recorrido.
"""
import json, os, sys, time, urllib.request, urllib.error
sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "Modulo5", "scripts"))
import _config as C  # noqa: E402

URL = C.N8N_BASE + "/webhook/agendabot-m11"
IDS = json.load(open(os.path.join(HERE, "..", "_ids_m11.json")))


def opcion(nombre, default=""):
    return sys.argv[sys.argv.index(nombre) + 1] if nombre in sys.argv else default


def enviar(body):
    req = urllib.request.Request(URL, data=json.dumps(body, ensure_ascii=False).encode("utf-8"), method="POST",
                                 headers={"Content-Type": "application/json; charset=utf-8"})
    t0 = time.time()
    try:
        r = urllib.request.urlopen(req, timeout=30)
        code, data = r.status, r.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        code, data = e.code, e.read().decode("utf-8")
    return code, json.loads(data or "{}"), time.time() - t0


def esperar(trace_id, timeout=150):
    fin = time.time() + timeout
    while time.time() < fin:
        time.sleep(5)
        for e in C.n8n("GET", f"/executions?workflowId={IDS['manager']}&limit=5&includeData=true")["data"]:
            run = e.get("data", {}).get("resultData", {}).get("runData", {})
            try:
                trc = run["Generar traceId"][0]["data"]["main"][0][0]["json"].get("traceId")
            except Exception:
                continue
            if trc == trace_id and e["status"] != "running":
                return e
    return None


def main():
    if len(sys.argv) < 3:
        raise SystemExit(__doc__)
    body = {"request_id": sys.argv[1], "mensaje": sys.argv[2], "nombre": opcion("--nombre", "Prueba Webhook")}
    if opcion("--email"):
        body["email"] = opcion("--email")
    if opcion("--tg"):
        body["tg_chat_id"] = opcion("--tg")
    code, resp, seg = enviar(body)
    print(f"HTTP {code} en {seg:.2f} s →", json.dumps(resp, ensure_ascii=False))
    if "--esperar" in sys.argv and code == 202:
        e = esperar(resp["traceId"])
        if not e:
            print("No terminó a tiempo")
            return
        rd = e["data"]["resultData"]
        dur = (time.mktime(time.strptime(e["stoppedAt"][:19], "%Y-%m-%dT%H:%M:%S"))
               - time.mktime(time.strptime(e["startedAt"][:19], "%Y-%m-%dT%H:%M:%S")))
        print(f"Manager {e['id']} · {e['status']} · {dur:.0f} s en segundo plano")
        print("  nodos:", " → ".join(f"{k}{' ✘' if v[-1].get('error') else ''}" for k, v in rd["runData"].items()))
        for k in ("Contrato de datos", "Resolver accion", "Supervisor (Juez) — acción", "Registrar turno (Worker 1)", "Responder al chat"):
            if k in rd["runData"]:
                try:
                    print(f"  {k}:", json.dumps(rd["runData"][k][-1]["data"]["main"][0][0]["json"], ensure_ascii=False)[:350])
                except Exception:
                    pass


if __name__ == "__main__":
    main()
