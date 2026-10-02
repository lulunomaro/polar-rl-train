#!/usr/bin/env bash
# ==============================================================================
# DeepSeek-V4.1：平地鲁棒性与稳定性 —— 结构性干预
#
# 前一步的负结果（SUMMARY §8）：
#   同一配置继续训练到迭代 42 后【完全收敛到平台】：
#       route_complete ≈ 0.77（训练口径）
#       base_contact   ≈ 0.205
#       wheel_contact  ≈ 0.108   ← 89% 时间轮子离地
#       vel_err        ≈ 1.15 m/s
#   ⇒ 排除"训练不足"，问题是结构性的。
#
# 根因：
#   `track_lin_vel` 用高斯核，`RM_TRACK_SIGMA=0.50`。
#   实测速度误差 1.15 m/s 时核值 = exp(-(1.15/0.5)^2) = exp(-5.29) ≈ 0.005
#   ⇒ 跟踪奖励【饱和为零】，策略失去把速度拉回指令的梯度
#   `skills_isaac.py:820` 的文档正是这么写的：
#     "The exponential tracking reward has almost no gradient after a warm-start
#      policy gets far outside its kernel."
#
# 干预（单一变量）：
#   RM_TRACK_SIGMA  0.50 → 1.00
#   零误差处核值仍为 1.0（最优不变），但衰减变缓：
#       误差 0.5 m/s: 0.368 → 0.779
#       误差 1.0 m/s: 0.018 → 0.368
#       误差 1.5 m/s: 0.000 → 0.105
#   ⇒ 在高误差区恢复有效梯度，形成真正的回复力
#
# 其余配置：逐项套用 v10 的 151 项 RM_* 变量，不做其他改动。
# ==============================================================================
set -uo pipefail

ROOT=/home/egde/rl_candidates/DEEPSEEK_V41_20260916
CODE="$ROOT/source/isaac/mod4"
PY=/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python
OUT="$ROOT/experiments/flat_robust_stability"

V10_MANIFEST=/home/egde/rl_candidates/MOD4_takeover_20260914/repair_zero_success_20260916/flat_dr/flat_run_reference_v10_continue/logs/2026-09-16_15-42-04_flat_run_reference_v10_continue/run_manifest.json

ITERS=${1:-120}
TAG=${2:-sigma10_a}
INIT=${3:?需要指定 init checkpoint}
SEED=${4:-20260918}
LR=${5:-7.5e-5}
SIGMA=${6:-1.00}

mkdir -p "$OUT/logs/isaac" "$OUT/results"
[ -f "$INIT" ] || { echo "init 不存在: $INIT" >&2; exit 2; }

exec 9>/tmp/mod4_takeover_gpu0.lock
if ! flock -n 9; then echo "[dsv41] GPU 锁被占，退出"; exit 80; fi
if pgrep -f "fangzhen-isaaclab/bin/python .*(train_mod4_ppo|eval_episodes_mod4)" >/dev/null 2>&1; then
  echo "[dsv41] 检测到 Isaac 进程，退出"; exit 81
fi
echo "[dsv41] $(date +%H:%M:%S) 取得 GPU 锁"

eval "$("$PY" - "$V10_MANIFEST" <<'PYEOF'
import json, sys, shlex
env = (json.load(open(sys.argv[1])).get('env') or {})
out=[]
for k in sorted(env):
    v=env[k]
    if v is None: continue
    if not (k[:1].isalpha() or k[0]=='_'): continue
    if not all(c.isalnum() or c=='_' for c in k): continue
    out.append('export %s=%s' % (k, shlex.quote(str(v))))
print('\n'.join(out))
PYEOF
)"

export OMNI_KIT_ACCEPT_EULA=YES PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
export CUDA_VISIBLE_DEVICES=0
export RM_GYRO_STEPS_PER_ITER=48

# ★ 唯一变量
export RM_TRACK_SIGMA="$SIGMA"

echo "[dsv41] 配置自检:"
for k in RM_TRACK_SIGMA RM_W_TRACK_LIN RM_W_RUN_VEL_ERROR RM_RUN_SPEED_MAX RM_W_ACTION_RATE \
         RM_W_RUN_AIRBORNE RM_W_WHEEL_CONTACT RM_DR_OFF RM_EPISODE_S; do
  printf '    %-26s %s\n' "$k" "${!k:-未设}"
done
echo "[dsv41] init=$(basename "$INIT")"

echo "[dsv41] $(date +%H:%M:%S) 开始训练 tag=$TAG iters=$ITERS sigma=$SIGMA"
"$PY" "$CODE/train_mod4_ppo.py" --headless \
  --num_envs 12000 --additional_iterations "$ITERS" --steps_per_env 48 \
  --save_interval 10 --learning_rate "$LR" --run_name "$TAG" --seed "$SEED" \
  --log_root "$OUT/logs/isaac" --init_checkpoint "$INIT" \
  --report "$OUT/results/${TAG}_train_report.json" \
  > "$OUT/logs/${TAG}_train.log" 2>&1
rc=$?
exec 9>&-
echo "[dsv41] $(date +%H:%M:%S) 训练结束 rc=$rc"
exit $rc
