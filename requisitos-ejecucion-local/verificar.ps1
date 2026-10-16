<#
.SYNOPSIS
  Revisa si esta computadora tiene todo lo necesario para correr Ñangarekó IA y ofrece instalar lo que falte.
.EXAMPLE
  .\requisitos-ejecucion-local\verificar.ps1               # revisa y pregunta antes de instalar cada cosa
  .\requisitos-ejecucion-local\verificar.ps1 -SoloRevisar  # solo muestra el estado, no instala nada
#>
param([switch]$SoloRevisar)
# No usar 'Stop': docker y winget escriben progreso en stderr y PowerShell 5.1 lo tomaría como error.
$ErrorActionPreference = 'Continue'
Set-Location (Split-Path $PSScriptRoot -Parent)

function Ok([string]$detalle) { [pscustomobject]@{ Ok = $true; Detalle = $detalle } }
function Falta([string]$detalle) { [pscustomobject]@{ Ok = $false; Detalle = $detalle } }
function Hay([string]$comando) { [bool](Get-Command $comando -ErrorAction SilentlyContinue) }
function RecargarPath {
    # Lo recién instalado no aparece en el PATH de esta ventana hasta releerlo.
    $env:Path = [Environment]::GetEnvironmentVariable('Path', 'Machine') + ';' + [Environment]::GetEnvironmentVariable('Path', 'User')
}
function Winget([string]$id) {
    if (-not (Hay winget)) {
        Write-Host '          winget no está disponible en esta PC: instalalo a mano desde el link de arriba.' -ForegroundColor Yellow
        return
    }
    winget install --id $id -e --accept-package-agreements --accept-source-agreements
}
function Version([string]$texto) {
    if ($texto -match '(\d+)\.(\d+)') { [version]"$($Matches[1]).$($Matches[2])" } else { $null }
}

$PUERTOS = 80, 8000, 5432, 2000
# Si el puerto lo tiene Docker, es porque Ñangarekó ya está corriendo: no es un conflicto.
$PROCESOS_DOCKER = 'com.docker.backend', 'com.docker.vpnkit', 'vpnkit', 'wslrelay', 'docker-proxy'

# ─────────────────────────────────────────────────────────────────────────────
#  LISTA DE REQUISITOS
#  Para sumar uno nuevo: agregá un bloque acá Y una fila en README.md (misma carpeta),
#  y anotalo en el "Historial de cambios" del README.
# ─────────────────────────────────────────────────────────────────────────────
$requisitos = @(
    @{
        Nombre      = 'Windows 10/11 de 64 bits'
        Para        = 'Docker Desktop solo corre en Windows 10 (versión 2004 o más nueva) u 11, de 64 bits'
        Obligatorio = $true
        Link        = 'https://www.microsoft.com/software-download/windows11'
        Probar      = {
            $v = [Environment]::OSVersion.Version
            if ([Environment]::Is64BitOperatingSystem -and $v.Build -ge 19041) { Ok "compilación $($v.Build)" }
            else { Falta "compilación $($v.Build): actualizá Windows" }
        }
    },
    @{
        Nombre      = 'WSL 2'
        Para        = 'Docker Desktop lo usa para correr los contenedores Linux'
        Obligatorio = $true
        Link        = 'https://learn.microsoft.com/windows/wsl/install'
        Probar      = {
            if (-not (Hay wsl)) { return Falta 'no instalado' }
            wsl --status *> $null
            if ($LASTEXITCODE -eq 0) { Ok 'instalado' } else { Falta 'no instalado' }
        }
        Instalar    = {
            Start-Process wsl -ArgumentList '--install', '--no-distribution' -Verb RunAs -Wait
            Write-Host '          Reiniciá la computadora para terminar de instalar WSL y volvé a correr este script.' -ForegroundColor Yellow
        }
    },
    @{
        Nombre      = 'Git'
        Para        = 'Descargar la repo y traer las actualizaciones del equipo (git pull)'
        Obligatorio = $true
        Link        = 'https://git-scm.com/download/win'
        Probar      = { if (Hay git) { Ok ((git --version) -replace 'git version ', '') } else { Falta 'no instalado' } }
        Instalar    = { Winget 'Git.Git' }
    },
    @{
        Nombre      = 'Docker Desktop'
        Para        = 'Corre la base de datos, la API, la web y el link público. Reemplaza instalar Python, Node y PostgreSQL'
        Obligatorio = $true
        Link        = 'https://www.docker.com/products/docker-desktop/'
        Probar      = { if (Hay docker) { Ok ((docker --version) -replace 'Docker version ', '') } else { Falta 'no instalado' } }
        Instalar    = {
            Winget 'Docker.DockerDesktop'
            Write-Host '          Abrí Docker Desktop una vez y aceptá los términos (puede pedir reiniciar).' -ForegroundColor Yellow
        }
    },
    @{
        Nombre      = 'Docker Compose v2'
        Para        = 'Los scripts usan "docker compose" para levantar todos los servicios juntos'
        Obligatorio = $true
        Link        = 'https://docs.docker.com/compose/install/'
        Probar      = {
            if (-not (Hay docker)) { return Falta 'requiere Docker Desktop' }
            $v = docker compose version --short 2>$null
            if ($LASTEXITCODE -eq 0) { Ok $v } else { Falta 'no disponible: actualizá Docker Desktop' }
        }
    },
    @{
        Nombre      = 'Docker Desktop abierto'
        Para        = 'Los scripts de iniciar y detener necesitan que Docker esté corriendo'
        Obligatorio = $true
        Link        = 'https://docs.docker.com/desktop/'
        Accion      = 'Abrir Docker Desktop'
        Probar      = {
            if (-not (Hay docker)) { return Falta 'requiere Docker Desktop' }
            docker info *> $null
            if ($LASTEXITCODE -eq 0) { Ok 'corriendo' } else { Falta 'está cerrado o todavía arrancando' }
        }
        Instalar    = {
            $exe = Join-Path $env:ProgramFiles 'Docker\Docker\Docker Desktop.exe'
            if (-not (Test-Path $exe)) { Write-Host "          No se encontró $exe" -ForegroundColor Yellow; return }
            Start-Process $exe
            Write-Host '          Esperando a que Docker arranque (hasta 2 minutos)...'
            for ($i = 0; $i -lt 60; $i++) {
                docker info *> $null
                if ($LASTEXITCODE -eq 0) { break }
                Start-Sleep 2
            }
        }
    },
    @{
        Nombre      = "Puertos libres ($($PUERTOS -join ', '))"
        Para        = '80: la app · 8000: la API · 5432: la base de datos · 2000: el link público'
        Obligatorio = $true
        Link        = 'https://learn.microsoft.com/windows-server/administration/windows-commands/netstat'
        Ayuda       = 'Cerrá el programa que usa el puerto (suelen ser IIS, XAMPP, Apache, Skype u otro PostgreSQL).'
        Probar      = {
            $ocupados = foreach ($p in $PUERTOS) {
                $c = Get-NetTCPConnection -State Listen -LocalPort $p -ErrorAction SilentlyContinue | Select-Object -First 1
                if ($c) {
                    $proc = (Get-Process -Id $c.OwningProcess -ErrorAction SilentlyContinue).ProcessName
                    if ($PROCESOS_DOCKER -notcontains $proc) { "$p (lo usa $proc)" }
                }
            }
            if ($ocupados) { Falta "ocupados: $($ocupados -join ', ')" } else { Ok 'libres o usados por Ñangarekó' }
        }
    },
    @{
        Nombre      = 'Espacio en disco (6 GB libres)'
        Para        = 'Las imágenes de Docker y la base de datos ocupan unos 4 GB'
        Obligatorio = $true
        Link        = 'https://support.microsoft.com/windows/free-up-drive-space-in-windows-85529ccb-c365-490d-b548-831022bc9b32'
        Probar      = {
            $libre = [math]::Round((Get-PSDrive $env:SystemDrive.TrimEnd(':')).Free / 1GB, 1)
            if ($libre -ge 6) { Ok "$libre GB libres en $env:SystemDrive" } else { Falta "solo $libre GB libres en $env:SystemDrive" }
        }
    },
    @{
        Nombre      = 'Conexión a internet'
        Para        = 'Descargar las imágenes la primera vez, el pronóstico del clima y el link público para celulares'
        Obligatorio = $true
        Link        = 'https://open-meteo.com/'
        Probar      = {
            try {
                Invoke-WebRequest 'https://api.open-meteo.com/v1/forecast?latitude=-25.5&longitude=-54.6&current=temperature_2m' `
                    -UseBasicParsing -TimeoutSec 8 | Out-Null
                Ok 'conectado'
            } catch { Falta 'sin conexión o bloqueada por un firewall' }
        }
    },
    @{
        Nombre      = 'Memoria RAM (8 GB recomendado)'
        Para        = 'Con menos, Docker anda lento con todos los servicios abiertos'
        Obligatorio = $false
        Link        = 'https://docs.docker.com/desktop/setup/install/windows-install/'
        Probar      = {
            $gb = [math]::Round((Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory / 1GB)
            if ($gb -ge 8) { Ok "$gb GB" } else { Falta "$gb GB: puede andar lento" }
        }
    },
    @{
        Nombre      = 'Node.js 24 o más nuevo'
        Para        = 'Solo para programar el frontend con recarga en caliente (npm run dev)'
        Obligatorio = $false
        Link        = 'https://nodejs.org/'
        Probar      = {
            if (-not (Hay node)) { return Falta 'no instalado' }
            $v = node --version
            if ((Version $v) -ge [version]'24.0') { Ok $v } else { Falta "$v es viejo" }
        }
        Instalar    = { Winget 'OpenJS.NodeJS.LTS' }
    },
    @{
        Nombre      = 'Python 3.12 o más nuevo'
        Para        = 'Solo para correr los tests del backend sin Docker'
        Obligatorio = $false
        Link        = 'https://www.python.org/downloads/'
        Probar      = {
            # El "python" de la Microsoft Store es un acceso directo vacío: se valida que responda una versión.
            $v = if (Hay python) { python -c "import sys; print('%d.%d' % sys.version_info[:2])" 2>$null } else { '' }
            $ver = Version "$v"
            if ($ver -and $ver -ge [version]'3.12') { Ok $v } elseif ($ver) { Falta "$v es viejo" } else { Falta 'no instalado' }
        }
        Instalar    = { Winget 'Python.Python.3.12' }
    }
)

Write-Host ''
Write-Host 'Requisitos para correr Ñangarekó IA en esta computadora' -ForegroundColor Cyan
Write-Host '(detalle de cada uno en requisitos-ejecucion-local\README.md)'
Write-Host ''

$faltan = 0
foreach ($r in $requisitos) {
    $res = & $r.Probar
    $opcional = if ($r.Obligatorio) { '' } else { ' (opcional)' }
    if ($res.Ok) {
        Write-Host "  [OK]    $($r.Nombre)$opcional — $($res.Detalle)" -ForegroundColor Green
        continue
    }
    $color = if ($r.Obligatorio) { 'Red' } else { 'Yellow' }
    $marca = if ($r.Obligatorio) { '[FALTA]' } else { '[--]   ' }
    Write-Host "  $marca $($r.Nombre)$opcional — $($res.Detalle)" -ForegroundColor $color
    Write-Host "          Para qué: $($r.Para)"
    if ($r.Ayuda) { Write-Host "          Qué hacer: $($r.Ayuda)" }
    Write-Host "          Más info: $($r.Link)"

    if ($r.Instalar -and -not $SoloRevisar) {
        $accion = if ($r.Accion) { $r.Accion } else { 'Instalarlo' }
        if ((Read-Host "          ¿$accion ahora? (s/n)") -match '^\s*[sS]') {
            & $r.Instalar
            RecargarPath
            $res = & $r.Probar
            if ($res.Ok) { Write-Host "          Listo — $($res.Detalle)" -ForegroundColor Green }
            else { Write-Host "          Todavía falta — $($res.Detalle). Puede hacer falta reiniciar." -ForegroundColor Yellow }
        }
    }
    if (-not $res.Ok -and $r.Obligatorio) { $faltan++ }
}

Write-Host ''
if ($faltan -eq 0) {
    Write-Host 'Todo listo. Para arrancar: doble clic en scripts\iniciar.cmd (o scripts\demo-publico.cmd para presentar).' -ForegroundColor Green
    exit 0
}
Write-Host "Faltan $faltan requisito(s) obligatorio(s). Resolvelos y volvé a correr este script." -ForegroundColor Red
exit 1
