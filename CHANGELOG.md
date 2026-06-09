# Changelog

All notable changes to this project are documented here.
The format follows [Keep a Changelog](https://keepachangelog.com/), and this project
adheres to [Semantic Versioning](https://semver.org/).

## [1.1.0](https://github.com/webmavens/claude-forge/compare/v1.0.0...v1.1.0) (2026-06-09)


### Features

* add FORGE_API_BASE override and offline demo harness ([856eb42](https://github.com/webmavens/claude-forge/commit/856eb42952aa1647cbdff5af6d157640ac8b92bd))

## [1.0.0] — 2026-06-09

Initial public release.

### Added
- Self-contained `forge.py` CLI (standard library only) wrapping the Laravel Forge API:
  - `servers` (list/get/reboot)
  - `sites` (list/get/create)
  - `deploy` (run/log/script get+set/quick-deploy on+off)
  - `db` and `db-user` (list/create)
  - `ssl` (list/letsencrypt)
  - `daemon` (list/create)
  - `job` — scheduled jobs (list/create)
  - `env` (get/set)
  - `api` — raw passthrough to any Forge endpoint
- One-time token auth (`auth`) with validation against `GET /user`; stored at
  `~/.claude/forge/credentials` (chmod 600). Also reads `FORGE_API_TOKEN`.
- `--yes` safety gate: mutating commands print a `WOULD: …` dry-run and exit `2` unless confirmed.
- Cloudflare-aware HTTP layer: custom User-Agent (avoids 1015 blocks) and automatic
  `Retry-After` / exponential backoff on 429 and 5xx.
- `--json` / `--yes` accepted before *or* after the subcommand.
- `SKILL.md` so Claude Code knows when and how to drive the CLI.
- Distribution: Claude Code plugin marketplace manifest + `install.sh` curl installer.

### Known limitations
- Forge's API runs commands but does not return their stdout, and exposes no live disk/CPU
  metrics — so per-server disk usage isn't available via the API (use server monitors or SSH).

[1.0.0]: https://github.com/webmavens/claude-forge/releases/tag/v1.0.0
