"""
Recrea la planilla Agenda_Turnos en Google Sheets con encabezados + datos del CSV.
Requiere una cuenta de servicio de Google con acceso a Sheets/Drive:
  pip install gspread google-auth
  export GOOGLE_SA_JSON="/ruta/service_account.json"
  python "Agenda_Turnos (recrear).py"
(El CSV de datos debe estar junto a este script: 'Agenda_Turnos (04).csv'.)
"""
import os, csv, gspread

SA = os.environ["GOOGLE_SA_JSON"]
gc = gspread.service_account(filename=SA)

sh = gc.create("Agenda_Turnos")
ws = sh.sheet1
with open("Agenda_Turnos (04).csv", encoding="utf-8") as f:
    rows = list(csv.reader(f))
ws.update("A1", rows)  # encabezados + filas
print("Planilla creada:", sh.url)
