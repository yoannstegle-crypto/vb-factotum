import os, sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
ROOT = sys.argv[1]
class H(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    def log_message(self, *a): pass
    def _r(self, code, body=b"", ct="text/plain"):
        self.send_response(code); self.send_header("Content-Type", ct)
        self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body)
    def do_GET(self):
        if self.path.startswith("/status"): return self._r(200, b"{}", "application/json")
        self._r(200, open(os.path.join(ROOT, "index.html"), "rb").read(), "text/html; charset=utf-8")
    def do_POST(self):
        self.rfile.read(int(self.headers.get("Content-Length", 0))); self._r(204)
ThreadingHTTPServer(("127.0.0.1", 8090), H).serve_forever()
