# Junta en una carpeta (por ejemplo, un pendrive) todo lo que hace falta para dejar la otra PC igual que esta.
#
#   n8n-<PC>-<fecha>.tar.gz  carpeta %USERPROFILE%\.n8n: workflows, credenciales, Data Tables, API key de n8n
#                            y el nodo de ElevenLabs
#   env-<PC>.env             Avanzado\Modulo5\scripts\.env (SECRETOS: N8N_API_KEY, NGROK_*, FRENO_TOKEN, ...)
#   <coleccion>.snapshot     snapshot de Qdrant de la base de conocimiento (la colección de QDRANT_COLLECTION)
#   memoria-claude\          memoria local de Claude Code para este proyecto
#   manifiesto.json, LEEME.txt  estado del repo, workflows, contenedores y SHA256 de cada archivo
#
# Antes de copiar, apaga n8n y el túnel en ESTA PC, igual que desactivar_aqui.ps1. Lo hace por dos motivos:
# la base de n8n tiene que estar quieta para copiarla, y el dominio de ngrok solo puede estar activo en una PC.
# Qdrant queda prendido.
#
# Uso (con el script en el pendrive):  powershell -ExecutionPolicy Bypass -File E:\exportar_para_otra_pc.ps1
#   -Destino <carpeta>  dónde dejar todo (por defecto, la carpeta donde está este script)
#   -Repo <carpeta>     repo del proyecto (por defecto, el de LOBO o el de WOLVERINE según el equipo)
#   -Si                 no pide confirmación
# El resultado lleva secretos: pasalo por pendrive, nunca por Drive ni por git, y borralo después de usarlo.
param([string]$Destino = $PSScriptRoot, [string]$Repo = "", [switch]$Si)

# PowerShell 5.1 convierte el stderr de docker, git y tar en errores: se sigue y se chequea a mano.
$ErrorActionPreference = "Continue"
$pc = $env:COMPUTERNAME.ToUpper()
$fecha = Get-Date -Format "yyyyMMdd-HHmm"
$problemas = New-Object System.Collections.ArrayList

# --- Repo y .env
$repos = @{ "LOBO" = "C:\MW\Trabajos\IA\SessionLocal\Learning\Learning"; "WOLVERINE" = "G:\Trabajos\MW\IA\SessionLocal\Learning" }
if (-not $Repo) { $Repo = $repos[$pc] }
$envFile = if ($Repo) { Join-Path $Repo "Avanzado\Modulo5\scripts\.env" } else { "" }
if (-not $Repo -or -not (Test-Path $envFile)) {
  throw "No encuentro el repo con Avanzado\Modulo5\scripts\.env en este equipo ($pc). Pasá -Repo <carpeta del repo>."
}
if (-not (Test-Path $Destino)) { throw "No existe la carpeta de destino: $Destino" }
$vars = @{}
Get-Content $envFile -Encoding UTF8 | Where-Object { $_ -match '^\s*([A-Z0-9_]+)\s*=\s*(.*)$' } |
  ForEach-Object { $vars[$Matches[1]] = $Matches[2].Trim() }
$coleccion = if ($vars["QDRANT_COLLECTION"]) { $vars["QDRANT_COLLECTION"] } else { "kb_lodetincho" }

cmd /c "docker info >nul 2>&1"
if ($LASTEXITCODE -ne 0) { throw "Docker Desktop no está corriendo: abrilo, esperá a que diga 'Engine running' y volvé a ejecutar." }

$sal = Join-Path $Destino "traspaso-$pc-$fecha"
New-Item -ItemType Directory -Path $sal -Force | Out-Null

Write-Host ""
Write-Host "=== Exportar el proyecto desde $pc ===" -ForegroundColor Cyan
Write-Host "  Repo:    $Repo"
Write-Host "  Destino: $sal"
Write-Host "  Esto APAGA n8n y el túnel en $pc (después, para volver a usarla: activar_aqui.ps1)."
if (-not $Si) {
  $r = Read-Host "  ¿Seguir? (s/n)"
  if ($r -notmatch '^[sS]') { Remove-Item $sal -Recurse -Force; Write-Host "Cancelado."; return }
}

# --- 1. Foto del estado antes de apagar (workflows por la API, si n8n está prendido; contenedores)
Write-Host "`n[1/6] Estado actual"
$workflows = @()
try {
  $cab = @{ "X-N8N-API-KEY" = $vars["N8N_API_KEY"]; "Accept" = "application/json" }
  $workflows = @((Invoke-RestMethod "http://localhost:5678/api/v1/workflows?limit=250" -Headers $cab -TimeoutSec 8).data |
    ForEach-Object { [ordered]@{ id = $_.id; nombre = $_.name; activo = [bool]$_.active } })
  Write-Host "  n8n prendido: $($workflows.Count) workflows ($(@($workflows | Where-Object { $_.activo }).Count) activos)."
} catch {
  Write-Host "  n8n no responde en localhost:5678 (apagado): la lista de workflows se saca después de restaurar."
}
$contenedores = @{}
foreach ($c in "n8n", "qdrant", "ngrok", "cloudflared") {
  $img = (cmd /c "docker inspect $c --format ""{{.Config.Image}}"" 2>nul" | Out-String).Trim()
  if ($img) { $contenedores[$c] = $img }
}
# Solo las variables de n8n que no son secretas (la del token de ngrok no se registra)
$n8nEnv = @(cmd /c "docker inspect n8n --format ""{{range .Config.Env}}{{println .}}{{end}}"" 2>nul" |
  Where-Object { $_ -match '^(WEBHOOK_URL|N8N_EDITOR_BASE_URL)=' })

# --- 2. Apagar n8n y el túnel (como desactivar_aqui.ps1)
Write-Host "`n[2/6] Apagar n8n y el túnel en $pc"
cmd /c "docker update --restart=no n8n cloudflared ngrok >nul 2>&1"
cmd /c "docker stop n8n cloudflared ngrok >nul 2>&1"
$sigue = (cmd /c "docker ps --filter name=^n8n$ --format {{.Names}} 2>nul" | Out-String).Trim()
if ($sigue) { throw "n8n sigue corriendo: no se puede copiar su base. Revisá 'docker ps' y volvé a ejecutar." }
Write-Host "  n8n, ngrok y cloudflared detenidos y sin arranque automático."

# --- 3. Carpeta .n8n
Write-Host "`n[3/6] Copiar %USERPROFILE%\.n8n (puede tardar un minuto)"
$tarFile = Join-Path $sal "n8n-$pc-$fecha.tar.gz"
$avisos = @(cmd /c "tar -czf ""$tarFile"" -C ""$env:USERPROFILE"" .n8n 2>&1")
# Los accesos directos de nodes\node_modules\.bin no se pueden empaquetar en Windows y n8n no los usa.
$otros = @($avisos | Where-Object { $_ -and $_ -notmatch 'node_modules/\.bin/|Error exit delayed' })
$lista = @(cmd /c "tar -tzf ""$tarFile"" 2>nul")
if (-not ($lista -contains ".n8n/database.sqlite") -or -not ($lista -contains ".n8n/config")) {
  [void]$problemas.Add("El tar de .n8n no tiene database.sqlite o config: no sirve para restaurar.")
  Write-Warning "  El tar de .n8n quedó incompleto."
} else {
  Write-Host "  OK: $($lista.Count) archivos ($([math]::Round((Get-Item $tarFile).Length/1MB,1)) MB)."
}
if ($otros) { [void]$problemas.Add("Avisos de tar: " + ($otros -join " | ")) }

# --- 4. .env
Write-Host "`n[4/6] Copiar el .env (secretos)"
Copy-Item $envFile (Join-Path $sal "env-$pc.env")
Write-Host "  OK: env-$pc.env"

# --- 5. Snapshot de Qdrant
Write-Host "`n[5/6] Snapshot de Qdrant ($coleccion)"
$puntos = $null; $colecciones = @(); $snapFile = Join-Path $sal "$coleccion.snapshot"
cmd /c "docker start qdrant >nul 2>&1"
$info = $null
for ($i = 0; $i -lt 30 -and -not $info; $i++) {
  try { $info = Invoke-RestMethod "http://localhost:6333/collections/$coleccion" -TimeoutSec 4 } catch { Start-Sleep -Seconds 2 }
}
if (-not $info) {
  [void]$problemas.Add("Qdrant no respondió o no existe la colección $coleccion.")
  Write-Warning "  Qdrant no respondió o no existe la colección $coleccion."
} else {
  $puntos = $info.result.points_count
  try { $colecciones = @((Invoke-RestMethod "http://localhost:6333/collections" -TimeoutSec 5).result.collections.name) } catch {}
  try {
    $snap = Invoke-RestMethod -Method Post "http://localhost:6333/collections/$coleccion/snapshots" -TimeoutSec 300
    $nombre = $snap.result.name
    cmd /c "docker cp ""qdrant:/qdrant/snapshots/$coleccion/$nombre"" ""$snapFile"" >nul 2>&1"
    try { Invoke-RestMethod -Method Delete "http://localhost:6333/collections/$coleccion/snapshots/$nombre" -TimeoutSec 30 | Out-Null } catch {}
    if (Test-Path $snapFile) { Write-Host "  OK: $coleccion.snapshot ($puntos fragmentos, $([math]::Round((Get-Item $snapFile).Length/1MB,1)) MB)." }
    else { [void]$problemas.Add("No se pudo sacar el snapshot del contenedor qdrant."); Write-Warning "  No se pudo sacar el snapshot del contenedor." }
  } catch {
    [void]$problemas.Add("Qdrant no generó el snapshot: $($_.Exception.Message)")
    Write-Warning "  Qdrant no generó el snapshot: $($_.Exception.Message)"
  }
}

# --- 6. Memoria de Claude, estado del repo y manifiesto
Write-Host "`n[6/6] Memoria de Claude, estado del repo y manifiesto"
$memorias = @(Get-ChildItem (Join-Path $env:USERPROFILE ".claude\projects") -Directory -ErrorAction SilentlyContinue |
  Where-Object { $_.Name -match 'Learning' -and (Test-Path (Join-Path $_.FullName "memory")) })
# Nombre corto de destino (memoria-claude, memoria-claude-2, ...): la carpeta del proyecto en .claude tiene un
# nombre largo y, sumado al destino, puede pasar el límite de 260 caracteres de las rutas de Windows.
$n = 0
foreach ($m in $memorias) {
  $n++
  $d = Join-Path $sal ("memoria-claude" + $(if ($n -gt 1) { "-$n" } else { "" }))
  New-Item -ItemType Directory -Path $d -Force | Out-Null
  $fuente = @(Get-ChildItem (Join-Path $m.FullName "memory") -File)
  $fallas = 0
  foreach ($f in $fuente) {
    try { Copy-Item $f.FullName (Join-Path $d $f.Name) -ErrorAction Stop } catch { $fallas++ }
  }
  if ($fallas) { [void]$problemas.Add("Memoria de Claude: no se copiaron $fallas de $($fuente.Count) archivos de $($m.Name).") }
  Write-Host "  memoria: $($m.Name) -> $(Split-Path $d -Leaf) ($($fuente.Count - $fallas) de $($fuente.Count) archivos)"
}
if (-not $memorias) { Write-Host "  No hay memoria local de Claude para este proyecto." }

# git escribe en UTF-8 y PowerShell 5.1 lo decodifica con la página de códigos de la consola (rompe los acentos):
# la salida pasa por un archivo temporal que se lee como UTF-8.
function Invoke-GitUtf8([string]$argumentos) {
  $tmp = [IO.Path]::GetTempFileName()
  cmd /c "git -C ""$Repo"" $argumentos > ""$tmp"" 2>&1"
  $texto = [IO.File]::ReadAllText($tmp, [Text.Encoding]::UTF8)
  Remove-Item $tmp -ErrorAction SilentlyContinue
  return $texto
}
cmd /c "git -C ""$Repo"" fetch -q 2>&1" | Out-Null
$head = (Invoke-GitUtf8 "log -1 --format=""%h %cd %s"" --date=iso").Trim()
$estado = @((Invoke-GitUtf8 "status -sb") -split "`r?`n" | Where-Object { $_ })
$cambios = @($estado | Select-Object -Skip 1)
if ($estado[0] -match 'ahead') { [void]$problemas.Add("El repo de $pc tiene commits sin subir a GitHub: $($estado[0])") }
if ($cambios) { [void]$problemas.Add("El repo de $pc tiene $($cambios.Count) cambio(s) sin commitear (ver manifiesto).") }

$archivos = @(Get-ChildItem $sal -File | Where-Object { $_.Name -notmatch '^(manifiesto\.json|LEEME\.txt)$' } | ForEach-Object {
  [ordered]@{ archivo = $_.Name; mb = [math]::Round($_.Length/1MB,2); sha256 = (Get-FileHash $_.FullName -Algorithm SHA256).Hash }
})
$manifiesto = [ordered]@{
  equipo = $pc; fecha = (Get-Date).ToString("s"); repo = $Repo
  git = [ordered]@{ ultimo_commit = $head; estado = $estado }
  n8n = [ordered]@{ workflows = $workflows; variables = $n8nEnv }
  contenedores = $contenedores
  qdrant = [ordered]@{ coleccion = $coleccion; fragmentos = $puntos; colecciones = $colecciones }
  memoria_claude = @($memorias | ForEach-Object { $_.Name })   # en orden: memoria-claude, memoria-claude-2, ...
  archivos = $archivos
  problemas = @($problemas)
}
$manifiesto | ConvertTo-Json -Depth 6 | Out-File (Join-Path $sal "manifiesto.json") -Encoding utf8

$leeme = @"
Traspaso del proyecto AgendaBot desde $pc ($((Get-Date).ToString("dd/MM/yyyy HH:mm")))

CONTIENE SECRETOS (env-$pc.env y las credenciales dentro del tar de n8n).
No lo subas a Drive ni a git. Borralo del pendrive cuando termines.

En la otra PC, pasale esta carpeta a Claude Code y pedile que restaure:
  - n8n-$pc-$fecha.tar.gz  -> %USERPROFILE%\.n8n (con n8n detenido)
  - env-$pc.env            -> Avanzado\Modulo5\scripts\.env
  - $coleccion.snapshot    -> Qdrant (POST /collections/$coleccion/snapshots/upload)
  - memoria-claude\        -> %USERPROFILE%\.claude\projects\<proyecto>\memory (origen en manifiesto.json)
Después: Avanzado\scripts\activar_aqui.ps1 y reconectar las credenciales de Google en http://localhost:5678.

Último commit en ${pc}: $head
Problemas: $(if ($problemas.Count) { "`r`n  - " + ($problemas -join "`r`n  - ") } else { "ninguno" })
"@
$leeme | Out-File (Join-Path $sal "LEEME.txt") -Encoding utf8

Write-Host ""
if ($problemas.Count) {
  Write-Warning "Listo, con observaciones:"
  $problemas | ForEach-Object { Write-Warning "  - $_" }
} else {
  Write-Host "Listo, sin problemas." -ForegroundColor Green
}
Write-Host "Carpeta: $sal"
Write-Host "Lleva secretos: no la subas a Drive ni a git, y borrala del pendrive cuando termines."
