import http.server
import json
import os
import mimetypes
from datetime import datetime

QUERIES_FILE = "queries.json"
PORT = 8000
DIR = os.path.dirname(os.path.abspath(__file__))

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self):
        if self.path == "/api/query":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            try:
                data = json.loads(body)
                text = data.get("text", "").strip()
                name = data.get("name", "Guest").strip()[:30]
                if text:
                    queries = []
                    if os.path.exists(QUERIES_FILE):
                        with open(QUERIES_FILE, "r", encoding="utf-8") as f:
                            queries = json.load(f)
                    now = datetime.now()
                    queries.append({
                        "id": len(queries) + 1,
                        "name": name,
                        "text": text,
                        "time": now.strftime("%Y-%m-%d %H:%M:%S"),
                        "ip": self.client_address[0]
                    })
                    with open(QUERIES_FILE, "w", encoding="utf-8") as f:
                        json.dump(queries, f, indent=2, ensure_ascii=False)
                    # Also save to a readable log file (no emoji, plain text)
                    log_line = f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] Name:{name} | Query:{text} | IP:{self.client_address[0]}\n"
                    with open("queries_log.txt", "a", encoding="utf-8") as f:
                        f.write(log_line)
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()
                    self.wfile.write(json.dumps({"ok": True, "id": len(queries)}).encode())
                    print(f"\n📩 NEW QUERY #{len(queries)} [{name}]: {text}")
                    return
            except Exception as e:
                print(f"Error: {e}")
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b'{"ok":false}')
        elif self.path == "/api/queries":
            queries = []
            if os.path.exists(QUERIES_FILE):
                with open(QUERIES_FILE, "r", encoding="utf-8") as f:
                    queries = json.load(f)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(queries).encode())
        elif self.path == "/api/clear":
            if os.path.exists(QUERIES_FILE):
                os.remove(QUERIES_FILE)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(b'{"ok":true}')
            print("\n🗑 All queries cleared")
        else:
            self.send_response(404)
            self.end_headers()

    def do_GET(self):
        if self.path == "/admin":
            self.path = "/admin.html"
        elif self.path == "/":
            self.path = "/calculator.html"
        elif self.path == "/api/queries":
            queries = []
            if os.path.exists(QUERIES_FILE):
                with open(QUERIES_FILE, "r", encoding="utf-8") as f:
                    queries = json.load(f)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(queries).encode())
            return
        super().do_GET()

    def log_message(self, format, *args):
        pass  # cleaner console

os.chdir(DIR)
print(f"\n{'='*50}")
print(f"  🚀 Server running on http://0.0.0.0:{PORT}")
print(f"  📋 Admin panel : http://localhost:{PORT}/admin")
print(f"  📱 Phone       : http://<YOUR_IP>:{PORT}/calculator.html")
print(f"  💾 Queries save: {QUERIES_FILE}")
print(f"{'='*50}\n")

server = http.server.HTTPServer(("0.0.0.0", PORT), Handler)
server.serve_forever()
