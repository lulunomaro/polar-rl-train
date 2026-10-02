#!/usr/bin/env bash
# Independent evaluation + stage gate for the MOD4 arena curriculum (audit P2: "a stage only
# advances when an INDEPENDENT evaluation passes -- a rising reward curve is not evidence").
#
#   ./eval_and_gate_mod4.sh <stage> <checkpoint> [num_envs] [steps]
#   stage: run | terrain | tunnel | fly | spin | jump
#   LOG=<training log>   optional; only needed for the stages that have log gates
#                        (run/jump).  A stub is created when it is omitted.
#
# Writes docs/terrain_<stage>_<ckpt>.json and exits with the gate's own status (0 = pass).
set -euo pipefail
cd "$(dirname "$0")/../.."

STAGE=${1:?usage: eval_and_gate_mod4.sh <stage> <checkpoint> [num_envs] [steps]}
CKPT=${2:?checkpoint required}
NUM_ENVS=${3:-64}
# The tunnel route needs the whole 20 s policy episode to be measurable (a crouched robot only
# makes ~0.06 m/s), so the default window is longer than the training episode.
STEPS=${4:-2200}

case "$STAGE" in
  run)     KINDS="run" ;;
  terrain) KINDS="ramp_up,ramp_down,step_up,step_down,rough_cross" ;;
  tunnel)  KINDS="tunnel_cross" ;;
  fly)     KINDS="fly_jump" ;;
  spin)    KINDS="slope_spin" ;;
  jump)    KINDS="jump_in_place" ;;
  *) echo "unknown stage: $STAGE" >&2; exit 2 ;;
esac
[ -f "$CKPT" ] || { echo "checkpoint missing: $CKPT" >&2; exit 3; }

# Audit 2026-09-12 (item 7): both training processes were started at 07:25 but the task sources
# were edited at 08:27, so an evaluation of an old checkpoint ran against NEW code.  Every run
# writes `code_sha256_12` into its run_manifest.json -- compare it with the files on disk and
# refuse to pretend the numbers are a same-version acceptance when they are not.
RUN_DIR="$(dirname "$CKPT")"
MANIFEST="$RUN_DIR/run_manifest.json"
# goal §1: the evaluator must verify the source AND asset hashes and REFUSE to print PASS when
# they differ.  Runs started after 2026-09-12 11:40 carry a byte-exact src_snapshot/; older runs
# only have the 12-char manifest hashes (then we can only warn).
if [ -f "$MANIFEST" ]; then
  echo "[gate-run] version check against $MANIFEST"
  python3 - "$MANIFEST" "$RUN_DIR" <<'PY'
import hashlib, json, pathlib, sys
man = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf8"))
run_dir = pathlib.Path(sys.argv[2])
HERE = pathlib.Path("isaac/mod4")
# 2026-09-12: mirror of check_run_version.sh -- resolve the asset directory from the run's own
# manifest (`robot_usd`) so a rolling-idler-plant run is not reported as a version mismatch.
_USD = str(man.get("robot_usd") or "").strip()
ASSET = (pathlib.Path(_USD).parent if _USD else
         pathlib.Path("incoming/mod4_fixed_20260912/chassis_mod4/isaac"))

def sha(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()

bad = []
snap = run_dir / "src_snapshot"
full = man.get("src_sha256") or {}
if snap.is_dir() and full:
    for name, want in sorted(full.items()):
        cur = (HERE / name) if (HERE / name).is_file() else (ASSET / name)
        got = sha(cur) if cur.is_file() else "missing"
        ok = got == want
        if not ok:
            bad.append("%s %s->%s" % (name, want[:12], got[:12]))
        print("[gate-run]   %-22s %s (%s)" % (name, "OK" if ok else "CHANGED", got[:12]))
    for name, want in (("robot.usd", man.get("robot_usd_sha256")),
                       ("import_contract.json", man.get("import_contract_sha256"))):
        p = ASSET / name
        got = sha(p) if p.is_file() else "missing"
        ok = (not want) or got == want
        if not ok:
            bad.append("%s(asset) %s->%s" % (name, str(want)[:12], got[:12]))
        print("[gate-run]   %-22s %s (%s)" % (name + " [asset]", "OK" if ok else "CHANGED", got[:12]))
else:
    for name, want in (man.get("code_sha256_12") or {}).items():
        p = HERE / name
        got = hashlib.sha256(p.read_bytes()).hexdigest()[:12] if p.is_file() else "missing"
        ok = got == want
        if not ok:
            bad.append("%s %s->%s" % (name, want, got))
        print("[gate-run]   %-22s %s (%s) [no snapshot]" % (name, "OK" if ok else "CHANGED", got))
if bad:
    print("[gate-run] VERSION MISMATCH: " + "; ".join(bad))
    raise SystemExit(4)
print("[gate-run] version check PASS (sources and asset match the training run)")
PY
  RC=$?
  if [ "$RC" -eq 4 ]; then
    echo "[gate-run] refusing to evaluate: code/asset changed since training" >&2
    exit 4
  fi
else
  echo "[gate-run] WARNING: no run_manifest.json next to the checkpoint; code version unknown"
fi

TAG=$(basename "$CKPT" .pt)
REPORT=docs/terrain_${STAGE}_${TAG}.json
LOG=${LOG:-}
if [ -z "$LOG" ]; then
  LOG=docs/_gate_stub.log
  [ -f "$LOG" ] || printf 'Learning iteration 0/1\n' > "$LOG"
fi

echo "[gate-run] stage=$STAGE kinds=$KINDS envs=$NUM_ENVS steps=$STEPS ckpt=$CKPT"
# OMNI_KIT_ACCEPT_EULA: without it Isaac Sim stops at the interactive EULA prompt and dies
# (measured 2026-09-12 -- same footgun as the training launcher).
OMNI_KIT_ACCEPT_EULA=YES \
RM_MOD4_MAP=rmuc2026 RM_MOD4_TERRAIN=field RM_DR_OFF=1 RM_ROUTE_KINDS=$KINDS \
  /home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python isaac/mod4/eval_terrain_mod4.py \
  --headless --checkpoint "$CKPT" --num_envs "$NUM_ENVS" --steps "$STEPS" --report "$REPORT"

/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python isaac/mod4/stage_gate.py \
  --stage "$STAGE" --log "$LOG" --eval "$REPORT"
RC=$?
echo "[gate-run] report=$REPORT gate_rc=$RC"
exit $RC
