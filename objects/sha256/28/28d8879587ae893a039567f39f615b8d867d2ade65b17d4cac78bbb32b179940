#!/usr/bin/env bash
# MOD4 Isaac stage launcher on the FIXED plant (2026-09-12 model fix: real CAD hard stop +
# eight guide rollers).  Warm-starts from an existing checkpoint -- a model swap does NOT
# invalidate the weights as an initialisation (verified 2026-09-12: v14gy model_7402 loaded on
# the fixed USD, continued to 7404, mimic 1.4e-3 rad, closure 1e-4 m).
#
#   ./start_mod4_stage_fixedplant.sh <stage> <init_checkpoint> [num_envs] [extra_iterations]
#   stage: run | terrain | tunnel | fly | spin
#   FORCE=1  allow starting while another RM_MOD4_MAP=rmuc2026 run is alive
#
# Logs: logs/isaac_mod4/stage_<stage>_fixedplant_<timestamp>.log
set -uo pipefail
# belt and braces: make the EULA acceptance part of THIS script's environment so a
# caller that sets nothing still gets a headless launch (see the note further down).
export OMNI_KIT_ACCEPT_EULA=YES
cd "$(dirname "$0")/../.."

STAGE=${1:?usage: start_mod4_stage_fixedplant.sh <stage> <init_checkpoint> [num_envs] [iters]}
CKPT=${2:?init checkpoint required}
NUM_ENVS=${3:-512}
ITERS=${4:-1000}

case "$STAGE" in
  run)     KINDS="run";                                                INIT_STD=0.15 ;;
  terrain) KINDS="ramp_up,ramp_down,step_up,step_down,rough_cross";    INIT_STD=0.15 ;;
  tunnel)  KINDS="tunnel_cross";                                       INIT_STD=0.15 ;;
  fly)     KINDS="fly_jump";                                           INIT_STD=0.15 ;;
  spin)    KINDS="slope_spin";                                         INIT_STD=0.15 ;;
  # P2 step 6: the whole delivered route table (15 routes) in one stage.  An empty
  # RM_ROUTE_KINDS means "no filter", which is how route_isaac reads it.
  mixed)   KINDS="";                                                   INIT_STD=0.15 ;;
  *) echo "unknown stage: $STAGE" >&2; exit 2 ;;
esac

# 2026-09-12: follow RM_MOD4_USD (set by migration/linux/tunnel_tuning.env and exported by the
# v3 chain) instead of hardcoding the delivered package.  The trainer reads RM_MOD4_USD itself
# (isaac/mod4/mod4_task.py), so the hardcode only made the `plant=` line LIE in every stage log
# -- exactly the "silent A/B no-op" failure mode the handoff forbids.
USD=${RM_MOD4_USD:-incoming/mod4_fixed_20260912/chassis_mod4/isaac/robot.usd}
[ -f "$USD" ] || { echo "fixed plant missing: $USD" >&2; exit 3; }
[ -f "$CKPT" ] || { echo "init checkpoint missing: $CKPT" >&2; exit 4; }

if [ "${FORCE:-0}" != "1" ]; then
  alive=$(pgrep -af "train_mod4_ppo.py" | grep -c "rmuc2026\|RM_MOD4_MAP" || true)
  if pgrep -af "train_mod4_ppo.py" >/dev/null; then
    echo "WARNING: a MOD4 training is already running:" >&2
    pgrep -af "train_mod4_ppo.py" >&2
    echo "set FORCE=1 to start anyway (GPU will be shared)." >&2
    exit 5
  fi
fi

STAMP=$(date +%Y%m%d_%H%M%S)
LOG=logs/isaac_mod4/stage_${STAGE}_fixedplant_${STAMP}.log
mkdir -p logs/isaac_mod4

echo "[launch] stage=$STAGE kinds=$KINDS envs=$NUM_ENVS iters=$ITERS ckpt=$CKPT" | tee "$LOG"
echo "[launch] plant=$USD sha256=$(sha256sum "$USD" | cut -d' ' -f1)" | tee -a "$LOG"

# OMNI_KIT_ACCEPT_EULA: without it Isaac Sim stops at the interactive EULA prompt and dies with
# "Unable to bootstrap inner kit kernel: EOF when reading a line" (measured 2026-09-12).
# v2 (2026-09-12): DR is ON by default for a training phase.  Pass RM_DR_OFF=1 to get
# the old nominal-only behaviour; the nominal EVALUATIONS in run_special_phases_v3.sh
# keep their explicit RM_DR_OFF=1 (train with DR, evaluate the nominal policy).
# NOTE (2026-09-13): this comment used to sit BETWEEN the backslash continuations below,
# which silently DROPPED OMNI_KIT_ACCEPT_EULA=YES (a comment ends the logical line, so the
# assignment applied to no command).  Isaac then died at the interactive EULA prompt with
# "Unable to bootstrap inner kit kernel: EOF when reading a line".  Keep it above the block.
OMNI_KIT_ACCEPT_EULA=YES \
RM_MOD4_MAP=rmuc2026 RM_MOD4_TERRAIN=field RM_DR_OFF=${RM_DR_OFF:-0} RM_INIT_STD=$INIT_STD \
RM_ROUTE_KINDS=$KINDS NUM_ENVS=$NUM_ENVS \
nohup /home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python \
  isaac/mod4/train_mod4_ppo.py --headless --num_envs "$NUM_ENVS" \
  --additional_iterations "$ITERS" --run_name "mod4_fixed_${STAGE}" \
  --init_checkpoint "$CKPT" >>"$LOG" 2>&1 &
echo "[launch] pid=$! log=$LOG"
