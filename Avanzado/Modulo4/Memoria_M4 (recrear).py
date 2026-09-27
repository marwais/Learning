"""Recrea esta tabla en la base existente (una base por proyecto, una tabla por modulo).
  export AIRTABLE_TOKEN=pat...
  export AIRTABLE_BASE_ID=appO1XQ6layHvQx6e
  python "Memoria_M4 (recrear).py"
"""
import json, os, urllib.request
fields = [
  {
    "name": "Session_ID",
    "type": "singleLineText"
  },
  {
    "name": "Fecha de Actualización",
    "type": "dateTime",
    "options": {
      "dateFormat": {
        "name": "iso",
        "format": "YYYY-MM-DD"
      },
      "timeFormat": {
        "name": "24hour",
        "format": "HH:mm"
      },
      "timeZone": "America/Argentina/Buenos_Aires"
    }
  },
  {
    "name": "Resumen Consolidado",
    "type": "multilineText"
  },
  {
    "name": "Estado del Caso",
    "type": "singleSelect",
    "options": {
      "choices": [
        {
          "name": "En Progreso"
        },
        {
          "name": "Pendiente"
        },
        {
          "name": "En Revisión"
        },
        {
          "name": "Cerrado"
        }
      ]
    }
  },
  {
    "name": "Datos Clave",
    "type": "multilineText"
  },
  {
    "name": "Mensajes",
    "type": "number",
    "options": {
      "precision": 0
    }
  }
]
payload = {"name": "Memoria_M4", "fields": fields}
req = urllib.request.Request("https://api.airtable.com/v0/meta/bases/" + os.environ["AIRTABLE_BASE_ID"] + "/tables",
    data=json.dumps(payload).encode(), method="POST",
    headers={"Authorization": "Bearer " + os.environ["AIRTABLE_TOKEN"], "Content-Type": "application/json"})
print(json.loads(urllib.request.urlopen(req).read()).get("id"))
