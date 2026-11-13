# Forward crouch, push, aerial tuck, landing

This is a new finite controller experiment requested by the human on 2026-11-13.
It starts during forward motion. It is separate from recovering an already blocked
wheel. No PPO or deployment change is authorized by this experiment.

The approved HW300N60 R3 plant, frozen teacher 715c40b6 and parent db6e9ccf,
35/6 interface, continuous joint-target clamp, voltage/torque-speed envelopes,
2.5ms physics, 100Hz legs, 400Hz wheels and 50Hz policy are retained. The new
episode closure reset is 10mm as required by the current repository's explicit
2026-11-01 human rule. The completed previous 2mm experiment is immutable.
Per-axis 40deg/0.2s and chassis/nonexempt-guide contact guards are unchanged.
No velocity injection, external forces, mechanical limits or robot assets change.
Only the new flat trial removes the stairs. The stair trial is the same two
200mm steps with original horizontal geometry.

A frozen policy supplies balance and wheel commands. A symmetric leg-difference
overlay commands measured forward approach, finite crouch, full allowed target
extension, contact-detected flight extension, aerial retraction, descending
landing extension and a 0.3s return to the unchanged policy. The policy's joint
pair means are retained. Targets remain inside original delta bounds. No artificial
airborne transition is accepted when ground contact remains.

Airborne evidence requires all external contact force norms summing to <1N for
at least20ms after the push and measured upward whole-robot COM speed >0.10m/s
near takeoff. Wheel lift while any part remains supported does not qualify.
Raw400Hz forces, COM/root, pose, joints, motor torques and closure are saved.
Contact geometry is from the beginning of each physics step and integrated
qpos/qvel are from its end, matching the original player without mj_forward.

The first7 pilot trajectories and their original strict reader outputs are retained.
That reader required paired-wheel force >5N on every2.5ms sample for0.5s. Even
normal rolling baseline has intermittent micro gaps. A separately identified
rolling criterion is therefore added, without altering raw or original results:
one0.5s window after landing, each wheel force >5N on >=80% of samples, no total
unsupported gap >=20ms, pitch/roll <15deg throughout, root height span <=30mm,
|root vertical speed| <=0.30m/s, and no chassis or guide force >=1N. Both raw
strict and rolling outcomes are reported. The200mm stair criterion additionally
requires wheel centers20mm past the edge, wheels near correct tread height and
the support duty specifically from that tread. Two-step success is separate.

First run a finite6-configuration pilot plus unchanged baseline. Then compare8
bounded deeper/tuck/height variants plus baseline for both frozen models. Select
successful moving-flat configurations by actual air/landing, check varied initial
states and200mm stair approaches separately. No new training budget is consumed.

Host72 workspace: /home/lc01/Zonglin Li/zonglin2/tasks/MOD4V3_MOVING_CROUCH_JUMP_20261113_R1
Do not change host210 training or the user's existing viewer. Preserve all failures,
invalid launches, reports and source revisions with Git and actual artifact hashes.
