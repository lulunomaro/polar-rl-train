#!/usr/bin/env bash
# Version gate for a checkpoint: compare the hashes recorded in the run's run_manifest.json
# (byte-exact src_snapshot/ when present, else the 12-char code_sha256_12) against the files on
# disk.  Exit 0 = same version, 4 = mismatch (refuse to call the numbers a same-version
# acceptance), 3 = no manifest next to the checkpoint (warning only).
#
#   ./check_run_version.sh <checkpoint>
#
# NOTE: this mirrors the inline check inside eval_and_gate_mod4.sh on purpose (the acceptance
# script must be self-contained); keep the two in sync until the check is extracted properly.
set -uo pipefail
cd "$(dirname "$0")/../.."
CKPT=${1:?usage: check_run_version.sh <checkpoint>}
[ -f "$CKPT" ] || { echo "[version] checkpoint not found: $CKPT" >&2; exit 2; }
RUN_DIR="$(dirname "$CKPT")"
MANIFEST="$RUN_DIR/run_manifest.json"
[ -f "$MANIFEST" ] || {
  echo "[version] WARNING: no run_manifest.json next to $CKPT -- code version unknown"
  exit 3
}

python3 - "$MANIFEST" "$RUN_DIR" <<'PY'
import hashlib, json, pathlib, sys
man = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf8"))
run_dir = pathlib.Path(sys.argv[2])
HERE = pathlib.Path("isaac/mod4")
# 2026-09-12: the plant a run actually used is recorded in its own manifest (RM_MOD4_USD may
# point at the rolling-idler package under incoming/mod4_rolling_20260913).  Deriving the asset
# directory from `robot_usd` instead of hardcoding the delivered package is required: the
# hardcode made every rolling-plant run report VERSION MISMATCH (rc=4) and silently skipped its
# acceptance eval (eval_phase() returns before eval_terrain_mod4.py runs).
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
        print("[version]   %-22s %s (%s)" % (name, "OK" if ok else "CHANGED", got[:12]))
    for name, want in (("robot.usd", man.get("robot_usd_sha256")),
                       ("import_contract.json", man.get("import_contract_sha256"))):
        p = ASSET / name
        got = sha(p) if p.is_file() else "missing"
        ok = (not want) or got == want
        if not ok:
            bad.append("%s(asset) %s->%s" % (name, str(want)[:12], got[:12]))
        print("[version]   %-22s %s (%s)" % (name + " [asset]", "OK" if ok else "CHANGED", got[:12]))
else:
    for name, want in (man.get("code_sha256_12") or {}).items():
        p = HERE / name
        got = hashlib.sha256(p.read_bytes()).hexdigest()[:12] if p.is_file() else "missing"
        ok = got == want
        if not ok:
            bad.append("%s %s->%s" % (name, want, got))
        print("[version]   %-22s %s (%s) [no snapshot]" % (name, "OK" if ok else "CHANGED", got))
if bad:
    print("[version] VERSION MISMATCH: " + "; ".join(bad))
    print("VERSION_CHECK=FAIL")
    raise SystemExit(4)
print("VERSION_CHECK=PASS (sources and asset match the training run)")
PY
RC=$?
[ "$RC" -eq 4 ] && echo "[version] refusing: code/asset changed since training" >&2
exit $RC
