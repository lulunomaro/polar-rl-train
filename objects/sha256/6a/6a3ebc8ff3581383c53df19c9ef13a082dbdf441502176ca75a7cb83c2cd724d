#!/usr/bin/env bash
# MOD4 dog-hole five-stage course (v2 item 4, path B -- task difficulty, no geometry change).
#
# Where this comes from
# ---------------------
# The isolated candidate package /home/egde/MOD4_RL_rewards_20260912 configures the tunnel as five
# progressing stages (configs/stages.json):
#
#     tunnel_hold      objective crouch_hold    episode 12 s
#     tunnel_crawl     objective crouch_crawl   episode 20 s
#     tunnel_approach  objective approach       episode 30 s
#     tunnel_cross                              episode 50 s
#     tunnel_recover                            episode 50 s     (progression chains them)
#
# That is the ONE thing in that package worth taking: its code is an EARLIER snapshot of the same
# lineage (its mod4_task.py 17:56 / skills_isaac.py 11:29 vs the live 20:30 / 20:30, and the live
# tree additionally carries CRANK_ACTION_SCALE and RM_LEG_KP, which the package lacks entirely --
# see docs/MOD4_V2_REDESIGN_AUDIT_20260912.md section 11).  Its process contribution is the staged
# course plus a per-route gate (>=100 complete episodes, success >= 0.80, three fixed seeds).
#
# We already have every knob the stages need, so this script only sequences them:
#     RM_ROUTE_KINDS=tunnel_cross   the route filter
#     RM_TUNNEL_SPAWN_DIST          how far back the env spawns
#     RM_TUNNEL_GOAL_X              where the goal sits (0 = the delivered 2.30 m endpoint)
#     RM_TUNNEL_CMD_HEIGHT          the commanded crouch height
#     RM_TUNNEL_LEAD_M              pre-crouch lead
#     RM_TUNNEL_PROGRESS_MULT       progress reward multiplier
#     RM_CROUCH_POSE_W              weight of the verified-pose reward (patch_crouch_pose_kernel)
#     RM_EPISODE_S                  episode budget
#
# Usage
# -----
#   bash migration/linux/run_tunnel_course.sh --dry-run                 # print the plan only
#   CKPT=logs/isaac_mod4/<run>/model_<N>.pt bash migration/linux/run_tunnel_course.sh
#   ... --from tunnel_crawl --iters 400 --envs 1024
#
# It refuses to launch while another training is alive (one task at a time) and never edits the
# repository: every stage is an ordinary stage-launcher invocation with explicit env vars.
set -uo pipefail
cd "$(dirname "$0")/../.."

DRY=0; FROM=""; ITERS=${ITERS:-400}; ENVS=${ENVS:-512}; CKPT=${CKPT:-}
while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run) DRY=1 ;;
    --from) FROM=${2:?}; shift ;;
    --iters) ITERS=${2:?}; shift ;;
    --envs)  ENVS=${2:?}; shift ;;
    *) echo "unknown arg: $1" >&2; exit 2 ;;
  esac
  shift
done
[ -f migration/linux/tunnel_tuning.env ] && { set -a; . migration/linux/tunnel_tuning.env; set +a; }
OUT=docs/tunnel_course_$(date +%Y%m%d_%H%M%S)
[ "$DRY" = "1" ] || mkdir -p "$OUT"      # a dry run must not leave directories behind

# TRAP (found 2026-09-13 while wiring this script): `RM_TUNNEL_LEAD_M` has TWO consumers with
# unrelated meanings --
#   * skills_isaac.py:90  TUNNEL_PRECROUCH_LEAD_M  -> how early the robot squats (default 0.40)
#   * route_isaac.py:221  lead                      -> shifts the tunnel SPAWN toward the goal
# so setting it for one purpose silently changes the other.  Staging must therefore use
# `RM_TUNNEL_SPAWN_DIST` (skills_isaac.py:553, the documented spawn override: it forces the spawn to
# `tunnel_entry - dist`), and `RM_TUNNEL_LEAD_M` is held CONSTANT across stages so its extra spawn
# nudge is a known constant rather than a per-stage confound.
#
# stage            spawn_dist  goal_x  cmd_height  lead    prog_mult  crouch_w  episode_s  gate
# FARMING ARITHMETIC (found 2026-09-13, audit section 15): `tunnel_stall` pays
#   -1.0 * 0.5 * (1 - clamp(|vx|/0.08,0,1))  = -0.5 per step at vx = 0
# while `tunnel_crouch_pose` pays
#   +RM_CROUCH_POSE_W * (1 - err/band)        = up to +RM_CROUCH_POSE_W per step
# so with the live weight 1.5 (and with the 2.0 this script first used for `hold`) SITTING STILL
# IN THE CROUCH IS NET POSITIVE -- which is exactly the measured failure (`fail/time_out` 6 of 8,
# `entered` 0, progress 0.38 m of the 0.48 m needed, `landed` 8/8: the robot crouches and waits).
# The Fudan package's tunnel_crawl stage warns about precisely this ("不能原地刷 crouch 奖励").
# Every stage from crawl onward therefore keeps crouch_pose_w BELOW the 0.5 stall penalty so that
# standing still is net NEGATIVE; only `hold` (a deliberate, time-boxed pose gate) pays more.
# INTERACTION with patch_tunnel_crouch_gate (found 2026-09-13): that patch multiplies the crouch
# reward by clamp(|vx|/0.05,0,1), so with the gate ON (its default) a STATIONARY crouch scores ZERO.
# That is what we want for crawl and later -- but `hold` exists to pay the robot for standing in the
# verified crouch, so it cannot work with the gate on.  `hold` therefore runs with
# RM_TUNNEL_CROUCH_MOVE_GATE=0 (a deliberate, time-boxed exception); every later stage runs with it
# ON, which is what makes standing still net -0.5/step no matter what RM_CROUCH_POSE_W is.
#
# stage            spawn_dist  goal_x  cmd_height  lead    prog_mult  crouch_w  episode_s  move_gate  gate
STAGES=(
  "tunnel_hold      0.05       0.12    0.178       0.18    0.5        1.5       12         0          hold_1s"
  "tunnel_crawl     0.35       0.45    0.178       0.18    1.0        0.30      20         1          crawl_0p08"
  "tunnel_approach  1.20       1.20    0.178       0.18    1.0        0.20      30         1          approach"
  "tunnel_cross     1.60       2.30    0.178       0.18    1.0        0.15      50         1          underpass_0p80"
  "tunnel_recover   0.90       1.60    0.230       0.18    1.0        0.10      50         1          recover"
)

STARTED=0
for row in "${STAGES[@]}"; do
  set -- $row
  NAME=$1; SPAWN=$2; GOAL=$3; HEIGHT=$4; LEAD=$5; PMULT=$6; CW=$7; EPS=$8; MGATE=$9; GATE=${10}
  if [ -n "$FROM" ] && [ "$STARTED" = "0" ]; then
    [ "$NAME" = "$FROM" ] && STARTED=1 || { echo "[course] skip $NAME (before --from $FROM)"; continue; }
  fi
  echo "[course] === $NAME  gate=$GATE"
  echo "[course]     RM_TUNNEL_SPAWN_DIST=$SPAWN RM_TUNNEL_GOAL_X=$GOAL RM_TUNNEL_CMD_HEIGHT=$HEIGHT"
  echo "[course]     RM_TUNNEL_LEAD_M=$LEAD (pre-crouch AND a spawn nudge -- see the TRAP note)"
  echo "[course]     RM_TUNNEL_PROGRESS_MULT=$PMULT RM_CROUCH_POSE_W=$CW RM_EPISODE_S=$EPS"
  if [ "$MGATE" = "0" ]; then
    echo "[course]     RM_TUNNEL_CROUCH_MOVE_GATE=0 (pose pays while stationary -- HOLD ONLY)"
  else
    echo "[course]     RM_TUNNEL_CROUCH_MOVE_GATE=1 (stationary crouch scores 0 -> net -0.5/step)"
  fi
  [ "$DRY" = "1" ] && continue

  # one task at a time: the guard the whole project runs on
  if pgrep -f "[t]rain_mod4_ppo.py" >/dev/null; then
    echo "[course] REFUSING: a training is already running (one task at a time)"; exit 6
  fi
  [ -n "$CKPT" ] && [ -f "$CKPT" ] || { echo "[course] CKPT not set or missing: '$CKPT'" >&2; exit 3; }

  LOG="$OUT/${NAME}.log"
  RM_ROUTE_KINDS=tunnel_cross RM_TUNNEL_SPAWN_DIST="$SPAWN" RM_TUNNEL_GOAL_X="$GOAL" \
  RM_TUNNEL_CMD_HEIGHT="$HEIGHT" RM_TUNNEL_LEAD_M="$LEAD" RM_TUNNEL_PROGRESS_MULT="$PMULT" \
  RM_CROUCH_POSE_W="$CW" RM_EPISODE_S="$EPS" RM_TUNNEL_CROUCH_MOVE_GATE="$MGATE" \
    bash migration/linux/start_mod4_stage_fixedplant.sh mixed "$CKPT" "$ENVS" "$ITERS" >"$LOG" 2>&1
  while pgrep -f "[t]rain_mod4_ppo.py" >/dev/null; do sleep 30; done
  CKPT=$(ls -t logs/isaac_mod4/*_mod4_fixed_mixed/model_*.pt | head -1)
  echo "[course] $NAME done -> $CKPT"

  # stage gate: the focused tunnel evaluation, then a per-route completion check.
  # ...and the same TIME BUDGET (--steps = EPS seconds at 100 Hz).  The delivered 2.00 m tunnel
  # route needs 22-40 s at the measured 0.05-0.09 m/s crouch, so the chain's fixed 2200 steps
  # (22 s) cannot even cover it; scoring a 50 s stage with a 22 s rollout is another way to make
  # the gate unpassable.  Found 2026-09-13.
  #
  # The eval MUST use the SAME goal the stage trained with.  The first version forced
  # RM_TUNNEL_GOAL_X=0 (= the delivered 2.30 m), so the crawl stage -- trained against a 0.45 m
  # goal -- was scored on a route 5x longer than the one it learned, i.e. the gate could never
  # pass no matter how well the skill worked (at the measured 0.05-0.09 m/s crawl, 2.3 m needs
  # 26-46 s inside a 20 s episode).  Found 2026-09-13 before the course was ever run.
  RM_ROUTE_KINDS=tunnel_cross RM_TUNNEL_GOAL_X="$GOAL" RM_ROUGH_SPEED_MAX=0 RM_ROUTE_WEIGHTS= \
    OMNI_KIT_ACCEPT_EULA=YES RM_MOD4_MAP=rmuc2026 RM_MOD4_TERRAIN=field RM_DR_OFF=1 \
    /home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python isaac/mod4/eval_terrain_mod4.py \
      --headless --checkpoint "$CKPT" --num_envs 64 --steps $((EPS * 100)) --seed 20260912 \
      --report "$OUT/${NAME}_eval.json" >>"$LOG" 2>&1 || true
  python3 - "$OUT/${NAME}_eval.json" "$GATE" <<'PY' | tee -a "$LOG"
import json, sys
try:
    d = json.load(open(sys.argv[1], encoding="utf8"))
except Exception as exc:
    print("[course] gate %s: NO REPORT (%s) -> do not advance" % (sys.argv[2], exc)); raise SystemExit(1)
b = (d.get("route_kinds") or {}).get("tunnel_cross") or {}
envs = max(1, int(b.get("envs", 1)))
comp = float(b.get("complete_rate", 0.0))
under = float(b.get("underpass_seen", 0)) / envs
roof = int(b.get("fail/tunnel_roof_hit", 0))
print("[course] gate %s: complete=%.3f underpass=%.3f roof_hit=%d envs=%d"
      % (sys.argv[2], comp, under, roof, envs))
# the package's bar is >=0.80 per route over >=100 episodes; at 64 envs that is unattainable, so
# this gate reports the number and refuses to ADVANCE while complete < 0.60 (the v3 bar).
raise SystemExit(0 if comp >= 0.60 else 1)
PY
  if [ "$?" -ne 0 ]; then
    echo "[course] $NAME gate NOT met -- stopping here (fix this stage before advancing)"; exit 4
  fi
done
echo "[course] all requested stages finished; final checkpoint = $CKPT"
echo "[course] reports in $OUT"
