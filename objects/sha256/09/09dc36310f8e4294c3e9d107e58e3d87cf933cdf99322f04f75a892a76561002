#!/usr/bin/env bash
# Special-heavy curriculum with rehearsal -- v2 (2026-09-12 15:25).
#
# WHY v2 exists
#   v1 built the phase weights as "tunnel_cross:6,$REHEARSAL" while REHEARSAL *also* carried
#   tunnel_cross:2.  route_isaac._ids_for() parses RM_ROUTE_WEIGHTS into a dict with LAST-WINS
#   semantics, so the special weight was silently overwritten: the "tunnel phase" sampled
#   tunnel_cross at 4/27 = 14.8% of envs -- LESS than the balanced mixed run it replaced
#   (6/36 = 16.7%) and far from the intended 12/35 = 34.3%.  Every v1 phase had the same defect
#   (rough 6->2, spin 7->2, fly 6->2, jump 5->1), i.e. the chain was a disguised balanced
#   rehearsal run, not the special curriculum goal 2026-09-12 §4 asks for.  The parser model is
#   validated by the measured balanced-run allocation in
#   docs/MOD4_FIXED_PLANT_INTEGRATION_20260912.md §39.3 (ramp_up 17.0 / rough 16.4 / step_up 16.4 /
#   tunnel 16.4 / downhill 2.7-2.9%).
#
# What v2 changes
#   1. weights_for() drops the special kind from the rehearsal base and appends it LAST, so the
#      special really dominates (tunnel/rough/fly 34.3%, spin 29.2%, jump 22.7%).
#   2. alloc_check() prints the effective per-kind allocation before every launch (self-check).
#   3. Everything else is unchanged from v1: one training at a time, full-route eval after each
#      phase, Traceback abort, version gate inside the evaluator.
#
#   ./run_special_phases_v2.sh <checkpoint> [envs]
#
# Phases: tunnel (short goal -> full goal) -> rough -> spin -> fly -> jump.
set -uo pipefail
cd "$(dirname "$0")/../.."
LOG=logs/isaac_mod4/special_phases_v2_$(date +%Y%m%d_%H%M%S).log
PY=/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python
ROUTES_JSON=incoming/rmuc2026_field_20260911/rmuc2026_training/data/routes.json
CKPT=${1:?usage: run_special_phases_v2.sh <checkpoint> [envs]}
ENVS=${2:-512}

# Rehearsal base: every route that already works keeps a slot, the hard ones a double slot.
BASE="run:2,ramp_up:2,ramp_down:1,step_up:2,step_down:1,rough_cross:2,tunnel_cross:2,slope_spin:2,jump_in_place:1,fly_jump:2"

log() { echo "[phases-v2] $*" | tee -a "$LOG"; }

weights_for() {   # weights_for <special_kind> <special_weight>
  local special=$1 sw=$2 out="" kv
  local IFS=','
  for kv in $BASE; do
    [ "${kv%%:*}" = "$special" ] && continue
    out="${out:+$out,}$kv"
  done
  echo "${out:+$out,}$special:$sw"
}

alloc_check() {   # alloc_check <weights-spec>: print the allocation the parser will really build
  python3 - "$ROUTES_JSON" "$1" <<'PY'
import json, sys
routes = json.load(open(sys.argv[1]))
routes = routes if isinstance(routes, list) else routes.get("routes", routes)
kinds = [r["kind"] for r in routes]
weights = {}
for item in sys.argv[2].split(","):
    if ":" in item:
        k, w = item.split(":")
        weights[k.strip()] = max(0, int(float(w)))      # same last-wins rule as route_isaac
slots = [kinds[i] for i, k in enumerate(kinds) for _ in range(weights.get(k, 0))]
tot = len(slots) or 1
per = {}
for k in slots:
    per[k] = per.get(k, 0) + 1
print("[phases-v2]   slots=%d  " % len(slots)
      + "  ".join("%s %.1f%%" % (k, 100.0 * v / tot)
                  for k, v in sorted(per.items(), key=lambda kv: -kv[1])))
PY
}

latest_checkpoint() {
  local run_dir last
  run_dir=$(ls -dt logs/isaac_mod4/*_mod4_fixed_mixed/ 2>/dev/null | head -1)
  last=$(ls -t "$run_dir" 2>/dev/null | grep "^model_" | head -1)
  CKPT="${run_dir}${last}"
}

wait_for_training() {
  local label=$1 stable=0
  while true; do
    if pgrep -f "train_mod4_ppo.py --headless" >/dev/null; then stable=0; else
      stable=$((stable + 1)); [ "$stable" -ge 3 ] && break
    fi
    if tail -60 "$TRAIN_LOG" 2>/dev/null | grep -q "Traceback"; then
      log "$label: Traceback detected -- aborting chain"; exit 1
    fi
    sleep 30
  done
  latest_checkpoint
  log "$label done -> $CKPT"
}

phase() {
  local label=$1 weights=$2 iters=$3 goalx=$4
  log "=== phase $label iters=$iters tunnel_goal_x=$goalx"
  log "    weights=$weights"
  alloc_check "$weights"
  export RM_ROUTE_WEIGHTS="$weights"
  export RM_TUNNEL_GOAL_X="$goalx"
  TRAIN_LOG=logs/isaac_mod4/phasev2_${label}_$(date +%H%M%S).log
  FORCE=1 bash migration/linux/start_mod4_stage_fixedplant.sh mixed "$CKPT" "$ENVS" "$iters" \
    >"$TRAIN_LOG" 2>&1 || true
  grep -h "^\[launch\]" "$TRAIN_LOG" | tail -2 | tee -a "$LOG"
  sleep 20
  pgrep -f "train_mod4_ppo.py --headless" >/dev/null || {
    log "$label: training did not start -- aborting"; exit 1; }
  wait_for_training "$label"
  local OUT=docs/acceptance_phase_${label}
  mkdir -p "$OUT"
  OMNI_KIT_ACCEPT_EULA=YES RM_MOD4_MAP=rmuc2026 RM_MOD4_TERRAIN=field RM_DR_OFF=1 \
    $PY isaac/mod4/eval_terrain_mod4.py --headless --checkpoint "$CKPT" --num_envs 64 \
    --steps 2200 --seed 20260912 --report "$OUT/eval.json" >>"$LOG" 2>&1 || true
  $PY - "$OUT/eval.json" <<'PY' | tee -a "$LOG"
import json, sys
try:
    d = json.load(open(sys.argv[1]))
except Exception as exc:
    print("[phases] eval missing:", exc); raise SystemExit(0)
for k, v in sorted(d["route_kinds"].items()):
    print("[phases]   %-14s complete %.3f  progress %7.1f  spin %6.1f"
          % (k, v["complete_rate"], v["progress_sum"], v.get("spin_deg", 0.0)))
PY
}

log "chain start checkpoint=$CKPT envs=$ENVS"
[ -f "$CKPT" ] || { log "start checkpoint missing: $CKPT"; exit 4; }

phase tunnel_short "$(weights_for tunnel_cross 6)"  800 1.60
phase tunnel_full  "$(weights_for tunnel_cross 6)"  800 2.30
phase rough        "$(weights_for rough_cross 6)"   600 2.30
phase spin         "$(weights_for slope_spin 7)"    600 2.30
phase fly          "$(weights_for fly_jump 6)"      600 2.30
phase jump         "$(weights_for jump_in_place 5)" 600 2.30
log "all phases finished; final checkpoint = $CKPT"
