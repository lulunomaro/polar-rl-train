#!/usr/bin/env bash
# Independent per-phase gate check: the authoritative stage_gate.py bars, applied by hand.
#
# Why this exists (audit section 43): the chain's own `smoke_verdict()` cannot find its metrics
# (it greps "^\[launch\] log=" but the launcher prints "[launch] pid=<n> log=<path>"), so it
# passes everything with "metrics not found -> WARNING".  The chain's per-phase verdict computes
# the right numbers but only PRINTS them -- it never blocks.  The FORMAL acceptance's gates are
# sound (they pass a stub log deliberately), so this script reproduces exactly that invocation:
#
#   stage_gate.py --stage <phase> --log docs/_gate_stub.log --eval <focus report>
#
# and uses the FOCUS report, because the mixed eval gives a single subject only ~4 environments
# (resolution 1/4) and can make a passing subject look like a failure (measured: slope_spin 0.500
# mixed vs 0.703 focused on the same checkpoint).
#
#   bash migration/linux/my_phase_gate.sh                       # newest v2 tag, all phases
#   TAG=v2 bash migration/linux/my_phase_gate.sh                 # a specific tag
#   DIR=docs/acceptance_phase_v3_spin bash migration/linux/my_phase_gate.sh
set -uo pipefail
cd "$(dirname "$0")/../.."

TAG=${TAG:-v2}
PY=/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python
STUB=docs/_gate_stub.log
[ -f "$STUB" ] || : > "$STUB"

# terrain/spin/tunnel/fly have empty log requirements in stage_gate.STAGES, so a stub is fine.
# `jump` (and `run`) DO require log metrics, so for those we must find the real stage log.  Parse
# the chain log's own phase transitions -- the launcher line is "[launch] pid=<n> log=<path>",
# which is precisely the line the chain's own broken grep ("^\[launch\] log=") never matched.
stage_log_for() {   # stage_log_for <phase>
  local ph=$1 f=${CHAIN_LOG:-logs/isaac_mod4/v2_chain_launch.log}
  [ -f "$f" ] || return 1
  awk -v want="$ph" '
    /^\[v3\] === phase / { cur=$4 }
    /^\[launch\] .*log=/ { if (cur==want) { sub(/.*log=/,""); last=$0 } }
    END { if (last != "") print last }
  ' "$f"
}

# phase -> the kind whose focus report carries the decisive numbers
phase_kind() {
  case "$1" in
    terrain) echo "rough_cross" ;;
    spin)    echo "slope_spin" ;;
    tunnel)  echo "tunnel_cross" ;;
    fly)     echo "fly_jump" ;;
    jump)    echo "jump_in_place" ;;
  esac
}

dir_for() {   # dir_for <phase>  -> newest matching acceptance dir
  local ph=$1 d
  for d in "docs/acceptance_phase_v3_${TAG}_${ph}" "docs/acceptance_phase_v3_${ph}"; do
    [ -d "$d" ] && { echo "$d"; return; }
  done
}

if [ -n "${DIR:-}" ]; then
  ph=${DIR##*_}
  dirs="$DIR"
else
  dirs=""
  for ph in terrain spin tunnel fly jump; do
    d=$(dir_for "$ph"); [ -n "$d" ] && dirs="$dirs $ph:$d"
  done
fi

rc_all=0
for entry in ${dirs:-}; do
  if [ -n "${DIR:-}" ]; then ph=${ph}; d=$entry; else ph=${entry%%:*}; d=${entry##*:}; fi
  kind=$(phase_kind "$ph")
  rep="$d/eval_focus_${kind}.json"
  echo "=== ${ph}  (${d}) ==="
  if [ ! -f "$rep" ]; then
    echo "  no focus report at $rep"; echo "  (falling back to the mixed eval.json if present)"
    rep="$d/eval.json"
    [ -f "$rep" ] || { echo "  nothing to check"; rc_all=1; continue; }
  fi
  # pick the log the stage actually needs: stub for the empty-log stages, the real one for `jump`
  log=$STUB
  case "$ph" in
    jump|run)
      real=$(stage_log_for "$ph")
      if [ -n "$real" ] && [ -f "$real" ]; then log=$real; echo "  (using the real stage log: $log)"
      else echo "  ⚠️  no real stage log found for $ph -- the log-based bars cannot be checked"; fi ;;
  esac
  "$PY" isaac/mod4/stage_gate.py --stage "$ph" --log "$log" --eval "$rep"
  rc=$?
  [ "$rc" = "0" ] || rc_all=$rc
  echo
done
exit $rc_all
