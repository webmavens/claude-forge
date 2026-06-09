---
name: forge
description: Drive Laravel Forge (forge.laravel.com) operations — servers, sites, deployments, databases, SSL, daemons, scheduled jobs, and env files — via the Forge API. Trigger when the user types /forge or asks to deploy, manage servers/sites, create databases, check deploy logs, or otherwise operate their Forge infrastructure.
---

# Laravel Forge CLI

Operate a user's [Laravel Forge](https://forge.laravel.com) account through its REST API
using the bundled `forge.py` helper. Use this whenever the user wants to deploy a site,
inspect or manage servers/sites, work with databases, SSL certs, daemons, scheduled jobs,
or env files.

## Locating the helper

`forge.py` sits in **this skill's own directory** — the absolute path is shown to you as the
skill's *base directory* when the skill loads. Always invoke it by absolute path:

```
python3 "<BASE_DIR>/forge.py" <group> <action> [args] [--json] [--yes]
```

where `<BASE_DIR>` is this skill's base directory (e.g. `~/.claude/skills/forge` for a manual
install, or the plugin's skill path for a plugin install). Use `python3` explicitly.

## First-time setup (one-time API key)

If any command returns `Not authenticated`, the user must authenticate once with their own
Forge API token from **forge.laravel.com → Account / API → Create API Token**.

Because Claude Code's `!` shell is non-interactive (no password prompt), have the user
authenticate one of these ways:

- **In a real terminal** (interactive prompt, token never echoed):
  `python3 "<BASE_DIR>/forge.py" auth`
- **Or pass the token inline** (works anywhere, but the token appears in shell history):
  `python3 "<BASE_DIR>/forge.py" auth <TOKEN>`
- **Or via env var** for the current command: `FORGE_API_TOKEN=<TOKEN> python3 ... auth`

The token is validated against `GET /user`, then saved to `~/.claude/forge/credentials`
(chmod 600) and reused on every later call. `auth --status` shows the authenticated identity;
`logout` removes the stored token.

Do NOT ask the user to paste the raw token into the chat. If they already did, still store it
via `auth`, then suggest they rotate it in Forge.

## Mutating-action safety

Read commands (`list`, `get`, `log`, `script`/`env`/`ssl list`) run freely.

Mutating commands (reboot, deploy, create, env set, script set, quick-deploy, letsencrypt)
are **gated**: without `--yes` they print a `WOULD: ...` dry-run and exit code 2 instead of
acting. Workflow:

1. Run the command WITHOUT `--yes`.
2. Show the user the `WOULD:` line and confirm with them.
3. Re-run the exact command WITH `--yes` only after they agree.

Never pass `--yes` on the first attempt for a destructive/mutating action.

## Rate limits

Forge sits behind Cloudflare with a global rate limit (Error 1015). `forge.py` automatically
honors `Retry-After` with exponential backoff, but **account-wide sweeps** (e.g. checking every
site across every server) make many calls and will be paced — run them sequentially, not with
heavy parallelism, and expect them to take a couple of minutes on large accounts.

## Finding ids

Most commands need a numeric `server` id, and site commands also need a `site` id.
Resolve them first with `servers list` and `sites list <server>` — don't guess. If the user
names a site by domain, list sites and match the `name` column to get the id.

## Command reference

Add `--json` to any read command for raw output you can parse. (`--json` / `--yes` work either
before or after the subcommand.)

### Auth
- `auth [token]` — store & validate token (interactive prompt, arg, or `FORGE_API_TOKEN`)
- `auth --status` — show who you're authenticated as
- `logout` — delete stored token

### Servers
- `servers list`
- `servers get <server>`
- `servers reboot <server>` *(mutating)*

### Sites
- `sites list <server>`
- `sites get <server> <site>`
- `sites create <server> --domain <d> [--project-type php] [--directory /path] [--php-version php83]` *(mutating)*

### Deployments
- `deploy run <server> <site>` *(mutating — triggers a deploy)*
- `deploy log <server> <site>` — last deployment output
- `deploy script <server> <site>` — show deploy script
- `deploy script <server> <site> --set <file|literal|->` *(mutating)*
- `deploy quick-deploy <server> <site> on|off` *(mutating)*

### Databases
- `db list <server>`
- `db create <server> --name <n> [--user <u> --password <p>]` *(mutating)*

### Database users
- `db-user list <server>`
- `db-user create <server> --name <n> --password <p> [--databases <id> <id>]` *(mutating)*

### SSL
- `ssl list <server> <site>`
- `ssl letsencrypt <server> <site> --domains <d> [<d> ...]` *(mutating)*

### Daemons
- `daemon list <server>`
- `daemon create <server> --command "<cmd>" [--user forge] [--directory /path] [--processes 1]` *(mutating)*

### Scheduled jobs
- `job list <server>`
- `job create <server> --command "<cmd>" --frequency <nightly|hourly|...> [--user forge]` *(mutating)*

### Env files
- `env get <server> <site>` — print site `.env`
- `env set <server> <site> --file <path|literal|->` *(mutating — overwrites .env)*

### Raw passthrough (escape hatch)
For any endpoint not wrapped above (e.g. deployment history, nginx config, site aliases):
- `api GET /servers/<id>/sites/<site>/deployment-history`
- `api POST /servers/<id>/... --data '<json|file|->'` *(mutating methods gated by --yes)*

See the full endpoint list at https://forge.laravel.com/api-documentation

## Notes & known limits

- **Disk usage / command output:** Forge's API can *run* commands (site commands, recipes) but
  does **not** return their stdout, and exposes no live disk/CPU field. Disk alerts are only
  visible via `api GET /servers/<id>/monitors` (threshold pass/fail, only on servers that have a
  monitor configured). For real disk numbers, SSH into the server (`ssh forge@<ip> df -h`).

## Typical flows

**Deploy a site by domain:**
1. `servers list` → find the server id
2. `sites list <server>` → match domain to site id
3. `deploy run <server> <site>` (dry-run) → confirm → re-run with `--yes`
4. `deploy log <server> <site>` to show the result
