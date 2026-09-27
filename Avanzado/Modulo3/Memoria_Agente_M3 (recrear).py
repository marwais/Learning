"""Recrea la base/tabla en Airtable. Uso:
  export AIRTABLE_TOKEN=pat... ; export AIRTABLE_WORKSPACE_ID=wsp...
  python "Memoria_Agente_M3 (recrear).py"
"""
import json, os, urllib.request
payload = {
  "workspaceId": "REEMPLAZAR_wspXXXXXXXXXXXXXX",
  "name": "Memoria_Agente_M3",
  "tables": [
    {
      "name": "Memoria",
      "fields": [
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
    }
  ]
}
payload["workspaceId"] = os.environ["AIRTABLE_WORKSPACE_ID"]
req = urllib.request.Request("https://api.airtable.com/v0/meta/bases", data=json.dumps(payload).encode(), method="POST",
    headers={"Authorization": "Bearer " + os.environ["AIRTABLE_TOKEN"], "Content-Type": "application/json"})
print(json.loads(urllib.request.urlopen(req).read()).get("id"))
