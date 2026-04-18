# PixelForge PowerShell Client
# Uso: . .\pixelforge.ps1   (importar funciones)
# O:   .\pixelforge.ps1     (ejecutar demo)

$PF_URL = "http://localhost:3000"

# ── Funciones base ─────────────────────────────────────────

function PF-Cmd {
    param([string]$cmd)
    $body = @{ cmd = $cmd } | ConvertTo-Json
    try {
        $r = Invoke-RestMethod -Uri "$PF_URL/cmd" -Method POST `
             -Body $body -ContentType "application/json"
        Write-Host "  OK: $cmd" -ForegroundColor Green
        return $r
    } catch {
        Write-Host "  ERR: $_" -ForegroundColor Red
    }
}

function PF-Batch {
    param([string[]]$commands)
    $body = @{ commands = $commands } | ConvertTo-Json
    try {
        $r = Invoke-RestMethod -Uri "$PF_URL/batch" -Method POST `
             -Body $body -ContentType "application/json"
        Write-Host "  BATCH OK: $($commands.Count) comandos" -ForegroundColor Cyan
        return $r
    } catch {
        Write-Host "  ERR batch: $_" -ForegroundColor Red
    }
}

function PF-Status {
    try {
        $r = Invoke-RestMethod -Uri "$PF_URL/status"
        Write-Host "  Server: OK (port $($r.port))" -ForegroundColor Green
    } catch {
        Write-Host "  Server: NO disponible en $PF_URL" -ForegroundColor Red
    }
}

# ── Helpers de alto nivel ───────────────────────────────────

function PF-SetPixel {
    param([int]$x, [int]$y, [string]$color = "")
    if ($color) { PF-Cmd "color $color" }
    PF-Cmd "setpixel $x $y"
}

function PF-DrawLine {
    param([int]$x0,[int]$y0,[int]$x1,[int]$y1,[string]$color="")
    if ($color) { PF-Cmd "color $color" }
    PF-Cmd "drawline $x0 $y0 $x1 $y1"
}

function PF-FillRect {
    param([int]$x0,[int]$y0,[int]$x1,[int]$y1,[string]$color="")
    if ($color) { PF-Cmd "color $color" }
    PF-Cmd "fillrect $x0 $y0 $x1 $y1"
}

function PF-Circle {
    param([int]$cx,[int]$cy,[int]$r,[string]$color="")
    if ($color) { PF-Cmd "color $color" }
    PF-Cmd "circle $cx $cy $r"
}

function PF-Clear    { PF-Cmd "clear" }
function PF-AddFrame { PF-Cmd "addframe" }
function PF-NextFrame{ PF-Cmd "nextframe" }
function PF-Export   { PF-Cmd "export" }
function PF-SetMode  { param([string]$m) PF-Cmd "setmode $m" }
function PF-SetSize  { param([int]$s)    PF-Cmd "setsize $s" }
function PF-SetBg    { param([string]$c) PF-Cmd "setbg $c" }
function PF-Zoom     { param([int]$z)    PF-Cmd "zoom $z" }

# ── Demo: dibuja un personaje simple 32x32 ──────────────────

function PF-Demo {
    Write-Host "`n  PixelForge Demo — Personaje pixel art" -ForegroundColor Cyan

    PF-Status
    Start-Sleep -Milliseconds 300

    PF-Batch @(
        "setsize 32",
        "setbg #1a1a2e",
        "clear"
    )
    Start-Sleep -Milliseconds 400

    # Cabeza (blanco)
    PF-FillRect 12 4 19 11 "#f5c5a3"
    Start-Sleep -Milliseconds 200

    # Ojos
    PF-Batch @(
        "color #1a1a2e",
        "setpixel 14 6",
        "setpixel 17 6"
    )
    Start-Sleep -Milliseconds 200

    # Boca
    PF-Batch @(
        "color #c0392b",
        "setpixel 14 9",
        "setpixel 15 10",
        "setpixel 16 10",
        "setpixel 17 9"
    )
    Start-Sleep -Milliseconds 200

    # Cuerpo
    PF-FillRect 11 12 20 20 "#3498db"
    Start-Sleep -Milliseconds 200

    # Brazos
    PF-Batch @(
        "color #3498db",
        "fillrect 8 12 10 18",
        "fillrect 21 12 23 18"
    )
    Start-Sleep -Milliseconds 200

    # Piernas
    PF-Batch @(
        "color #2c3e50",
        "fillrect 11 21 15 27",
        "fillrect 16 21 20 27"
    )
    Start-Sleep -Milliseconds 200

    # Zapatos
    PF-Batch @(
        "color #1a1a2e",
        "fillrect 10 28 15 29",
        "fillrect 16 28 21 29"
    )

    Write-Host "  Demo completo!" -ForegroundColor Green
}

# ── Entry point ─────────────────────────────────────────────

# Si se ejecuta directo (no importado), corre el demo
if ($MyInvocation.InvocationName -ne '.') {
    Write-Host "
    ██████╗ ██╗██╗  ██╗███████╗██╗     ███████╗
    ██╔══██╗██║╚██╗██╔╝██╔════╝██║     ██╔════╝
    ██████╔╝██║ ╚███╔╝ █████╗  ██║     ███████╗
    ██╔═══╝ ██║ ██╔██╗ ██╔══╝  ██║     ╚════██║
    ██║     ██║██╔╝ ██╗███████╗███████╗███████║
    ╚═╝     ╚═╝╚═╝  ╚═╝╚══════╝╚══════╝╚══════╝
    " -ForegroundColor Red

    Write-Host "  Importa con:  . .\pixelforge.ps1" -ForegroundColor Yellow
    Write-Host "  Luego usa:    PF-Demo, PF-SetPixel, PF-DrawLine, etc.`n"

    PF-Demo
}