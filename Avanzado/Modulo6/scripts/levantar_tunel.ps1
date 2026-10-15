# Levanta (o reinicia) el quick tunnel de Cloudflare y recrea el contenedor n8n
# con WEBHOOK_URL apuntando a la URL nueva. Telegram necesita una URL publica HTTPS
# para su webhook; la del quick tunnel cambia en cada reinicio.
# N8N_EDITOR_BASE_URL=localhost: el retorno de OAuth (Gmail, Google) usa localhost, que es la URI registrada en
# Google Cloud; si no, n8n usaría la URL del túnel y Google responde redirect_uri_mismatch.
# --protocol http2: algunas redes bloquean QUIC (UDP 7844) y el túnel no conecta ("failed to dial to edge with quic").
#
# Uso:  powershell -File Avanzado\Modulo6\scripts\levantar_tunel.ps1
# Los datos de n8n no se tocan: viven en %USERPROFILE%\.n8n (bind mount).

# PowerShell 5.1 convierte el stderr de docker en errores: se lee via cmd y se chequea a mano.
$ErrorActionPreference = "Continue"

cmd /c "docker rm -f cloudflared >nul 2>&1"
docker run -d --name cloudflared --restart unless-stopped cloudflare/cloudflared:latest `
  tunnel --no-autoupdate --protocol http2 --url http://host.docker.internal:5678 | Out-Null

$url = $null
for ($i = 0; $i -lt 30 -and -not $url; $i++) {
  Start-Sleep -Seconds 2
  $m = (cmd /c "docker logs cloudflared 2>&1" | Out-String) | Select-String -Pattern 'https://[a-z0-9-]+\.trycloudflare\.com'
  if ($m) { $url = $m.Matches[0].Value }
}
if (-not $url) { throw "No se obtuvo la URL del tunel (docker logs cloudflared)" }

cmd /c "docker rm -f n8n >nul 2>&1"
docker run -d --name n8n --restart unless-stopped -p 5678:5678 `
  -v "$env:USERPROFILE\.n8n:/home/node/.n8n" `
  -e WEBHOOK_URL="$url/" `
  -e N8N_EDITOR_BASE_URL="http://localhost:5678/" `
  n8nio/n8n:2.39.5 | Out-Null

Write-Host "Tunel: $url"
Write-Host "n8n recreado con WEBHOOK_URL=$url/ (UI local: http://localhost:5678)"
Write-Host "Si el tunel se cae, el chat de prueba falla con 'Failed to receive response': volve a correr este script."
