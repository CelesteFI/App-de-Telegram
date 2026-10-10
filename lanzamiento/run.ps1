# run.ps1 - Levanta la app (backend + Mini App), abre el tunel y corre el bot
#
# Como usarlo (en PowerShell, dentro de "Mejora de telegram"):
#   .\lanzamiento\run.ps1
#   (o doble clic en lanzamiento\run.bat)
#
# El token vive fuera del repo, en "token.local.ps1" (esta en .gitignore), asi
# que la carpeta se puede subir a GitHub sin filtrar el secreto. Se toma, en
# orden:
#   1) .\run.ps1 -BotToken 123456789:AAABBB...
#   2) $env:BOT_TOKEN
#   3) la variable $TOKEN_FIJO de token.local.ps1 (recomendado)
#   4) si no hay ninguno, el script lo pide sin mostrarlo en pantalla
#
# OJO: el token es un secreto. Nunca lo pegues en run.ps1 ni en el README;
# si alguna vez se filtra, revocalo en @BotFather (/revoke) y pon el nuevo
# en token.local.ps1.
#
# Si Windows bloquea por Execution Policy:
#   powershell -ExecutionPolicy Bypass -File .\run.ps1
#
# Opciones utiles:
#   -Tunel cloudflare  fuerza Cloudflare Tunnel (por defecto en auto)
#   -Tunel ngrok       fuerza ngrok (ojo: el plan gratis muestra aviso)
#   -Tunel ninguno     solo servidor local (para probar en el navegador)
#   -SinTunel          igual que -Tunel ninguno
#   -SinBot            no lanza el bot, solo la app
#   -Puerto 8080       Puerto fijo en vez de buscar el primero libre
#   -Comprobar         valida quizzes y minijuegos y sale
#   -ExigirIdentidad   apaga el modo de pruebas en navegador (por defecto viene
#                      encendido para que ".\run.ps1" funcione solo, sin flags:
#                      en Telegram se valida tu identidad real y en el navegador
#                      entras como Invitado para probar los juegos).
#   -SinIdentidad      (quedo por compatibilidad, ya no hace falta)
#
# Sobre el tunel: Telegram exige HTTPS. Cloudflare Tunnel da una URL HTTPS
# (https://algo.trycloudflare.com) que NO muestra ninguna pantalla de aviso,
# asi que es la opcion por defecto. ngrok en plan gratis si muestra una
# pantalla "You are about to visit..." que suele dejar la Mini App colgada:
# por eso solo se usa como respaldo.

param(
    [string]$BotToken,                       # token del bot (opcional)
    [string]$NgrokAuthtoken,                 # authtoken de ngrok (opcional)
    [int]$Puerto = 0,                        # 0 = buscar el primero libre
    [ValidateSet("auto", "cloudflare", "ngrok", "ninguno")]
    [string]$Tunel = "auto",
    [switch]$SinTunel,
    [switch]$SinBot,
    [switch]$SinIdentidad,
    [switch]$ExigirIdentidad,
    [switch]$Comprobar
)

$ErrorActionPreference = "Stop"

if ($SinTunel) { $Tunel = "ninguno" }

# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  TOKEN DE TELEGRAM                                                       ║
# ║  El token real NO va aqui (iria a GitHub). Ponlo en el archivo local     ║
# ║  "token.local.ps1", que esta en .gitignore, con una sola linea:          ║
# ║      $TOKEN_FIJO = "123456789:AAABBB..."                                 ║
# ║  Lo sacas de @BotFather -> /newbot, o /token para ver el existente.      ║
# ╚══════════════════════════════════════════════════════════════════════════╝
$TOKEN_FIJO = ""

# ---------- Rutas ------------------------------------------------------------
# Este script vive en "lanzamiento/"; el proyecto es la carpeta de arriba.
# Todo se resuelve en absoluto desde $Root para que funcione igual sin importar
# desde donde se invoque (.\lanzamiento\run.ps1 o doble clic en run.bat).
$LanDir      = $PSScriptRoot
$Root        = Split-Path -Parent $LanDir
$Principal   = Join-Path $Root "app\nucleo\principal.py"
$BotPy       = Join-Path $LanDir "bot.py"
$Ngrok       = "D:\08 Semestre\Servicio Social\ngrok.exe"
$Cloudflared = Join-Path $LanDir "cloudflared.exe"
$PidsFile    = Join-Path $LanDir ".run-pids.json"
$LogsDir     = Join-Path $Root "logs"

if (-not (Test-Path $Principal)) { throw "No encuentro app\nucleo\principal.py en $Root" }
if (-not (Test-Path $LogsDir)) { New-Item -ItemType Directory -Path $LogsDir | Out-Null }
# Los modulos se importan como "app.nucleo.principal": hay que pararse en la raiz.
Set-Location $Root

$Py = (Get-Command python -ErrorAction Stop).Source

# ---------- Comprobar (no pide token ni levanta nada) -------------------------
# Va antes de pedir el token a proposito: para validar el contenido no hace
# falta ningun secreto.
if ($Comprobar) {
    Write-Host "Comprobando el contenido del servidor..." -ForegroundColor Cyan
    & $Py -m app.nucleo.principal --comprobar
    exit $LASTEXITCODE
}

# ---------- Limpiar corridas anteriores --------------------------------------
# Si quedaron el bot, el servidor o un tunel viejos, dan problemas reales:
# dos bots haciendo long-polling (Telegram responde 409) y botones que
# apuntan a una URL muerta. Los cerramos antes de empezar.
function Detener-CorridasAnteriores {
    if (Test-Path $PidsFile) {
        try {
            $guardados = Get-Content $PidsFile -Raw | ConvertFrom-Json
            foreach ($procId in @($guardados.web, $guardados.bot, $guardados.ng)) {
                if ($procId) { Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue }
            }
        } catch { /* archivo ilegible: seguimos */ }
        Remove-Item $PidsFile -ErrorAction SilentlyContinue
    }
    # Respaldo: procesos nuestros que quedaran sueltos (por ruta del proyecto).
    Get-CimInstance Win32_Process -Filter "Name = 'python.exe'" -ErrorAction SilentlyContinue |
        Where-Object { $_.CommandLine -and
            ($_.CommandLine -like "*app.nucleo.principal*" -or $_.CommandLine -like "*bot.py*") } |
        ForEach-Object {
            Write-Host "Cerrando python viejo (PID $($_.ProcessId))..." -ForegroundColor DarkYellow
            Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
        }
    foreach ($nombre in @("ngrok.exe", "cloudflared.exe")) {
        Get-CimInstance Win32_Process -Filter "Name = '$nombre'" -ErrorAction SilentlyContinue |
            ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
    }
}

Detener-CorridasAnteriores

# ---------- Puerto -----------------------------------------------------------
if ($Puerto -eq 0) {
    $Puerto = 8080
    while ($Puerto -lt 8100 -and (Get-NetTCPConnection -LocalPort $Puerto -State Listen -ErrorAction SilentlyContinue)) {
        $Puerto++
    }
    if ($Puerto -ge 8100) { throw "No hay puerto libre entre 8080 y 8099" }
    if ($Puerto -ne 8080) {
        Write-Host "8080 esta ocupado; usare el puerto $Puerto." -ForegroundColor Yellow
    }
}

# ---------- Token de Telegram ------------------------------------------------
# Prioridad: -BotToken -> $env:BOT_TOKEN -> token.local.ps1 -> pregunta oculta.
$TokenLocal = Join-Path $Root "token.local.ps1"
if (Test-Path $TokenLocal) { . $TokenLocal }
if ($SinBot) {
    $BotToken = "sin-bot"
} else {
    if ([string]::IsNullOrWhiteSpace($BotToken)) { $BotToken = $env:BOT_TOKEN }
    if ([string]::IsNullOrWhiteSpace($BotToken)) { $BotToken = $TOKEN_FIJO }
    if ($BotToken -eq "PEGA_AQUI_EL_TOKEN" -or [string]::IsNullOrWhiteSpace($BotToken)) {
        $BotToken = $null
        $seguro = Read-Host "Token de Telegram (@BotFather)" -AsSecureString
        if ($null -ne $seguro) {
            $ptr = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($seguro)
            $BotToken = [System.Runtime.InteropServices.Marshal]::PtrToStringBSTR($ptr)
            [System.Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr)
        }
    }
    if ([string]::IsNullOrWhiteSpace($BotToken)) {
        throw "Falta el token. Pegalo en `$TOKEN_FIJO (arriba), usa -BotToken o escribe -SinBot."
    }
    Write-Host "Token OK (no se muestra)." -ForegroundColor Green
}

# ---------- Funciones de tunel ----------------------------------------------
function Asegurar-Cloudflared {
    if (Test-Path $Cloudflared) { return $Cloudflared }
    $enPath = (Get-Command cloudflared -ErrorAction SilentlyContinue).Source
    if ($enPath) { return $enPath }
    Write-Host "No encontre cloudflared. Lo descargo una sola vez..." -ForegroundColor Yellow
    $url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"
    try {
        Invoke-WebRequest -Uri $url -OutFile $Cloudflared -TimeoutSec 180
    } catch {
        Write-Warning "No se pudo descargar cloudflared: $($_.Exception.Message)"
        return $null
    }
    if (-not (Test-Path $Cloudflared) -or (Get-Item $Cloudflared).Length -lt 1MB) {
        Write-Warning "La descarga de cloudflared quedo incompleta."
        return $null
    }
    return $Cloudflared
}

function Abrir-TunelCloudflare {
    param([int]$Puerto)
    $exe = Asegurar-Cloudflared
    if (-not $exe) { return $null }
    $log = Join-Path $LogsDir "tunel.log"
    $err = Join-Path $LogsDir "tunel.err.log"
    Remove-Item $log, $err -ErrorAction SilentlyContinue
    Write-Host "Abriendo Cloudflare Tunnel..." -ForegroundColor Cyan
    $proc = Start-Process $exe `
        -ArgumentList @("tunnel", "--url", "http://localhost:$Puerto", "--no-autoupdate") `
        -WindowStyle Hidden -PassThru `
        -RedirectStandardOutput $log -RedirectStandardError $err
    $url = ""
    for ($i = 0; $i -lt 45; $i++) {
        Start-Sleep -Milliseconds 700
        if ($proc.HasExited) { break }
        foreach ($archivo in @($err, $log)) {
            if (-not (Test-Path $archivo)) { continue }
            $coincidencia = Select-String -Path $archivo -Pattern "https://[a-z0-9-]+\.trycloudflare\.com" `
                -AllMatches -ErrorAction SilentlyContinue
            if ($coincidencia) { $url = $coincidencia.Matches[0].Value; break }
        }
        if ($url) { break }
    }
    return @{ Proceso = $proc; Url = $url }
}

function Buscar-Ngrok {
    if (Test-Path $Ngrok) { return $Ngrok }
    $enPath = (Get-Command ngrok -ErrorAction SilentlyContinue).Source
    if ($enPath) { return $enPath }
    return $null
}

function Abrir-TunelNgrok {
    param([int]$Puerto)
    $exe = Buscar-Ngrok
    if (-not $exe) {
        Write-Warning "No encontre ngrok.exe en $Ngrok ni en PATH."
        return $null
    }
    if (-not [string]::IsNullOrWhiteSpace($NgrokAuthtoken)) {
        Write-Host "Configurando authtoken de ngrok..." -ForegroundColor Yellow
        & $exe config add-authtoken $NgrokAuthtoken
        if ($LASTEXITCODE -ne 0) { throw "ngrok no acepto el authtoken (revisa -NgrokAuthtoken)" }
    }
    Write-Host "Abriendo ngrok..." -ForegroundColor Cyan
    $proc = Start-Process $exe -ArgumentList @("http", "$Puerto") -WindowStyle Hidden -PassThru
    $url = ""
    for ($i = 0; $i -lt 60; $i++) {
        Start-Sleep -Seconds 1
        if ($proc.HasExited) { break }
        try {
            $tunnels = Invoke-RestMethod -Uri "http://127.0.0.1:4040/api/tunnels" -ErrorAction Stop
            $url = $tunnels.tunnels | Where-Object { $_.public_url -like "https://*" } |
                Select-Object -First 1 -ExpandProperty public_url
        } catch { /* aun no esta listo */ }
        if ($url) { break }
    }
    return @{ Proceso = $proc; Url = $url }
}

# ---------- 1) Servidor + Mini App ------------------------------------------
$ServerLog = Join-Path $LogsDir "server.log"
$ServerErr = Join-Path $LogsDir "server.err.log"

# El token TIENE que estar en el entorno ANTES de arrancar el servidor: es el
# que valida la firma (initData) de cada persona que entra desde Telegram.
$env:PUERTO = "$Puerto"
if (-not $SinBot) { $env:BOT_TOKEN = $BotToken }
if (-not $ExigirIdentidad) {
    $env:DEV_AUTHPASS = "1"
    Write-Host "Modo de pruebas en navegador: activado (Telegram sigue validando tu identidad real)." -ForegroundColor DarkCyan
} elseif ($SinIdentidad) {
    $env:DEV_AUTHPASS = "1"
    Write-Host "AVISO: identidad apagada. Entra cualquiera como usuario 1." -ForegroundColor Yellow
}
Write-Host "Sirviendo app + backend en http://localhost:$Puerto ..." -ForegroundColor Cyan
$ServerArg = '"-m" "app.nucleo.principal" "--puerto" "' + $Puerto + '"'
$web = Start-Process $Py -ArgumentList $ServerArg -WorkingDirectory $Root -WindowStyle Hidden -PassThru `
    -RedirectStandardOutput $ServerLog -RedirectStandardError $ServerErr

Start-Sleep -Seconds 2
if ($web.HasExited) {
    Write-Host "---- server.log ----" -ForegroundColor Red
    if (Test-Path $ServerLog) { Get-Content $ServerLog -Tail 25 }
    Write-Host "---- server.err.log ----" -ForegroundColor Red
    if (Test-Path $ServerErr) { Get-Content $ServerErr -Tail 25 }
    throw "El servidor no arranco (exit code $($web.ExitCode)). Revisa los logs de arriba."
}

$espera = 0
while ($espera -lt 20) {
    try {
        $hit = Invoke-WebRequest -Uri "http://localhost:$Puerto/api/config" -UseBasicParsing -TimeoutSec 5
        if ($hit.StatusCode -eq 200) { break }
    } catch { /* aun no responde */ }
    Start-Sleep -Milliseconds 400
    $espera++
}
try {
    $pagina = Invoke-WebRequest -Uri "http://localhost:$Puerto/" -UseBasicParsing -TimeoutSec 5
    if ($pagina.StatusCode -ne 200 -or $pagina.Content -notmatch "Repaso de Ecuaciones") {
        throw "el puerto $Puerto no sirve la app"
    }
} catch {
    Stop-Process -Id $web.Id -Force -ErrorAction SilentlyContinue
    throw "La app no responde en http://localhost:$Puerto : $($_.Exception.Message)"
}
Write-Host "App local OK (http://localhost:$Puerto)." -ForegroundColor Green

# ---------- 1.5) Que el servidor sepa validar la identidad ------------------
if (-not $SinBot -and -not $SinIdentidad) {
    $chequeo = Start-Process $Py `
        -ArgumentList ('"-m" "app.nucleo.principal" "--puerto" "' + $Puerto + '" "--chequeo-identidad"') `
        -WorkingDirectory $Root -WindowStyle Hidden -PassThru -Wait `
        -RedirectStandardOutput "$env:TEMP\chequeo_ok.log" -RedirectStandardError "$env:TEMP\chequeo_err.log"
    if (Test-Path "$env:TEMP\chequeo_ok.log") { Get-Content "$env:TEMP\chequeo_ok.log" | ForEach-Object { Write-Host $_ } }
    if ($chequeo.ExitCode -ne 0) {
        if (Test-Path "$env:TEMP\chequeo_err.log") { Get-Content "$env:TEMP\chequeo_err.log" | ForEach-Object { Write-Host $_ -ForegroundColor Red } }
        Stop-Process -Id $web.Id -Force -ErrorAction SilentlyContinue
        throw "El servidor no puede validar la identidad de Telegram. Corrige el token antes de seguir."
    }
}

# ---------- 2) Tunel --------------------------------------------------------
$ng = $null
$publicUrl = ""
$tunelUsado = "ninguno"

if ($Tunel -ne "ninguno") {
    if ($Tunel -eq "auto" -or $Tunel -eq "cloudflare") {
        $res = Abrir-TunelCloudflare -Puerto $Puerto
        if ($res -and $res.Url) {
            $ng = $res.Proceso
            $publicUrl = $res.Url
            $tunelUsado = "cloudflare"
            Write-Host "URL publica HTTPS (Cloudflare): $publicUrl" -ForegroundColor Green
        } else {
            if ($res -and $res.Proceso -and -not $res.Proceso.HasExited) {
                Stop-Process -Id $res.Proceso.Id -Force -ErrorAction SilentlyContinue
            }
            if ($Tunel -eq "cloudflare") {
                Stop-Process -Id $web.Id -Force -ErrorAction SilentlyContinue
                throw "Cloudflare Tunnel no publico una URL. Revisa tunel.err.log."
            }
            Write-Warning "Cloudflare Tunnel no quedo listo; probare con ngrok."
        }
    }

    if (-not $publicUrl -and ($Tunel -eq "auto" -or $Tunel -eq "ngrok")) {
        $res = Abrir-TunelNgrok -Puerto $Puerto
        if ($res -and $res.Url) {
            $ng = $res.Proceso
            $publicUrl = $res.Url
            $tunelUsado = "ngrok"
            Write-Host "URL publica HTTPS (ngrok): $publicUrl" -ForegroundColor Green
            Write-Host "OJO: el plan gratis de ngrok muestra una pantalla de aviso en el navegador." -ForegroundColor DarkGray
            Write-Host "Para que la Mini App no se cuelgue en Telegram, usa -Tunel cloudflare." -ForegroundColor DarkGray
        } else {
            if ($res -and $res.Proceso -and -not $res.Proceso.HasExited) {
                Stop-Process -Id $res.Proceso.Id -Force -ErrorAction SilentlyContinue
            }
            if ($Tunel -eq "ngrok") {
                Stop-Process -Id $web.Id -Force -ErrorAction SilentlyContinue
                throw "ngrok no publico una URL HTTPS. Revisa el authtoken."
            }
            Write-Warning "Tampoco pude abrir ngrok. Sigo sin tunel (solo servira en el navegador local)."
        }
    }

    if ($publicUrl) {
        # La primera respuesta puede ser 530 mientras Cloudflare termina de
        # conectar el tunel con el servidor local: se reintenta unos segundos.
        $cabeceras = @{}
        if ($tunelUsado -eq "ngrok") { $cabeceras["ngrok-skip-browser-warning"] = "1" }
        $verificada = $false
        for ($i = 0; $i -lt 12; $i++) {
            try {
                $pub = Invoke-WebRequest -Uri $publicUrl -UseBasicParsing -TimeoutSec 12 -Headers $cabeceras
                if ($pub.Content -match "Repaso de Ecuaciones") {
                    Write-Host "URL publica verificada (HTTPS): $publicUrl" -ForegroundColor Green
                    $verificada = $true
                    break
                }
                Write-Host "La URL publica responde, pero aun no parece la app (intento $($i + 1))..." -ForegroundColor DarkGray
            } catch {
                Write-Host "Esperando al tunel (intento $($i + 1)): $($_.Exception.Message)" -ForegroundColor DarkGray
            }
            Start-Sleep -Seconds 2
        }
        if (-not $verificada) {
            Write-Warning "No pude verificar la URL publica tras varios intentos; suele ser transitorio. Sigo adelante."
        }
    }
}

# ---------- 3) Bot ----------------------------------------------------------
if ($SinBot) {
    Write-Host "Sin bot: la app queda en http://localhost:$Puerto . Ctrl+C para salir." -ForegroundColor Cyan
    try { while ($true) { Start-Sleep -Seconds 5 } }
    finally {
        Stop-Process -Id $web.Id -Force -ErrorAction SilentlyContinue
        if ($ng -and -not $ng.HasExited) { Stop-Process -Id $ng.Id -Force -ErrorAction SilentlyContinue }
    }
}

& $Py -c "import telegram" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Falta python-telegram-bot, instalando..." -ForegroundColor Yellow
    & $Py -m pip install python-telegram-bot
    if ($LASTEXITCODE -ne 0) { throw "No se pudo instalar python-telegram-bot" }
}

$env:WEBAPP_URL = if ($publicUrl) { $publicUrl } else { "http://localhost:$Puerto" }
if (-not $publicUrl) {
    Write-Warning "Sin tunel: el bot apuntara a http://localhost:$Puerto y Telegram NO podra abrirlo."
}
Write-Host "Lanzando bot.py ... Ctrl+C para terminar." -ForegroundColor Cyan

# Guardamos los PID para que la proxima corrida cierre lo que quede suelto.
@{ web = $web.Id; ng = if ($ng) { $ng.Id } else { $null } } | ConvertTo-Json |
    Set-Content -Path $PidsFile -Encoding UTF8

try {
    & $Py $BotPy
} finally {
    if ($web -and -not $web.HasExited) { Stop-Process -Id $web.Id -Force -ErrorAction SilentlyContinue }
    if ($ng  -and -not $ng.HasExited)  { Stop-Process -Id $ng.Id  -Force -ErrorAction SilentlyContinue }
    Remove-Item $PidsFile -ErrorAction SilentlyContinue
    Write-Host "Servidor y tunel detenidos." -ForegroundColor Green
}
