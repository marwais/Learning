# scripts/ — Exportación de artefactos por módulo

Automatiza el versionado de **todos** los artefactos de cada módulo del proyecto AgendaBot.
Convención: el `.docx`/`.pdf` de la entrega los hace el usuario a mano; **el resto se exporta con este script**.

## Qué genera (por módulo, en `Avanzado/Modulo<N>/`)
- **Workflows (JSON):** el principal + todos los workers (aunque no se hayan tocado).
- **Por cada tabla:**
  - `<Tabla> (esquema).json` — estructura (columnas, tipos, opciones).
  - `<Tabla> (recrear).py` — reconstruye la tabla desde cero.
  - `<Tabla> (registros).csv` — snapshot de datos.
  - Airtable, además: `<Tabla> (create_base payload).json` — cuerpo listo para la API `create_base`.

## Uso
```bash
export N8N_API_KEY="..."                 # Settings -> n8n API
export AIRTABLE_TOKEN="pat..."           # si el módulo usa Airtable
export GOOGLE_SA_JSON="/ruta/sa.json"    # opcional: cuenta de servicio Google para exportar Sheets
python export_modulo.py modulo3.config.json
```
Si no está `GOOGLE_SA_JSON`, el export de Google Sheets se omite (el CSV se puede refrescar aparte).

## Config por módulo (`modulo<N>.config.json`)
- `out_dir`: carpeta destino (relativa a este config).
- `workflows`: mapa `{ workflowId: "nombre archivo.json" }`.
- `google_sheets`: `[ { id, base_name } ]` (una entrada por planilla).
- `airtable_tables`: `[ { base, table, base_name } ]` (una entrada por tabla).

Para un módulo nuevo: copiar `modulo3.config.json` a `modulo<N>.config.json`, actualizar IDs y correr.

## Cambiar de máquina: `activar_aqui.ps1` / `desactivar_aqui.ps1`

El proyecto corre en dos PCs, **LOBO** y **WOLVERINE** (nombres en `maquinas.json`). Solo una puede tener n8n activo a la vez: las dos comparten el bot de Telegram y la casilla de Gmail.

```powershell
# En la máquina que vas a usar (desactiva la otra por la red si responde):
powershell -ExecutionPolicy Bypass -File Avanzado\scripts\activar_aqui.ps1
# En la máquina que dejás, si la otra no la pudo desactivar por la red:
powershell -ExecutionPolicy Bypass -File Avanzado\scripts\desactivar_aqui.ps1
```

`activar_aqui.ps1`:
1. Desactiva en el n8n de la otra máquina (`http://<OTRA>:5678`, por nombre o por la IP de `maquinas.json`) los workflows activos con disparadores externos (Gmail, Telegram, webhooks, chat). Los sub-workflows no se tocan.
2. `git pull --ff-only`.
3. Levanta Qdrant y el túnel de Telegram (`Modulo6/scripts/levantar_tunel.ps1`) y deja n8n y cloudflared con `--restart=no`: no arrancan solos al reiniciar, solo con este script. Con `-SinTunel` arranca n8n sin recrear el túnel.
4. Activa en el n8n local los workflows del último módulo (`ModuloN/_ids_mN.json`), el Manager al final.

Requisitos:
- `Avanzado/Modulo5/scripts/.env` con `N8N_API_KEY` (la misma key sirve en las dos máquinas porque la base de n8n se copió entre ellas).
- Para desactivar la otra por la red, las dos tienen que estar en la misma red y el puerto 5678 abierto en el firewall de Windows de la otra (si no, el script avisa y hay que correr `desactivar_aqui.ps1` allá). Si el nombre no resuelve, cargar su IP en `maquinas.json`.
- La base de n8n no se sincroniza: si en una máquina cambiaste workflows o credenciales, exportalos al repo o copiá la carpeta `.n8n` antes de cambiar.
