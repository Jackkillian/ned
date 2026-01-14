import threading
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer


class OAuthCallbackServer:
    def __init__(self, host="127.0.0.1", port=8080, path="/callback"):
        self.host = host
        self.port = port
        self.path = path
        self.code: str | None = None
        self._ready = threading.Event()

    def start(self):
        def handler_factory():
            server = self

            class Handler(BaseHTTPRequestHandler):
                def do_GET(self):
                    parsed = urllib.parse.urlparse(self.path)
                    if parsed.path != server.path:
                        self.send_response(404)
                        self.end_headers()
                        return

                    params = urllib.parse.parse_qs(parsed.query)
                    server.code = params.get("code", [None])[0]

                    self.send_response(200)
                    self.send_header("Content-Type", "text/html")
                    self.end_headers()
                    self.wfile.write(b"<p>You may close this window.</p>")

                    threading.Thread(
                        target=self.server.shutdown,
                        daemon=True,
                    ).start()

                def log_message(self, *args, **kwargs):
                    pass

            return Handler

        def run():
            self.httpd = HTTPServer(
                (self.host, self.port),
                handler_factory(),
            )
            self._ready.set()
            self.httpd.serve_forever()

        threading.Thread(target=run, daemon=True).start()
        self._ready.wait()

    def wait_for_code(self) -> str:
        while self.code is None:
            pass
        return self.code
