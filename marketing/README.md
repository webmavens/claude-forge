# Marketing kit

Assets and paste-ready copy for launching **claude-forge**.

- [`launch-copy.md`](./launch-copy.md) — Show HN, r/laravel, X thread, Laravel News, Discord
- [`blog-post.md`](./blog-post.md) — full article for the Webmavens blog + dev.to (with front-matter)
- `../docs/social-preview.png` — 1280×640 social/OG card
- `../docs/demo.gif` — terminal demo

## Set the GitHub social preview (2 clicks, manual — no API for this)

1. Repo → **Settings** → scroll to **Social preview**
2. **Edit → Upload an image** → pick `docs/social-preview.png` → done

After that, every link to the repo (X, Slack, Discord, LinkedIn) unfurls with the branded card.

## Submit to Anthropic's plugin directory (form — needs your Console login)

Go to **https://clau.de/plugin-directory-submission** (or platform.claude.com/plugins/submit).
Submissions land in `anthropics/claude-plugins-community`; Anthropic promotes selected ones into the
official directory. Paste-ready values:

| Field | Value |
|-------|-------|
| Plugin name | `forge` |
| Marketplace / repo | `https://github.com/webmavens/claude-forge` |
| Install | `/plugin marketplace add webmavens/claude-forge` → `/plugin install forge@claude-forge` |
| Category | DevOps / Deployment |
| Short description | Drive Laravel Forge from Claude Code — servers, sites, deployments, databases, SSL, daemons, scheduled jobs, and env files, with a confirm-first dry-run on every change. |
| Author | Webmavens |
| License | MIT |
| Dependencies | None (standard-library Python) |
| Security notes | User supplies their own scoped Forge API token, stored locally chmod 600; never transmitted except to forge.laravel.com. Mutating actions require explicit `--yes` confirmation. |

## Channel checklist

- [ ] Laravel News link submission — laravel-news.com/links
- [ ] r/laravel post (with demo GIF)
- [ ] X/Twitter thread (with demo GIF)
- [ ] Show HN (separate day; reply actively)
- [ ] Laravel / Laracasts / Claude Discords
- [ ] Webmavens blog post + dev.to cross-post (canonical → blog)
- [ ] GitHub social preview uploaded
- [ ] Anthropic plugin directory submission
- [x] ComposioHQ/awesome-claude-plugins (PR #279)
- [ ] jmanhype/awesome-claude-code (PR)
