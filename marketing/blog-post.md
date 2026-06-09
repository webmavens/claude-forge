---
title: "We Now Deploy Laravel Apps by Talking to Claude"
description: "How we built claude-forge — an open-source Claude Code plugin that drives the Laravel Forge API in plain English, with a confirm-first safety model."
tags: [laravel, devops, claude, ai, forge]
canonical_url: https://github.com/webmavens/claude-forge
cover_image: https://raw.githubusercontent.com/webmavens/claude-forge/main/docs/social-preview.png
---

# We Now Deploy Laravel Apps by Talking to Claude

At Webmavens we run a lot of Laravel apps on [Laravel Forge](https://forge.laravel.com). Forge is
excellent, but day to day there's a steady tax of small, repetitive trips to the dashboard:
trigger a deploy, scroll the log to see why one failed, create a database, check a site's `.env`.
None of it is hard. It's just *clicky*.

So we built [**claude-forge**](https://github.com/webmavens/claude-forge): an open-source
[Claude Code](https://code.claude.com) plugin that wraps the Forge API and lets you operate your
infrastructure in plain English.

![demo](https://raw.githubusercontent.com/webmavens/claude-forge/main/docs/demo.gif)

```
You:  deploy acme.com
You:  which of my deployments failed recently?
You:  create a database called analytics on web-prod-1
```

It's MIT-licensed, has zero dependencies, and you connect it to your own Forge account.

## What it does

The plugin covers the operations we actually use:

- **Servers** — list, inspect, reboot
- **Sites** — list, inspect, create
- **Deployments** — trigger, read the log, edit the deploy script, toggle quick deploy
- **Databases & users** — list, create
- **SSL** — list certs, request Let's Encrypt
- **Daemons & scheduled jobs** — list, create
- **Env files** — read and write a site's `.env`
- **A raw API passthrough** for anything we didn't wrap yet

Under the hood it's a single, self-contained Python script (standard library only — nothing to
`pip install`) plus a `SKILL.md` that teaches Claude Code when and how to call it.

## The part we cared about most: safety

Handing an AI agent the keys to production is exactly as nerve-wracking as it sounds. So the design
rule was simple: **the model can never change infrastructure without you confirming.**

Every mutating action — deploy, reboot, create, env edit — first prints a dry run and stops:

```
$ forge deploy run 101 5001
WOULD: deploy site 5001 on server 101
This is a mutating action. Re-run with --yes to execute.
```

Claude shows you that line, you say yes, and only then does it run with `--yes`. Read-only commands
(listing, logs, status) run freely. Your Forge token is stored locally with `chmod 600` and never
leaves your machine except to talk to Forge over HTTPS.

## Three things we learned about the Forge API

Building this surfaced a few non-obvious things worth writing down:

1. **Forge is behind Cloudflare.** The default `Python-urllib` User-Agent gets a flat `403`. Send a
   real User-Agent and you're fine. Cloudflare also rate-limits aggressively (Error 1015), so any
   account-wide sweep needs to honor `Retry-After` with exponential backoff — which the plugin now
   does automatically.

2. **The API runs commands but won't return their output.** You can execute a site command or a
   recipe, but stdout isn't exposed over the API (only in the web UI). That has a real consequence:
   "which servers are low on disk?" *isn't answerable through the Forge API* — there's no live
   disk/CPU field either. We fall back to SSH (`ssh forge@<ip> df -h`) for that.

3. **Deployment state vs. history are different questions.** A site's `deployment_status` only
   reflects its *latest* deploy; to find historical failures you have to walk each site's
   deployment history endpoint. Worth knowing before you build a "what's broken?" report.

## Install it

**As a Claude Code plugin:**

```
/plugin marketplace add webmavens/claude-forge
/plugin install forge@claude-forge
```

**Or via curl:**

```
curl -fsSL https://raw.githubusercontent.com/webmavens/claude-forge/main/install.sh | bash
```

Then create a token at *forge.laravel.com → Account → API*, and authenticate once:

```
python3 ~/.claude/skills/forge/forge.py auth
```

## It's open source — tell us what to add

The whole thing is two files and a clean `api()` seam. We kept it deliberately small so it's easy
to read and extend, and there's a mock server in the repo so you can try it (or run tests) without
touching a real Forge account.

If there's a Forge operation you'd want to just *say out loud*, open an issue or a PR:
**https://github.com/webmavens/claude-forge**

---

*Built by [Webmavens](https://webmavens.com). If you'd like help putting AI agents to work safely on
your own infrastructure and workflows, [get in touch](https://webmavens.com/contact).*
