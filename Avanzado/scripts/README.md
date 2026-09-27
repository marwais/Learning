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
