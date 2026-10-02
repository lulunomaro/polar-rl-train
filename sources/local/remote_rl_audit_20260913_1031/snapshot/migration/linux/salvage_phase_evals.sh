#!/usr/bin/env bash
# Rebuild the phase evaluation reports that the v2 chain lost, from the phase checkpoints.
#
# Why (audit section 49): every phase evaluation failed with
#   RuntimeError: Error(s) in loading state_dict for MLPModel ... checkpoint [256, 38] vs [256, 175]
# because eval_terrain_mod4.py built a plain MLPModel for an encoder checkpoint.  The `|| true` on
# the eval invocation hid it, so no eval.json / eval_focus_*.json was ever written and the chain's
# verdict died on FileNotFoundError.  The TRAINING is fine and every phase checkpoint is on disk.
#
# Prerequisite: apply migration/linux/patch_eval_actor_class.py first (it makes the evaluator pick
# the actor class from the run manifest, like the trainer does).
#
#   DRY=1 bash migration/linux/salvage_phase_evals.sh          # list what it would do
#   bash migration/linux/salvage_phase_evals.sh                # rebuild everything
#
# Output: docs/acceptance_phase_v3_<TAG>_<phase>/{eval.json,eval_focus_<kind>.json}
set -uo pipefail
cd "$(dirname "$0")/../.."

TAG=${TAG:-v2}
DRY=${DRY:-0}
CHAIN_LOG=${CHAIN_LOG:-logs/isaac_mod4/v2_chain_launch.log}
PY=/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python
STEPS=${RM_EVAL_STEPS:-4500}          # audit 46: match the widened episode
EPISODE=${RM_EPISODE_S:-45}
SEED=${SEED:-20260912}
KIND_OF_TERRAIN="ramp_up ramp_down step_up step_down rough_cross"

kind_of() {   # the focus kind for a phase
  case "$1" in
    tunnel) echo "tunnel_cross" ;;
    terrain) echo "rough_cross" ;;
    spin)   echo "slope_spin" ;;
    fly)    echo "fly_jump" ;;
    jump)   echo "jump_in_place" ;;
  esac
}

# phase -> the checkpoint the chain recorded for it ("<phase> done -> <path>")
ckpt_of() {
  awk -v want="$1" '
    $0 ~ ("^\\[v3\\] " want " done -> ") { sub(/.*done -> /, ""); last=$0 }
    END { if (last != "") print last }' "$CHAIN_LOG" 2>/dev/null
}

live=$(ps -eo pid,args | grep -E "[t]rain_mod4_ppo|[e]val_terrain_mod4|[r]un_special_phases_v3" | grep -v salvage | wc -l)
if [ "$live" != "0" ]; then
  echo "[salvage] REFUSING: $live chain/eval process(es) live -- run this after the chain ends"
  exit 3
fi

if ! grep -q "_ACTOR_CLASS" isaac/mod4/eval_terrain_mod4.py; then
  echo "[salvage] the evaluator is NOT encoder-aware yet."
  echo "[salvage] run: python3 migration/linux/patch_eval_actor_class.py"
  exit 4
fi

rc_all=0
for ph in tunnel terrain spin fly jump; do
  ck=$(ckpt_of "$ph")
  [ -n "$ck" ] || { echo "[salvage] $ph: no checkpoint recorded (phase never ran) -- skip"; continue; }
  [ -f "$ck" ] || { echo "[salvage] $ph: checkpoint missing: $ck"; rc_all=1; continue; }
  out="docs/acceptance_phase_v3_${TAG}_${ph}"
  kd=$(kind_of "$ph")
  echo "[salvage] $ph  ckpt=$ck  out=$out  steps=$STEPS episode=${EPISODE}s"
  if [ "$DRY" = "1" ]; then continue; fi
  mkdir -p "$out"
  bash migration/linux/check_run_version.sh "$ck" > "$out/version_check.txt" 2>&1 || true
  # normal eval: nominal (DR off), the same way the chain does it
  OMNI_KIT_ACCEPT_EULA=YES RM_MOD4_MAP=rmuc2026 RM_MOD4_TERRAIN=field RM_DR_OFF=1 \
  RM_EPISODE_S="$EPISODE" RM_TUNNEL_GOAL_X=0 RM_ROUGH_SPEED_MAX=0 \
    "$PY" isaac/mod4/eval_terrain_mod4.py --checkpoint "$ck" --mode arena \
      --steps "$STEPS" --seed "$SEED" --report "$out/eval.json" > "$out/eval.log" 2>&1 || true
  # focus eval: all envs on the phase's subject
  OMNI_KIT_ACCEPT_EULA=YES RM_MOD4_MAP=rmuc2026 RM_MOD4_TERRAIN=field RM_DR_OFF=1 \
  RM_EPISODE_S="$EPISODE" RM_TUNNEL_GOAL_X=0 RM_ROUGH_SPEED_MAX=0 \
  RM_ROUTE_KINDS="$kd" \
    "$PY" isaac/mod4/eval_terrain_mod4.py --checkpoint "$ck" --mode arena \
      --steps "$STEPS" --seed "$SEED" --report "$out/eval_focus_${kd}.json" \
      > "$out/eval_focus.log" 2>&1 || true
  for f in "eval.json" "eval_focus_${kd}.json"; do
    if [ -f "$out/$f" ]; then echo "[salvage]   ✅ $f"
    else echo "[salvage]   ❌ $f MISSING -- see $out/eval*.log"; tail -3 "$out/eval_focus.log" 2>/dev/null | sed 's/^/      /'; rc_all=1; fi
  done
done

if [ "$DRY" = "1" ]; then echo "[salvage] DRY=1 -- nothing changed"; exit 0; fi
echo
echo "[salvage] now judging with the authoritative bars:"
TAG="$TAG" bash migration/linux/my_phase_gate.sh || rc_all=$?
exit $rc_all
