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

function PF-Brush {
    param([int]$size)
    PF-Cmd "brush $size"
}

function PF-Dot {
    param([int]$cx,[int]$cy,[object]$sizeOrColor=$null,[string]$color="")
    $cmd = "dot $cx $cy"
    if ($null -ne $sizeOrColor -and "$sizeOrColor" -ne "") {
        $value = [string]$sizeOrColor
        if ($value.StartsWith("#") -or $value -eq "transparent") {
            $color = $value
        } else {
            $cmd += " $value"
        }
    }
    if ($color) { $cmd += " $color" }
    PF-Cmd $cmd
}

function PF-Block {
    param([int]$cx,[int]$cy,[int]$w,[int]$h,[string]$color="")
    $cmd = "block $cx $cy $w $h"
    if ($color) { $cmd += " $color" }
    PF-Cmd $cmd
}

function PF-RectXY {
    param([int]$x,[int]$y,[int]$w,[int]$h,[string]$color="")
    $cmd = "rectxy $x $y $w $h"
    if ($color) { $cmd += " $color" }
    PF-Cmd $cmd
}

function PF-FillCircle {
    param([int]$cx,[int]$cy,[int]$r,[string]$color="")
    $cmd = "fillcircle $cx $cy $r"
    if ($color) { $cmd += " $color" }
    PF-Cmd $cmd
}

function PF-Ellipse {
    param([int]$cx,[int]$cy,[int]$rx,[int]$ry,[string]$color="")
    $cmd = "ellipse $cx $cy $rx $ry"
    if ($color) { $cmd += " $color" }
    PF-Cmd $cmd
}

function PF-FillEllipse {
    param([int]$cx,[int]$cy,[int]$rx,[int]$ry,[string]$color="")
    $cmd = "fillellipse $cx $cy $rx $ry"
    if ($color) { $cmd += " $color" }
    PF-Cmd $cmd
}

function PF-Polyline {
    param([Parameter(ValueFromRemainingArguments=$true)][object[]]$Args)
    if (-not $Args -or $Args.Count -lt 4) {
        Write-Host "  Usage: PF-Polyline x1 y1 x2 y2 [... color]" -ForegroundColor Yellow
        return
    }
    PF-Cmd ("polyline " + (($Args | ForEach-Object { [string]$_ }) -join " "))
}

function PF-Stroke {
    param([int]$size)
    PF-Cmd "stroke $size"
}

function PF-Polygon {
    param([Parameter(ValueFromRemainingArguments=$true)][object[]]$Args)
    if (-not $Args -or $Args.Count -lt 6) {
        Write-Host "  Usage: PF-Polygon x1 y1 x2 y2 x3 y3 [... color]" -ForegroundColor Yellow
        return
    }
    PF-Cmd ("polygon " + (($Args | ForEach-Object { [string]$_ }) -join " "))
}

function PF-FillPoly {
    param([Parameter(ValueFromRemainingArguments=$true)][object[]]$Args)
    if (-not $Args -or $Args.Count -lt 6) {
        Write-Host "  Usage: PF-FillPoly x1 y1 x2 y2 x3 y3 [... color]" -ForegroundColor Yellow
        return
    }
    PF-Cmd ("fillpoly " + (($Args | ForEach-Object { [string]$_ }) -join " "))
}

function PF-Arc {
    param([int]$cx,[int]$cy,[int]$rx,[int]$ry,[int]$startDeg,[int]$endDeg,[string]$color="")
    $cmd = "arc $cx $cy $rx $ry $startDeg $endDeg"
    if ($color) { $cmd += " $color" }
    PF-Cmd $cmd
}

function PF-Curve {
    param([int]$x0,[int]$y0,[int]$cx,[int]$cy,[int]$x1,[int]$y1,[string]$color="")
    $cmd = "curve $x0 $y0 $cx $cy $x1 $y1"
    if ($color) { $cmd += " $color" }
    PF-Cmd $cmd
}

function PF-Gradient {
    param([int]$x,[int]$y,[int]$w,[int]$h,[string]$from,[string]$to,[string]$direction="v")
    PF-Cmd "gradient $x $y $w $h $from $to $direction"
}

function PF-Copy {
    param([int]$x,[int]$y,[int]$w,[int]$h)
    PF-Cmd "copy $x $y $w $h"
}

function PF-Paste {
    param([int]$x,[int]$y)
    PF-Cmd "paste $x $y"
}

function PF-Translate {
    param([int]$x,[int]$y,[int]$w,[int]$h,[int]$dx,[int]$dy)
    PF-Cmd "translate $x $y $w $h $dx $dy"
}

function PF-MirrorX {
    param([int]$x,[int]$y,[int]$w,[int]$h)
    PF-Cmd "mirrorx $x $y $w $h"
}

function PF-MirrorY {
    param([int]$x,[int]$y,[int]$w,[int]$h)
    PF-Cmd "mirrory $x $y $w $h"
}

function PF-Rotate90 {
    param([int]$x,[int]$y,[int]$w,[int]$h,[string]$direction="cw")
    PF-Cmd "rotate90 $x $y $w $h $direction"
}

function PF-LoadState {
    param([string]$id="current")
    PF-Cmd "loadstate $id"
}

function PF-ExportMax {
    param([int]$Max)
    PF-Cmd "exportmax $Max"
}

function PF-ExportFrame {
    param([int]$Max = 0)
    $cmd = "exportframe"
    if ($Max -gt 0) { $cmd += " $Max" }
    PF-Cmd $cmd
}

function PF-ExportAll {
    param([string]$Category = "", [int]$Max = 0)
    $cmd = "exportall"
    if ($Category) { $cmd += " $Category" }
    if ($Max -gt 0) { $cmd += " $Max" }
    PF-Cmd $cmd
}

function PF-Spritesheet {
    param([object]$CategoryOrCols = $null, [int]$Cols = 0, [int]$Max = 0)
    $cmd = "spritesheet"
    if ($null -ne $CategoryOrCols -and "$CategoryOrCols" -ne "") { $cmd += " $CategoryOrCols" }
    if ($Cols -gt 0) { $cmd += " $Cols" }
    if ($Max -gt 0) { $cmd += " $Max" }
    PF-Cmd $cmd
}

function PF-DupFrame {
    PF-Cmd "dupframe"
}

function PF-DelFrame {
    param([int]$Index = 0)
    if ($Index -gt 0) { PF-Cmd "delframe $Index" }
    else { PF-Cmd "delframe" }
}

function PF-MoveFrame {
    param([int]$From,[int]$To)
    PF-Cmd "moveframe $From $To"
}

function PF-SetFps {
    param([int]$Fps)
    PF-Cmd "setfps $Fps"
}

function Invoke-PixelForgeOp {
    param(
        [string]$Op,
        [string[]]$Arguments = @(),
        [switch]$NewFrame,
        [int]$TimeoutSec = 8
    )
    $state = PF-State -TimeoutSec $TimeoutSec
    if (-not $state) { return $null }

    $root = PF-Root
    $script = Join-Path $root "pixelforge_ops.py"
    if (-not (Test-Path -LiteralPath $script)) {
        Write-Host "  ERR pixelop: no existe $script" -ForegroundColor Red
        return $null
    }

    $cmdArgs = @($script, "--source", $state.JsonPath, "--op", $Op) + $Arguments
    $raw = & python @cmdArgs 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  ERR pixelop: $raw" -ForegroundColor Red
        return $null
    }

    try {
        $result = (($raw | Out-String).Trim() | ConvertFrom-Json)
    } catch {
        Write-Host "  ERR pixelop: salida inválida $raw" -ForegroundColor Red
        return $null
    }

    if ($NewFrame) {
        PF-Cmd "cloneframe" | Out-Null
    }
    PF-Cmd "loadpixels $($result.id)" | Out-Null
    Write-Host "  PIXELOP: $Op -> $($result.JsonPath)" -ForegroundColor Cyan
    return $result
}

function PF-PixelOp {
    param(
        [Parameter(Mandatory=$true)][string]$Op,
        [Parameter(ValueFromRemainingArguments=$true)][string[]]$Arguments
    )
    Invoke-PixelForgeOp -Op $Op -Arguments $Arguments
}

function PF-CloneFrame {
    PF-Cmd "cloneframe"
}

function PF-SmoothPixels {
    param([int]$Passes = 1)
    Invoke-PixelForgeOp -Op "smoothpixels" -Arguments @([string]$Passes)
}

function PF-Despeckle {
    param([int]$MinSize = 2)
    Invoke-PixelForgeOp -Op "despeckle" -Arguments @([string]$MinSize)
}

function PF-Outline {
    param([string]$Color = "#000000")
    Invoke-PixelForgeOp -Op "outline" -Arguments @($Color)
}

function PF-ZombieStep {
    $result = Invoke-PixelForgeOp -Op "zombiestep" -NewFrame
    PF-Cmd "setfps 6" | Out-Null
    return $result
}

function PF-Clear    { PF-Cmd "clear" }
function PF-AddFrame { PF-Cmd "addframe" }
function PF-NextFrame{ PF-Cmd "nextframe" }
function PF-Export   { PF-Cmd "export" }
function PF-SetMode  { param([string]$m) PF-Cmd "setmode $m" }
function PF-SetSize  { param([int]$s)    PF-Cmd "setsize $s" }
function PF-SetBg    { param([string]$c) PF-Cmd "setbg $c" }
function PF-Zoom     { param([int]$z)    PF-Cmd "zoom $z" }

function PF-Root {
    if ($PSScriptRoot) { return $PSScriptRoot }
    return (Get-Location).Path
}

function PF-NewCaptureId {
    return "snapshot_$(Get-Date -Format 'yyyyMMdd_HHmmss_fff')"
}

function PF-WaitForFile {
    param(
        [string]$Path,
        [int]$TimeoutSec = 8
    )
    $sw = [Diagnostics.Stopwatch]::StartNew()
    while ($sw.Elapsed.TotalSeconds -lt $TimeoutSec) {
        if (Test-Path -LiteralPath $Path) { return $true }
        Start-Sleep -Milliseconds 200
    }
    return $false
}

function PF-Snapshot {
    param(
        [int]$Scale = 16,
        [int]$TimeoutSec = 8
    )
    $Scale = [Math]::Max(1, [Math]::Min(32, $Scale))
    $id = PF-NewCaptureId
    $root = PF-Root
    $png = Join-Path $root "snapshots\$id.png"
    $json = Join-Path $root "snapshots\$id.json"

    PF-Cmd "snapshot $id $Scale" | Out-Null

    if (-not (PF-WaitForFile -Path $png -TimeoutSec $TimeoutSec)) {
        Write-Host "  ERR snapshot: no llegó $png en ${TimeoutSec}s. Abre http://localhost:3000 para que la app consuma comandos." -ForegroundColor Red
        return $null
    }

    $result = [pscustomobject]@{
        Id = $id
        PngPath = (Resolve-Path -LiteralPath $png).Path
        JsonPath = if (Test-Path -LiteralPath $json) { (Resolve-Path -LiteralPath $json).Path } else { $null }
        CurrentPngPath = Join-Path $root "snapshots\current.png"
        CurrentJsonPath = Join-Path $root "snapshots\current.json"
    }
    Write-Host "  SNAPSHOT: $($result.PngPath)" -ForegroundColor Cyan
    return $result
}

function PF-State {
    param([int]$TimeoutSec = 8)
    $id = PF-NewCaptureId
    $root = PF-Root
    $json = Join-Path $root "snapshots\$id.json"

    PF-Cmd "statepush $id" | Out-Null

    if (-not (PF-WaitForFile -Path $json -TimeoutSec $TimeoutSec)) {
        Write-Host "  ERR state: no llegó $json en ${TimeoutSec}s. Abre http://localhost:3000 para que la app consuma comandos." -ForegroundColor Red
        return $null
    }

    $result = [pscustomobject]@{
        Id = $id
        JsonPath = (Resolve-Path -LiteralPath $json).Path
        CurrentJsonPath = Join-Path $root "snapshots\current.json"
    }
    Write-Host "  STATE: $($result.JsonPath)" -ForegroundColor Cyan
    return $result
}

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
