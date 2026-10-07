# RAG LoDeTincho — Runbook de mantenimiento (Módulo 5)

Guía para seguir trabajando el RAG en **local desde VSCode**. El "cerebro" del
bot vive en **dos contenedores Docker** (no en el repo); el repo tiene los
documentos, los workflows y estos scripts.

## Arquitectura (resumen)

```
15 .docx  →  extract_kb  →  nodo "Cargar documentos" (n8n)  →  Embeddings Cohere  →  QDRANT
                                                                                        ↑
                                                         el Agente RAG consulta acá (no LlamaCloud)
```

- **n8n** (`localhost:5678`): workflow `AI Automation Avanzado - M5` (id `f1Yl3BRwYouF660l`).
- **Qdrant** (`localhost:6333`): vector store **persistente**, colección `lodetincho_kb` (1024 dims, Cosine).
- La fuente de verdad del conocimiento son los **`.docx` de `../documentacion/`**.
- LlamaCloud **no** alimenta el RAG (su índice es pago); se usó solo para el parseo de la pieza 1.

## 1) Prerrequisitos (una sola vez)

- **Docker Desktop** abierto. Los contenedores `n8n` y `qdrant` vuelven solos
  (`--restart unless-stopped`). Verificá: `docker ps` (deben estar `n8n` y `qdrant`).
  - Si **no** está Qdrant, levantalo:
    ```
    docker run -d --name qdrant --restart unless-stopped -p 6333:6333 -p 6334:6334 -v qdrant_storage:/qdrant/storage qdrant/qdrant
    ```
- **Python** con **python-docx**: `pip install python-docx`
- **API key de n8n**: en n8n → **Settings → n8n API → Create API key**.
- **Config local**: copiá `.env.example` a `.env` y pegá tu `N8N_API_KEY`.
  (El `.env` no se sube al repo.)

## 2) Operación típica: actualizar el conocimiento

Cada vez que **editás un `.docx`** de `../documentacion/`:

```
cd Avanzado/Modulo5/scripts
python update_kb.py
```

Eso: extrae el texto → actualiza el nodo de ingesta en n8n → recrea la colección Qdrant limpia.
**Después, en n8n**: abrí el workflow, desplegá el botón *Execute workflow* →
**`from ▶ Ingerir KB (RAG)`** y ejecutalo (eso embebe y carga a Qdrant).

Verificá:
```
python verify_qdrant.py      # points: 51 | con datos viejos: 0
```

> Nota: el vector store es persistente; **no** hay que re-ingerir tras reiniciar n8n.
> Solo re-ingerís cuando **cambiás la documentación**.

## 3) Versionar los workflows (cuando los modificás en n8n)

```
cd Avanzado/Modulo5/scripts
python export_workflows.py   # vuelca el Manager M5 + workers a ../*.json
cd ../../..
git add Avanzado/Modulo5 && git commit -m "chore(M5): export workflows" && git push
```

## 4) Scripts

| Script | Qué hace |
|---|---|
| `update_kb.py` | **El principal.** Corre extract → update node → recreate Qdrant. |
| `extract_kb.py` | Extrae texto de los `.docx` → `kb_b64.txt`. |
| `update_codenode.py` | Mete ese texto en el nodo "Cargar documentos" de n8n. |
| `recreate_qdrant.py` | Borra y recrea la colección Qdrant (limpia). |
| `verify_qdrant.py` | Chequea cantidad de puntos y que no queden datos viejos. |
| `export_workflows.py` | Exporta los workflows de n8n al repo. |
| `_config.py` | Config común (lee `.env`). |

## Datos útiles (IDs)

- Workflow M5: `f1Yl3BRwYouF660l`
- Credenciales n8n: Anthropic `qyqhv8Oy5wq4bqNd` · Cohere `GIJyTK4Omxo0Qr5x` · Qdrant `pLYIfGUwJbF5oMN7` · Gmail `LCpAQRDOeUUC99pU` · Slack `6kYo49Hy2suBgtSl` · HubSpot `hPGs8x3WWMPWG5Sk`
- Qdrant: colección `lodetincho_kb` (1024 dims, Cosine)
- Modelo del Agente RAG: `claude-sonnet-4-6` (Anthropic)

> Rotá las API keys que puedan haber quedado expuestas (Cohere, Gemini) y nunca
> subas el `.env` al repo.
