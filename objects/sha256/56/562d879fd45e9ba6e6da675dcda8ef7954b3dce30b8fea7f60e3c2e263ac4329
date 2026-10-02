#!/usr/bin/env bash
# Resume the v2 special-heavy curriculum (run_special_phases_v2.sh) after its supervisor died.
#
# WHY THIS EXISTS (2026-09-12 17:30 .. 18:05)
#   The v2 chain supervisor (PID 788994) was killed while it sat in wait_for_training() for
#   phase 2 (tunnel_full).  Its phase-2 training (PID 808616) kept running as an orphan
#   (PPid = 1), which means the phase-2 evaluation and phases 3..6 -- rough / spin / fly /
#   jump -- would never have started.  That training is healthy, so it is NOT restarted: this
#   script waits for the phase that is already running to end, evaluates it exactly the way
#   v2's phase() did, and then continues the v2 phase list with identical weights, iteration
#   counts and tunnel goal_x.
#
# WHAT IT ADDS over v2
#   1. flock single instance (/tmp/mod4_special_chain.lock): two chains can never interleave.
#   2. wait_for_training() first -- a chain restarted while a 512-env training is alive waits
#      for it instead of starting a second one (one training at a time is a hard rule).
#   3. Crash-safe state file docs/mod4_chain_resume_state.txt: every phase transition and every
#      evaluation is appended, so a later session knows exactly what is already done.
#   4. It never relaunches a training that died.  A Traceback in the stage log aborts the chain
#      and leaves the evidence in place for the evaluator and the next session.
#
#   ./resume_special_phases_v2.sh [first-phase] [envs]
#     first-phase = tunnel_full | rough | spin | fly | jump   (default rough)
#     "tunnel_full" means: wait for the phase-2 training that is running right now, evaluate it,
#     then continue with rough.
set -uo pipefail

exec 9>/tmp/mod4_special_chain.lock
flock -n 9 || { echo "[resume] lock /tmp/mod4_special_chain.lock is held -- refusing to start a second chain"; exit 5; }

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR/../.."
PY=/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python
ROUTES_JSON=incoming/rmuc2026_field_20260911/rmuc2026_training/data/routes.json
LOG=logs/isaac_mod4/special_phases_resume_$(date +%Y%m%d_%H%M%S).log
STATE=docs/mod4_chain_resume_state.txt
FIRST=${1:-rough}
ENVS=${2:-512}
# Stage log of the orphaned phase-2 training (only used when FIRST=tunnel_full).
ORPHAN_LOG=logs/isaac_mod4/stage_mixed_fixedplant_20260912_173044.log
BASE="run:2,ramp_up:2,ramp_down:1,step_up:2,step_down:1,rough_cross:2,tunnel_cross:2,slope_spin:2,jump_in_place:1,fly_jump:2"
TRAIN_LOG=""
CKPT=""

log()   { echo "[resume] $*" | tee -a "$LOG"; }
state() { echo "$(date +%F_%H:%M:%S) $*" | tee -a "$STATE" >> "$LOG"; }

weights_for() {   # weights_for <special_kind> <special_weight>
  local special=$1 sw=$2 out="" kv
  local IFS=','
  for kv in $BASE; do
    [ "${kv%%:*}" = "$special" ] && continue
    out="${out:+$out,}$kv"
  done
  echo "${out:+$out,}$special:$sw"
}

alloc_check() {   # alloc_check <weights-spec>: print the allocation route_isaac will really build
  python3 - "$ROUTES_JSON" "$1" <<'PY'
import json, sys
routes = json.load(open(sys.argv[1]))
routes = routes if isinstance(routes, list) else routes.get("routes", routes)
kinds = [r["kind"] for r in routes]
weights = {}
for item in sys.argv[2].split(","):
    if ":" in item:
        k, w = item.split(":")
        weights[k.strip()] = max(0, int(float(w)))
slots = [kinds[i] for i, k in enumerate(kinds) for _ in range(weights.get(k, 0))]
tot = len(slots) or 1
per = {}
for k in slots:
    per[k] = per.get(k, 0) + 1
print("[resume]   slots=%d  " % len(slots)
      + "  ".join("%s %.1f%%" % (k, 100.0 * v / tot)
                  for k, v in sorted(per.items(), key=lambda kv: -kv[1])))
PY
}

latest_checkpoint() {
  local run_dir last
  run_dir=$(ls -dt logs/isaac_mod4/*_mod4_fixed_mixed/ 2>/dev/null | head -1)
  last=$(ls -t "$run_dir" 2>/dev/null | grep '^model_' | head -1)
  CKPT="${run_dir}${last}"
}

wait_for_training() {   # blocks until no train_mod4_ppo.py ran for 3 consecutive checks
  local label=$1 stable=0
  while true; do
    if pgrep -f "train_mod4_ppo.py --headless" >/dev/null; then
      stable=0
    else
      stable=$((stable + 1)); [ "$stable" -ge 3 ] && break
    fi
    if tail -80 "$TRAIN_LOG" 2>/dev/null | grep -q "Traceback"; then
      log "$label: Traceback in $TRAIN_LOG -- NOT relaunching, aborting chain"
      state "$label ABORT traceback"; exit 1
    fi
    sleep 30
  done
  latest_checkpoint
  log "$label training finished -> $CKPT"
  state "$label training-finished ckpt=$CKPT"
}

read_eval() {   # read_eval <eval.json>
  python3 "$SCRIPT_DIR/read_phase_eval.py" "$1" 2>/dev/null | tee -a "$LOG"
  [ -s "$1" ] || log "eval report missing or empty: $1"
}

eval_phase() {   # eval_phase <label> <checkpoint> [goal_x]
  local label=$1 ckpt=$2 goalx=${3:-2.30}
  local OUT=docs/acceptance_phase_${label}
  mkdir -p "$OUT"
  log "eval $label checkpoint=$ckpt tunnel_goal_x=$goalx"
  OMNI_KIT_ACCEPT_EULA=YES RM_MOD4_MAP=rmuc2026 RM_MOD4_TERRAIN=field RM_DR_OFF=1 \
    RM_TUNNEL_GOAL_X="$goalx" \
    $PY isaac/mod4/eval_terrain_mod4.py --headless --checkpoint "$ckpt" --num_envs 64 \
    --steps 2200 --seed 20260912 --report "$OUT/eval.json" >>"$LOG" 2>&1 || true
  read_eval "$OUT/eval.json"
  state "$label evaluated report=$OUT/eval.json"
}

phase() {   # phase <label> <weights> <iters> <goalx>
  local label=$1 weights=$2 iters=$3 goalx=$4
  log "=== phase $label iters=$iters tunnel_goal_x=$goalx"
  log "    weights=$weights"
  alloc_check "$weights"
  export RM_ROUTE_WEIGHTS="$weights"
  export RM_TUNNEL_GOAL_X="$goalx"
  TRAIN_LOG=logs/isaac_mod4/phasev2_${label}_$(date +%H%M%S).log
  FORCE=1 bash migration/linux/start_mod4_stage_fixedplant.sh mixed "$CKPT" "$ENVS" "$iters" \
    >"$TRAIN_LOG" 2>&1 || true
  grep -h '^\[launch\]' "$TRAIN_LOG" | tail -2 | tee -a "$LOG"
  state "$label launched log=$TRAIN_LOG"
  sleep 20
  pgrep -f "train_mod4_ppo.py --headless" >/dev/null || {
    log "$label: training did not start -- aborting (never auto-relaunch)"; state "$label ABORT no-start"; exit 1; }
  wait_for_training "$label"
  eval_phase "$label" "$CKPT" "$goalx"
}

case "$FIRST" in tunnel_full|rough|spin|fly|jump) ;; *) echo "[resume] unknown first-phase '$FIRST'"; exit 4;; esac

log "resume start first=$FIRST envs=$ENVS"
state "resume-start first=$FIRST envs=$ENVS"

if [ "$FIRST" = "tunnel_full" ]; then
  [ -f "$ORPHAN_LOG" ] || { log "orphan stage log missing: $ORPHAN_LOG"; exit 4; }
  TRAIN_LOG="$ORPHAN_LOG"
  wait_for_training tunnel_full
  eval_phase tunnel_full "$CKPT" 2.30
  FIRST=rough
fi

if [ "$FIRST" = "rough" ]; then phase rough "$(weights_for rough_cross 6)"   600 2.30; FIRST=spin; fi
if [ "$FIRST" = "spin"  ]; then phase spin  "$(weights_for slope_spin 7)"    600 2.30; FIRST=fly;  fi
if [ "$FIRST" = "fly"   ]; then phase fly   "$(weights_for fly_jump 6)"      600 2.30; FIRST=jump; fi
if [ "$FIRST" = "jump"  ]; then phase jump  "$(weights_for jump_in_place 5)" 600 2.30; fi

latest_checkpoint
log "resume chain finished; final checkpoint = $CKPT"
state "chain-finished ckpt=$CKPT"
echo "$CKPT" > docs/mod4_chain_resume_final_ckpt.txt
