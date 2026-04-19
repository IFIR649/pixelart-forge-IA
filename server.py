"""
PixelForge HTTP Server
Corre la app en localhost:3000 y acepta comandos via HTTP.
Uso: python server.py
"""
import http.server
import base64
import binascii
import json
import os
import re
import threading
import webbrowser
from datetime import datetime
from urllib.parse import urlparse

HOST = "localhost"
PORT = 3000

# Cola de comandos pendientes que la app consume via polling
command_queue = []
command_lock = threading.Lock()

HTML_FILE = "pixelforge.html"
SNAPSHOT_DIR = "snapshots"

latest_snapshot = None


def safe_capture_id(raw_id=None):
    if raw_id:
        capture_id = re.sub(r"[^A-Za-z0-9_.-]+", "_", str(raw_id).strip())
        capture_id = capture_id.strip("._-")
        if capture_id:
            return capture_id[:80]
    return datetime.now().strftime("%Y%m%d_%H%M%S_%f")


def snapshot_path(filename):
    return os.path.abspath(os.path.join(SNAPSHOT_DIR, filename))


def read_capture_state(raw_id="current"):
    capture_id = "current" if not raw_id or raw_id == "current" else safe_capture_id(raw_id)
    json_file = snapshot_path(f"{capture_id}.json")
    if capture_id == "current":
        json_file = snapshot_path("current.json")
    if not os.path.exists(json_file):
        return capture_id, json_file, None
    with open(json_file, "r", encoding="utf-8") as f:
        return capture_id, json_file, json.load(f)


def strip_data_url(data_url):
    prefix = "data:image/png;base64,"
    if not isinstance(data_url, str) or not data_url.startswith(prefix):
        raise ValueError("Campo 'png' debe ser un data URL PNG base64")
    try:
        png_bytes = base64.b64decode(data_url[len(prefix):], validate=True)
    except binascii.Error as exc:
        raise ValueError("PNG base64 inválido") from exc
    if not png_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
        raise ValueError("El payload decodificado no es un PNG válido")
    return png_bytes


def capture_metadata(payload, capture_id):
    metadata = {k: v for k, v in payload.items() if k != "png"}
    metadata["id"] = capture_id
    metadata["savedAt"] = datetime.now().isoformat(timespec="seconds")
    return metadata


def save_capture_json(capture_id, metadata):
    os.makedirs(SNAPSHOT_DIR, exist_ok=True)
    json_file = snapshot_path(f"{capture_id}.json")
    current_json = snapshot_path("current.json")
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    with open(current_json, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    return json_file, current_json


def save_capture_png(capture_id, png_bytes):
    os.makedirs(SNAPSHOT_DIR, exist_ok=True)
    png_file = snapshot_path(f"{capture_id}.png")
    current_png = snapshot_path("current.png")
    with open(png_file, "wb") as f:
        f.write(png_bytes)
    with open(current_png, "wb") as f:
        f.write(png_bytes)
    return png_file, current_png


def clear_current_png():
    current_png = snapshot_path("current.png")
    if os.path.exists(current_png):
        os.remove(current_png)


def set_latest_capture(capture_id, metadata, png_file=None, json_file=None):
    global latest_snapshot
    latest_snapshot = {
        "id": capture_id,
        "pngPath": os.path.abspath(png_file) if png_file else None,
        "jsonPath": os.path.abspath(json_file) if json_file else None,
        "currentPngPath": snapshot_path("current.png") if png_file else None,
        "currentJsonPath": snapshot_path("current.json"),
        "metadata": {k: v for k, v in metadata.items() if k != "pixels"},
    }
    return latest_snapshot

class PixelForgeHandler(http.server.BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        # Silencia logs por defecto, solo muestra errores
        if args and str(args[1]) not in ('200', '204'):
            print(f"  [{args[1]}] {args[0]}")

    def send_cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_cors()
        self.end_headers()

    def do_GET(self):
        path = urlparse(self.path).path

        # Servir la app HTML
        if path == "/" or path == "/index.html":
            if not os.path.exists(HTML_FILE):
                self.send_error(404, f"No se encontró {HTML_FILE}")
                return
            with open(HTML_FILE, "rb") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_cors()
            self.end_headers()
            self.wfile.write(content)

        # La app hace polling aquí para obtener comandos pendientes
        elif path == "/poll":
            with command_lock:
                pending = command_queue.copy()
                command_queue.clear()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_cors()
            self.end_headers()
            self.wfile.write(json.dumps({"commands": pending}).encode())

        # Estado del servidor
        elif path == "/status":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_cors()
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok", "port": PORT}).encode())

        # Última captura recibida desde el navegador
        elif path == "/snapshot/latest":
            data = latest_snapshot
            if data is None and os.path.exists(snapshot_path("current.json")):
                with open(snapshot_path("current.json"), "r", encoding="utf-8") as f:
                    metadata = json.load(f)
                current_png = snapshot_path("current.png")
                data = {
                    "id": metadata.get("id"),
                    "pngPath": current_png if os.path.exists(current_png) else None,
                    "jsonPath": snapshot_path("current.json"),
                    "currentPngPath": current_png if os.path.exists(current_png) else None,
                    "currentJsonPath": snapshot_path("current.json"),
                    "metadata": {k: v for k, v in metadata.items() if k != "pixels"},
                }
            self._json_response(200, {"ok": True, "latest": data})

        # Estado guardado para loadstate desde la app
        elif path == "/snapshot/state/current" or path.startswith("/snapshot/state/"):
            raw_id = path.rsplit("/", 1)[-1]
            capture_id, json_file, state = read_capture_state(raw_id)
            if state is None:
                self._json_response(404, {"ok": False, "error": f"No existe estado: {capture_id}"})
                return
            self._json_response(200, {
                "ok": True,
                "id": capture_id,
                "jsonPath": os.path.abspath(json_file),
                "state": state,
            })

        else:
            self.send_error(404)

    def do_POST(self):
        path = urlparse(self.path).path
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8")

        # POST /cmd — un comando
        if path == "/cmd":
            try:
                data = json.loads(body)
                cmd = data.get("cmd", "").strip()
                if not cmd:
                    self._json_response(400, {"error": "Campo 'cmd' vacío"})
                    return
                with command_lock:
                    command_queue.append(cmd)
                print(f"  CMD: {cmd}")
                self._json_response(200, {"ok": True, "cmd": cmd, "queued": len(command_queue)})
            except json.JSONDecodeError:
                self._json_response(400, {"error": "JSON inválido"})

        # POST /batch — múltiples comandos
        elif path == "/batch":
            try:
                data = json.loads(body)
                cmds = data.get("commands", [])
                if not isinstance(cmds, list):
                    self._json_response(400, {"error": "'commands' debe ser lista"})
                    return
                with command_lock:
                    command_queue.extend([c.strip() for c in cmds if c.strip()])
                print(f"  BATCH: {len(cmds)} comandos encolados")
                self._json_response(200, {"ok": True, "count": len(cmds), "queued": len(command_queue)})
            except json.JSONDecodeError:
                self._json_response(400, {"error": "JSON inválido"})

        # POST /snapshot — PNG renderizado + estado
        elif path == "/snapshot":
            try:
                data = json.loads(body)
                if not isinstance(data, dict):
                    self._json_response(400, {"error": "JSON debe ser un objeto"})
                    return
                capture_id = safe_capture_id(data.get("id"))
                png_bytes = strip_data_url(data.get("png"))
                metadata = capture_metadata(data, capture_id)
                png_file, current_png = save_capture_png(capture_id, png_bytes)
                json_file, current_json = save_capture_json(capture_id, metadata)
                latest = set_latest_capture(capture_id, metadata, png_file, json_file)
                print(f"  SNAPSHOT: {capture_id}")
                self._json_response(200, {
                    "ok": True,
                    "id": capture_id,
                    "pngPath": png_file,
                    "jsonPath": json_file,
                    "currentPngPath": current_png,
                    "currentJsonPath": current_json,
                    "latest": latest,
                })
            except json.JSONDecodeError:
                self._json_response(400, {"error": "JSON inválido"})
            except ValueError as exc:
                self._json_response(400, {"error": str(exc)})

        # POST /state — estado/píxeles sin PNG
        elif path == "/state":
            try:
                data = json.loads(body)
                if not isinstance(data, dict):
                    self._json_response(400, {"error": "JSON debe ser un objeto"})
                    return
                capture_id = safe_capture_id(data.get("id"))
                metadata = capture_metadata(data, capture_id)
                json_file, current_json = save_capture_json(capture_id, metadata)
                clear_current_png()
                latest = set_latest_capture(capture_id, metadata, None, json_file)
                print(f"  STATE: {capture_id}")
                self._json_response(200, {
                    "ok": True,
                    "id": capture_id,
                    "jsonPath": json_file,
                    "currentJsonPath": current_json,
                    "latest": latest,
                })
            except json.JSONDecodeError:
                self._json_response(400, {"error": "JSON inválido"})

        else:
            self.send_error(404)

    def _json_response(self, code, data):
        body = json.dumps(data).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_cors()
        self.end_headers()
        self.wfile.write(body)


def main():
    print("=" * 48)
    print("  PixelForge Server")
    print(f"  http://{HOST}:{PORT}")
    print("=" * 48)
    print(f"  Sirviendo: {HTML_FILE}")
    print("  Endpoints:")
    print("    GET  /         — abre la app")
    print("    POST /cmd      — {\"cmd\": \"setpixel 5 5 #ff0000\"}")
    print("    POST /batch    — {\"commands\": [\"color #ff0\", \"setpixel 0 0\"]}")
    print("    POST /snapshot — guarda PNG + estado desde el navegador")
    print("    POST /state    — guarda estado/píxeles desde el navegador")
    print("    GET  /snapshot/latest — última captura guardada")
    print("    GET  /snapshot/state/<id|current> — estado guardado para loadstate")
    print("    GET  /poll     — la app consume comandos (interno)")
    print("    GET  /status   — health check")
    print("  Ctrl+C para detener\n")

    server = http.server.HTTPServer((HOST, PORT), PixelForgeHandler)
    threading.Timer(1.0, lambda: webbrowser.open(f"http://{HOST}:{PORT}")).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Servidor detenido.")


if __name__ == "__main__":
    main()
