"""
PixelForge HTTP Server
Corre la app en localhost:3000 y acepta comandos via HTTP.
Uso: python server.py
"""
import http.server
import json
import os
import threading
import webbrowser
from urllib.parse import urlparse

HOST = "localhost"
PORT = 3000

# Cola de comandos pendientes que la app consume via polling
command_queue = []
command_lock = threading.Lock()

HTML_FILE = "pixelforge.html"

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