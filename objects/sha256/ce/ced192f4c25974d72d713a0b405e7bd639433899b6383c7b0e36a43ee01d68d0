#!/usr/bin/env bash
# Special-heavy curriculum chain v3 (2026-09-12) -- supersedes run_special_phases_v2.sh.
#
# WHY v3
#   v2 ran tunnel_short -> tunnel_full -> rough -> spin -> fly -> jump and was stopped by hand
#   after tunnel_full, because the dog-hole phase cannot pass with the v2 schedule: the
#   delivered 247.2 mm hole only fits root z in [0.178, 0.180] m and in that pose the drive
#   wheels are ~1.8 mm off the ground while the eight chassis guide rollers carry the load, so
#   the robot can only COAST under the roof.  v2's step command forced the full crouch 0.06 m
#   after spawn (0.40 m lead against a 0.46 m spawn->mouth runway) and every tunnel episode
#   ended in place (Metrics/tunnel_underpass_rate 0.0000 for 800 iterations, eval 18/18
#   time_out, mean advance 0.35 m).
#
#   v3 (a) makes the approach/fold/speed schedule a knob file (migration/linux/tunnel_tuning.env,
#   applied by migration/linux/patch_tunnel_knobs.py), (b) trains with the DELIVERED 2.30 m
#   tunnel goal instead of a shortened curriculum goal, (c) freezes source/asset hashes at chain
#   start and re-checks them after every phase (mismatch => exit 4), (d) runs the checkpoint
#   version gate + the per-route reader before every phase verdict, (e) starts with a 64-env /
#   6000-step smoke test, (f) adds one focused single-kind evaluation per special phase so the
#   phase verdict does not rest on the 2-3 environments a balanced 64-env mix gives that kind.
#
#   ./run_special_phases_v3.sh <checkpoint> [from_phase] [iters]
#     from_phase: smoke | tunnel | rough | spin | fly | jump   (default smoke)
#   DRY_RUN=1  print the plan (no GPU use)      SMOKE=0  skip the smoke phase
#   ENVS=512   iterations per special phase    ITERS=<n> overrides
set -uo pipefail
cd "$(dirname "$0")/../.."

LOG=logs/isaac_mod4/special_phases_v3_$(date +%Y%m%d_%H%M%S).log
PY=/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python
ROUTES_JSON=incoming/rmuc2026_field_20260911/rmuc2026_training/data/routes.json
TUNING=migration/linux/tunnel_tuning.env
FROZEN=logs/isaac_mod4/chain_v3_$(date +%Y%m%d_%H%M%S)_frozen.txt
ROOT_CKPT=${1:?usage: run_special_phases_v3.sh <checkpoint> [from_phase] [iters]}
CKPT="$ROOT_CKPT"
FROM=${2:-smoke}
ENVS=${ENVS:-512}
ITERS=${3:-${ITERS:-700}}
DRY_RUN=${DRY_RUN:-0}
SMOKE=${SMOKE:-1}
# 2026-09-12: overridable so a session can run the non-tunnel specials while the dog-hole
# physics is still being settled, e.g. PHASES="smoke terrain spin fly jump" (the tunnel phase is
# then launched separately with from_phase=tunnel once the plant question is answered).
PHASES=${PHASES:-"smoke tunnel terrain spin fly jump"}

# Rehearsal base: every route keeps a slot, the known-hard ones a double slot.  weights_for()
# removes the special kind from the base and appends it LAST, because route_isaac._ids_for()
# parses RM_ROUTE_WEIGHTS with LAST-WINS semantics -- v1 silently overwrote every special
# weight this way (tunnel 6 -> 2) and ran a disguised balanced rehearsal.
BASE="run:2,ramp_up:2,ramp_down:1,step_up:2,step_down:1,rough_cross:2,tunnel_cross:2,slope_spin:2,jump_in_place:1,fly_jump:2"

log() { echo "[v3] $*" | tee -a "$LOG"; }

weights_for() {
  local special=$1 sw=$2 out="" kv
  local IFS=','
  for kv in $BASE; do
    [ "${kv%%:*}" = "$special" ] && continue
    out="${out:+$out,}$kv"
  done
  echo "${out:+$out,}$special:$sw"
}

# Multi-kind version (goal 3: the uphill routes and rough_cross must be trained and diagnosed
# separately, and the two downhill routes that already pass must not dominate the sampling).
weights_multi() {   # weights_multi "ramp_up:4 step_up:4 rough_cross:4"
  local spec="$1" out="" kv k
  local -A ADD=()
  local -a PAIRS=()
  # NOTE: split the space-separated spec BEFORE local IFS=',' -- with IFS=',' the words would
  # not split and the whole spec would land in RM_ROUTE_WEIGHTS as a single malformed item.
  for kv in $spec; do PAIRS+=("$kv"); ADD["${kv%%:*}"]="${kv##*:}"; done
  local IFS=','
  for kv in $BASE; do
    k="${kv%%:*}"
    [ -n "${ADD[$k]:-}" ] && continue
    out="${out:+$out,}$kv"
  done
  for kv in "${PAIRS[@]}"; do out="${out:+$out,}$kv"; done
  echo "$out"
}

alloc_check() {
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
slots = [k for k in kinds for _ in range(weights.get(k, 0))]
tot = len(slots) or 1
per = {}
for k in slots:
    per[k] = per.get(k, 0) + 1
print("[v3]   slots=%d  " % len(slots)
      + "  ".join("%s %.1f%%" % (k, 100.0 * v / tot)
                  for k, v in sorted(per.items(), key=lambda kv: -kv[1])))
PY
}

# --- schedule knobs -----------------------------------------------------------------------
declare -A KNOB=()
if [ -f "$TUNING" ]; then
  while IFS= read -r line; do
    line="${line%%#*}"
    case "$line" in
      *"="*) KNOB["$(echo "${line%%=*}" | tr -d '[:space:]')"]="$(echo "${line#*=}" | tr -d '[:space:]')" ;;
    esac
  done < "$TUNING"
fi
apply_knobs() { local kv; for kv in "${!KNOB[@]}"; do export "$kv=${KNOB[$kv]}"; done; }

# --- version freeze -----------------------------------------------------------------------
# 2026-09-12: freeze the plant that RM_MOD4_USD points at (tunnel_tuning.env), not the
# hard-coded delivered package -- the delivered paths left the ACTUAL plant unfrozen and
# made the frozen record name a file that was never loaded.
_PLANT=${KNOB[RM_MOD4_USD]:-incoming/mod4_fixed_20260912/chassis_mod4/isaac/robot.usd}
_PLANT_DIR=$(dirname "$_PLANT")
FROZEN_FILES="isaac/mod4/mod4_task.py isaac/mod4/skills_isaac.py isaac/mod4/route_isaac.py
isaac/mod4/mod4_curriculum.py isaac/mod4/mod4_sequence_model.py
incoming/rmuc2026_field_20260911/rmuc2026_training/isaac/route_commands.py incoming/rmuc2026_field_20260911/rmuc2026_training/data/routes.json incoming/rmuc2026_field_20260911/rmuc2026_training/assets/arena_collision.usdc
isaac/mod4/train_mod4_ppo.py isaac/mod4/mod4_env.py
$_PLANT_DIR/robot_cfg.py
$_PLANT
$_PLANT_DIR/import_contract.json"

freeze_hashes() {
  : > "$1"
  local f
  for f in $FROZEN_FILES; do
    if [ -f "$f" ]; then sha256sum "$f" >> "$1"; else echo "# MISSING $f" >> "$1"; fi
  done
  echo "[v3] frozen $(grep -c '^[0-9a-f]' "$1") files -> $1" | tee -a "$LOG"
}

check_hashes() {
  local rc=0
  while read -r want path; do
    case "$want" in \#*) continue ;; esac
    got=$(sha256sum "$path" 2>/dev/null | cut -d' ' -f1)
    if [ "$got" != "$want" ]; then
      log "HASH CHANGED: $path ${want:0:12} -> ${got:0:12}"
      rc=4
    fi
  done < "$1"
  return $rc
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
    if pgrep -f "[t]rain_mod4_ppo.py" >/dev/null; then stable=0; else
      stable=$((stable + 1)); [ "$stable" -ge 3 ] && break
    fi
    if tail -80 "$TRAIN_LOG" 2>/dev/null | grep -q "Traceback"; then
      log "$label: Traceback detected -- aborting chain"; exit 1
    fi
    sleep 30
  done
  latest_checkpoint
  log "$label done -> $CKPT"
}

smoke_verdict() {
  # NOTE (2026-09-13): $1 is the LAUNCHER log (start_mod4_stage_fixedplant.sh stdout); the
  # metrics live in the stage log it prints as "log=<path>".  The first version grepped the
  # launcher log, found no metrics, and declared a spurious FAIL that stopped the chain after
  # the smoke.  Now: metrics are read from the real stage log, and a missing metric is a
  # WARNING, not a failure - only an explicit NaN/OOM/Traceback fails the smoke.
  local launcher=$1 stage
  # v2 fix (2026-09-13): the launcher prints "[launch] pid=<n> log=<path>", so a pattern anchored
  # on "^\[launch\] log=" never matched; the stage log was never found, the metrics were never
  # read, and this gate silently passed everything (see the patch docstring / audit section 43).
  stage=$(grep -h "^\[launch\] .*log=" "$launcher" 2>/dev/null | tail -1 | sed 's/.*log=//')
  [ -n "$stage" ] && [ -f "$stage" ] || stage="$launcher"
  local bad
  bad=$(grep -cE "Traceback|RuntimeError|CUDA out of memory|Error:|: +nan|: +-nan" "$stage" 2>/dev/null || true)
  bad=$(echo "$bad" | head -1)
  local clo mim
  clo=$(grep -o "closure_err_session_max_m: [0-9.eE+-]*" "$stage" | tail -1 | awk '{print $2}')
  mim=$(grep -o "mimic_err_session_max_rad: [0-9.eE+-]*" "$stage" | tail -1 | awk '{print $2}')
  log "smoke: stage_log=$stage nan/oom hits=$bad closure_session_max=${clo:-none} mimic_session_max=${mim:-none}"
  if [ "$bad" != "0" ]; then log "smoke: FAIL (see $stage)"; exit 1; fi
  if [ -z "${clo:-}" ] || [ -z "${mim:-}" ]; then
    log "smoke: WARNING metrics not found in $stage - not failing on that alone"; return 0; fi
  # DR-aware limit (audit 39): DR roughly doubles the closed-chain residual on this plant
  # (measured 0.000607 m with DR off vs 0.0012 m and stepping with DR on), so the DR-off
  # threshold must not be applied to a DR-on run.
  if [ "${RM_DR_OFF:-0}" = "1" ]; then _CLO_LIM=${RM_SMOKE_CLOSURE_MAX:-0.002};
  else _CLO_LIM=${RM_SMOKE_CLOSURE_MAX:-0.004}; fi
  if awk -v v="$clo" -v L="$_CLO_LIM" 'BEGIN{exit !(v < L)}'; then :; else
    log "smoke: FAIL closure session max ${clo} >= ${_CLO_LIM} m (RM_DR_OFF=${RM_DR_OFF:-0})"; exit 1; fi
  if awk -v v="$mim" 'BEGIN{exit !(v < 0.01)}'; then :; else
    log "smoke: FAIL mimic session max >= 0.01 rad"; exit 1; fi
  log "smoke: PASS"
}

phase_report() {   # phase_report <label> <eval.json>
  $PY - "$1" "$2" <<'PY' | tee -a "$LOG"
import json, sys
label, path = sys.argv[1], sys.argv[2]
d = json.load(open(path))
rk = d.get("route_kinds") or {}
def rate(b, key):
    v = b.get(key, 0.0)
    if isinstance(v, int):
        return v / max(1, b.get("envs", 1))
    return float(v)
bars = {"ramp_up": 0.60, "ramp_down": 0.60, "step_up": 0.60, "step_down": 0.60,
        "rough_cross": 0.60, "tunnel_cross": 0.60, "slope_spin": 0.60, "fly_jump": 0.50}
print("[v3] --- phase %s verdict (complete_rate / gate) ---" % label)
for k in sorted(rk):
    b = rk[k]
    bar = bars.get(k)
    ok = "" if bar is None else (" PASS" if b["complete_rate"] >= bar else " FAIL(bar %.2f)" % bar)
    extra = ""
    if k == "tunnel_cross":
        extra = " underpass_rate=%.2f roof_hit=%s" % (
            rate(b, "underpass_seen"), b.get("fail/tunnel_roof_hit", 0))
    if k == "slope_spin":
        extra = " spin_deg=%.1f" % b.get("spin_deg", 0.0)
    if k == "fly_jump":
        extra = " air_after=%.2f" % rate(b, "air_after_launch")
    print("[v3]     %-14s envs=%-3s complete=%.3f progress=%8.1f%s%s"
          % (k, b.get("envs"), b["complete_rate"], b.get("progress_sum", 0.0), extra, ok))
print("[v3] phase %s applied_from_manifest=%s" % (label, d.get("applied_from_manifest")))
PY
}


# --- skill retention (audit 61.3) ------------------------------------------------------------
# The v2 chain trained slope_spin 0.703 -> 0.000 over 5 hours while every automated check
# passed: smoke only looked at closure/mimic, and the per-phase verdict only printed.  This
# asks the ONE question none of them asked -- "is the skill that worked before still
# working?" -- and STOPS the chain when the answer is no.
_retention_check() {   # _retention_check <phase-label> <out-dir>
  local label=$1 out=$2 base=docs/_retention_baseline.json
  [ "${RM_RETENTION_OFF:-0}" = "1" ] && return 0
  local py=/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python
  [ -x "$py" ] || py=python3
  local rc=0
  "$py" - "$label" "$out" "$base" "${RM_RETENTION_MIN:-0.50}" <<'RETENTION_PY'
import json, pathlib, sys
label, out, basep, mn = sys.argv[1], pathlib.Path(sys.argv[2]), pathlib.Path(sys.argv[3]), float(sys.argv[4])
KINDS = ("slope_spin", "step_up", "tunnel_cross", "fly_jump")

def rate_for(kind):
    cands = sorted(out.glob("eval_focus_*.json")) + [out / "eval.json"]
    for name in cands:
        if not name.is_file():
            continue
        try:
            d = json.loads(name.read_text())
        except Exception:
            continue
        rk = (d.get("route_kinds") or {}).get(kind)
        if rk and rk.get("complete_rate") is not None:
            return float(rk["complete_rate"]), name.name
    return None, None

cur, prov = {}, {}
for k in KINDS:
    v, f = rate_for(k)
    if v is not None:
        cur[k], prov[k] = v, f

base = {}
if basep.is_file():
    try:
        base = json.loads(basep.read_text())
    except Exception:
        base = {}
if not base:
    basep.write_text(json.dumps(cur, indent=1))
    print("[retention] baseline written: " + str({k: round(v, 3) for k, v in cur.items()}))
    sys.exit(0)

bad = []
for k, v in cur.items():
    was = base.get(k)
    reg = was is not None and was >= mn and v < mn
    print("[retention] %-13s was=%s now=%.3f (%s)%s"
          % (k, ("%.3f" % was) if was is not None else "n/a", v, prov.get(k),
             "   <-- REGRESSED" if reg else ""))
    if reg:
        bad.append((k, was, v, prov.get(k)))
if bad:
    print("[retention] FAIL -- these skills worked before this run and no longer do:")
    for k, was, v, f in bad:
        print("[retention]   %s: %.3f -> %.3f  (%s)" % (k, was, v, f))
    print("[retention] stopping the chain (set RM_RETENTION_OFF=1 to override)")
    sys.exit(9)
RETENTION_PY
  rc=$?
  if [ "$rc" = "9" ]; then log "phase $label: SKILL RETENTION FAIL -- stopping"; exit 9; fi
  return 0
}

eval_phase() {   # eval_phase <label> <checkpoint> ["kind1 kind2 ..."]
  local label=$1 ckpt=$2 focus="${3:-}"
  # v2 fix (2026-09-13, audit 41): a chain-specific tag so a later chain cannot overwrite
  # this one's evidence in place.  Unset tag => the original path (unchanged behaviour).
  local OUT=docs/acceptance_phase_v3_${RM_ACCEPT_TAG:+${RM_ACCEPT_TAG}_}${label}
  mkdir -p "$OUT"
  bash migration/linux/check_run_version.sh "$ckpt" > "$OUT/version_check.txt" 2>&1
  local rc=$?
  tail -3 "$OUT/version_check.txt" | tee -a "$LOG"
  if [ "$rc" -ne 0 ] && [ "$rc" -ne 3 ]; then
    log "$label: VERSION GATE FAILED (rc=$rc) -- reporting FAIL_VERSION"; return 4
  fi
  # Honest route length: pin the delivered values.  The manifest of this run carries the
  # training knobs, and eval_terrain_mod4.py replays every RM_* key that is not already set,
  # so RM_TUNNEL_GOAL_X=0 / RM_ROUGH_SPEED_MAX=0 / RM_ROUTE_WEIGHTS= must be explicit.
  # The poke schedule knobs (lead/fold/speed) are NOT pinned: they are part of the task the
  # policy was trained for, not a shortened route.
  OMNI_KIT_ACCEPT_EULA=YES RM_MOD4_MAP=rmuc2026 RM_MOD4_TERRAIN=field RM_DR_OFF=1 \
    RM_TUNNEL_GOAL_X=0 RM_ROUGH_SPEED_MAX=0 RM_ROUTE_WEIGHTS= \
    $PY isaac/mod4/eval_terrain_mod4.py --headless --checkpoint "$ckpt" --num_envs 64 \
    --steps ${RM_EVAL_STEPS:-2200} --seed 20260912 --report "$OUT/eval.json" >>"$LOG" 2>&1 || true
  $PY migration/linux/read_phase_eval.py "$OUT/eval.json" 2>&1 | tee -a "$LOG" || true
  phase_report "$label" "$OUT/eval.json"
  local kind
  for kind in $focus; do
    log "$label: focused single-kind eval ($kind, 64 env, 2200 steps)"
    OMNI_KIT_ACCEPT_EULA=YES RM_MOD4_MAP=rmuc2026 RM_MOD4_TERRAIN=field RM_DR_OFF=1 \
      RM_ROUTE_KINDS="$kind" RM_TUNNEL_GOAL_X=0 RM_ROUGH_SPEED_MAX=0 RM_ROUTE_WEIGHTS= \
      $PY isaac/mod4/eval_terrain_mod4.py --headless --checkpoint "$ckpt" --num_envs 64 \
      --steps ${RM_EVAL_STEPS:-2200} --seed 20260912 --report "$OUT/eval_focus_${kind}.json" >>"$LOG" 2>&1 || true
    phase_report "${label}_focus_${kind}" "$OUT/eval_focus_${kind}.json"
  done
  _retention_check "$label" "$OUT"
}

phase_index() { local i=0 p; for p in $PHASES; do [ "$p" = "$1" ] && { echo "$i"; return; }; i=$((i+1)); done; echo 99; }

[ -f "$CKPT" ] || { echo "[v3] start checkpoint missing: $CKPT" >&2; exit 4; }
START=$(phase_index "$FROM")
[ "$START" -ge 99 ] && { echo "[v3] unknown from_phase '$FROM' (use: $PHASES)" >&2; exit 2; }
[ "$SMOKE" = "0" ] && [ "$START" -eq 0 ] && START=1

log "chain v3 start checkpoint=$CKPT from=$FROM envs=$ENVS iters=$ITERS dry_run=$DRY_RUN"
freeze_hashes "$FROZEN"
if [ -f "$TUNING" ]; then log "tuning file $TUNING:"; sed 's/^/[v3]   /' "$TUNING" | tee -a "$LOG"; else log "no $TUNING (delivered defaults)"; fi

for PH in $PHASES; do
  IDX=$(phase_index "$PH")
  [ "$IDX" -lt "$START" ] && { log "skip phase $PH (resuming at $FROM)"; continue; }
  case "$PH" in
    smoke)  WEIGHTS="$BASE";                          P_ENVS=64;  P_ITERS=250 ;;
    tunnel) WEIGHTS="$(weights_for tunnel_cross 8)";  P_ENVS=$ENVS; P_ITERS=$ITERS ;;
    terrain) WEIGHTS="$(weights_multi "ramp_up:4 step_up:4 rough_cross:4")"; P_ENVS=$ENVS; P_ITERS=$ITERS ;;
    spin)   WEIGHTS="$(weights_for slope_spin 7)";    P_ENVS=$ENVS; P_ITERS=$ITERS ;;
    fly)    WEIGHTS="$(weights_for fly_jump 6)";      P_ENVS=$ENVS; P_ITERS=$ITERS ;;
    jump)   WEIGHTS="$(weights_for jump_in_place 5)"; P_ENVS=$ENVS; P_ITERS=$ITERS ;;
  esac
  log "=== phase $PH envs=$P_ENVS iters=$P_ITERS"
  log "    weights=$WEIGHTS"
  alloc_check "$WEIGHTS"
  if [ "$DRY_RUN" = "1" ]; then log "    DRY_RUN: not launching"; continue; fi

  if pgrep -f "[t]rain_mod4_ppo.py" >/dev/null; then
    log "REFUSING: another training is alive (one task at a time):"; pgrep -af "[t]rain_mod4_ppo.py" | tee -a "$LOG"; exit 6
  fi
  # Delivered route lengths in training as well: no shortened goal, no extra spawn lead.
  # RM_TUNNEL_GOAL_X / RM_TUNNEL_SPAWN_DIST / RM_ROUGH_SPEED_MAX stay unset: the goal distance
  # and the spawn must stay the delivered ones (goal 2 forbids a shortened course as "proof").
  # RM_TUNNEL_LEAD_M is deliberately NOT unset: the idler-friction finding
  # (docs/TUNNEL_IDLER_FRICTION_FINDING_20260912.md) shows the crossing is a momentum problem and
  # that 0.40 m of pre-crouch lead burns the entry speed, so the lead is a legitimately tuned
  # schedule knob (RM_TUNNEL_LEAD_M=0.18), not a shorter route.
  unset RM_TUNNEL_GOAL_X RM_TUNNEL_SPAWN_DIST RM_ROUGH_SPEED_MAX
  export RM_ROUTE_WEIGHTS="$WEIGHTS"
  apply_knobs

  TRAIN_LOG=logs/isaac_mod4/phasev3_${PH}_$(date +%H%M%S).log
  FORCE=1 bash migration/linux/start_mod4_stage_fixedplant.sh mixed "$CKPT" "$P_ENVS" "$P_ITERS" \
    >"$TRAIN_LOG" 2>&1 || true
  grep -h "^\[launch\]" "$TRAIN_LOG" | tail -2 | tee -a "$LOG"
  sleep 20
  pgrep -f "[t]rain_mod4_ppo.py" >/dev/null || { log "$PH: training did not start -- aborting"; exit 1; }
  wait_for_training "$PH"
  check_hashes "$FROZEN" || { log "$PH: CHAIN_V3_HASH_MISMATCH -- sources changed during the chain"; exit 4; }

  if [ "$PH" = "smoke" ]; then
    smoke_verdict "$TRAIN_LOG"
    CKPT="$ROOT_CKPT"   # the smoke phase must not become the chain parent
    continue
  fi
  case "$PH" in
    tunnel) eval_phase "$PH" "$CKPT" tunnel_cross ;;
    terrain) eval_phase "$PH" "$CKPT" "ramp_up step_up rough_cross" ;;
    spin)   eval_phase "$PH" "$CKPT" slope_spin ;;
    fly)    eval_phase "$PH" "$CKPT" fly_jump ;;
    jump)   eval_phase "$PH" "$CKPT" jump_in_place ;;
  esac
done

log "all phases finished; final checkpoint = $CKPT"
log "next: bash migration/linux/final_acceptance_mod4.sh $CKPT <tag>"
