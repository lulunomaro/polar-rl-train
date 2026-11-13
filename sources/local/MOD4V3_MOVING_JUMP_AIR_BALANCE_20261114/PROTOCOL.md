# Airborne balance during the moving jump

Human steering on2026-11-14: constrain balance while airborne. This new independent
version follows the completed133-case moving crouch/push/tuck/land experiment.
The old trial and raw data remain immutable. No new training or deployment change.

Use the original approved R3 plant and frozen teacher/parent. Keep35/6, original
motor envelopes, action clip6, continuous delta bounds,2.5ms/100Hz legs/400Hz wheels/
50Hz policy,10mm per-episode closure reset and original contact/orientation guards.
Enter airborne control only after the existing20ms unsupported confirmation.

The airborne objective is pitch within10deg and roll within5deg, with reduced
angular velocity, while preserving actual flight, tuck clearance and landing.
This is measured feedback through existing motor servos, never a frozen quaternion,
disabled gravity, added physical constraint or a new reset used to hide failures.

Common wheel reaction torque opposes measured pitch and pitch rate. It is converted
to a velocity target through the existing0.6Nm/(rad/s) wheel servo, then the unchanged
voltage/torque-speed envelope applies. Optional bounded left/right leg-delta feedback
opposes roll/roll rate. A bounded common-leg-angle offset also uses measured pitch
and pitch rate, while retaining the leg difference used for extension/tuck. This
second pilot was added after the wheel-only gain comparison showed limited effect.
Baseline policy and jump sequence are identical otherwise.

First compare8 bounded gain configurations at command0.6 and seed0. Preserve each
actual attempt. Select by physical airborne pitch/roll, actual rim clearance,
airtime, body/guide contact and rolling landing; do not select merely low angle.
Then compare7 bounded leg-feedback variants. Compare the selected controller and baseline at matched0.4/0.6/0.8 commands,
5 initial states and both frozen models. Any stair transfer remains separate.

The existing rolling landing criterion is retained alongside the original strict
continuous-support result. No gains are allowed to alter robot assets or motor
limits. Airborne angle maxima and time inside10deg/5deg are measured from all400Hz
samples in the actual longest continuous airborne interval, including the initial
20ms detection delay. No cherry-picked later subinterval.

After reviewing the measured whole trajectory, compare4 actual landing handoff
probes: instantaneous versus0.30s fading of the final common-leg offset, both models
at0.6 and seed0. Then verify the selected fadeout at30 initial conditions, reusing
the existing30 unchanged baseline conditions. Preserve the original30 instant-exit
cases. Report the postlanding1s maximum separately from the airborne bounds.

Final observed decision: reject the fadeout after20/30 rolling recovery and10 tile
boundary resets. Restore the byte-identical validated direct-exit controller,
whose30 matched cases all passed airborne10deg/5deg and rolling recovery. Preserve
the failed fadeout source, reports and30 cases. Its directory's historical name
air_final_* does not imply selection. Landing pitch rebound remains an explicit
limitation of the selected controller; do not claim the airborne bound after landing.

All sources, gains, results, failed configurations, reports and rawSHA indexes
must enter the normal Git trial workflow. Host72 root is
/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V3_MOVING_JUMP_AIR_BALANCE_20261114_R1.
