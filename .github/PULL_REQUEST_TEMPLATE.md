<!-- Thanks for contributing! Keep PRs focused — one change per PR. -->

## What does this change?

<!-- Brief description. Link any related issue: Closes #123 -->

## Type

- [ ] New command / endpoint
- [ ] Bug fix
- [ ] Docs (`SKILL.md` / README)
- [ ] Other:

## Checklist

- [ ] `forge.py` uses **standard library only** (no new deps)
- [ ] Mutating actions go through `confirm_gate()` (require `--yes`)
- [ ] New subparser has `parents=[common]` (so `--json`/`--yes` work anywhere)
- [ ] `SKILL.md` updated if commands changed
- [ ] `CHANGELOG.md` updated; version bumped in both manifest files if needed
- [ ] No secrets/tokens committed

## How did you test it?

<!-- Which Forge resources, read vs. mutating, any rate-limit behavior observed. -->
