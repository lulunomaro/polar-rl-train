#!/usr/bin/env bash
# ==============================================================================
# DeepSeek-V4.1：植物层 A/B —— RM_LEG_KP 是否驱动"腾空"
#
# 背景（见 SUMMARY.md §11）：
#   三项反跳跃/跟踪奖励（权重 −2.0 / +5.0 / −2.0）全部确认生效，
#   但机器人依然 89% 时间轮子离地（`drive_wheel_contact_rate = 0.274`）。
#   ⇒ 奖励层面的杠杆已用尽，怀疑是【植物层】现象。
#
# 候选根因：`RM_LEG_KP`
#   训练用 2500，而交付合同 `DELIVERY_CONTRACT["leg_kp"]` = **60**
#   （`mod4_task.py:127` 的默认值就是合同值，注释写着 # 60.0）
#   差 **41.7 倍**。极硬的关节位置控制会把目标微振放大成力振荡 ⇒ 弹跳。
#
# 设计：同一 checkpoint、同一协议、只改 RM_LEG_KP
#   arm A: 2500  （训练时的值，基线）
#   arm B: 1000  （中间点）
#   arm C: 250
#   arm D: 60    （交付合同值 ← sim2real 的真实工作点）
#
# 判读（预先登记）：
#   1. 着地率随 kp 下降而【显著上升】 ⇒ 根因是增益不匹配
#      （同时说明：策略在真机会比在训练里更"跳"，或反之）
#   2. 着地率不随 kp 变化 ⇒ 根因在气弹簧/蹲姿/控制频率
#   3. 完成率在 kp=60 时【崩塌】 ⇒ 直接量化 sim2real 风险
#
# 纯推理，每臂约 5 分钟。GPU 锁每臂单独取放。
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
V10_MANIFEST=/home/egde/rl_candidates/MOD4_takeover_20260914/repair_zero_success_20260916/flat_dr/flat_run_reference_v10_continue/logs/2026-09-16_15-42-04_flat_run_reference_v10_continue/run_manifest.json

TAG=${1:?用法: run_plant_ab.sh <tag> <checkpoint> [kp 列表]}
CKPT=${2:?需要 checkpoint}
shift 2
KPS=("$@")
[ ${#KPS[@]} -eq 0 ] && KPS=(2500 1000 250 60)

NUM_ENVS=256
STEPS=1500
SEED=20260917

mkdir -p "$LOGS" "$RES"
[ -f "$CKPT" ] || { echo "checkpoint 不存在: $CKPT" >&2; exit 2; }

run_arm() {
  local kp="$1"
  local report="$RES/${TAG}_kp${kp}.json"
  local log="$LOGS/${TAG}_kp${kp}.log"
  [ -f "$report" ] && { echo "[dsv41] kp=$kp 已有结果，跳过"; return 0; }

  exec 9>/tmp/mod4_takeover_gpu0.lock
  if ! flock -n 9; then echo "[dsv41] 锁被占，跳过 kp=$kp"; exec 9>&-; return 80; fi
  if pgrep -f "fangzhen-isaaclab/bin/python .*(train_mod4_ppo|eval_episodes_mod4)" >/dev/null 2>&1; then
    echo "[dsv41] Isaac 在跑，跳过 kp=$kp"; exec 9>&-; return 81
  fi
  echo "[dsv41] $(date +%H:%M:%S) 评测 kp=$kp"
  (
    # 逐项复现 v10 配置
    eval "$("$PY" - "$V10_MANIFEST" <<'PYEOF'
import json, sys, shlex
env=(json.load(open(sys.argv[1])).get('env') or {})
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
    export RM_MOD4_USD="$USD" RM_MOD4_MAP=rmuc2026 RM_MOD4_TERRAIN=field
    export RM_ROUTE_KINDS=run RM_EPISODE_S=15
    # ★ 唯一变量
    export RM_LEG_KP="$kp"
    "$PY" "$CODE/eval_episodes_mod4.py" --headless \
      --checkpoint "$CKPT" --num_envs "$NUM_ENVS" --steps "$STEPS" --seed "$SEED" \
      --report "$report"
  ) > "$log" 2>&1
  local rc=$?
  exec 9>&-
  echo "[dsv41] $(date +%H:%M:%S) kp=$kp rc=$rc"
  return $rc
}

for kp in "${KPS[@]}"; do run_arm "$kp" || true; done
echo "[dsv41] 完成。结果: $RES/${TAG}_kp*.json"
