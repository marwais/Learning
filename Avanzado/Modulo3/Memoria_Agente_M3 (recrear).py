"""
Recrea la base/tabla de memoria en Airtable (Memoria_Agente_M3 / Memoria).
Uso:
  export AIRTABLE_TOKEN="patXXXX..."            # PAT con scopes schema.bases:write, data...
  export AIRTABLE_WORKSPACE_ID="wspXXXXXXXX"    # de list_workspaces / URL del workspace
  python "Memoria_Agente_M3 (recrear).py"
Crea la base con la tabla y los campos (vacia). Los datos se cargan aparte con el CSV de registros.
"""
import json, os, urllib.request

TOKEN = os.environ["AIRTABLE_TOKEN"]
WORKSPACE = os.environ["AIRTABLE_WORKSPACE_ID"]

payload = {
  "workspaceId": WORKSPACE,
  "name": "Memoria_Agente_M3",
  "tables": [{
    "name": "Memoria",
    "description": "Memoria de largo plazo del agente. Una fila por Session_ID.",
    "fields": [
      {"name": "Session_ID", "type": "singleLineText"},
      {"name": "Fecha de Actualizacion", "type": "dateTime",
       "options": {"dateFormat": {"name": "iso"}, "timeFormat": {"name": "24hour"},
                   "timeZone": "America/Argentina/Buenos_Aires"}},
      {"name": "Resumen Consolidado", "type": "multilineText"},
      {"name": "Estado del Caso", "type": "singleSelect",
       "options": {"choices": [{"name": "En Progreso"}, {"name": "Pendiente"},
                                {"name": "En Revision"}, {"name": "Cerrado"}]}},
      {"name": "Datos Clave", "type": "multilineText"},
      {"name": "Mensajes", "type": "number", "options": {"precision": 0}}
    ]
  }]
}

req = urllib.request.Request(
    "https://api.airtable.com/v0/meta/bases",
    data=json.dumps(payload).encode(),
    method="POST",
    headers={"Authorization": "Bearer " + TOKEN, "Content-Type": "application/json"})
resp = json.loads(urllib.request.urlopen(req).read())
print("Base creada:", resp.get("id"), "| tabla:", resp["tables"][0]["id"])
