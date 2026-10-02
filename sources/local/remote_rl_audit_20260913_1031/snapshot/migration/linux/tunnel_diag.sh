#!/usr/bin/env bash
# One-shot tunnel diagnosis (goal section 2): run every tunnel probe back-to-back on an idle GPU
# and save the whole transcript.  Refuses to start while a training job is alive, because the goal
# is one task at a time and a contended GPU invalidates the numbers.
#
#   ./tunnel_diag.sh <checkpoint> [out_tag]
#
# Produces docs/tunnel_diag_<tag>.txt with:
#   1. probe_tunnel_inertia   -- can the robot COAST through after it squats?  (physics)
#   2. probe_crouch_drive     -- how fast can it drive in each crouch pose?    (physics)
#   3. probe_tunnel_contacts  -- guide / belly / roof contact split at the crouch (physics)
#   4. probe_tunnel_traj      -- what does the trained POLICY do at the mouth? (behaviour)
set -uo pipefail
cd "$(dirname "$0")/../.."
PY=/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python
CKPT=${1:?usage: tunnel_diag.sh <checkpoint> [tag]}
TAG=${2:-$(date +%Y%m%d_%H%M%S)}
OUT=docs/tunnel_diag_${TAG}.txt

if [ "${FORCE:-0}" != "1" ] && pgrep -f "train_mod4_ppo.py" >/dev/null; then
  echo "REFUSING: a training job is alive (one task at a time):" >&2
  pgrep -af "train_mod4_ppo.py" >&2
  exit 5
fi

export OMNI_KIT_ACCEPT_EULA=YES RM_MOD4_MAP=rmuc2026 RM_MOD4_TERRAIN=field RM_DR_OFF=1
mkdir -p docs
{
  echo "=== tunnel diagnosis $(date) ==="
  echo "checkpoint: $CKPT"
  echo "checkpoint sha256: $(sha256sum "$CKPT" | cut -d' ' -f1)"
  echo
  echo "--- 1/4 inertia: can it coast through after squatting? (physics, no policy) ---"
  RM_ROUTE_KINDS=tunnel_cross $PY isaac/mod4/probe_tunnel_inertia.py --headless \
    --num_envs 4 --steps 400 --speeds 0.15,0.25,0.40,0.60 2>&1
  echo
  echo "--- 2/4 crouch drive: achieved speed per crouch pose (physics, no policy) ---"
  RM_ROUTE_KINDS=tunnel_cross $PY isaac/mod4/probe_crouch_drive.py --headless \
    --num_envs 8 --steps 300 2>&1
  echo
  echo "--- 3/4 contact split at the crouch (guide / belly / roof) ---"
  RM_ROUTE_KINDS=tunnel_cross $PY isaac/mod4/probe_tunnel_contacts.py --headless \
    --num_envs 4 --steps 600 --every 100 2>&1
  echo
  echo "--- 4/4 trained policy trajectory at the mouth ---"
  RM_ROUTE_KINDS=tunnel_cross $PY isaac/mod4/probe_tunnel_traj.py --headless \
    --checkpoint "$CKPT" --num_envs 4 --steps 600 --every 50 2>&1
  echo
  echo "=== done $(date) ==="
} 2>&1 | tee "$OUT"
echo "[tunnel-diag] saved $OUT"
