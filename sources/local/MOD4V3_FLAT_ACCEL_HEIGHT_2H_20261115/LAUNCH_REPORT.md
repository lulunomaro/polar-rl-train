# Flat acceleration, level chassis and spring-assisted jump height

Phase: launch. Start: 2026-11-15T03:56:32.022211+08:00. Absolute deadline: 2026-11-15T05:56:32.022211+08:00.
One original7200s window, Host72 GPU0,2048 environments, one PPO owner. GPU1 evaluates
fixed256-case checkpoints. Initial admission and baseline precede the window;
repair and repaired-profile admission/baseline count inside the original window.
No consumed training window is replayed. Full checkpoints every300 seconds.

## Parent and behavior

Parent: /home/lc01/Zonglin Li/zonglin2/tasks/MOD4V3_FORWARD_JUMP_HEIGHT_2H_20261114_R1/train7200/model_040m.pt
SHA256: 43fbc78c7647ffe6dc108fd4b60dd1d986c30639ec0c59f5ac2707879621bae8; iteration 27382.
Old fixed evidence: H40 nominal51/51 recovered, median wheel rim30.93cm, body rise25.06cm;
fullDR117/205. Repaired85 is the robustness reference with172/205 fullDR recoveries.
These old numbers use the old profile. The following baseline uses the new profile.
Actor, critic, STD and Adam are restored without parameter transformations.

- fullDR: {"episodes": 205, "requested": 165, "takeoff": 143, "landed": 132, "sequence_complete": 32, "success": 0, "failed": 96, "prep_skipped": 158, "median_rim_m": 0.14605937898159027, "median_body_rise_m": 0.1856653392314911, "recovered_median_rim_m": 0.16792692244052887, "median_flight_quality": 0.4271087348461151, "max_air_pitch_deg": 14.08412839877497, "max_air_roll_deg": 6.351650748836025, "max_air_pitch_roll_rate_rad_s": 7.28366756439209, "median_estimated_spring_release_J": 22.299549102783203}
- nominal: {"episodes": 51, "requested": 51, "takeoff": 51, "landed": 51, "sequence_complete": 48, "success": 0, "failed": 0, "prep_skipped": 51, "median_rim_m": 0.2073194682598114, "median_body_rise_m": 0.1943386197090149, "recovered_median_rim_m": 0.20758682489395142, "median_flight_quality": 0.6121126413345337, "max_air_pitch_deg": 7.713275426861101, "max_air_roll_deg": 2.5152077703470868, "max_air_pitch_roll_rate_rad_s": 2.646928310394287, "median_estimated_spring_release_J": 22.13735580444336}

## Objective and physical mechanism

Level chassis and height are the main objectives. Height is measured separately as
the lower wheel rim above the ground and chassis rise from the request height.
Only the first flight collects height.20pct is incremental;80pct is paid after
stable recovery and multiplied by mean flight attitude/angular-rate quality.
The recovery gate requires maximum flight pitch<=10deg, roll<=5deg, airborne>=.16s,
both-wheel support duty>=80pct, and0.5s stable moving landing.35cm rim/25cm chassis rise
is the high-jump reporting threshold, not a cap on the continuous height reward.

Spring compression is upper physical travel stop minus actual slide coordinate.
The out-of-travel drive reference is not interpreted as available stroke.
Requests skip preparation if chassis<=.275m or both springs are compressed>=30mm.
Otherwise preparation ends on measured readiness or after.32s. Three approach height
commands(.26,.30,.36m) exercise low/preloaded and ordinary approach states.
No reward is paid for crouching or repeated takeoff events. A bounded<=2-point
spring potential-release bonus is paid once after recovered flight; it is an
energy-release estimate, not a claim of exact net mechanical work.

Original plant, motors, spring stiffness/damping and limits remain the physical
source of takeoff. No jump impulse or external scripted lift is applied.
FullDR and20pct nominal mixture remain. Physics2.5ms/TGS32/4, legs100Hz,
wheels400Hz, policy50Hz,35/78/6 interface, closure10mm and mimic.01rad per-episode reset.

## Validation and retained failures

CPU:9 accounting/preload regressions passed. Native admission:2048 environments,
2048 complete episodes, console/clock/motor checks passed.
Already-low/preloaded immediate-push cases:1741.
First update changes:{"actor": true, "critic": true, "STD": true, "Adam": true}.
R1 admission and baseline failed at the first spring calculation due to a CPU/CUDA
parameter mismatch; neither performed optimization. Original source, ERROR and
SAFE_CLOSED evidence are retained. R2 moves only immutable spring query tensors
to the environment device. R2's command-relative upper speed gate incorrectly erased
height rewards for physically stable forward launches. It was replaced in R3 by a
soft command-speed penalty with the existing2m/s task limit. The R2 segment was
saved at an update boundary, and R3 retains the original absolute deadline.
Source revisions and individual attempt IDs are preserved.

## Player and remaining work

Existing MuJoCo WASD plus one-shot Space player and single visible terrain tile are
preserved. New weights require the spring-aware phase producer and a qualified
MuJoCo replay before promotion; no new model is silently deployed to the old player.
Ongoing results:LAUNCH_SUMMARY.json. Training reward is not treated as measured height.
Reports generated later are collected and appended by the task's finalizer.
