# Levanta el túnel de ngrok con el dominio FIJO de la cuenta y deja n8n apuntando a él.
# Reemplaza a Modulo6\scripts\levantar_tunel.ps1 (quick tunnel de Cloudflare):
#   - ngrok sale por el puerto 443 (funciona en redes que bloquean el 7844 de Cloudflare, como "ACCESOGRAL 3");
#   - el dominio no cambia: Telegram, los botones de Slack y los links viejos siguen funcionando;
#   - si se corta la red, el agente se reconecta solo al mismo dominio (no hay que recrear n8n).
# n8n solo se recrea si su WEBHOOK_URL no es el dominio de ngrok (la primera vez o si se usó Cloudflare).
#
# Requisitos: Docker Desktop abierto y en Avanzado\Modulo5\scripts\.env (fuera de git):
#   NGROK_AUTHTOKEN=...   (dashboard.ngrok.com > Your Authtoken)
#   NGROK_DOMAIN=...      (dashboard.ngrok.com > Domains, sin https://)
# Uso:  powershell -ExecutionPolicy Bypass -File Avanzado\scripts\levantar_ngrok.ps1
# Los datos de n8n no se tocan: viven en %USERPROFILE%\.n8n (bind mount).

$ErrorActionPreference = "Continue"
$Repo = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$envFile = Join-Path $Repo "Avanzado\Modulo5\scripts\.env"
if (-not (Test-Path $envFile)) { throw "Falta $envFile" }
$vars = @{}
Get-Content $envFile -Encoding UTF8 | Where-Object { $_ -match '^\s*([A-Z0-9_]+)\s*=\s*(.*)$' } |
  ForEach-Object { $vars[$Matches[1]] = $Matches[2].Trim() }
$token = $vars["NGROK_AUTHTOKEN"]; $dominio = ($vars["NGROK_DOMAIN"] -replace '^https?://', '').TrimEnd('/')
if (-not $token -or -not $dominio) { throw "Faltan NGROK_AUTHTOKEN o NGROK_DOMAIN en $envFile" }
$url = "https://$dominio/"

# 1. Cloudflare afuera (si estaba) y agente de ngrok con el dominio fijo (ngrok no acepta "/" final; n8n sí lo usa)
cmd /c "docker rm -f cloudflared >nul 2>&1"
cmd /c "docker rm -f ngrok >nul 2>&1"
docker run -d --name ngrok --restart unless-stopped -e NGROK_AUTHTOKEN=$token `
  ngrok/ngrok:latest http --url="https://$dominio" host.docker.internal:5678 | Out-Null
Remove-Variable token

# 2. n8n con WEBHOOK_URL = dominio de ngrok (solo si hace falta recrearlo)
$actual = (cmd /c "docker inspect n8n --format ""{{range .Config.Env}}{{println .}}{{end}}"" 2>nul" | Select-String '^WEBHOOK_URL=') -replace '^WEBHOOK_URL=', ''
if ("$actual".Trim() -ne $url) {
  cmd /c "docker rm -f n8n >nul 2>&1"
  docker run -d --name n8n --restart unless-stopped -p 5678:5678 `
    -v "$env:USERPROFILE\.n8n:/home/node/.n8n" `
    -e WEBHOOK_URL="$url" `
    -e N8N_EDITOR_BASE_URL="http://localhost:5678/" `
    n8nio/n8n:2.39.5 | Out-Null
  Write-Host "n8n recreado con WEBHOOK_URL=$url (UI local: http://localhost:5678)"
} else {
  cmd /c "docker start n8n >nul 2>&1"
  Write-Host "n8n ya apuntaba a $url (no se recrea)"
}

# 3. Verificación desde afuera
$ok = $false
for ($i = 0; $i -lt 30 -and -not $ok; $i++) {
  Start-Sleep -Seconds 2
  try { if ((Invoke-WebRequest -Uri ($url + "healthz") -UseBasicParsing -TimeoutSec 10).StatusCode -eq 200) { $ok = $true } } catch {}
}
if ($ok) { Write-Host "Túnel ngrok OK: $url" -ForegroundColor Green }
else { Write-Warning "El dominio $url no responde todavía (revisar: docker logs ngrok)" }
