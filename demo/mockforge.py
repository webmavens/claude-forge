#!/usr/bin/env python3
"""
Tiny mock of the Laravel Forge API — serves canned, fake data so the demo (and tests) never
touch a real account. Start it, point forge.py at it with FORGE_API_BASE, and every command
works offline against made-up servers/sites.

    python3 demo/mockforge.py &        # listens on http://127.0.0.1:8771
    export FORGE_API_BASE=http://127.0.0.1:8771/api/v1
    export FORGE_API_TOKEN=demo-token
    python3 forge/skills/forge/forge.py servers list

All data here is fictional.
"""
import json
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

USER = {"user": {"id": 1, "name": "Ada Lovelace", "email": "ada@example.com"}}
SERVERS = [
    {"id": 101, "name": "web-prod-1", "ip_address": "203.0.113.10", "region": "London",
     "php_version": "php83", "is_ready": True},
    {"id": 102, "name": "web-prod-2", "ip_address": "203.0.113.11", "region": "London",
     "php_version": "php83", "is_ready": True},
    {"id": 103, "name": "worker-1", "ip_address": "203.0.113.20", "region": "Frankfurt",
     "php_version": "php84", "is_ready": True},
]
SITES = {
    101: [
        {"id": 5001, "name": "acme.com", "directory": "/public", "php_version": "php83",
         "repository": "acme/store", "status": "installed", "deployment_status": None},
        {"id": 5002, "name": "api.acme.com", "directory": "/public", "php_version": "php83",
         "repository": "acme/api", "status": "installed", "deployment_status": None},
    ],
}
DEPLOY_LOG = ("Cloning into 'acme.com'...\n"
              "composer install --no-dev -o ... done\n"
              "npm ci && npm run build ... done\n"
              "php artisan migrate --force ... Nothing to migrate.\n"
              "Restarting FPM ... ok\n"
              "Deployment finished successfully.\n")


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass  # quiet

    def _send(self, code, body):
        payload = json.dumps(body).encode() if not isinstance(body, str) else body.encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def route(self, method):
        p = self.path
        if p.endswith("/api/v1/user"):
            return self._send(200, USER)
        if re.search(r"/api/v1/servers$", p):
            return self._send(200, {"servers": SERVERS})
        m = re.search(r"/servers/(\d+)/sites$", p)
        if m:
            return self._send(200, {"sites": SITES.get(int(m.group(1)), [])})
        if re.search(r"/deployment/deploy$", p) and method == "POST":
            return self._send(200, {"deployment": {"id": 99, "status": "deploying"}})
        if re.search(r"/deployment/log$", p):
            return self._send(200, DEPLOY_LOG)
        if re.search(r"/databases$", p) and method == "POST":
            return self._send(200, {"database": {"id": 7, "name": "analytics", "status": "installed"}})
        return self._send(404, {"message": "not found in mock"})

    def do_GET(self):
        self.route("GET")

    def do_POST(self):
        # drain body
        length = int(self.headers.get("Content-Length", 0))
        if length:
            self.rfile.read(length)
        self.route("POST")


if __name__ == "__main__":
    ThreadingHTTPServer(("127.0.0.1", 8771), Handler).serve_forever()
