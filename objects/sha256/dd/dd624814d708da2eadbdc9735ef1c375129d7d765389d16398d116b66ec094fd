#!/usr/bin/env bash
# Final acceptance for the unified MOD4 policy (goal 2026-09-12 §5 / final deliverables).
#
#   ./final_acceptance_mod4.sh <checkpoint> [tag]
#
# Produces, under docs/acceptance_<tag>/:
#   nominal.json        fixed seed 20260912, DR OFF, all routes, 64 env x 2200 steps
#   nominal_gate.txt    stage_gate output for every route kind (terrain/spin/tunnel/fly)
#   dr_seed_<s>.json    DR ON, seeds 0..4
#   dr_summary.json     min/mean completion across the DR seeds
#   FROZEN_VERSION.txt  source/asset hashes of the run that produced the checkpoint
set -euo pipefail
cd "$(dirname "$0")/../.."
PY=/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python
CKPT=${1:?usage: final_acceptance_mod4.sh <checkpoint> [tag]}
TAG=${2:-$(basename "$CKPT" .pt)}
OUT=docs/acceptance_${TAG}
mkdir -p "$OUT"

# Curriculum overrides must NOT leak into the verdict: eval_terrain_mod4.py copies every RM_*
# key of the checkpoint's run_manifest.json into the environment when that variable is unset,
# so a phase checkpoint trained with the shortened tunnel goal (RM_TUNNEL_GOAL_X=1.60) would
# otherwise be scored against 1.60 m instead of the delivered goal (found 2026-09-12 15:40).
# Pin the delivered values explicitly; "0" means "no override".
export RM_TUNNEL_GOAL_X=0     # delivered tunnel goal, not the curriculum goal
export RM_ROUGH_SPEED_MAX=0   # no rough-route speed cap
# Same leak, second half: the phase manifest also carries the phase's RM_ROUTE_WEIGHTS
# ("...tunnel_cross:6"), which would score the verdict on the curriculum allocation -- at 1/35
# slots a kind such as ramp_down / jump_in_place gets ~2 of 64 envs and its gate becomes noise.
# Empty = the delivered 15-route table, i.e. every route keeps a slot (goal 3, balanced sampling).
export RM_ROUTE_WEIGHTS=
echo "[accept] pinned RM_TUNNEL_GOAL_X=$RM_TUNNEL_GOAL_X (delivered) RM_ROUGH_SPEED_MAX=$RM_ROUGH_SPEED_MAX RM_ROUTE_WEIGHTS=(delivered all-route)"

# Same plant/controller as the training run that produced the checkpoint: the evaluator
# replays the manifest RM_* keys, but pinning them here makes the acceptance log
# self-describing (goal: a model swap voids every checkpoint).
if [ -f migration/linux/tunnel_tuning.env ]; then
  set -a; . migration/linux/tunnel_tuning.env; set +a
  echo "[accept] sourced migration/linux/tunnel_tuning.env (plant/controller)"
fi
echo "[accept] plant=${RM_MOD4_USD:-delivered} leg_kp=${RM_LEG_KP:-delivered}"
echo "[accept] checkpoint=$CKPT tag=$TAG"
echo "[accept] version check (hashes of the run that produced this checkpoint vs disk)"
set +e
bash migration/linux/check_run_version.sh "$CKPT" > "$OUT/version_check.txt" 2>&1
VRC=$?
set -e
cat "$OUT/version_check.txt"
case "$VRC" in
  0) : ;;
  3) echo "[accept] WARNING: no manifest -- version unknown, recorded as a warning" ;;
  *) echo "[accept] refusing to accept: version mismatch (rc=$VRC)" >&2; exit 4 ;;
esac

echo "[accept] nominal run (seed 20260912, DR off, 64 env x 2200 steps)"
OMNI_KIT_ACCEPT_EULA=YES RM_MOD4_MAP=rmuc2026 RM_MOD4_TERRAIN=field RM_DR_OFF=1 \
  $PY isaac/mod4/eval_terrain_mod4.py --headless --checkpoint "$CKPT" --num_envs 64 \
  --steps 2200 --seed 20260912 --report "$OUT/nominal.json"

echo "[accept] per-route gates"
: > "$OUT/nominal_gate.txt"
for stage in terrain spin tunnel fly; do
  echo "--- $stage ---" >> "$OUT/nominal_gate.txt"
  $PY isaac/mod4/stage_gate.py --stage "$stage" --log docs/_gate_stub.log \
    --eval "$OUT/nominal.json" >> "$OUT/nominal_gate.txt" 2>&1 || true
done
cat "$OUT/nominal_gate.txt"

echo "[accept] roof-hit check (goal: the tunnel roof must not be scraped)"
$PY - "$OUT" <<'PY' | tee "$OUT/roof_check.txt"
import json, pathlib, sys
out = pathlib.Path(sys.argv[1])
def roof(d):
    b = (d.get("route_kinds") or {}).get("tunnel_cross") or {}
    return b.get("envs", 0), b.get("fail/tunnel_roof_hit", 0.0), b.get("underpass_seen", 0.0)
nom = json.loads((out / "nominal.json").read_text(encoding="utf8"))
envs, hits, under = roof(nom)
print("nominal      : tunnel envs=%s roof_hit_terminations=%s underpass_seen=%s" % (envs, hits, under))
verdict = "PASS" if hits == 0 else "FAIL"
for p in sorted(out.glob("dr_seed_*.json")):
    d = json.loads(p.read_text(encoding="utf8"))
    e, h, u = roof(d)
    print("%-13s: tunnel envs=%s roof_hit_terminations=%s underpass_seen=%s" % (p.stem, e, h, u))
    if h != 0:
        verdict = "FAIL"
print("ROOF_CHECK=%s (bar: 0 terminations; the term fires when the CAD skin is 2 mm inside the roof)" % verdict)
PY

echo "[accept] domain-randomised seeds"
for s in 0 1 2 3 4; do
  # RM_DR_OFF=0 is REQUIRED: every training manifest pins RM_DR_OFF=1, and eval_terrain_mod4.py
  # copies unset RM_* keys out of that manifest, so without this line the five "DR" seeds would
  # silently be five DR-OFF runs (found 2026-09-12 15:37).
  OMNI_KIT_ACCEPT_EULA=YES RM_MOD4_MAP=rmuc2026 RM_MOD4_TERRAIN=field RM_DR_OFF=0 \
    $PY isaac/mod4/eval_terrain_mod4.py --headless --checkpoint "$CKPT" --num_envs 64 \
    --steps 2200 --seed "$s" --report "$OUT/dr_seed_${s}.json"
done

$PY - "$OUT" <<'PY'
import json, pathlib, sys
out = pathlib.Path(sys.argv[1])
seeds = {}
for p in sorted(out.glob("dr_seed_*.json")):
    d = json.loads(p.read_text(encoding="utf8"))
    seeds[p.stem.split("_")[-1]] = {k: v["complete_rate"] for k, v in d["route_kinds"].items()}
kinds = sorted({k for s in seeds.values() for k in s})
summary = {"seeds": len(seeds), "per_route": {}}
for k in kinds:
    vals = [s.get(k, 0.0) for s in seeds.values()]
    summary["per_route"][k] = {"min": min(vals), "mean": sum(vals) / len(vals),
                               "all_seeds_ge_0.6": all(v >= 0.6 for v in vals)}
(out / "dr_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf8")
print("[accept] DR summary:", json.dumps(summary["per_route"], indent=1))
PY

# --- v2 (docs section 11.2): train-vs-contract actuator gain parity -------------------------
# The training runs at RM_LEG_KP=2500 while the delivery contract says 60 (41.7x).  Nothing used to
# compare them, so a checkpoint could pass every gate while describing a plant 41.7x softer than the
# one it was trained on.  The training value is in the run manifest's `effective` block.
echo "[accept] actuator gain parity (training vs delivery contract)"
RUN_DIR=$(dirname "$CKPT")
"$PY" - "$RUN_DIR/run_manifest.json" \
       train/deploy/contract_rm2025_later.json "${RM_GAIN_PARITY_MAX:-2.0}" <<'PYEOF'
import json, os, sys
man, contract, limit = sys.argv[1], sys.argv[2], float(sys.argv[3])
try:
    eff = (json.load(open(man, encoding="utf8")) or {}).get("effective") or {}
except Exception as exc:
    print("[accept] gain parity: NO MANIFEST (%s) -- cannot compare; apply "
          "patch_manifest_effective_knobs.py" % exc)
    raise SystemExit(0)
try:
    c = json.load(open(contract, encoding="utf8"))
except Exception as exc:
    print("[accept] gain parity: no contract (%s)" % exc)
    raise SystemExit(0)
bad, rows = [], []
# v2 fix (2026-09-13): the `effective` block records RM_* KNOB names (123 of them on the
# live v2 run), not bare constant names -- the original lookup was silently finding nothing.
# RM_WHEEL_KD has no knob (wheel_kd is not environment-settable), so it is not compared.
for tk, ck in (("RM_LEG_KP", "leg_kp"), ("RM_LEG_KD", "leg_kd")):
    try:
        t = float(str(eff.get(tk, "")).strip() or "nan")
        v = float(c.get(ck, "nan"))
    except Exception:
        continue
    if t != t or v != v or v == 0:
        continue
    r = t / v
    rows.append((tk, t, v, r))
    if limit > 0 and (r > limit or r < 1.0 / limit):
        bad.append((tk, t, v, r))
for tk, t, v, r in rows:
    print("[accept]   %-8s training=%-9.4g contract=%-9.4g ratio=%6.2fx" % (tk, t, v, r))
if not rows:
    if not eff:
        print("[accept] gain parity: this run predates patch_manifest_effective_knobs (no "
              "`effective` block) -- CANNOT COMPARE.  Re-run acceptance on a v2 checkpoint.")
    else:
        # v2 fix (2026-09-13): an `effective` block WITHOUT the expected keys means this check
        # cannot see the gains at all -- failing loudly beats passing quietly (which is exactly
        # what it did before this fix: 123 keys present, none of the looked-up ones).
        print("[accept] GAIN PARITY FAIL -- `effective` has %d keys but none of %s; this check "
              "cannot compare the gains and must not report success."
              % (len(eff), ["RM_LEG_KP", "RM_LEG_KD"]))
        raise SystemExit(9)
elif bad:
    print("[accept] GAIN PARITY FAIL -- the policy was trained on a different actuator than the")
    print("[accept] contract describes: %s" % ", ".join("%s %.4gx" % (t, r) for t, _, _, r in bad))
    print("[accept] Refuse to declare acceptance, or set RM_GAIN_PARITY_MAX=0 and record WHY.")
    raise SystemExit(8)
else:
    print("[accept] gain parity OK (all ratios within %.2fx)" % limit)
PYEOF
_gp=$?
if [ "$_gp" = "8" ]; then exit 8; fi

# --- v2: DR-ON focused per-kind evaluations (measurement resolution) ------------------------
# The five mixed seeds above give each kind only ~8 environments (resolution 1/8), which cannot
# separate "DR breaks this skill" from "this seed was unlucky" -- measured on baseline_16295:
# step_up 6/8 -> 0/8 and run 0.600 -> 1.000 under DR.  The chain's focused single-kind eval at
# 64 environments gives 1/64; this runs it with DR ON for every kind that has a gate bar.
echo "[accept] DR-on focused per-kind evals (64 env, resolution 1/64)"
for _k in ramp_up ramp_down step_up step_down rough_cross tunnel_cross slope_spin fly_jump; do
  OMNI_KIT_ACCEPT_EULA=YES RM_MOD4_MAP=rmuc2026 RM_MOD4_TERRAIN=field RM_DR_OFF=0 \
    RM_ROUTE_KINDS="$_k" RM_TUNNEL_GOAL_X=0 RM_ROUGH_SPEED_MAX=0 RM_ROUTE_WEIGHTS= \
    $PY isaac/mod4/eval_terrain_mod4.py --headless --checkpoint "$CKPT" --num_envs 64 \
    --steps 2200 --seed 20260912 --report "$OUT/dr_focus_${_k}.json" >>"$OUT/dr_focus_eval.log" 2>&1 || true
  echo "[accept]   dr_focus_${_k}.json"
done
# and the same kinds with DR OFF at the SAME resolution, so the pair is comparable
echo "[accept] DR-off focused per-kind evals (the comparison arm)"
for _k in ramp_up ramp_down step_up step_down rough_cross tunnel_cross slope_spin fly_jump; do
  OMNI_KIT_ACCEPT_EULA=YES RM_MOD4_MAP=rmuc2026 RM_MOD4_TERRAIN=field RM_DR_OFF=1 \
    RM_ROUTE_KINDS="$_k" RM_TUNNEL_GOAL_X=0 RM_ROUGH_SPEED_MAX=0 RM_ROUTE_WEIGHTS= \
    $PY isaac/mod4/eval_terrain_mod4.py --headless --checkpoint "$CKPT" --num_envs 64 \
    --steps 2200 --seed 20260912 --report "$OUT/off_focus_${_k}.json" >>"$OUT/dr_focus_eval.log" 2>&1 || true
done
$PY - "$OUT" <<'PYEOF'
import json, pathlib, sys
out = pathlib.Path(sys.argv[1])
rows = []
for p in sorted(out.glob("off_focus_*.json")):
    k = p.stem.replace("off_focus_", "")
    drp = out / ("dr_focus_%s.json" % k)
    try:
        off = (json.loads(p.read_text(encoding="utf8"))["route_kinds"].get(k) or {}).get("complete_rate")
        on = (json.loads(drp.read_text(encoding="utf8"))["route_kinds"].get(k) or {}).get("complete_rate") \
            if drp.is_file() else None
    except Exception:
        continue
    rows.append((k, off, on))
print("[accept] DR robustness at 64 envs (resolution 1/64):")
for k, off, on in rows:
    if off is None or on is None:
        print("[accept]   %-14s off=%s on=%s" % (k, off, on)); continue
    verdict = "HOLDS" if on >= 0.60 else "DROPS"
    print("[accept]   %-14s off=%.3f on=%.3f delta=%+.3f  %s" % (k, off, on, on - off, verdict))
(out / "dr_focus_summary.json").write_text(
    json.dumps({"per_kind": {k: {"off": off, "on": on} for k, off, on in rows}}, indent=2) + "\n",
    encoding="utf8")
PYEOF

echo "[accept] frozen version record"
{
  echo "checkpoint: $CKPT"; sha256sum "$CKPT"
  echo "pinned_env: RM_TUNNEL_GOAL_X=$RM_TUNNEL_GOAL_X RM_ROUGH_SPEED_MAX=$RM_ROUGH_SPEED_MAX"
  # 2026-09-12: record the plant the acceptance actually used (RM_MOD4_USD, sourced from
  # tunnel_tuning.env above) instead of the delivered package -- otherwise the frozen record
  # names a plant that was never loaded.
  _PLANT=${RM_MOD4_USD:-incoming/mod4_fixed_20260912/chassis_mod4/isaac/robot.usd}
  for f in isaac/mod4/mod4_task.py isaac/mod4/skills_isaac.py isaac/mod4/route_isaac.py \
           "$_PLANT" "$(dirname "$_PLANT")/import_contract.json"; do
    sha256sum "$f"
  done
} | tee "$OUT/FROZEN_VERSION.txt"

# --- v2 item 5: sim2sim gate -- ONNX -> MuJoCo must PASS before a delivery is produced -----
# Artefact half: contract rates, plant loading, ONNX input/output layout and the contract
# metadata inside the ONNX.  Behavioural half still needs the linkage mapping (see section 5.6
# of docs/MOD4_V2_REDESIGN_AUDIT_20260912.md).
if [ "${RM_SKIP_SIM2SIM:-0}" = "1" ]; then
  echo "[accept] sim2sim gate BYPASSED (RM_SKIP_SIM2SIM=1) -- record this in the report"
else
  echo "[accept] sim2sim gate: exporting ONNX + checking contract/plant/layout"
  # v2 fix (2026-09-13): take the encoder layout from the RUN MANIFEST, not from the ambient
  # environment.  tunnel_tuning.env does not set RM_SEQ_ENCODER, so this block used to export a
  # 35-D ONNX from a 175-D v2 checkpoint -> the exporter refuses -> exit 6 at the LAST step of the
  # acceptance, after the nominal run and five DR seeds.  The evaluator already replays the
  # manifest (audit section 40); this block now does the same.
  _HIST=0
  _MAN="${RUN_DIR:-$(dirname "$CKPT")}/run_manifest.json"
  if [ -f "$_MAN" ]; then
    _HIST=$("$PY" -c "
import json,sys
d=json.load(open('$_MAN'))
e=d.get('effective') or d.get('env') or {}
print(int(e.get('RM_SEQ_HISTORY','5')) if str(e.get('RM_SEQ_ENCODER','0'))=='1' else 0)
" 2>/dev/null || echo 0)
    echo "[accept] sim2sim encoder history from the manifest: $_HIST"
  else
    if [ "${RM_SEQ_ENCODER:-0}" = "1" ]; then _HIST=${RM_SEQ_HISTORY:-5}; fi
    echo "[accept] sim2sim encoder history from the environment (no manifest): $_HIST"
  fi
  _MOD4_POLICY="$OUT/policy.onnx"
  "$PY" sim2sim_mod4/export_mod4_onnx.py --checkpoint "$CKPT" --out "$_MOD4_POLICY" \
    --encoder-history "$_HIST" || { echo "[accept] sim2sim ONNX EXPORT FAILED" >&2; exit 6; }
  _SIM2SIM_PY=third_party/rc_mjlab/.venv/bin/python
  if [ ! -x "$_SIM2SIM_PY" ]; then
    echo "[accept] SIM2SIM GATE BLOCKED: $_SIM2SIM_PY missing (mujoco + onnxruntime live there)" >&2
    exit 6
  fi
  if ! "$_SIM2SIM_PY" sim2sim_mod4/check_sim2sim_mod4.py --onnx "$_MOD4_POLICY" \
       | tee "$OUT/sim2sim_gate.txt"; then
    echo "[accept] SIM2SIM GATE FAILED -- refusing to declare this acceptance (see $OUT/sim2sim_gate.txt)" >&2
    exit 7
  fi
  echo "[accept] sim2sim gate PASS -> $OUT/policy.onnx"
fi

echo "[accept] done -> $OUT"
