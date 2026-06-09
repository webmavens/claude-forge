#!/usr/bin/env python3
"""
forge.py — a self-contained CLI for the Laravel Forge API (https://forge.laravel.com).

Stdlib only. Auth token is stored at ~/.claude/forge/credentials (chmod 600).
Mutating commands require --yes; without it they print a dry-run and exit 2 so the
caller can confirm with the user first.

Run `forge.py --help` or `forge.py <group> --help` for usage.
"""

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request

API_BASE = "https://forge.laravel.com/api/v1"
CRED_PATH = os.path.expanduser("~/.claude/forge/credentials")
MAX_RETRIES = 5  # for 429 / transient errors


# ----------------------------------------------------------------------------- creds
def load_token():
    # Env var wins — handy for CI / ephemeral use without writing a file.
    env = os.environ.get("FORGE_API_TOKEN")
    if env and env.strip():
        return env.strip()
    try:
        with open(CRED_PATH, "r") as f:
            tok = f.read().strip()
        return tok or None
    except FileNotFoundError:
        return None


def save_token(token):
    os.makedirs(os.path.dirname(CRED_PATH), exist_ok=True)
    # write restrictively from the start
    fd = os.open(CRED_PATH, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as f:
        f.write(token.strip() + "\n")
    os.chmod(CRED_PATH, 0o600)


def require_token():
    tok = load_token()
    if not tok:
        die("Not authenticated. Run:  forge.py auth   (paste your Forge API token)")
    return tok


# ----------------------------------------------------------------------------- http
def die(msg, code=1):
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(code)


def api(method, path, data=None, token=None):
    """Make an API call. Returns (status_code, parsed_body). Body is dict/list or str."""
    token = token or require_token()
    url = API_BASE + path
    body = None
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        # Forge sits behind Cloudflare, which 403s the default Python-urllib UA.
        "User-Agent": "forge-cli/1.0 (+claude-skill)",
    }
    if data is not None:
        body = json.dumps(data).encode()
        headers["Content-Type"] = "application/json"
    attempt = 0
    while True:
        req = urllib.request.Request(url, data=body, method=method, headers=headers)
        try:
            with urllib.request.urlopen(req) as resp:
                return resp.status, parse_body(resp.read().decode())
        except urllib.error.HTTPError as e:
            parsed = parse_body(e.read().decode())
            # 429 (Cloudflare 1015) and 5xx are retryable with backoff.
            if e.code in (429, 502, 503, 504) and attempt < MAX_RETRIES:
                wait = retry_after(e, parsed, attempt)
                attempt += 1
                print(f"  rate-limited ({e.code}); waiting {wait:.0f}s "
                      f"(retry {attempt}/{MAX_RETRIES})...", file=sys.stderr)
                time.sleep(wait)
                continue
            return e.code, parsed
        except urllib.error.URLError as e:
            if attempt < MAX_RETRIES:
                attempt += 1
                time.sleep(2 ** attempt)
                continue
            die(f"network error: {e.reason}")


def retry_after(err, body, attempt):
    """Seconds to wait: prefer Retry-After header / body, else exponential backoff."""
    hdr = err.headers.get("Retry-After") if err.headers else None
    for v in (hdr, isinstance(body, dict) and body.get("retry_after")):
        try:
            if v is not None:
                return max(float(v), 1.0)
        except (TypeError, ValueError):
            pass
    return min(2 ** attempt, 60)  # 1,2,4,8,16,...capped


def parse_body(raw):
    raw = raw.strip()
    if not raw:
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return raw  # e.g. env file content is plain text


def check(status, body, context=""):
    """Raise a friendly error for non-2xx responses."""
    if 200 <= status < 300:
        return body
    ctx = f" ({context})" if context else ""
    if status == 401:
        die("401 Unauthorized — token invalid or expired. Run:  forge.py auth")
    if status == 404:
        die(f"404 Not Found{ctx} — check the server/site/resource id.")
    if status == 422 and isinstance(body, dict):
        errs = body.get("errors") or body.get("message") or body
        die(f"422 Validation failed{ctx}: {json.dumps(errs)}")
    msg = body.get("message") if isinstance(body, dict) else body
    die(f"HTTP {status}{ctx}: {msg}")


# ----------------------------------------------------------------------------- output
def out(body, args, table_fn=None):
    if getattr(args, "json", False) or table_fn is None:
        print(json.dumps(body, indent=2))
    else:
        table_fn(body)


def table(rows, headers):
    if not rows:
        print("(none)")
        return
    cols = list(zip(*([headers] + rows)))
    widths = [max(len(str(c)) for c in col) for col in cols]
    fmt = "  ".join("{:<" + str(w) + "}" for w in widths)
    print(fmt.format(*headers))
    print(fmt.format(*["-" * w for w in widths]))
    for r in rows:
        print(fmt.format(*[str(c) for c in r]))


def confirm_gate(args, action):
    """Mutating guard. If --yes not passed, describe and exit 2."""
    if getattr(args, "yes", False):
        return
    print(f"WOULD: {action}")
    print("This is a mutating action. Re-run with --yes to execute.")
    sys.exit(2)


# ----------------------------------------------------------------------------- auth
def cmd_auth(args):
    if args.status:
        status, body = api("GET", "/user")
        check(status, body, "verify token")
        u = body.get("user", body)
        print(f"Authenticated as {u.get('name')} <{u.get('email')}>")
        return
    token = args.token or os.environ.get("FORGE_API_TOKEN")
    if not token:
        if sys.stdin.isatty():
            try:
                import getpass
                token = getpass.getpass("Forge API token: ")
            except Exception:
                token = input("Forge API token: ")
        else:
            token = sys.stdin.read().strip()
    if not token:
        die("no token provided")
    # validate before saving
    status, body = api("GET", "/user", token=token)
    if status != 200:
        check(status, body, "validate token")
    save_token(token)
    u = body.get("user", body)
    print(f"Saved. Authenticated as {u.get('name')} <{u.get('email')}>  ({CRED_PATH})")


def cmd_logout(args):
    if os.path.exists(CRED_PATH):
        os.remove(CRED_PATH)
        print("Logged out — credentials removed.")
    else:
        print("No credentials stored.")


# ----------------------------------------------------------------------------- servers
def cmd_servers(args):
    if args.action == "list":
        status, body = api("GET", "/servers")
        check(status, body)
        rows = [[s["id"], s["name"], s.get("ip_address"), s.get("region"),
                 s.get("php_version"), s.get("is_ready")] for s in body.get("servers", [])]
        out(body, args, lambda b: table(rows, ["ID", "NAME", "IP", "REGION", "PHP", "READY"]))
    elif args.action == "get":
        status, body = api("GET", f"/servers/{args.server}")
        check(status, body, f"server {args.server}")
        out(body, args, lambda b: print(json.dumps(b.get("server", b), indent=2)))
    elif args.action == "reboot":
        confirm_gate(args, f"reboot server {args.server}")
        status, body = api("POST", f"/servers/{args.server}/reboot")
        check(status, body, f"reboot {args.server}")
        print(f"Reboot triggered for server {args.server}.")


# ----------------------------------------------------------------------------- sites
def cmd_sites(args):
    if args.action == "list":
        status, body = api("GET", f"/servers/{args.server}/sites")
        check(status, body)
        rows = [[s["id"], s["name"], s.get("directory"), s.get("php_version"),
                 s.get("repository"), s.get("status")] for s in body.get("sites", [])]
        out(body, args, lambda b: table(rows, ["ID", "NAME", "DIR", "PHP", "REPO", "STATUS"]))
    elif args.action == "get":
        status, body = api("GET", f"/servers/{args.server}/sites/{args.site}")
        check(status, body, f"site {args.site}")
        out(body, args, lambda b: print(json.dumps(b.get("site", b), indent=2)))
    elif args.action == "create":
        payload = {"domain": args.domain, "project_type": args.project_type}
        if args.directory:
            payload["directory"] = args.directory
        if args.php_version:
            payload["php_version"] = args.php_version
        confirm_gate(args, f"create site {args.domain} on server {args.server} ({payload})")
        status, body = api("POST", f"/servers/{args.server}/sites", payload)
        check(status, body, "create site")
        s = body.get("site", body)
        print(f"Created site {s.get('name')} (id {s.get('id')}).")


# ----------------------------------------------------------------------------- deploy
def cmd_deploy(args):
    base = f"/servers/{args.server}/sites/{args.site}"
    if args.action == "run":
        confirm_gate(args, f"deploy site {args.site} on server {args.server}")
        status, body = api("POST", f"{base}/deployment/deploy")
        check(status, body, "deploy")
        print(f"Deployment started for site {args.site}.")
    elif args.action == "log":
        status, body = api("GET", f"{base}/deployment/log")
        check(status, body, "deploy log")
        print(body if isinstance(body, str) else json.dumps(body, indent=2))
    elif args.action == "script":
        if args.set is not None:
            content = read_content(args.set)
            confirm_gate(args, f"replace deploy script for site {args.site}")
            status, body = api("PUT", f"{base}/deployment/script",
                               {"content": content, "auto_source": True})
            check(status, body, "set deploy script")
            print("Deploy script updated.")
        else:
            status, body = api("GET", f"{base}/deployment/script")
            check(status, body, "get deploy script")
            print(body if isinstance(body, str) else json.dumps(body, indent=2))
    elif args.action == "quick-deploy":
        if args.toggle == "on":
            confirm_gate(args, f"ENABLE quick deploy for site {args.site}")
            status, body = api("POST", f"{base}/deployment")
            check(status, body, "enable quick deploy")
            print("Quick deploy enabled.")
        else:
            confirm_gate(args, f"DISABLE quick deploy for site {args.site}")
            status, body = api("DELETE", f"{base}/deployment")
            check(status, body, "disable quick deploy")
            print("Quick deploy disabled.")


# ----------------------------------------------------------------------------- databases
def cmd_db(args):
    base = f"/servers/{args.server}/databases"
    if args.action == "list":
        status, body = api("GET", base)
        check(status, body)
        rows = [[d["id"], d["name"], d.get("status")] for d in body.get("databases", [])]
        out(body, args, lambda b: table(rows, ["ID", "NAME", "STATUS"]))
    elif args.action == "create":
        payload = {"name": args.name}
        if args.user:
            payload["user"] = args.user
        if args.password:
            payload["password"] = args.password
        confirm_gate(args, f"create database '{args.name}' on server {args.server}")
        status, body = api("POST", base, payload)
        check(status, body, "create database")
        d = body.get("database", body)
        print(f"Created database {d.get('name')} (id {d.get('id')}).")


def cmd_db_user(args):
    base = f"/servers/{args.server}/database-users"
    if args.action == "list":
        status, body = api("GET", base)
        check(status, body)
        rows = [[u["id"], u["name"], ",".join(str(x) for x in u.get("databases", []))]
                for u in body.get("users", [])]
        out(body, args, lambda b: table(rows, ["ID", "NAME", "DATABASES"]))
    elif args.action == "create":
        payload = {"name": args.name, "password": args.password}
        if args.databases:
            payload["databases"] = [int(x) for x in args.databases]
        confirm_gate(args, f"create db user '{args.name}' on server {args.server}")
        status, body = api("POST", base, payload)
        check(status, body, "create db user")
        u = body.get("user", body)
        print(f"Created database user {u.get('name')} (id {u.get('id')}).")


# ----------------------------------------------------------------------------- ssl
def cmd_ssl(args):
    base = f"/servers/{args.server}/sites/{args.site}/certificates"
    if args.action == "list":
        status, body = api("GET", base)
        check(status, body)
        rows = [[c["id"], c.get("domain"), c.get("type"), c.get("status"),
                 c.get("active")] for c in body.get("certificates", [])]
        out(body, args, lambda b: table(rows, ["ID", "DOMAIN", "TYPE", "STATUS", "ACTIVE"]))
    elif args.action == "letsencrypt":
        domains = args.domains
        confirm_gate(args, f"obtain Let's Encrypt cert for {domains} on site {args.site}")
        status, body = api("POST", f"{base}/letsencrypt", {"domains": domains})
        check(status, body, "letsencrypt")
        print(f"Let's Encrypt certificate requested for {domains}.")


# ----------------------------------------------------------------------------- daemons
def cmd_daemon(args):
    base = f"/servers/{args.server}/daemons"
    if args.action == "list":
        status, body = api("GET", base)
        check(status, body)
        rows = [[d["id"], d.get("command"), d.get("user"), d.get("processes"),
                 d.get("status")] for d in body.get("daemons", [])]
        out(body, args, lambda b: table(rows, ["ID", "COMMAND", "USER", "PROCS", "STATUS"]))
    elif args.action == "create":
        payload = {"command": args.command, "user": args.user or "forge"}
        if args.directory:
            payload["directory"] = args.directory
        if args.processes:
            payload["processes"] = args.processes
        confirm_gate(args, f"create daemon '{args.command}' on server {args.server}")
        status, body = api("POST", base, payload)
        check(status, body, "create daemon")
        d = body.get("daemon", body)
        print(f"Created daemon (id {d.get('id')}).")


# ----------------------------------------------------------------------------- jobs (scheduler)
def cmd_job(args):
    base = f"/servers/{args.server}/jobs"
    if args.action == "list":
        status, body = api("GET", base)
        check(status, body)
        rows = [[j["id"], j.get("command"), j.get("frequency"), j.get("user"),
                 j.get("status")] for j in body.get("jobs", [])]
        out(body, args, lambda b: table(rows, ["ID", "COMMAND", "FREQ", "USER", "STATUS"]))
    elif args.action == "create":
        payload = {"command": args.command, "frequency": args.frequency,
                   "user": args.user or "forge"}
        confirm_gate(args, f"create scheduled job '{args.command}' ({args.frequency})")
        status, body = api("POST", base, payload)
        check(status, body, "create job")
        j = body.get("job", body)
        print(f"Created scheduled job (id {j.get('id')}).")


# ----------------------------------------------------------------------------- env
def cmd_env(args):
    base = f"/servers/{args.server}/sites/{args.site}/env"
    if args.action == "get":
        status, body = api("GET", base)
        check(status, body, "get env")
        print(body if isinstance(body, str) else json.dumps(body, indent=2))
    elif args.action == "set":
        content = read_content(args.file)
        confirm_gate(args, f"OVERWRITE .env for site {args.site} on server {args.server}")
        status, body = api("PUT", base, {"content": content})
        check(status, body, "set env")
        print("Environment file updated.")


# ----------------------------------------------------------------------------- raw passthrough
def cmd_api(args):
    data = None
    if args.data:
        data = json.loads(read_content(args.data))
    method = args.method.upper()
    if method not in ("GET", "HEAD") and not args.yes:
        confirm_gate(args, f"{method} {args.path}")
    path = args.path if args.path.startswith("/") else "/" + args.path
    status, body = api(method, path, data)
    print(f"# HTTP {status}", file=sys.stderr)
    print(body if isinstance(body, str) else json.dumps(body, indent=2))
    if not (200 <= status < 300):
        sys.exit(1)


# ----------------------------------------------------------------------------- helpers
def read_content(value):
    """If value points to a file, read it; otherwise treat value as literal content.
    '-' means read stdin."""
    if value == "-":
        return sys.stdin.read()
    if os.path.isfile(value):
        with open(value) as f:
            return f.read()
    return value


# ----------------------------------------------------------------------------- argparse
def build_parser():
    p = argparse.ArgumentParser(prog="forge.py", description="Laravel Forge API CLI")
    # Shared flags live on a parent so they work AFTER the subcommand too
    # (e.g. `forge.py sites list 123 --json`), matching the documented usage.
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--json", action="store_true", help="raw JSON output")
    common.add_argument("--yes", action="store_true", help="confirm mutating actions")
    sub = p.add_subparsers(dest="group", required=True)

    # auth
    a = sub.add_parser("auth", parents=[common], help="store/validate API token")
    a.add_argument("token", nargs="?", help="token (else prompt/stdin)")
    a.add_argument("--status", action="store_true", help="show current identity")
    a.set_defaults(func=cmd_auth)

    lo = sub.add_parser("logout", parents=[common], help="remove stored token")
    lo.set_defaults(func=cmd_logout)

    # servers
    s = sub.add_parser("servers", parents=[common], help="manage servers")
    s.add_argument("action", choices=["list", "get", "reboot"])
    s.add_argument("server", nargs="?", help="server id")
    s.set_defaults(func=cmd_servers)

    # sites
    si = sub.add_parser("sites", parents=[common], help="manage sites")
    si.add_argument("action", choices=["list", "get", "create"])
    si.add_argument("server", help="server id")
    si.add_argument("site", nargs="?", help="site id (get)")
    si.add_argument("--domain")
    si.add_argument("--project-type", default="php")
    si.add_argument("--directory")
    si.add_argument("--php-version")
    si.set_defaults(func=cmd_sites)

    # deploy
    d = sub.add_parser("deploy", parents=[common], help="deployments")
    d.add_argument("action", choices=["run", "log", "script", "quick-deploy"])
    d.add_argument("server", help="server id")
    d.add_argument("site", help="site id")
    d.add_argument("toggle", nargs="?", choices=["on", "off"], help="for quick-deploy")
    d.add_argument("--set", help="for 'script': new content (file path, literal, or -)")
    d.set_defaults(func=cmd_deploy)

    # db
    db = sub.add_parser("db", parents=[common], help="databases")
    db.add_argument("action", choices=["list", "create"])
    db.add_argument("server", help="server id")
    db.add_argument("--name")
    db.add_argument("--user")
    db.add_argument("--password")
    db.set_defaults(func=cmd_db)

    # db-user
    dbu = sub.add_parser("db-user", parents=[common], help="database users")
    dbu.add_argument("action", choices=["list", "create"])
    dbu.add_argument("server", help="server id")
    dbu.add_argument("--name")
    dbu.add_argument("--password")
    dbu.add_argument("--databases", nargs="*", help="database ids to grant")
    dbu.set_defaults(func=cmd_db_user)

    # ssl
    ssl = sub.add_parser("ssl", parents=[common], help="SSL certificates")
    ssl.add_argument("action", choices=["list", "letsencrypt"])
    ssl.add_argument("server", help="server id")
    ssl.add_argument("site", help="site id")
    ssl.add_argument("--domains", nargs="*", help="domains for letsencrypt")
    ssl.set_defaults(func=cmd_ssl)

    # daemon
    dm = sub.add_parser("daemon", parents=[common], help="daemons")
    dm.add_argument("action", choices=["list", "create"])
    dm.add_argument("server", help="server id")
    dm.add_argument("--command")
    dm.add_argument("--user")
    dm.add_argument("--directory")
    dm.add_argument("--processes", type=int)
    dm.set_defaults(func=cmd_daemon)

    # job
    jb = sub.add_parser("job", parents=[common], help="scheduled jobs")
    jb.add_argument("action", choices=["list", "create"])
    jb.add_argument("server", help="server id")
    jb.add_argument("--command")
    jb.add_argument("--frequency", help="e.g. nightly, hourly, custom")
    jb.add_argument("--user")
    jb.set_defaults(func=cmd_job)

    # env
    ev = sub.add_parser("env", parents=[common], help="site .env file")
    ev.add_argument("action", choices=["get", "set"])
    ev.add_argument("server", help="server id")
    ev.add_argument("site", help="site id")
    ev.add_argument("--file", help="for 'set': file path, literal, or -")
    ev.set_defaults(func=cmd_env)

    # raw api
    rw = sub.add_parser("api", parents=[common], help="raw API passthrough")
    rw.add_argument("method", help="GET/POST/PUT/DELETE")
    rw.add_argument("path", help="e.g. /servers/123/sites")
    rw.add_argument("--data", help="JSON body (file path, literal, or -)")
    rw.set_defaults(func=cmd_api)

    return p


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
