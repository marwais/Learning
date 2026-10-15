# Desactiva el proyecto AgendaBot en ESTA máquina: apaga n8n y el túnel, y los deja sin arranque
# automático. Usalo en la máquina que dejás cuando la otra no la puede desactivar por la red.
#
# Uso:  powershell -ExecutionPolicy Bypass -File Avanzado\scripts\desactivar_aqui.ps1
# Qdrant no se apaga (no recibe nada de afuera). Para volver a usar esta máquina: activar_aqui.ps1.
$ErrorActionPreference = "Continue"
Write-Host "Desactivando el proyecto en $($env:COMPUTERNAME)..."
cmd /c "docker update --restart=no n8n cloudflared ngrok >nul 2>&1"
cmd /c "docker stop n8n cloudflared ngrok 2>&1" | ForEach-Object { Write-Host "  detenido: $_" }
Write-Host "Listo: n8n y el túnel quedaron apagados y no arrancan solos." -ForegroundColor Green
