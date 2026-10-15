# Activa el proyecto AgendaBot en ESTA máquina (LOBO o WOLVERINE) y lo desactiva en la otra.
#
# Uso:  powershell -ExecutionPolicy Bypass -File Avanzado\scripts\activar_aqui.ps1 [-SinTunel] [-SinGitPull]
#
# Pasos:
#   1. Desactiva en el n8n de la otra máquina (por la red local) los workflows con disparadores
#      externos (Gmail, Telegram, webhooks, chat). Va primero para que Telegram quede apuntando acá.
#      Si la otra no responde, avisa: con los contenedores sin arranque automático (paso 3), al
#      prenderla su n8n no arranca solo.
#   2. git pull del repo.
#   3. Levanta Qdrant y el túnel público: ngrok con el dominio fijo (levantar_ngrok.ps1) si NGROK_DOMAIN está en
#      el .env; si no, el quick tunnel de Cloudflare (Modulo6\scripts\levantar_tunel.ps1). Deja n8n y el túnel con
#      --restart=no: solo arrancan cuando se corre este script.
#   4. Activa en el n8n local los workflows del último módulo que exista en ESTE n8n
#      (Avanzado/ModuloN/_ids_mN.json) y apaga los disparadores externos de los módulos anteriores.
#      Si el último módulo todavía no está en este n8n (se creó en la otra máquina), usa el anterior.
#
# Requisitos: Docker Desktop abierto, Avanzado/Modulo5/scripts/.env con N8N_API_KEY (la misma key
# sirve en las dos máquinas porque la base de n8n se copió entre ellas) y maquinas.json.
param([switch]$SinTunel, [switch]$SinGitPull)

# PowerShell 5.1 convierte el stderr de docker/git en errores: se sigue y se chequea a mano.
$ErrorActionPreference = "Continue"
$Repo = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$cfg = Get-Content (Join-Path $PSScriptRoot "maquinas.json") -Raw -Encoding UTF8 | ConvertFrom-Json
$puerto = $cfg.puerto_n8n
$aqui = $env:COMPUTERNAME.ToUpper()
$nombres = @($cfg.maquinas.PSObject.Properties.Name)
if ($nombres -notcontains $aqui) { throw "Este equipo ($aqui) no figura en maquinas.json ($($nombres -join ', '))." }
$otra = $nombres | Where-Object { $_ -ne $aqui } | Select-Object -First 1

$envFile = Join-Path $Repo "Avanzado\Modulo5\scripts\.env"
if (-not (Test-Path $envFile)) { throw "Falta $envFile con N8N_API_KEY." }
$key = ((Get-Content $envFile -Encoding UTF8) | Where-Object { $_ -match '^N8N_API_KEY=' } | Select-Object -First 1) -replace '^N8N_API_KEY=', ''
$Cab = @{ "X-N8N-API-KEY" = $key.Trim(); "Accept" = "application/json" }

function Get-Workflows([string]$base) {
  (Invoke-RestMethod -Uri "$base/api/v1/workflows?limit=250" -Headers $Cab -TimeoutSec 15).data
}
function Test-DisparadorExterno($wf) {
  # Disparadores que reciben eventos de afuera; los sub-workflows (Execute Workflow Trigger) y el manual no cuentan.
  foreach ($n in $wf.nodes) {
    $t = [string]$n.type
    if ($t -match 'executeWorkflowTrigger|manualTrigger') { continue }
    if ($t -match 'Trigger$|\.webhook$|chatTrigger|formTrigger') { return $true }
  }
  return $false
}

Write-Host ""
Write-Host "=== Activando el proyecto en $aqui (la otra es $otra) ===" -ForegroundColor Cyan

# 1. Desactivar en la otra máquina
Write-Host "`n[1/4] Desactivar en $otra"
$baseOtra = $null
foreach ($destino in @($otra, $cfg.maquinas.$otra.ip) | Where-Object { $_ }) {
  try { Invoke-RestMethod -Uri "http://${destino}:$puerto/healthz" -TimeoutSec 4 | Out-Null; $baseOtra = "http://${destino}:$puerto"; break } catch {}
}
if ($baseOtra) {
  try {
    $activos = Get-Workflows $baseOtra | Where-Object { $_.active -and (Test-DisparadorExterno $_) }
    if (-not $activos) { Write-Host "  $otra no tenía workflows con disparadores externos activos." }
    foreach ($w in $activos) {
      Invoke-RestMethod -Method Post -Uri "$baseOtra/api/v1/workflows/$($w.id)/deactivate" -Headers $Cab -TimeoutSec 30 | Out-Null
      Write-Host "  desactivado en ${otra}: $($w.name)"
    }
  } catch {
    Write-Warning "  $otra responde pero la API rechazó la operación: $($_.Exception.Message)"
  }
} else {
  Write-Warning "  No pude contactar el n8n de $otra (apagada, fuera de la red o firewall en el puerto $puerto)."
  Write-Warning "  Si $otra está prendida, corré allá: Avanzado\scripts\desactivar_aqui.ps1"
}

# 2. git pull
Write-Host "`n[2/4] git pull"
if ($SinGitPull) { Write-Host "  (omitido)" } else {
  $out = cmd /c "git -C `"$Repo`" pull --ff-only 2>&1"
  $out | ForEach-Object { Write-Host "  $_" }
}

# 3. Contenedores
Write-Host "`n[3/4] Docker: Qdrant, túnel y n8n"
cmd /c "docker start qdrant >nul 2>&1"
if ($SinTunel) {
  cmd /c "docker start n8n >nul 2>&1"
  Write-Host "  n8n iniciado sin recrear el túnel (-SinTunel): Telegram usa la URL anterior, si sigue viva."
} else {
  if ((Get-Content $envFile -Encoding UTF8) -match '^NGROK_DOMAIN=\S+') {
    & (Join-Path $Repo "Avanzado\scripts\levantar_ngrok.ps1")   # dominio fijo, sale por el 443
  } else {
    & (Join-Path $Repo "Avanzado\Modulo6\scripts\levantar_tunel.ps1")
  }
}
cmd /c "docker update --restart=no n8n cloudflared ngrok >nul 2>&1"
Write-Host "  n8n y el túnel quedan sin arranque automático (solo arrancan con este script)."

$base = "http://localhost:$puerto"
$listo = $false
for ($i = 0; $i -lt 45 -and -not $listo; $i++) {
  try { Invoke-RestMethod -Uri "$base/healthz" -TimeoutSec 3 | Out-Null; $listo = $true } catch { Start-Sleep -Seconds 2 }
}
if (-not $listo) { throw "n8n no respondió en $base (revisá: docker logs n8n)." }
Start-Sleep -Seconds 8  # n8n reactiva sus workflows al arrancar

# 4. Activar los workflows del último módulo
$locales = @(Get-Workflows $base | ForEach-Object { [string]$_.id })
$ultimo = $null; $ids = $null
$modulos = Get-ChildItem (Join-Path $Repo "Avanzado") -Directory |
  Where-Object { $_.Name -match '^Modulo(\d+)$' -and (Get-ChildItem $_.FullName -Filter "_ids_m*.json") } |
  Sort-Object { [int]($_.Name -replace '\D', '') } -Descending
foreach ($m in $modulos) {
  $cand = Get-ChildItem $m.FullName -Filter "_ids_m*.json" | Select-Object -First 1 | Get-Content -Raw -Encoding UTF8 | ConvertFrom-Json
  if ($locales -contains [string]$cand.manager) { $ultimo = $m; $ids = $cand; break }
  Write-Warning "  $($m.Name) no está en este n8n (¿se creó en la otra máquina?): se usa el módulo anterior."
}
if (-not $ultimo) { throw "Ningún módulo del repo tiene su Manager en este n8n." }
Write-Host "`n[4/4] Activar workflows de $($ultimo.Name)"
# Sub-workflows primero, el Manager al final (necesita a los demás publicados).
$orden = $ids.PSObject.Properties | Sort-Object { if ($_.Name -eq 'manager') { 1 } else { 0 } }
$errores = 0
# Apagar acá los disparadores externos de módulos anteriores (comparten bot de Telegram y casilla de Gmail).
$idsModulo = @($ids.PSObject.Properties | ForEach-Object { [string]$_.Value })
foreach ($w in (Get-Workflows $base | Where-Object { $_.active -and ($idsModulo -notcontains $_.id) -and (Test-DisparadorExterno $_) })) {
  try {
    Invoke-RestMethod -Method Post -Uri "$base/api/v1/workflows/$($w.id)/deactivate" -Headers $Cab -TimeoutSec 30 | Out-Null
    Write-Host "  desactivado (módulo anterior): $($w.name)"
  } catch { $errores++; Write-Warning "  no se pudo desactivar $($w.name): $($_.Exception.Message)" }
}
foreach ($p in $orden) {
  try {
    $w = Invoke-RestMethod -Uri "$base/api/v1/workflows/$($p.Value)" -Headers $Cab -TimeoutSec 15
    if ($w.active) { Write-Host "  ya activo: $($w.name)" }
    else {
      Invoke-RestMethod -Method Post -Uri "$base/api/v1/workflows/$($p.Value)/activate" -Headers $Cab -TimeoutSec 60 | Out-Null
      Write-Host "  activado: $($w.name)"
    }
  } catch { $errores++; Write-Warning "  no se pudo activar $($p.Name) ($($p.Value)): $($_.Exception.Message)" }
}

Write-Host ""
if ($errores) { Write-Warning "Listo con $errores error(es): revisá 'docker logs n8n'." }
else { Write-Host "Listo: el proyecto quedó activo en $aqui. UI: http://localhost:$puerto" -ForegroundColor Green }
