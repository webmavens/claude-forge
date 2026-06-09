# VHS tape for the claude-forge demo GIF.
# Reproduce:  start the mock, then render.
#   python3 demo/mockforge.py &
#   vhs demo/demo.tape          # writes docs/demo.gif
#   (run from the repo root)
#
# All data shown comes from demo/mockforge.py — it is fictional.

Output docs/demo.gif

Set Shell "bash"
Set FontSize 20
Set Width 1180
Set Height 760
Set Padding 24
Set Margin 16
Set BorderRadius 10
Set WindowBar Colorful
Set Theme "Catppuccin Mocha"
Set TypingSpeed 55ms
Set PlaybackSpeed 1.0

# --- off-camera setup: point CLI at the local mock, clean prompt, short alias ---
Hide
Type "export FORGE_API_BASE=http://127.0.0.1:8771/api/v1 FORGE_API_TOKEN=demo-token" Enter
Type `export PS1='\[\e[38;5;213m\]forge-demo\[\e[0m\] $ '` Enter
Type "alias forge='python3 forge/skills/forge/forge.py'" Enter
Type "clear" Enter
Show

Sleep 800ms
Type "# Laravel Forge — driven from Claude Code. Authenticate once:" Sleep 500ms Enter
Type "forge auth --status" Sleep 400ms Enter
Sleep 1600ms

Type "forge servers list" Sleep 400ms Enter
Sleep 2200ms

Type "forge sites list 101" Sleep 400ms Enter
Sleep 2200ms

Type "# Every change is gated — dry-run first, no surprises:" Sleep 500ms Enter
Type "forge deploy run 101 5001" Sleep 400ms Enter
Sleep 2200ms

Type "# Confirm with --yes to actually do it:" Sleep 500ms Enter
Type "forge deploy run 101 5001 --yes" Sleep 400ms Enter
Sleep 1600ms

Type "forge deploy log 101 5001" Sleep 400ms Enter
Sleep 2600ms

Type "# That's it — servers, sites, deploys, DBs, SSL, jobs… in plain English." Sleep 500ms Enter
Sleep 2500ms
