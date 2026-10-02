#!/usr/bin/env python3
"""Per-phase SKILL-RETENTION gate: stop the chain when a skill that used to work regresses.

Why this exists (audit 61.3, the failure that cost the night)
-------------------------------------------------------------
The v2 chain ran 5+ hours and trained `slope_spin` from 0.703 down to 0.000.  The terrain-phase
evaluation that PROVED it had already landed at 07:44 (3 hours in) -- and the chain kept going,
because the only mid-run checks were (a) `smoke_verdict`, which reads closure/mimic and was anyway
inert (audit 43), and (b) the chain's per-phase verdict, which only PRINTS and never blocks
(audit 43.7).  Nothing anywhere asked "is the skill that worked yesterday still working?"

This patch adds exactly that, after every phase's reports are written.  Skills checked (the four
the goal names), read from the phase's FOCUS report when present, else the mixed one:

    slope_spin (小陀螺)  step_up (上台阶)  tunnel_cross (过洞)  fly_jump (飞坡)

    * the first phase writes `docs/_retention_baseline.json` and never blocks;
    * later phases compare: a skill that was >= RM_RETENTION_MIN and is now below it prints a
      loud RETENTION FAIL and exits 9, so the chain STOPS instead of burning more hours;
    * RM_RETENTION_OFF=1 disables it (for runs that intentionally trade skills away).

Apply between runs only -- bash reads a running script incrementally.

    python3 migration/linux/patch_skill_retention_gate.py --check
    python3 migration/linux/patch_skill_retention_gate.py
"""
from __future__ import annotations

import argparse
import pathlib
import sys

TARGET = pathlib.Path("migration/linux/run_special_phases_v3.sh")

ANCHOR = ('    phase_report "${label}_focus_${kind}" "$OUT/eval_focus_${kind}.json"\n'
          '  done\n'
          '}')
MARKER = "_retention_check"

BLOCK = ('    phase_report "${label}_focus_${kind}" "$OUT/eval_focus_${kind}.json"\n'
         '  done\n'
         '  _retention_check "$label" "$OUT"\n'
         '}')

_PY = """import json, pathlib, sys
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
"""

FUNC = ('\n# --- skill retention (audit 61.3) ------------------------------------------------------------\n'
        '# The v2 chain trained slope_spin 0.703 -> 0.000 over 5 hours while every automated check\n'
        '# passed: smoke only looked at closure/mimic, and the per-phase verdict only printed.  This\n'
        '# asks the ONE question none of them asked -- "is the skill that worked before still\n'
        '# working?" -- and STOPS the chain when the answer is no.\n'
        '_retention_check() {   # _retention_check <phase-label> <out-dir>\n'
        '  local label=$1 out=$2 base=docs/_retention_baseline.json\n'
        '  [ "${RM_RETENTION_OFF:-0}" = "1" ] && return 0\n'
        '  local py=/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python\n'
        '  [ -x "$py" ] || py=python3\n'
        '  local rc=0\n'
        '  "$py" - "$label" "$out" "$base" "${RM_RETENTION_MIN:-0.50}" <<\'RETENTION_PY\'\n'
        + _PY
        + 'RETENTION_PY\n'
        '  rc=$?\n'
        '  if [ "$rc" = "9" ]; then log "phase $label: SKILL RETENTION FAIL -- stopping"; exit 9; fi\n'
        '  return 0\n'
        '}\n\n')


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    text = TARGET.read_text(encoding="utf8")
    if MARKER in text:
        print("already patched (%s has the retention gate)" % TARGET)
        return 0
    if text.count(ANCHOR) != 1:
        print("ANCHOR FAIL: %d matches for the eval_phase report line" % text.count(ANCHOR),
              file=sys.stderr)
        return 2
    if text.count("eval_phase() {") != 1:
        print("ANCHOR FAIL: eval_phase() not found exactly once", file=sys.stderr)
        return 2
    if args.check:
        print("check OK: anchors found exactly once, no write")
        return 0
    bak = TARGET.with_suffix(".sh.bak_pre_retention")
    if not bak.exists():
        bak.write_bytes(TARGET.read_bytes())
    txt = text.replace(ANCHOR, BLOCK, 1).replace("eval_phase() {", FUNC + "eval_phase() {", 1)
    TARGET.write_text(txt, encoding="utf8")
    print("patched %s (backup %s)" % (TARGET, bak))
    return 0


if __name__ == "__main__":
    sys.exit(main())
