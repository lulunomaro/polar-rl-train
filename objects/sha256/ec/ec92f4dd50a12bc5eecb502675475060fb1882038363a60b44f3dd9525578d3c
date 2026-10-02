#!/usr/bin/env bash
set -Eeuo pipefail
P=/home/egde/rl_candidates/MOD4_takeover_20260914/repair_1536_20260915
C=/home/egde/rl_candidates/MOD4_takeover_20260914/env_scaling_20260915/source/isaac/mod4
sed -i 's/\r$//' "$P"/files/*.py "$P"/files/*.sh "$P"/files/*.md
bash -n "$P/files/train_1536_skill_recovery.sh"
/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python -m py_compile "$P"/files/*.py
cp "$P/files/route_isaac.py" "$P/files/skills_isaac.py" "$P/files/mod4_task.py" \
  "$P/files/train_mod4_ppo.py" "$P/files/eval_episodes_mod4.py" \
  "$P/files/aggregate_acceptance.py" "$C/"
cp "$P/files/train_1536_skill_recovery.sh" "$P/train_1536_skill_recovery.sh"
cp "$P/files/TASK_CHECKLIST.md" "$P/TASK_CHECKLIST.md"
chmod +x "$P/train_1536_skill_recovery.sh"
sha256sum "$C/route_isaac.py" "$C/skills_isaac.py" "$C/mod4_task.py" \
  "$C/train_mod4_ppo.py" "$C/eval_episodes_mod4.py" "$C/aggregate_acceptance.py" \
  "$P/train_1536_skill_recovery.sh" > "$P/DEPLOYED.sha256"
cat "$P/DEPLOYED.sha256"
