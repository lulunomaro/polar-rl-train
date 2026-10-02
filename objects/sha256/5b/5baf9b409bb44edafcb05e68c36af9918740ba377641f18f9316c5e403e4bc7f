#!/usr/bin/env bash
# ==============================================================================
# DeepSeek-V4.1：平地鲁棒性与稳定性训练
#
# 目标（goal）：继续训练，把平底鲁棒性和稳定性做好
#
# 诊断（见 SUMMARY.md §诊断）：
#   - `model_25.pt` 在 nominal 下完成率仅 0.330，失败的 77% 是 base_contact（摔倒）
#   - 失败回合终点 x 中位 = -4.90，【已冲过目标 -5.5】—— 冲出终点后摔倒
#   - 起点 -9.0 → 1.59 s 走 3.18 m = 2.0 m/s，而指令上限是 1.2 m/s
#   ⇒ 机器人不跟踪指令速度，超速冲刺导致摔倒
#
# 干预（单一变量）：
#   RM_W_TRACK_LIN  6.0 → 12.0     强制跟踪指令速度 ≤1.2 m/s
#   其余保持 v10 配置不变（DR 开、ep 15 s、动作惩罚 −0.25/−0.080 等）
#
# 不干扰 GPT 侧：共用 GPU 锁，拿不到就退出，绝不抢。
# ==============================================================================
set -uo pipefail

ROOT=/home/egde/rl_candidates/DEEPSEEK_V41_20260916
CODE="$ROOT/source/isaac/mod4"
PY=/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python
OUT="$ROOT/experiments/flat_robust_stability"
LOGS="$OUT/logs"
RES="$OUT/results"

CKPT=/home/egde/rl_candidates/MOD4_takeover_20260914/repair_zero_success_20260916/flat_dr/flat_run_reference_v10_continue/logs/2026-09-16_15-42-04_flat_run_reference_v10_continue/model_25.pt
USD=/home/egde/rl_candidates/MOD4_takeover_20260914/repair_1536_20260915/asset/robot_tireload12_mat3.usd
COMMON=/home/egde/rl_candidates/MOD4_takeover_20260914/takeover/common.env

NUM_ENVS=12000
STEPS_PER_ENV=48
ITERS=${1:-150}
TRACK=${2:-12.0}
TAG=${3:-track12}
SEED=20260917

mkdir -p "$LOGS" "$RES"
for f in "$CKPT" "$USD" "$COMMON" "$CODE/train_mod4_ppo.py"; do
  [ -f "$f" ] || { echo "缺少: $f" >&2; exit 2; }
done

# --- 取锁 ---
exec 9>/tmp/mod4_takeover_gpu0.lock
if ! flock -n 9; then echo "[dsv41] GPU 锁被占，退出"; exit 80; fi
if pgrep -f "fangzhen-isaaclab/bin/python .*(train_mod4_ppo|eval_episodes_mod4)" >/dev/null 2>&1; then
  echo "[dsv41] 检测到 Isaac 进程，退出"; exit 81
fi

# --- 载入 GPT 侧植物/网络参数（只读）---
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

# --- 平地专用配置（基线 = v10 配置）---
export RM_ROUTE_KINDS=run RM_ROUTE_WEIGHTS=run:1
export RM_DR_OFF=0 RM_DR_PROFILE=mild RM_ROUTE_CURRICULUM=0
export RM_EPISODE_S=15
export RM_RUN_SPEED_MIN=0.30 RM_RUN_SPEED_MAX=1.20
export RM_ROUTE_PROGRESS_SCALE=100 RM_ROUTE_PROGRESS_W=0.10
export RM_ROUTE_SUCCESS_W=20 RM_RUN_SUCCESS_WEIGHT=20
export RM_W_ACTION_RATE=-0.25 RM_W_ACTION_ACC=-0.080
export RM_W_FLAT_ORIENT=-25 RM_W_ANG_VEL_XY=-1.0 RM_W_LEG_SYMMETRY=-0.7
export RM_W_TORQUES=-0.00005 RM_W_ACTION_L2_LEG=-0.05 RM_W_ACTION_L2_WHEEL=-0.015
export RM_ENTROPY_COEF=0.0002
export RM_PARTIAL_WARMSTART=1 RM_KEEP_STD=0 RM_INIT_STD=0.07
export RM_SOLVER_POS=16 RM_SOLVER_VEL=4
export RM_ENCODER_BIAS=0.008 RM_OBS_DELAY_MAX_LAG=1 RM_ACTION_DELAY_MS_MAX=2
export RM_TEACHER_BLEND_TUNNEL=0 RM_TEACHER_BLEND_FLY=0 RM_TEACHER_BLEND_JUMP=0
export RM_W_TUNNEL_ACTION_REFERENCE_ERROR=0 RM_W_FLY_ACTION_REFERENCE_ERROR=0 RM_W_JUMP_ACTION_REFERENCE_ERROR=0
export RM_GYRO_STEPS_PER_ITER=48

# ★ 唯一变量
export RM_W_TRACK_LIN="$TRACK"

echo "[dsv41] $(date +%H:%M:%S) 开始训练 tag=$TAG iters=$ITERS W_TRACK_LIN=$TRACK"
"$PY" "$CODE/train_mod4_ppo.py" --headless \
  --num_envs "$NUM_ENVS" --additional_iterations "$ITERS" --steps_per_env "$STEPS_PER_ENV" \
  --save_interval 10 --learning_rate 7.5e-5 --run_name "$TAG" --seed "$SEED" \
  --log_root "$OUT/logs/isaac" --init_checkpoint "$CKPT" \
  --report "$RES/${TAG}_train_report.json" \
  > "$LOGS/${TAG}_train.log" 2>&1
rc=$?
exec 9>&-
echo "[dsv41] $(date +%H:%M:%S) 训练结束 rc=$rc"
exit $rc
