# Contributing to claude-forge

Thanks for helping improve it! This is a small, focused project — two files do the work:

- `forge/skills/forge/forge.py` — the CLI that talks to the Forge API. **All API logic lives here.**
- `forge/skills/forge/SKILL.md` — instructions that teach Claude Code when/how to call the CLI.

## Ground rules

- **Standard library only.** No `pip` dependencies — `forge.py` must run on a stock
  `python3` (3.8+). This keeps install frictionless.
- **Keep the two concerns separate.** Endpoints and behavior go in `forge.py`; guidance and
  command docs go in `SKILL.md`. Don't put API URLs in the skill markdown.
- **Mutating actions stay gated.** Anything that changes infrastructure (deploy, reboot,
  create, delete, env writes) must go through `confirm_gate()` so it requires `--yes`.
- **Be polite to the API.** Forge is behind Cloudflare with a global rate limit. Preserve the
  `Retry-After` / backoff handling; avoid heavy parallelism in new sweeps.
- **Never commit secrets.** Tokens live in `~/.claude/forge/credentials`, never in the repo.

## Dev loop

```bash
# clone your fork
git clone https://github.com/<you>/claude-forge && cd claude-forge

# point a local Claude skill at your working copy (optional)
ln -s "$PWD/forge/skills/forge" ~/.claude/skills/forge

# authenticate against a test Forge account
python3 forge/skills/forge/forge.py auth

# try things
python3 forge/skills/forge/forge.py servers list
```

`forge.py` is plain `argparse` — `--help` on any subcommand shows usage.

## Adding a command

1. Add the endpoint wrapper as a `cmd_*` function in `forge.py`.
2. Register its subparser in `build_parser()` (give it `parents=[common]` so `--json`/`--yes`
   work in any position). Gate mutations with `confirm_gate(...)`.
3. Document it in `SKILL.md` under **Command reference** (mark mutating ones).
4. Bump the version in `CHANGELOG.md`, `.claude-plugin/marketplace.json`, and
   `forge/.claude-plugin/plugin.json`.

## Pull requests

- One focused change per PR.
- Note what you tested it against (which Forge resources, read vs. mutating).
- If it changes behavior, update `SKILL.md` and `CHANGELOG.md` in the same PR.

## Reporting bugs / security

- Functional bugs → open an issue.
- Anything involving credential exposure → see [SECURITY.md](./SECURITY.md), don't open a public issue.
