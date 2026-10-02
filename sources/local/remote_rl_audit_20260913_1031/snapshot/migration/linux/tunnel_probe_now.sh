#!/usr/bin/env bash
# Focused tunnel physics probe, runnable while the phase chain owns the GPU (goal section 2).
#
# WHY THIS DEVIATES FROM tunnel_diag.sh
#   tunnel_diag.sh runs four probes and refuses to start while a training job is alive, because a
#   contended GPU invalidates *training* throughput numbers.  The tunnel is the blocking gate of
#   the goal, and the alternative was to keep training 6+ h on a route whose physics is unknown.
#   This launcher therefore runs only the two physics probes that decide the fix (inertia coast +
#   crouch drive speed), back to back, at 4 / 8 environments and 400 / 300 steps, i.e. a few
#   minutes of GPU, and writes one transcript.  It never starts, stops or touches a training.
#
#   ./tunnel_probe_now.sh            # inertia + crouch_drive
#   ./tunnel_probe_now.sh contacts   # also run probe_tunnel_contacts.py
set -uo pipefail
cd "$(dirname "$0")/../.."
PY=/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python
OUT=docs/tunnel_probe_$(date +%Y%m%d_%H%M%S).txt
export OMNI_KIT_ACCEPT_EULA=YES RM_MOD4_MAP=rmuc2026 RM_MOD4_TERRAIN=field RM_DR_OFF=1

{
  echo "=== focused tunnel probe $(date) ==="
  echo "training job alive at start: $(pgrep -f 'train_mod4_ppo.py' | tr '\n' ' ')"
  echo
  echo "--- 1/3 inertia: can it coast through after squatting? (physics, no policy) ---"
  RM_ROUTE_KINDS=tunnel_cross $PY isaac/mod4/probe_tunnel_inertia.py --headless \
    --num_envs 4 --steps 400 --speeds 0.15,0.25,0.40,0.60 2>&1
  echo
  echo "--- 2/3 crouch drive: achieved speed per crouch pose (physics, no policy) ---"
  RM_ROUTE_KINDS=tunnel_cross $PY isaac/mod4/probe_crouch_drive.py --headless \
    --num_envs 8 --steps 300 2>&1
  if [ "${1:-}" = "contacts" ]; then
    echo
    echo "--- 3/3 contacts: guide / belly / roof contact split at the crouch ---"
    RM_ROUTE_KINDS=tunnel_cross $PY isaac/mod4/probe_tunnel_contacts.py --headless \
      --num_envs 8 --steps 300 2>&1
  fi
  echo
  echo "=== probe finished $(date) ==="
} > "$OUT" 2>&1
echo "$OUT"
