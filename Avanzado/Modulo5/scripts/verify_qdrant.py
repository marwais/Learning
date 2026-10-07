# -*- coding: utf-8 -*-
"""Verifica el estado de la coleccion Qdrant: cantidad de puntos y chequeo
de que no queden datos viejos en los payloads."""
import sys, json
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
import _config as C

OLD = ["0800-666-6587", "4493-2017", "1144932017", "4821-1600", "miportalclinicas"]

def main():
    d = C.qdrant("GET", "/collections/" + C.COLLECTION)["result"]
    print(f"coleccion: {C.COLLECTION} | points: {d.get('points_count')} | status: {d.get('status')}")
    pts = C.qdrant("POST", "/collections/" + C.COLLECTION + "/points/scroll",
                   {"limit": 500, "with_payload": True, "with_vector": False})["result"]["points"]
    old = sum(1 for p in pts if any(o in json.dumps(p.get("payload", {}), ensure_ascii=False) for o in OLD))
    print(f"puntos revisados: {len(pts)} | con datos viejos: {old}")

if __name__ == "__main__":
    main()
