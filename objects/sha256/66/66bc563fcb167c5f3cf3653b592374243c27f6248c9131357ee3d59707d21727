#!/usr/bin/env bash
# Manual integration tool. Uploading this package never runs this script.
set -euo pipefail
if [ "$#" -lt 3 ]; then
  echo "usage: $0 CANDIDATE_ROOT CHECKPOINT NEW_OUTPUT_DIR [NUM_ENVS=64] [STEPS=9000] [KINDS=all]" >&2
  exit 2
fi
ROOT=$(realpath "$1")
CKPT=$(realpath "$2")
OUT=$(realpath -m "$3")
PY=${MOD4_EVAL_PYTHON:-/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python}
[ -f "$ROOT/REPAIR_ORIGIN.json" ] || { echo "Not a staged repair candidate" >&2; exit 2; }
[ ! -e "$OUT" ] || { echo "Output exists; refusing to mix evaluation evidence" >&2; exit 2; }
if pgrep -f '[t]rain_mod4_ppo.py|[e]val_terrain_mod4.py|[e]val_episodes_mod4.py' >/dev/null; then
  echo "RL process already active; no evaluation launched" >&2; exit 3
fi
export PYTHONDONTWRITEBYTECODE=1 OMNI_KIT_ACCEPT_EULA=YES
export RM_MOD4_MAP=rmuc2026 RM_MOD4_TERRAIN=field RM_DR_OFF=1 RM_ROUTE_CURRICULUM=0
export RM_TUNNEL_GOAL_X=0 RM_TUNNEL_SPAWN_LEAD_M=0 RM_ROUTE_WEIGHTS=
export RM_MOD4_USD=/home/egde/fangzhen_linux/incoming/mod4_rolling_20260913/chassis_mod4/isaac/robot.usd
export RM_ROUTE_KINDS=${6:-}
mkdir -p "$OUT"
cd "$ROOT"
for seed in 20260912 20260913 20260914; do
  "$PY" isaac/mod4/eval_episodes_mod4.py --headless --checkpoint "$CKPT" \
    --num_envs "${4:-64}" --steps "${5:-9000}" --seed "$seed" \
    --report "$OUT/seed_${seed}.json" >"$OUT/seed_${seed}.log" 2>&1
done
echo "ROLLOUT_REPORTS_WRITTEN=$OUT (not an automatic skill/clearance pass)"
