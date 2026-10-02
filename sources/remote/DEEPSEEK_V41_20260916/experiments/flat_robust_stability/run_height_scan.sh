#!/usr/bin/env bash
# 高度指令范围扫描（纯推理）。用法: run_height_scan.sh <tag> <ckpt> hmin hmax [hmin hmax ...]
set -uo pipefail
ROOT=/home/egde/rl_candidates/DEEPSEEK_V41_20260916
CODE="$ROOT/source/isaac/mod4"; PY=/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python
OUT="$ROOT/experiments/flat_robust_stability"; LOGS="$OUT/logs"; RES="$OUT/results"
USD=/home/egde/rl_candidates/MOD4_takeover_20260914/repair_1536_20260915/asset/robot_tireload12_mat3.usd
V10=/home/egde/rl_candidates/MOD4_takeover_20260914/repair_zero_success_20260916/flat_dr/flat_run_reference_v10_continue/logs/2026-09-16_15-42-04_flat_run_reference_v10_continue/run_manifest.json
TAG=$1; CKPT=$2; shift 2; PAIRS=("$@")
mkdir -p "$LOGS" "$RES"
i=0
while [ $i -lt ${#PAIRS[@]} ]; do
  HMIN=${PAIRS[$i]}; HMAX=${PAIRS[$((i+1))]}; i=$((i+2))
  rep="$RES/${TAG}_h${HMIN}_${HMAX}.json"; log="$LOGS/${TAG}_h${HMIN}_${HMAX}.log"
  [ -f "$rep" ] && { echo "[dsv41] h=$HMIN/$HMAX 已存在，跳过"; continue; }
  exec 9>/tmp/mod4_takeover_gpu0.lock
  if ! flock -n 9; then echo "[dsv41] 锁被占，跳过"; exec 9>&-; continue; fi
  if pgrep -f "fangzhen-isaaclab/bin/python .*(train_mod4_ppo|eval_episodes_mod4)" >/dev/null 2>&1; then
    echo "[dsv41] Isaac 在跑，跳过"; exec 9>&-; continue; fi
  echo "[dsv41] $(date +%H:%M:%S) 评测 h=$HMIN/$HMAX"
  (
    eval "$("$PY" - "$V10" <<'PYEOF'
import json,sys,shlex
env=(json.load(open(sys.argv[1])).get('env') or {})
for k in sorted(env):
    v=env[k]
    if v is None or not (k[:1].isalpha() or k[0]=='_') or not all(c.isalnum() or c=='_' for c in k): continue
    print('export %s=%s' % (k, shlex.quote(str(v))))
PYEOF
)"
    export OMNI_KIT_ACCEPT_EULA=YES PYTHONUNBUFFERED=1 CUDA_VISIBLE_DEVICES=0
    export RM_MOD4_USD="$USD" RM_MOD4_MAP=rmuc2026 RM_MOD4_TERRAIN=field
    export RM_ROUTE_KINDS=run RM_EPISODE_S=15 RM_LEG_KP=250
    export RM_HEIGHT_MIN="$HMIN" RM_HEIGHT_MAX="$HMAX"
    "$PY" "$CODE/eval_episodes_mod4.py" --headless --checkpoint "$CKPT" \
      --num_envs 256 --steps 1500 --seed 20260923 --report "$rep"
  ) > "$log" 2>&1
  rc=$?; exec 9>&-
  echo "[dsv41] $(date +%H:%M:%S) h=$HMIN/$HMAX rc=$rc"
done
