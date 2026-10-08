# RAG LoDeTincho — Runbook de mantenimiento (Módulo 5)

Guía para operar el RAG en local desde VSCode. El "cerebro" del bot vive en **dos contenedores Docker** (n8n y Qdrant); el repo guarda los documentos, el markdown parseado, los workflows exportados y estos scripts.

## Arquitectura (resumen)

```
documentacion/*.docx ──parse_kb.py──▶ LlamaParse (Agentic) ──▶ kb_md/*.md
kb_md/*.md ──update_codenode.py──▶ nodo "Cargar KB" (n8n)
n8n "▶ Ingerir KB": recrear colección → chunking por sección → Cohere → QDRANT (kb_lodetincho_m5)

Chat/email ─▶ Router ─(INFO)─▶ Agente RAG ─tool─▶ Tool_ConsultarConocimiento
                                                   (Top-K 5 · Min Score 0.60 · Qdrant search)
```

- **n8n** (`localhost:5678`): Manager `AI Automation Avanzado - M5` (`ciy1C6pB26Urfmlj`) y herramienta `Tool_ConsultarConocimiento (M5)` (`aEnYAA9K1l7YAwRj`).
- **Qdrant** (`localhost:6333`; desde n8n, `host.docker.internal:6333`): colección `kb_lodetincho_m5` (1024 dims, Cosine), persistente.
- La fuente de verdad son los **`.docx` de `../documentacion/`**. El markdown de `../kb_md/` se genera con LlamaParse y no se edita a mano.

## 1) Prerrequisitos (una sola vez)

- **Docker Desktop** abierto, con los contenedores `n8n` y `qdrant` arriba (`docker ps`). Ambos vuelven solos (`--restart unless-stopped`).
  - El contenedor `n8n` tiene que tener `WEBHOOK_URL=http://localhost:5678/`. Si apunta a un túnel caído, el chat de prueba falla con "Failed to receive response".
- **Python** con el paquete `markdown` (solo para armar el PDF).
- **`scripts/.env`** (copiá `.env.example`): `N8N_API_KEY` (n8n → Settings → n8n API) y `LLAMA_CLOUD_API_KEY` (cloud.llamaindex.ai → API Keys). El `.env` no se sube al repo.
- En n8n, la herramienta y los 4 workers del M5 tienen que estar **publicados**: en n8n 2.x, un sub-workflow sin publicar no se puede llamar.

## 2) Operación típica: actualizar el conocimiento

Cada vez que agregás o editás un `.docx` de `../documentacion/`:

```
cd Avanzado/Modulo5/scripts
python update_kb.py            # parsea lo nuevo con LlamaParse + carga el markdown en n8n
```

Después, **en n8n**: abrí el workflow M5, desplegá *Execute workflow* → **`from ▶ Ingerir KB (RAG)`** y ejecutalo. Eso recrea la colección y la vuelve a llenar.

Verificá:
```
python verify_qdrant.py        # fragmentos por documento y largos
```

Para re-parsear un documento que ya tenía `.md`, borrá su `.md` en `kb_md/` (o usá `--force` para todos; consume unos 400 créditos de LlamaCloud).

## 3) Auditar respuestas

```
python ver_ejecuciones.py 5    # últimas 5 consultas: intent, respuesta, búsquedas y scores
```

## 4) Versionar los workflows (cuando los modificás en n8n)

```
python export_workflows.py     # Manager M5 + 4 workers + herramienta RAG → ../*.json
```

## 5) Scripts

| Script | Qué hace |
|---|---|
| `update_kb.py` | **El principal.** `parse_kb` + `update_codenode`. |
| `parse_kb.py` | Parsea los documentos con LlamaParse (API v2, tier Agentic) → `kb_md/*.md`. |
| `update_codenode.py` | Carga los `.md` en el nodo "Cargar KB (markdown LlamaParse)" de n8n. |
| `verify_qdrant.py` | Fragmentos por documento y largo de los fragmentos en Qdrant. |
| `ver_ejecuciones.py` | Últimas ejecuciones del Manager y de la herramienta RAG (auditoría). |
| `export_workflows.py` | Exporta los workflows de n8n al repo. |
| `_config.py` | Config común (lee `.env`). |

## 6) Continuar en otra máquina

Lo que **está en Git**: documentos, markdown parseado (`kb_md/`), los 6 workflows (con su id), scripts y la pre-entrega.
Lo que **no está en Git**: el estado de n8n (credenciales y ejecuciones), los vectores de Qdrant y `scripts/.env`.

1. **Repo:** `git clone https://github.com/marwais/Learning.git` (o `git pull`).
2. **Contenedores** (Docker Desktop):
   ```
   docker run -d --name qdrant --restart unless-stopped -p 6333:6333 -p 6334:6334 -v qdrant_storage:/qdrant/storage qdrant/qdrant
   docker run -d --name n8n --restart unless-stopped -p 5678:5678 -v "%USERPROFILE%\.n8n:/home/node/.n8n" -e WEBHOOK_URL=http://localhost:5678/ n8nio/n8n:2.39.5
   ```
3. **n8n**, por una de dos vías:
   - **A) Copiar el estado entero (lo más rápido):** con n8n detenido en las dos máquinas, copiar la carpeta `C:\Users\<usuario>\.n8n` de la máquina original a la nueva. Trae workflows, credenciales y la clave de cifrado. **Contiene secretos:** copiala por un medio privado (pendrive, red local), nunca por Git ni por una carpeta compartida.
   - **B) Importar los workflows:** crear las credenciales con **los mismos nombres** (Anthropic account, Cohere n8n, Qdrant local con URL `http://host.docker.internal:6333`, Gmail account, Google Sheets account, Airtable Memoria M3, Slack account, Slack AgendaBot (Bot Token), HubSpot AgendaBot (App Token)). Después importar conservando los ids:
     ```
     cd Avanzado/Modulo5
     for %f in ("Tool_ConsultarConocimiento (M5).json" "Worker1_RegistrarTurno (M5).json" "Worker2_Confirmacion (M5).json" "Worker3_ConsultarTurno (M5).json" "Worker4_ModificarTurno (M5).json" "AI Automation Avanzado - M5.json") do docker cp %f n8n:/tmp/wf.json && docker exec n8n n8n import:workflow --input=/tmp/wf.json
     ```
     Abrí cada workflow y, si algún nodo marca la credencial como faltante, reasignala.
4. **Publicar** en n8n la herramienta RAG y los 4 workers (si no, el Manager no puede llamarlos).
5. **`scripts/.env`** desde `.env.example`: `N8N_API_KEY` (crear en n8n → Settings → n8n API) y `LLAMA_CLOUD_API_KEY` (solo para re-parsear).
6. **Base vectorial:** en el Manager, *Execute workflow* → `from ▶ Ingerir KB (RAG)`. No hace falta re-parsear: el markdown ya viene dentro del nodo "Cargar KB". Verificá con `python verify_qdrant.py` (195 fragmentos).
7. **Prueba:** desde el chat del Manager, preguntá algo de la base (por ejemplo, "¿Qué profesionales atienden Cardiología?") y revisá con `python ver_ejecuciones.py 1`.

## Datos útiles (IDs)

- Manager M5: `ciy1C6pB26Urfmlj` · Herramienta RAG: `aEnYAA9K1l7YAwRj` · Workers M5: `OhqlaD9owJHhZ0Xp`, `Ft8psvxAlilfFKuw`, `mC0rTN5ylCLiu6gX`, `47lULDxTZa8YGKjj`
- Intento 1 archivado: `f1Yl3BRwYouF660l` ("M5 (intento 1)"), colección Qdrant `lodetincho_kb`, tag de git `m5-intento1`.
- Credenciales n8n: Anthropic `qyqhv8Oy5wq4bqNd` · Cohere `GIJyTK4Omxo0Qr5x` · Qdrant `pLYIfGUwJbF5oMN7` · Gmail `LCpAQRDOeUUC99pU` · Slack `6kYo49Hy2suBgtSl` · HubSpot `hPGs8x3WWMPWG5Sk`
- Modelo del Agente RAG: `claude-sonnet-4-6`. Embeddings: Cohere `embed-multilingual-v3.0`.
