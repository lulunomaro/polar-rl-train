#!/usr/bin/env bash
# MOD4 domain-randomised stage launcher (goal 2026-09-12 section 5).
#
# Same contract as start_mod4_stage_fixedplant.sh, with two deliberate differences:
#   * RM_DR_OFF defaults to 0 (randomisation ON).  Pass RM_DR_OFF=1 to use it as a
#     nominal control run.
#   * every RM_DR_* / RM_BATT_* / RM_TERRAIN_FRICTION_* knob in the environment is
#     passed through untouched and echoed into the log, so the run manifest and the
#     log agree on what was sampled.
#
#   ./start_mod4_dr_fixedplant.sh <init_checkpoint> [num_envs] [iters] [route_weights]
#   FORCE=1  allow starting while another train_mod4_ppo.py is alive
set -euo pipefail
cd "$(dirname "$0")/../.."

CKPT=${1:?usage: start_mod4_dr_fixedplant.sh <init_checkpoint> [num_envs] [iters] [weights]}
NUM_ENVS=${2:-1024}
ITERS=${3:-800}
WEIGHTS=${4:-"run:2,ramp_up:2,ramp_down:1,step_up:2,step_down:1,rough_cross:2,tunnel_cross:2,slope_spin:2,jump_in_place:1,fly_jump:2"}

# Plant + controller knobs: the DR stage must run on exactly the same machine as the
# nominal chain (rolling idlers + leg loop stiffness), otherwise its numbers describe a
# different robot.  See incoming/mod4_rolling_20260913/README.md.
if [ -f migration/linux/tunnel_tuning.env ]; then
  set -a; . migration/linux/tunnel_tuning.env; set +a
  echo "[dr-launch] sourced migration/linux/tunnel_tuning.env"
fi
USD=${RM_MOD4_USD:-incoming/mod4_fixed_20260912/chassis_mod4/isaac/robot.usd}
[ -f "$USD" ] || { echo "fixed plant missing: $USD" >&2; exit 3; }
[ -f "$CKPT" ] || { echo "init checkpoint missing: $CKPT" >&2; exit 4; }

if [ "${FORCE:-0}" != "1" ] && pgrep -f "train_mod4_ppo.py" >/dev/null; then
  echo "WARNING: a MOD4 training is already running:" >&2
  pgrep -af "train_mod4_ppo.py" >&2
  echo "one training at a time (goal section 5). set FORCE=1 only if you really mean it." >&2
  exit 5
fi

# battery / terrain-friction knobs: only exist after patch_dr_battery_terrain.py has been
# applied.  Refuse to start a DR run on unpatched code, otherwise the manifest would claim
# two randomisations that the task never performs.
if ! grep -q "resample_battery_scale" isaac/mod4/mod4_task.py; then
  echo "REFUSING: isaac/mod4/mod4_task.py has no battery/terrain-friction patch" >&2
  echo "           apply migration/linux/patch_dr_battery_terrain.py first" >&2
  exit 6
fi

STAMP=$(date +%Y%m%d_%H%M%S)
LOG=logs/isaac_mod4/stage_dr_fixedplant_${STAMP}.log
mkdir -p logs/isaac_mod4

echo "[dr-launch] envs=$NUM_ENVS iters=$ITERS ckpt=$CKPT" | tee "$LOG"
echo "[dr-launch] plant=$USD sha256=$(sha256sum "$USD" | cut -d' ' -f1)" | tee -a "$LOG"
echo "[dr-launch] weights=$WEIGHTS" | tee -a "$LOG"
echo "[dr-launch] mod4_task.py sha256=$(sha256sum isaac/mod4/mod4_task.py | cut -d' ' -f1)" | tee -a "$LOG"
echo "[dr-launch] DR knobs: RM_DR_OFF=${RM_DR_OFF:-0} RM_BATT_LEG=${RM_BATT_LEG_MIN:-0.85}-${RM_BATT_LEG_MAX:-1.00}" \
     "RM_BATT_WHEEL=${RM_BATT_WHEEL_MIN:-0.90}-${RM_BATT_WHEEL_MAX:-1.00}" \
     "RM_TERRAIN_FRICTION=${RM_TERRAIN_FRICTION_MIN:-0.65}-${RM_TERRAIN_FRICTION_MAX:-1.15}" | tee -a "$LOG"

OMNI_KIT_ACCEPT_EULA=YES \
RM_MOD4_MAP=rmuc2026 RM_MOD4_TERRAIN=field \
RM_DR_OFF=${RM_DR_OFF:-0} RM_INIT_STD=0.15 \
RM_ROUTE_KINDS="" RM_ROUTE_WEIGHTS="$WEIGHTS" \
RM_TUNNEL_GOAL_X=0 RM_ROUGH_SPEED_MAX=0 \
NUM_ENVS=$NUM_ENVS \
nohup /home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python \
  isaac/mod4/train_mod4_ppo.py --headless --num_envs "$NUM_ENVS" \
  --additional_iterations "$ITERS" --run_name "mod4_fixed_dr" \
  --init_checkpoint "$CKPT" >>"$LOG" 2>&1 &
echo "[dr-launch] pid=$! log=$LOG"
