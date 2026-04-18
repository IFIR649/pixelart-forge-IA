# PIXELFORGE — Manual de Herramienta para IA

> Este documento describe cómo una IA (Claude Code, Codex, GPT, etc.) puede controlar
> PixelForge al 100% para crear pixel art y sprites animados de forma autónoma.

---

## Arquitectura del sistema

```
IA / Terminal
    │
    ▼
PowerShell (pixelforge.ps1)
    │  HTTP POST /cmd o /batch
    ▼
Python Server (server.py) — localhost:3000
    │  GET /poll cada 300ms
    ▼
PixelForge App (navegador)
    │  execCmd()
    ▼
Canvas HTML5 (pixel art en tiempo real)
```

---

## Inicio rápido

```powershell
# 1. Iniciar servidor
python server.py

# 2. Importar cliente PowerShell
. .\pixelforge.ps1

# 3. Verificar conexión
PF-Status

# 4. Dibujar
PF-SetPixel 10 10 "#ff0000"
```

---

## Endpoints HTTP

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/` | Sirve la app HTML |
| GET | `/status` | Health check del servidor |
| GET | `/poll` | La app consume comandos pendientes (interno) |
| POST | `/cmd` | Envía un comando |
| POST | `/batch` | Envía múltiples comandos en una sola llamada |
| POST | `/snapshot` | Recibe PNG renderizado + estado desde la app |
| POST | `/state` | Recibe estado/píxeles sin PNG |
| GET | `/snapshot/latest` | Devuelve la última captura guardada |

### POST /cmd
```json
{ "cmd": "setpixel 5 5 #ff0000" }
```
Respuesta:
```json
{ "ok": true, "cmd": "setpixel 5 5 #ff0000", "queued": 1 }
```

### POST /batch
```json
{ "commands": ["color #ff0000", "setpixel 0 0", "setpixel 1 1"] }
```
Respuesta:
```json
{ "ok": true, "count": 3, "queued": 3 }
```

### POST /snapshot
Lo llama la app al ejecutar `snapshot [id] [scale]`.

```json
{
  "id": "snapshot_20260418_120000_000",
  "mode": "pixelart",
  "gridSize": 48,
  "currentFrame": 1,
  "bgColor": "#0e1116",
  "pixels": [[null, "#ff0000"]],
  "png": "data:image/png;base64,..."
}
```

Guarda:
- `snapshots/<id>.png`
- `snapshots/<id>.json`
- `snapshots/current.png`
- `snapshots/current.json`

### POST /state
Lo llama la app al ejecutar `statepush [id]`. Guarda JSON con estado y matriz de píxeles, sin PNG.

### GET /snapshot/latest
Devuelve el último `id`, rutas absolutas y metadatos de la captura más reciente.

---

## Comandos disponibles

### Canvas y configuración

| Comando | Argumentos | Descripción |
|---------|-----------|-------------|
| `clear` | — | Limpia el canvas actual |
| `setsize` | `<16\|32\|48\|64>` | Cambia el tamaño del canvas en píxeles |
| `setbg` | `<#hex\|transparent>` | Define el color de fondo |
| `setmode` | `<pixelart\|sprite>` | Cambia el modo de la app |
| `zoom` | `<4–24>` | Nivel de zoom visual |
| `export` | — | Exporta el frame actual como PNG |
| `getstate` | — | Devuelve JSON con el estado completo |
| `snapshot` | `[id] [scale]` | Envía PNG escalado + estado al servidor |
| `statepush` | `[id]` | Envía estado/píxeles al servidor sin PNG |

### Color

| Comando | Argumentos | Descripción |
|---------|-----------|-------------|
| `color` | `<#hex>` | Cambia el color activo |
| `alpha` | `<0–255>` | Transparencia del color activo |

### Dibujo

| Comando | Argumentos | Descripción |
|---------|-----------|-------------|
| `setpixel` | `<x> <y> [#hex]` | Pinta un píxel |
| `setpixels` | `<x> <y> <#hex> ...` | Pinta múltiples píxeles (batch inline) |
| `getpixel` | `<x> <y>` | Consulta el color de un píxel |
| `fill` | `<x> <y> [#hex]` | Flood fill desde una posición |
| `drawline` | `<x0> <y0> <x1> <y1> [#hex]` | Dibuja una línea (algoritmo Bresenham) |
| `drawrect` | `<x0> <y0> <x1> <y1> [#hex]` | Dibuja un rectángulo (solo borde) |
| `fillrect` | `<x0> <y0> <x1> <y1> [#hex]` | Dibuja un rectángulo relleno |
| `circle` | `<cx> <cy> <radio> [#hex]` | Dibuja un círculo (solo borde) |

> El argumento `[#hex]` es opcional. Si se omite, se usa el color activo.

### Frames y animación

| Comando | Argumentos | Descripción |
|---------|-----------|-------------|
| `addframe` | — | Agrega un nuevo frame vacío |
| `nextframe` | — | Va al frame siguiente |
| `prevframe` | — | Va al frame anterior |
| `setframe` | `<n>` | Va al frame número n (base 1) |
| `listframes` | — | Muestra cuántos frames hay y cuál es el actual |

### Categorías de sprites (modo sprite)

| Comando | Argumentos | Descripción |
|---------|-----------|-------------|
| `addcat` | `<nombre>` | Crea una categoría nueva (idle, walk, attack...) |
| `setcat` | `<nombre>` | Activa una categoría existente |

---

## Funciones PowerShell disponibles

```powershell
PF-Status                          # Verifica conexión con el servidor
PF-Cmd      "comando args"         # Envía cualquier comando
PF-Batch    @("cmd1","cmd2",...)   # Envía varios comandos

PF-SetPixel  x y [color]           # Pinta un píxel
PF-DrawLine  x0 y0 x1 y1 [color]   # Línea
PF-FillRect  x0 y0 x1 y1 [color]   # Rectángulo relleno
PF-Circle    cx cy radio [color]    # Círculo

PF-Clear                           # Limpiar canvas
PF-AddFrame                        # Nuevo frame
PF-NextFrame                       # Frame siguiente
PF-Export                          # Exportar PNG
PF-SetMode   pixelart|sprite       # Cambiar modo
PF-SetSize   16|32|48|64           # Tamaño canvas
PF-SetBg     "#hex"|transparent    # Fondo
PF-Zoom      4..24                 # Zoom
PF-Snapshot  [-Scale 16]           # Pide PNG renderizado y devuelve rutas
PF-State                           # Pide JSON de estado/píxeles

PF-Demo                            # Corre el demo de personaje incluido
```

---

## Sistema de coordenadas

```
(0,0) ──────────────► X
  │   . . . . . . .
  │   . . . . . . .
  │   . . . . . . .
  ▼
  Y
```

- Origen en esquina **superior izquierda**
- X aumenta hacia la **derecha**
- Y aumenta hacia **abajo**
- Rango válido: `0` a `gridSize - 1` (ej: 0–31 para canvas 32x32)

---

## Flujo recomendado para la IA

### Crear pixel art desde cero

```powershell
# 1. Obtener estado actual
PF-Cmd "getstate"

# 2. Configurar canvas
PF-Batch @(
    "setmode pixelart",
    "setsize 32",
    "setbg #1a1a2e",
    "clear"
)

# 3. Dibujar usando batch para eficiencia
PF-Batch @(
    "fillrect 8 4 23 19 #f5c5a3",   # cuerpo base
    "color #e94560",
    "setpixel 12 8",                 # detalle
    "circle 15 11 6 #ffffff"         # elemento circular
)

# 4. Exportar
PF-Export
```

### Revisar visualmente el canvas

```powershell
# La app debe estar abierta en http://localhost:3000
$snap = PF-Snapshot -Scale 16
$snap.PngPath

# Solo estado/píxeles, sin PNG
$state = PF-State
$state.JsonPath
```

Las capturas se guardan en `snapshots/`. `current.png` y `current.json` siempre apuntan a la última captura recibida.

### Crear sprite animado

```powershell
# 1. Configurar modo sprite
PF-Batch @(
    "setmode sprite",
    "setsize 32",
    "setbg transparent"
)

# 2. Crear categorías
PF-Cmd "addcat idle"
PF-Cmd "addcat walk"
PF-Cmd "addcat attack"

# 3. Dibujar frame 1 de idle
PF-Cmd "setcat idle"
# ... comandos de dibujo ...

# 4. Agregar frame 2 (pequeña variación)
PF-AddFrame
# ... pequeñas modificaciones para dar sensación de vida ...

# 5. Cambiar a categoría walk
PF-Cmd "setcat walk"
PF-AddFrame
# ... dibujar pose de caminar ...
```

---

## Convenciones de color

Usa colores HEX estándar. Ejemplos de paleta recomendada para personajes:

| Elemento | Color sugerido |
|----------|---------------|
| Piel clara | `#f5c5a3` |
| Piel oscura | `#8d5524` |
| Cabello negro | `#1a1a2e` |
| Cabello rubio | `#f9ca24` |
| Ropa azul | `#3498db` |
| Ropa roja | `#e74c3c` |
| Fondo oscuro | `#1a1a2e` |
| Fondo transparente | `transparent` |
| Contorno | `#000000` |
| Sombra | `#333333` |

---

## Estrategia de dibujo eficiente

La IA debe preferir `/batch` sobre comandos individuales para minimizar latencia.

**Mal (lento):**
```powershell
PF-Cmd "setpixel 0 0 #ff0000"
PF-Cmd "setpixel 1 0 #ff0000"
PF-Cmd "setpixel 2 0 #ff0000"
# ... 30 llamadas HTTP individuales
```

**Bien (rápido):**
```powershell
PF-Batch @(
    "color #ff0000",
    "drawline 0 0 31 0",    # toda la fila de una sola vez
    "drawline 0 31 31 31"
)
```

**Jerarquía de eficiencia:**
1. `fillrect` — mejor para áreas grandes
2. `drawline` / `circle` — mejor para formas geométricas
3. `fill` — mejor para rellenar áreas irregulares ya dibujadas
4. `setpixels x y c x y c ...` — batch inline para puntos sueltos
5. `setpixel` — solo para píxeles individuales específicos

---

## Respuesta de getstate (referencia)

```json
{
  "mode": "pixelart",
  "gridSize": 32,
  "currentColor": "#e94560",
  "currentAlpha": 255,
  "bgColor": "#1a1a2e",
  "currentFrame": 1,
  "tool": "pencil",
  "frameCount": 3,
  "categories": ["idle", "walk", "attack"]
}
```

Úsalo al inicio de cada sesión para conocer el estado actual antes de dibujar.

---

## Notas importantes

- Los comandos se ejecutan **en orden**, con ~300ms de delay de polling
- Usar `PF-Batch` encola todos los comandos a la vez — se ejecutan en ráfaga
- El canvas se actualiza en **tiempo real** en el navegador
- El frame activo se guarda automáticamente al dibujar
- `setpixel` y `drawline` usan el **color activo** si no se especifica color
- Coordenadas fuera de rango se ignoran silenciosamente
- Al cambiar `setsize` se **borran todos los frames** — hacerlo primero

---

*PixelForge — herramienta colaborativa humano + IA para pixel art y sprites*
