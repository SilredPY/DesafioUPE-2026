<#
.SYNOPSIS
  Levanta Ñangarekó IA completo (base de datos, API, web) con Docker.
.EXAMPLE
  .\scripts\iniciar.ps1                 # normal, en http://localhost
  .\scripts\iniciar.ps1 -Demo           # tormenta simulada + datos de ejemplo
  .\scripts\iniciar.ps1 -Demo -Publico  # además, link HTTPS público para celulares
  .\scripts\iniciar.ps1 -Detener        # apaga todo (los datos se conservan)
#>
param([switch]$Demo, [switch]$Publico, [switch]$Detener)
# No usar 'Stop': Docker escribe su progreso en stderr y PowerShell 5.1 lo tomaría como error.
# Los fallos se detectan con $LASTEXITCODE.
$ErrorActionPreference = 'Continue'
Set-Location (Split-Path $PSScriptRoot -Parent)

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    throw 'No se encontró Docker. Instalá Docker Desktop: https://www.docker.com/products/docker-desktop/'
}
docker info *> $null
if ($LASTEXITCODE -ne 0) { throw 'Docker no está corriendo: abrí Docker Desktop, esperá que inicie y reintentá.' }

if ($Detener) {
    docker compose --profile publico stop
    Write-Host 'Ñangarekó IA detenido.' -ForegroundColor Green
    exit 0
}

if (-not (Test-Path .env)) {
    Copy-Item .env.example .env
    Write-Host 'Se creó .env: completá ANTHROPIC_API_KEY para activar la IA (opcional).' -ForegroundColor Yellow
}
# El modo se guarda en .env (Compose lo lee siempre): así un "docker compose up" posterior no lo apaga sin querer.
$modo = if ($Demo) { 'tormenta' } else { '' }
$lineas = [System.Collections.Generic.List[string]](Get-Content .env)
$i = $lineas.FindIndex({ param($l) $l -match '^CLIMA_DEMO=' })
if ($i -ge 0) { $lineas[$i] = "CLIMA_DEMO=$modo" } else { $lineas.Add("CLIMA_DEMO=$modo") }
[IO.File]::WriteAllLines((Join-Path (Get-Location) '.env'), $lineas)  # UTF-8 sin BOM
Remove-Item Env:CLIMA_DEMO -ErrorAction SilentlyContinue  # que mande .env, no una variable vieja de la sesión

$perfil = if ($Publico) { @('--profile', 'publico') } else { @() }
docker compose @perfil up -d --build
if ($LASTEXITCODE -ne 0) { throw 'Falló docker compose up. Revisá el mensaje de arriba.' }

Write-Host 'Esperando a que la API responda...'
$lista = $false
for ($i = 0; $i -lt 60 -and -not $lista; $i++) {
    try { Invoke-RestMethod http://localhost/api/salud -TimeoutSec 2 -ErrorAction Stop | Out-Null; $lista = $true }
    catch { Start-Sleep 2 }
}
if (-not $lista) { throw 'La API no respondió. Mirá los logs con: docker compose logs api' }

if ($Demo) {
    docker compose exec -T db psql -q -U naangareko -f /demo/demo.sql
    if ($LASTEXITCODE -ne 0) { throw 'No se pudieron cargar los datos de ejemplo.' }
    Write-Host 'Datos de ejemplo cargados (las Zonas Rojas duran ~2 h).' -ForegroundColor Green
}

Write-Host ''
Write-Host 'Ñangarekó IA está listo:' -ForegroundColor Green
Write-Host '  App en esta computadora:  http://localhost'
Write-Host '  API (Swagger):            http://localhost:8000/docs'
$ips = Get-NetIPAddress -AddressFamily IPv4 -ErrorAction SilentlyContinue |
    Where-Object { $_.IPAddress -notmatch '^(127|169\.254)\.' -and $_.InterfaceAlias -notmatch 'vEthernet|WSL|Loopback' }
foreach ($ip in $ips) { Write-Host "  Otros equipos de tu red:  http://$($ip.IPAddress)  (sin cámara/GPS: requieren HTTPS)" }

if ($Publico) {
    # Se pregunta al propio túnel (no a los logs, que guardan URLs viejas de arranques anteriores).
    $url = $null
    for ($i = 0; $i -lt 30 -and -not $url; $i++) {
        try { $url = (Invoke-RestMethod http://localhost:2000/quicktunnel -TimeoutSec 2 -ErrorAction Stop).hostname } catch {}
        if (-not $url) { Start-Sleep 2 }
    }
    if ($url) { Write-Host "  Link público (celulares): https://$url" -ForegroundColor Cyan }
    else { Write-Host '  El túnel tarda en arrancar: docker compose logs tunel' -ForegroundColor Yellow }
}
