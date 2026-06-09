# Demo assets

The README GIF (`docs/demo.gif`) is generated deterministically — no real Forge account
involved. Everything you see is canned, fictional data served by `mockforge.py`.

## Regenerate the GIF

Requires [`vhs`](https://github.com/charmbracelet/vhs) (`brew install vhs`). From the repo root:

```bash
python3 demo/mockforge.py &           # fake Forge API on http://127.0.0.1:8771
vhs demo/demo.tape                    # renders docs/demo.gif
kill %1                               # stop the mock
```

## Files

- `mockforge.py` — a ~60-line mock of the Forge API (servers, sites, deploy, log, db) with
  made-up data. Point the CLI at it with `FORGE_API_BASE`:
  ```bash
  export FORGE_API_BASE=http://127.0.0.1:8771/api/v1
  export FORGE_API_TOKEN=demo-token
  python3 forge/skills/forge/forge.py servers list
  ```
- `demo.tape` — the VHS script that types the commands and records the GIF.

This is also a handy way to try the CLI or run it in tests without a Forge account.
