# Security Policy

`claude-forge` handles a **Laravel Forge API token** that can control your servers and sites.
Please treat it accordingly.

## How the tool handles your token

- The token is stored locally at `~/.claude/forge/credentials` with `chmod 600` (owner read/write
  only). It is never transmitted anywhere except to `https://forge.laravel.com` over HTTPS.
- The token is **never** written into the repository, logs, or command output.
- You can remove it any time with `forge.py logout`, or use `FORGE_API_TOKEN` to avoid writing a
  file at all.

## Recommendations for users

- **Scope your token.** Create a Forge token with only the permissions you need.
- **Don't paste your token into chat.** Authenticate in a real terminal, or pass it via env var.
- **Rotate** the token if it may have been exposed (e.g. pasted into a transcript).
- Review every `WOULD: …` dry-run before approving a mutating action.

## Reporting a vulnerability

If you find a security issue — especially anything that could expose tokens or run unintended
mutations — **do not open a public issue**. Email **security@webmavens.com** with details and
steps to reproduce. We'll acknowledge within a few business days and coordinate a fix and
disclosure.
