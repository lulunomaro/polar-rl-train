#!/usr/bin/env bash
# ==============================================================================
# DeepSeek-V4.1：平地评测（nominal + DR），口径对齐验收协议
#
# 用法：bash run_eval.sh <tag> <checkpoint>
#   tag        结果文件名前缀
#   checkpoint 被评测的 .pt
#
# 口径（与 GPT 侧 flat_eval_* 及我的 obs_noise_ab 一致）：
#   RM_ROUTE_KINDS=run, 256 env × 1500 步, RM_EPISODE_S=15
#   nominal = 不加 --domain_rand；DR = 加 --domain_rand
#
# 每臂单独取锁、跑完立刻释放；拿不到锁就跳过。
# ==============================================================================
set -uo pipefail

ROOT=/home/egde/rl_candidates/DEEPSEEK_V41_20260916
CODE="$ROOT/source/isaac/mod4"
PY=/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python
OUT="$ROOT/experiments/flat_robust_stability"
LOGS="$OUT/logs"
RES="$OUT/results"

USD=/home/egde/rl_candidates/MOD4_takeover_20260914/repair_1536_20260915/asset/robot_tireload12_mat3.usd
COMMON=/home/egde/rl_candidates/MOD4_takeover_20260914/takeover/common.env

TAG=${1:?用法: run_eval.sh <tag> <checkpoint>}
CKPT=${2:?用法: run_eval.sh <tag> <checkpoint>}
NUM_ENVS=256
STEPS=1500
SEED=20260917

mkdir -p "$LOGS" "$RES"
[ -f "$CKPT" ] || { echo "checkpoint 不存在: $CKPT" >&2; exit 2; }

load_env() {
  while IFS= read -r line; do
    payload=${line#export }
    name=${payload%%=*}
    value=${payload#*=}
    if [[ "$line" == export\ * && "$name" =~ ^RM_[A-Z0-9_]+$ && "$value" =~ ^[-A-Za-z0-9_.,:/+]+$ ]]; then
      export "$name=$value"
    fi
  done < "$COMMON"
  export OMNI_KIT_ACCEPT_EULA=YES PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
  export CUDA_VISIBLE_DEVICES=0
  export RM_MOD4_USD="$USD" RM_MOD4_MAP=rmuc2026 RM_MOD4_TERRAIN=field
  export RM_ROUTE_KINDS=run RM_ROUTE_WEIGHTS=run:1
  export RM_EPISODE_S=15
  export RM_RUN_SPEED_MIN=0.30 RM_RUN_SPEED_MAX=1.20
  export RM_SOLVER_POS=16 RM_SOLVER_VEL=4
  # 评测必须复现训练时的动作空间（否则策略输出会被放大/缩小）
  export RM_LEG_ACTION_SCALE="${LEG_SCALE:-0.5}"
  export RM_SOFT_LIMIT_FACTOR="${SOFT_LIMIT:-1.0}"
  export RM_HEIGHT_STD="${HEIGHT_STD:-0.06}"
  export RM_CLAMP_LEG_TARGETS="${CLAMP_LEG:-0}"
  export RM_LEG_KP="${LEG_KP:-250}"
  export RM_DIFF_MAX="${DIFF_MAX:-0.85}"
}

eval_arm() {
  local mode="$1" extra="$2"
  local report="$RES/${TAG}_${mode}.json"
  local log="$LOGS/${TAG}_${mode}.log"
  [ -f "$report" ] && { echo "[dsv41] $TAG/$mode 已存在，跳过"; return 0; }

  exec 9>/tmp/mod4_takeover_gpu0.lock
  if ! flock -n 9; then echo "[dsv41] 锁被占，跳过 $TAG/$mode"; exec 9>&-; return 80; fi
  if pgrep -f "fangzhen-isaaclab/bin/python .*(train_mod4_ppo|eval_episodes_mod4)" >/dev/null 2>&1; then
    echo "[dsv41] Isaac 在跑，跳过 $TAG/$mode"; exec 9>&-; return 81
  fi
  echo "[dsv41] $(date +%H:%M:%S) 评测 $TAG/$mode"
  (
    load_env
    # shellcheck disable=SC2086
    "$PY" "$CODE/eval_episodes_mod4.py" --headless \
      --checkpoint "$CKPT" --num_envs "$NUM_ENVS" --steps "$STEPS" --seed "$SEED" \
      $extra --report "$report"
  ) > "$log" 2>&1
  local rc=$?
  exec 9>&-
  echo "[dsv41] $(date +%H:%M:%S) $TAG/$mode rc=$rc"
  return $rc
}

eval_arm nominal ""            || true
eval_arm dr      "--domain_rand" || true
echo "[dsv41] 完成：$RES/${TAG}_{nominal,dr}.json"
