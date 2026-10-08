# -*- coding: utf-8 -*-
"""Verifica la colección de Qdrant: cantidad de fragmentos, fragmentos por
documento y largo de los fragmentos (para detectar cortes raros)."""
import sys, collections
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
import _config as C

def main():
    d = C.qdrant("GET", "/collections/" + C.COLLECTION)["result"]
    print(f"colección: {C.COLLECTION} | points: {d.get('points_count')} | status: {d.get('status')}")
    pts = C.qdrant("POST", "/collections/" + C.COLLECTION + "/points/scroll",
                   {"limit": 1000, "with_payload": True, "with_vector": False})["result"]["points"]
    por_doc = collections.Counter(p["payload"]["metadata"].get("source") for p in pts)
    for doc, n in por_doc.most_common():
        print(f"  {n:4}  {doc}")
    largos = sorted(len(p["payload"]["content"]) for p in pts)
    if largos:
        print(f"largo de fragmentos (chars): min {largos[0]} | mediana {largos[len(largos)//2]} | max {largos[-1]}")

if __name__ == "__main__":
    main()
