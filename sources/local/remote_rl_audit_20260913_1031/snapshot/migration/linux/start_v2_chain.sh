#!/usr/bin/env bash
# v2 launch: turn the six requested changes ON in ONE place, and prove the knob names are real.
#
# Why a launcher instead of a long command line
# --------------------------------------------
# The v2 change set spans 13 patches and ~15 environment knobs.  A typo in a knob name is SILENT:
# `os.environ.get("RM_TYPO", default)` just returns the default and the run looks normal while the
# change is off.  This session found four such traps in the existing tree (RM_MOD4_USD directory vs
# file, check_run_version's hardcoded asset path, onnx_play.py's Windows contract path, and
# RM_TUNNEL_LEAD_M's two meanings).  So this script VERIFIES every knob it exports against the
# patched sources before launching, and refuses to start if one is not actually read.
#
# It also refuses to start while any training is alive (one task at a time), and it does not edit
# anything: the patches are expected to be applied already (docs section 9.1).
#
#   CKPT=logs/isaac_mod4/<run>/model_<N>.pt bash migration/linux/start_v2_chain.sh
#   ... FROM=fly ITERS=200 ENVS=1024
set -uo pipefail
cd "$(dirname "$0")/../.."
# Isaac Sim dies at the interactive EULA prompt without this (measured 2026-09-13: the first
# v2 smoke died with "Unable to bootstrap inner kit kernel: EOF when reading a line", because
# a comment in start_mod4_stage_fixedplant.sh silently dropped its own copy of this variable).
export OMNI_KIT_ACCEPT_EULA=YES

CKPT=${CKPT:-}
FROM=${FROM:-tunnel}          # INHERITED SKIP, NOT RE-VERIFIED.  The previous chain was itself
                              # started with from_phase=tunnel ("[v3] skip phase smoke (resuming at
                              # tunnel)"), so the smoke gate has NOT been exercised on the rolling
                              # plant.  The reason to skip was a PROBE measurement (0.002035 m, over
                              # the strict <0.002 gate), while the EVALUATIONS measure only
                              # 0.00056-0.00085 m against a 0.002 termination threshold.  Before
                              # trusting the skip, run `SMOKE=1 PHASES="smoke" bash
                              # migration/linux/run_special_phases_v3.sh <ckpt> smoke 1` once
                              # (about a minute of GPU) and set FROM=smoke if it passes.
ITERS=${ITERS:-400}
ENVS=${ENVS:-1024}            # build_layout caps at 1024 (measured); 1024 costs ~the same per
                              # iteration as 512 (9.02 vs 9.00 s) -- see docs section 6.2
DRY=${DRY:-0}

# ---------------------------------------------------------------- the v2 configuration, one place
# item 1: actor obs loses base_lin_vel -> 5-frame history + latent encoder; critic keeps privilege
export RM_SEQ_ENCODER=1 RM_SEQ_HISTORY=5 RM_SEQ_LATENT=3 RM_SEQ_ENCODER_HIDDEN=128,64
export RM_PARTIAL_WARMSTART=1        # required: the encoder makes strict warm-start impossible
# item 2: DR on.  Audit section 30 measured that the DR stack is WIDER than the checklist implies
# -- seven perturbation families, not three -- and that a DR-OFF-trained checkpoint collapses under
# it (slope_spin 0.75 -> 0.25, step_up 0.75 -> 0.06; both far under their 0.60 bars).  That is
# expected for a checkpoint that never trained with DR, but it means the intensity is worth choosing
# deliberately.  The full surface, with the values this launcher uses:
#   RM_EFFORT_LEG_MIN/MAX    0.75/1.25   torque limit   (checklist: "+-10%"; the default is wider)
#   RM_EFFORT_WHEEL_MIN/MAX  0.90/1.10
#   RM_EFFORT_NOISE(_WHEEL)  0.03/0.02   torque noise
#   RM_STIFFNESS_MIN/MAX     0.9/1.1     joint Kp/Kd    <- checklist item 2's "+-10%" (was frozen)
#   RM_ARMATURE_MIN/MAX      0.7/1.6     rotor inertia  <- WIDEST in the stack (was frozen)
#   RM_OBS_DELAY_MIN/MAX_LAG 1/2 steps   observation delay 10-20 ms  <- NOT in the checklist
#   RM_ACTION_DELAY_MS_MIN/MAX 0/5 ms    action delay (ms mode supersedes the control-step queue)
#   RM_LEG/WHEEL_FRICTION_MAX 0.10/0.02  |  RM_ENCODER_BIAS 0.015 rad
export RM_DR_OFF=0
# audit 46: the dog-hole route is 2.00 m and the crouch does 0.05-0.09 m/s, so the default
# 20 s episode caps the travel at 1.80 m -- tunnel_cross could never complete.  Raise the
# episode AND the eval window TOGETHER (a wider episode alone is truncated by the eval's
# --steps).
export RM_EPISODE_S=${RM_EPISODE_S:-45}
export RM_EVAL_STEPS=${RM_EVAL_STEPS:-4500}
if [ "${V2_MILD_DR:-0}" = "1" ]; then
  # One-switch conservative start: tighten the two widest components and halve the observation lag.
  # Raise them back once the gates hold -- this is a starting point, not a destination.
  export RM_ARMATURE_MIN=0.85 RM_ARMATURE_MAX=1.25
  export RM_OBS_DELAY_MAX_LAG=1
  echo "[v2] MILD DR preset: armature 0.85-1.25, obs delay <=1 step (10 ms)"
fi
export RM_ARMATURE_MIN=${RM_ARMATURE_MIN:-0.7} RM_ARMATURE_MAX=${RM_ARMATURE_MAX:-1.6}
export RM_STIFFNESS_MIN=${RM_STIFFNESS_MIN:-0.9} RM_STIFFNESS_MAX=${RM_STIFFNESS_MAX:-1.1}
export RM_OBS_DELAY_MIN_LAG=${RM_OBS_DELAY_MIN_LAG:-1} RM_OBS_DELAY_MAX_LAG=${RM_OBS_DELAY_MAX_LAG:-2}
export RM_ACTION_DELAY_MS_MIN=0 RM_ACTION_DELAY_MS_MAX=5.0
# item 3: per-term reward clip, reference-faithful tracking sigma (sigma 0.25 => std 0.5)
export RM_REWARD_CLIP=2.5 RM_REWARD_CLIP_MODE=safe RM_TRACK_SIGMA=0.5
# item 4 (path B): windowed route-difficulty curriculum.
# ✅ FIXED 2026-09-13 (audit §38): the curriculum used to kill the run at the first WINDOW CLOSE
#    (12 iterations x 24 steps = 288 ~= RM_CURR_WINDOW_STEPS 300) with a CUDA device-side assert,
#    because it did CUDA work (tensor build / clone / sync) inside events.  It now scales the route
#    controller's SPEED TABLE host-side once per window -- the same mechanism the proven
#    RM_ROUGH_SPEED_MAX uses -- so there is no per-step work at all.  VERIFIED: 40/60 iterations,
#    zero errors, all 10 Curriculum/route_curriculum/level_* metrics published.
# (History, kept for the next person:)
# ⚠️ 2026-09-13: RM_ROUTE_CURRICULUM=1 makes the run die AT THE FIRST STEP with
#    "CUDA error: device-side assert" in the PhysX contact view (47 asserts, 0 iterations),
#    regardless of env count (64 and 1024 both) and with the correct plant.  Isolated by a
#    single-variable experiment: with RM_ROUTE_CURRICULUM=0 the SAME configuration trains
#    normally (30/30 iterations, no errors).  Vectorising the per-step GPU->CPU sync was
#    necessary but NOT sufficient, so the cause is elsewhere in the curriculum wiring
#    (the CurrTerm or the route_isaac consumer).  DEFAULT OFF until that is fixed --
#    the other five checklist items all work.
export RM_ROUTE_CURRICULUM=${RM_ROUTE_CURRICULUM:-1}   # FIXED 2026-09-13: see below
# RM_CURR_WINDOW_STEPS must be sized against the PHASE, not left at its 4000-step default:
#   --steps_per_env defaults to 24  ->  1 iteration = 24 control steps
#   400 iterations per phase        ->  9600 control steps
#   window 4000                     ->  only 2.4 windows per phase, so the level can move at most
#                                       2 of the 4 steps (4 -> 2) and a route could never be eased
#                                       down to 0.60x inside one phase (it would need 1600
#                                       iterations, i.e. four phases).
# 1000 steps = ~42 iterations per window -> ~9 windows per phase, so easing completes in-phase.
# (Measured 2026-09-13 from --steps_per_env's default and the phase length.)
# The window size and the ENV COUNT are coupled through RM_CURR_MIN_ATTEMPTS (40):
#   attempts per window ~= (envs on that kind) x (window / episode_steps)
#   512 envs, window 1000 -> the low-slot kinds get only ~24 attempts  -> the gate blocks every
#                             window and the curriculum does nothing (measured 2026-09-13)
#   1024 envs, window 1000 -> ~49 attempts -> the gate opens, and 9.6 windows fit in a 400-iteration
#                             phase, so a route can actually be eased 4 -> 0 inside one phase
# So item 4's curriculum REQUIRES item 6's 1024 envs; either one alone leaves it inert.
# Diagnostic: watch Curriculum/route_curriculum/attempts_<kind> -- if it stays under 40 the
# mechanism is blocked (lower RM_CURR_MIN_ATTEMPTS, don't just wait).
export RM_CURR_WINDOW_STEPS=${RM_CURR_WINDOW_STEPS:-1000}
# audit 13: the fly reward must point at the launch platform, not at "off the ground anywhere"
export RM_JUMP_LAUNCH_READY=1 RM_JUMP_LAUNCH_READY_W=2.0
# audit 15: make "crouch and stand still" net-negative instead of +1.00/step
export RM_TUNNEL_CROUCH_MOVE_GATE=1 RM_TUNNEL_CROUCH_VMIN=0.05
export RM_TUNNEL_STALL_VMIN=0.08 RM_TUNNEL_STALL_GAIN=0.5
# and keep the pose term from being farmed at the new kernel width
export RM_CROUCH_POSE_W=0.30

# ------------------------------------------------------------------- verify the knobs are real
KNOBS=$(printf '%s\n' \
  RM_SEQ_ENCODER RM_SEQ_HISTORY RM_SEQ_LATENT RM_SEQ_ENCODER_HIDDEN RM_PARTIAL_WARMSTART \
  RM_DR_OFF RM_ACTION_DELAY_MS_MIN RM_ACTION_DELAY_MS_MAX \
  RM_REWARD_CLIP RM_REWARD_CLIP_MODE RM_TRACK_SIGMA RM_ROUTE_CURRICULUM \
  RM_JUMP_LAUNCH_READY RM_JUMP_LAUNCH_READY_W \
  RM_ARMATURE_MIN RM_ARMATURE_MAX RM_STIFFNESS_MIN RM_STIFFNESS_MAX \
  RM_OBS_DELAY_MIN_LAG RM_OBS_DELAY_MAX_LAG \
  RM_TUNNEL_CROUCH_MOVE_GATE RM_TUNNEL_CROUCH_VMIN RM_TUNNEL_STALL_VMIN RM_TUNNEL_STALL_GAIN \
  RM_CROUCH_POSE_W)
MISSING=""
for K in $KNOBS; do
  # a knob is "real" only if some module reads it through os.environ
  # match the quoted literal ANYWHERE (helper-mediated reads such as `_f("RM_X", d)` are invisible
  # to an `environ.get("RM_X"` pattern -- measured 2026-09-13: 32 of 112 knobs are read that way)
  if ! grep -rqE "[\"']$K[\"']" isaac/mod4/ 2>/dev/null; then
    MISSING="$MISSING $K"
  fi
done
if [ -n "$MISSING" ]; then
  echo "[v2] REFUSING: these knobs are not read by any module -- a typo here would be silent:" >&2
  echo "[v2]  $MISSING" >&2
  echo "[v2] (apply the patches in docs section 9.1 first; this script does not patch anything)" >&2
  exit 4
fi
echo "[v2] verified: all $(printf '%s\n' $KNOBS | wc -l) knobs are read by isaac/mod4"

# --------------------------------------------------------------------------- one task at a time
if pgrep -f "[t]rain_mod4_ppo.py" >/dev/null; then
  echo "[v2] REFUSING: a training is already running" >&2; exit 6
fi
[ -n "$CKPT" ] || { echo "[v2] CKPT is not set (warm-start checkpoint)" >&2; exit 3; }
[ -f "$CKPT" ] || { echo "[v2] CKPT does not exist: $CKPT" >&2; exit 3; }

echo "[v2] checkpoint : $CKPT"
echo "[v2] from_phase : $FROM   iters=$ITERS   envs=$ENVS"
echo "[v2] encoders   : history=5 latent=3    clips: mode=$RM_REWARD_CLIP_MODE clip=$RM_REWARD_CLIP"
echo "[v2] DR         : off=$RM_DR_OFF  delay=${RM_ACTION_DELAY_MS_MIN}-${RM_ACTION_DELAY_MS_MAX} ms"
if [ "$DRY" = "1" ]; then
  echo "[v2] DRY=1 -- configuration verified, not launching"
  exit 0
fi
exec env ENVS="$ENVS" bash migration/linux/run_special_phases_v3.sh "$CKPT" "$FROM" "$ITERS"
