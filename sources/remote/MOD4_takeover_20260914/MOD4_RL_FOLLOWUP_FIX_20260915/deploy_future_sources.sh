#!/usr/bin/env bash
set -Eeuo pipefail

ROOT=/home/egde/rl_candidates/MOD4_takeover_20260914
PKG="$ROOT/MOD4_RL_FOLLOWUP_FIX_20260915"
CODE="$ROOT/env_scaling_20260915/source/isaac/mod4"
PY=/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python
STAMP=$(date +%Y%m%d_%H%M%S)
BACKUP="$PKG/backups/$STAMP"

mkdir -p "$BACKUP"
sed -i 's/\r$//' "$PKG"/files/*.py "$PKG"/*.sh "$PKG"/*.md
"$PY" -m py_compile "$PKG"/files/*.py
"$PY" "$PKG/tests/test_followup_static.py"
PYTHONPATH="$CODE" "$PY" -m pytest -q "$PKG/tests/test_takeover_contracts.py"

for src in "$PKG"/files/*.py; do
  name=$(basename "$src")
  [[ ! -f "$CODE/$name" ]] || cp -a "$CODE/$name" "$BACKUP/$name"
  cp "$src" "$CODE/$name"
done

# Never replace the shell script that currently owns GPU0.  Install the reviewed resume script
# under a new name; the supervisor can switch to it at the s2 checkpoint boundary.
cp "$PKG/train_1536_skill_recovery_v2.sh" "$PKG/train_1536_skill_recovery_v2.installed.sh"
chmod +x "$PKG/train_1536_skill_recovery_v2.installed.sh"

sha256sum "$PKG"/files/*.py "$PKG/train_1536_skill_recovery_v2.installed.sh" \
  > "$PKG/DEPLOYED_FUTURE_SOURCES.sha256"
echo "future-stage sources installed; current Python process was not restarted"
echo "backup=$BACKUP"
