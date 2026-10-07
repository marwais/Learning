# -*- coding: utf-8 -*-
"""Recrea la coleccion de Qdrant LIMPIA (borra y crea), para que al re-ingerir
no queden vectores viejos ni duplicados."""
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
import _config as C

def main():
    try:
        C.qdrant("DELETE", "/collections/" + C.COLLECTION)
    except Exception:
        pass
    C.qdrant("PUT", "/collections/" + C.COLLECTION,
             {"vectors": {"size": C.EMBED_DIM, "distance": "Cosine"}})
    d = C.qdrant("GET", "/collections/" + C.COLLECTION)["result"]
    print(f"Coleccion '{C.COLLECTION}' recreada | points: {d.get('points_count')} | status: {d.get('status')}")

if __name__ == "__main__":
    main()
