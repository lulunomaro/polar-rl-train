#!/usr/bin/env bash
# ==============================================================================
# DeepSeek-V4.1：平地鲁棒性与稳定性 —— 继续训练
#
# goal: 继续训练，把平底鲁棒性和稳定性做好
#
# 诊断依据（见 SUMMARY.md）：
#   GPT 侧的 `flat_run_reference_v10_continue` 在 **26/40 迭代被主动暂停**，
#   而训练期 route_complete 当时仍在单调上升：
#       迭代 0  → 0.0000
#       迭代 10 → 0.4125
#       迭代 20 → 0.7004     ← 已越过 0.70 门限
#       迭代 26 → 0.7506     ← 暂停点
#   说明【训练有效但被过早停止】。
#
# 因此本轮【不修改任何超参】——原样复现 v10 配置，只是训练得更久。
# 复现方式：直接套用 v10 run_manifest.json 里的全部 151 项 RM_* 环境变量，
#           避免手工抄写引入偏差。
#
# 不干扰 GPT 侧：共用 GPU 锁，拿不到就退出；只写本工作区。
# ==============================================================================
set -uo pipefail

ROOT=/home/egde/rl_candidates/DEEPSEEK_V41_20260916
CODE="$ROOT/source/isaac/mod4"
PY=/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python
OUT="$ROOT/experiments/flat_robust_stability"

# v10 的配置来源（只读）
V10_MANIFEST=/home/egde/rl_candidates/MOD4_takeover_20260914/repair_zero_success_20260916/flat_dr/flat_run_reference_v10_continue/logs/2026-09-16_15-42-04_flat_run_reference_v10_continue/run_manifest.json
CKPT=/home/egde/rl_candidates/MOD4_takeover_20260914/repair_zero_success_20260916/flat_dr/flat_run_reference_v10_continue/logs/2026-09-16_15-42-04_flat_run_reference_v10_continue/model_25.pt

ITERS=${1:-150}
TAG=${2:-cont_v10_a}
SEED=${3:-20260917}
LR=${4:-7.5e-5}

mkdir -p "$OUT/logs/isaac" "$OUT/results"
for f in "$V10_MANIFEST" "$CKPT" "$CODE/train_mod4_ppo.py"; do
  [ -f "$f" ] || { echo "缺少: $f" >&2; exit 2; }
done

# --- 取锁（整个训练期间持有；训练是长任务，这是必要的）---
exec 9>/tmp/mod4_takeover_gpu0.lock
if ! flock -n 9; then echo "[dsv41] GPU 锁被占，退出"; exit 80; fi
if pgrep -f "fangzhen-isaaclab/bin/python .*(train_mod4_ppo|eval_episodes_mod4)" >/dev/null 2>&1; then
  echo "[dsv41] 检测到 Isaac 进程，退出"; exit 81
fi
echo "[dsv41] $(date +%H:%M:%S) 取得 GPU 锁"

# --- 逐项复现 v10 配置 ---
eval "$("$PY" - "$V10_MANIFEST" <<'PYEOF'
import json, sys, shlex
env = (json.load(open(sys.argv[1])).get('env') or {})
out = []
for k in sorted(env):
    v = env[k]
    if v is None: continue
    # bash 变量名只允许 [A-Za-z_][A-Za-z0-9_]*
    if not (k[:1].isalpha() or k[0] == '_'): continue
    if not all(c.isalnum() or c == '_' for c in k): continue
    out.append('export %s=%s' % (k, shlex.quote(str(v))))
print('\n'.join(out))
PYEOF
)"

export OMNI_KIT_ACCEPT_EULA=YES PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
export CUDA_VISIBLE_DEVICES=0
export RM_GYRO_STEPS_PER_ITER=48

# --- 校验：关键项与 v10 一致 ---
echo "[dsv41] 配置自检:"
for k in RM_ROUTE_KINDS RM_DR_OFF RM_EPISODE_S RM_W_TRACK_LIN RM_W_RUN_VEL_ERROR \
         RM_W_ACTION_RATE RM_W_ACTION_ACC RM_W_FLAT_ORIENT RM_SOLVER_POS RM_RUN_SPEED_MAX; do
  printf '    %-26s %s\n' "$k" "${!k:-未设}"
done

# --- 训练 ---
echo "[dsv41] $(date +%H:%M:%S) 开始训练 tag=$TAG iters=$ITERS lr=$LR (增量自 model_25.pt)"
"$PY" "$CODE/train_mod4_ppo.py" --headless \
  --num_envs 12000 --additional_iterations "$ITERS" --steps_per_env 48 \
  --save_interval 10 --learning_rate "$LR" --run_name "$TAG" --seed "$SEED" \
  --log_root "$OUT/logs/isaac" --init_checkpoint "$CKPT" \
  --report "$OUT/results/${TAG}_train_report.json" \
  > "$OUT/logs/${TAG}_train.log" 2>&1
rc=$?
exec 9>&-
echo "[dsv41] $(date +%H:%M:%S) 训练结束 rc=$rc"
exit $rc
