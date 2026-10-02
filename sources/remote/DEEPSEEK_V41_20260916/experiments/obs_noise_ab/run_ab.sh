#!/usr/bin/env bash
# ==============================================================================
# DeepSeek-V4.1 独立实验：RM_ENCODER_BIAS 是不是动作抖动的来源
#
# 设计：同一 checkpoint、同一 seed、同一协议，只改 RM_ENCODER_BIAS 一个变量。
#       三臂 = 剂量-反应曲线（0.0 / 0.008 / 0.015）。
#
# 不干扰 GPT 侧：
#   - 共用 /tmp/mod4_takeover_gpu0.lock，拿不到锁就直接退出（exit 80）
#   - 纯推理评测，不训练、不写他们的目录、不产 checkpoint
#
# 用法：
#   bash run_ab.sh              # 跑全部三臂
#   bash run_ab.sh 0.008        # 只跑一臂
# ==============================================================================
set -uo pipefail

ROOT=/home/egde/rl_candidates/DEEPSEEK_V41_20260916
CODE="$ROOT/source/isaac/mod4"
PY=/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python
OUT="$ROOT/experiments/obs_noise_ab"
LOGS="$OUT/logs"
RES="$OUT/results"

# 被评测的 checkpoint（GPT 侧产物，只读引用）
CKPT=/home/egde/rl_candidates/MOD4_takeover_20260914/repair_zero_success_20260916/flat_dr/flat_run_reference_v10_continue/logs/2026-09-16_15-42-04_flat_run_reference_v10_continue/model_25.pt
# 合并材质后的资产（GPT 侧产物，只读引用）
USD=/home/egde/rl_candidates/MOD4_takeover_20260914/repair_1536_20260915/asset/robot_tireload12_mat3.usd
# GPT 侧的 common.env（只读引用，用于复现植物/网络架构参数）
COMMON=/home/egde/rl_candidates/MOD4_takeover_20260914/takeover/common.env

SEED=20260916
NUM_ENVS=256
STEPS=1500

mkdir -p "$LOGS" "$RES"

for f in "$CKPT" "$USD" "$COMMON" "$CODE/eval_episodes_mod4.py"; do
  if [ ! -f "$f" ]; then echo "缺少必需文件: $f" >&2; exit 2; fi
done

# ---------------------------------------------------------------------------
# 拿 GPU 锁：GPT 侧在跑就退出，不抢
# ---------------------------------------------------------------------------
# 跑一臂
#
# 锁【每臂单独获取、跑完立刻释放】，不是整轮持有 ——
# 这样 GPT 侧最多被挡一次评测的时长（约 3 分钟），而不是整轮 9 分钟。
# 拿不到锁 / 检测到他们的进程，就跳过这一臂：绝不等待、绝不抢。
# ---------------------------------------------------------------------------
run_arm() {
  local bias="$1"
  local tag; tag=$(echo "$bias" | tr '.' 'p')
  local report="$RES/dr_bias_${tag}.json"
  local log="$LOGS/dr_bias_${tag}.log"

  if [ -f "$report" ]; then
    echo "[dsv41] bias=$bias 已有结果，跳过"
    return 0
  fi

  # --- 取锁（只覆盖这一臂）---
  exec 9>/tmp/mod4_takeover_gpu0.lock
  if ! flock -n 9; then
    echo "[dsv41] $(date +%H:%M:%S) GPT 侧持有 GPU 锁，跳过 bias=$bias"
    exec 9>&-
    return 80
  fi
  if pgrep -f "[t]rain_mod4_ppo|[e]val_episodes_mod4" >/dev/null 2>&1; then
    echo "[dsv41] $(date +%H:%M:%S) 检测到 Isaac 进程，跳过 bias=$bias"
    exec 9>&-
    return 81
  fi
  echo "[dsv41] $(date +%H:%M:%S) 拿到锁，开始 bias=$bias"
  (
    set -a
    # 复现 GPT 侧的植物/网络参数（只读 common.env）
    while IFS= read -r line; do
      payload=${line#export }
      name=${payload%%=*}
      value=${payload#*=}
      if [[ "$line" == export\ * && "$name" =~ ^RM_[A-Z0-9_]+$ && "$value" =~ ^[-A-Za-z0-9_.,:/+]+$ ]]; then
        export "$name=$value"
      fi
    done < "$COMMON"
    set +a

    export OMNI_KIT_ACCEPT_EULA=YES PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
    export CUDA_VISIBLE_DEVICES=0
    export RM_MOD4_USD="$USD"
    export RM_MOD4_MAP=rmuc2026
    export RM_MOD4_TERRAIN=field
    export RM_ROUTE_KINDS=run
    export RM_ROUTE_WEIGHTS=run:1
    # ★ 唯一变量
    export RM_ENCODER_BIAS="$bias"

    "$PY" "$CODE/eval_episodes_mod4.py" --headless \
      --checkpoint "$CKPT" \
      --num_envs "$NUM_ENVS" --steps "$STEPS" --seed "$SEED" \
      --domain_rand \
      --report "$report"
  ) > "$log" 2>&1
  local rc=$?
  # --- 立刻释放锁，绝不长期占用 ---
  exec 9>&-
  echo "[dsv41] $(date +%H:%M:%S) bias=$bias rc=$rc  （锁已释放）"
  return $rc
}

# ---------------------------------------------------------------------------
if [ $# -ge 1 ]; then
  run_arm "$1"
else
  for b in 0.0 0.008 0.015; do
    run_arm "$b" || echo "[dsv41] bias=$b 失败，继续下一臂"
  done
fi

echo "[dsv41] 完成。结果在 $RES"
