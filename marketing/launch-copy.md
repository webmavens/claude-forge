# Launch copy — paste-and-go

Ready-to-post copy for each channel. Tweak the voice to yours; the facts are accurate to v1.1.0.
Repo: https://github.com/webmavens/claude-forge

---

## Hacker News — "Show HN"

**Title:**
> Show HN: Manage Laravel Forge from Claude Code

**First comment (post immediately after submitting):**
> I run a bunch of sites on Laravel Forge and kept bouncing between the dashboard and the
> terminal for routine stuff — trigger a deploy, check why one failed, spin up a database. So I
> built a small Claude Code plugin that drives the Forge API in plain English: "deploy acme.com",
> "show me failed deployments", "create a database on web-prod-1".
>
> It's one self-contained Python file (standard library only — no pip install) plus a SKILL.md
> that teaches Claude when to call it. You authenticate once with your own Forge token (stored
> locally, chmod 600). Every mutating action is gated: it prints a dry-run and refuses to act
> until you confirm, so the model can't surprise-deploy anything.
>
> A few things I learned building it that might save someone time:
> - Forge sits behind Cloudflare, which 403s the default `Python-urllib` User-Agent and rate-limits
>   hard (Error 1015). You need a real UA and `Retry-After` backoff.
> - The API runs commands but doesn't return their stdout, and exposes no live disk/CPU — so
>   "which servers are low on disk?" isn't answerable via the API (I fall back to SSH).
>
> MIT, installable as a Claude Code plugin or a curl one-liner. Feedback welcome — especially on
> which Forge operations you'd want wrapped next.
>
> https://github.com/webmavens/claude-forge

---

## Reddit — r/laravel

**Title:**
> I built a Claude Code plugin to run Laravel Forge in plain English

**Body:**
> Managing Forge from the dashboard is fine, but I wanted to just *ask* — "deploy this site",
> "why did the last deploy fail", "create a db" — without clicking around. So I made a small open-source
> plugin that wraps the Forge API and lets Claude Code drive it.
>
> ![demo](https://raw.githubusercontent.com/webmavens/claude-forge/main/docs/demo.gif)
>
> - Servers, sites, deployments, databases, SSL, daemons, scheduled jobs, env files — plus a raw API passthrough.
> - You bring your own Forge token; it's stored locally (chmod 600), never leaves your machine except to call Forge.
> - Safety first: anything that changes infra shows a dry-run and needs an explicit confirm.
> - Zero dependencies — one stdlib Python file. Install as a Claude Code plugin or via curl.
>
> Repo + install instructions: https://github.com/webmavens/claude-forge
>
> It's MIT and early — would love feedback on what to add. What Forge tasks do you find yourself
> repeating that you'd want to just say out loud?

*(r/laravel etiquette: reply to comments, don't just drop and leave. Same post works for r/ClaudeAI with a one-line tweak of the intro.)*

---

## X / Twitter thread

**1/**
> I got tired of clicking around Laravel Forge for routine deploys, so I taught Claude Code to do it.
>
> "deploy acme.com" → done. "show failed deployments" → done.
>
> Open source, MIT. 🧵
> [attach docs/demo.gif]

**2/**
> It wraps the @laravelphp Forge API: servers, sites, deployments, databases, SSL, daemons,
> scheduled jobs, env files — plus a raw passthrough for anything else.

**3/**
> Safety was the whole point. Every change (deploy, reboot, create, env edit) prints a dry-run and
> refuses to run until you confirm. The model can't surprise-deploy your prod.

**4/**
> You connect your own Forge token once — stored locally, chmod 600, never goes anywhere but Forge.
> Zero dependencies: one standard-library Python file + a SKILL.md.

**5/**
> Install as a Claude Code plugin:
> /plugin marketplace add webmavens/claude-forge
> /plugin install forge@claude-forge
>
> Repo, curl install, docs 👇
> https://github.com/webmavens/claude-forge

*(Hashtags to sprinkle, not spam: #Laravel #LaravelForge #ClaudeCode)*

---

## Laravel News — link submission (laravel-news.com/links)

**URL:** https://github.com/webmavens/claude-forge

**Title:** claude-forge — drive Laravel Forge from Claude Code

**Description:**
> An open-source Claude Code plugin that wraps the Laravel Forge API so you can manage servers,
> sites, deployments, databases, SSL, daemons, scheduled jobs, and env files in plain English.
> Bring your own token (stored locally), with a confirm-first dry-run on every mutating action.
> Zero dependencies — one standard-library Python file. MIT.

---

## Discord (Laravel / Laracasts #packages, Claude communities)

> Built a little open-source thing: **claude-forge** — manage Laravel Forge from Claude Code in
> plain English (deploys, servers, sites, DBs, SSL, jobs…). Your own token, local + chmod 600,
> dry-run confirm on every change, zero deps. MIT → https://github.com/webmavens/claude-forge

---

## Posting order (suggested)

1. **Laravel News** submission (slow to publish, do it first).
2. **r/laravel** + **X thread** same morning (mid-week, ~9–11am ET tends to do well).
3. **Show HN** on a separate day (don't split your own attention; HN needs you replying for hours).
4. **Discords** anytime; **dev.to/blog** when the article is ready (see `blog-post.md`).
