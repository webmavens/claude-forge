#!/usr/bin/env bash
#
# claude-forge installer — drops the `forge` skill into ~/.claude/skills/forge
# for Claude Code users who don't use the plugin system.
#
#   curl -fsSL https://raw.githubusercontent.com/webmavens/claude-forge/main/install.sh | bash
#
set -euo pipefail

REPO="webmavens/claude-forge"
BRANCH="${CLAUDE_FORGE_BRANCH:-main}"
DEST="${HOME}/.claude/skills/forge"
RAW="https://raw.githubusercontent.com/${REPO}/${BRANCH}/forge/skills/forge"

echo "→ Installing the 'forge' skill into ${DEST}"

command -v python3 >/dev/null 2>&1 || { echo "✗ python3 is required but not found."; exit 1; }
command -v curl    >/dev/null 2>&1 || { echo "✗ curl is required but not found.";    exit 1; }

mkdir -p "${DEST}"
for f in SKILL.md forge.py; do
  echo "  • ${f}"
  curl -fsSL "${RAW}/${f}" -o "${DEST}/${f}"
done
chmod +x "${DEST}/forge.py"

cat <<EOF

✓ Installed.

Next steps:
  1. Get a Forge API token: forge.laravel.com → Account → API → Create API Token
  2. Authenticate (run in a real terminal so the prompt is hidden):
       python3 "${DEST}/forge.py" auth
     …or pass it inline:
       python3 "${DEST}/forge.py" auth <YOUR_TOKEN>
  3. In Claude Code, type /forge and ask away — e.g. "/forge list my servers".

Your token is stored at ~/.claude/forge/credentials (chmod 600). Remove it anytime with:
  python3 "${DEST}/forge.py" logout
EOF
