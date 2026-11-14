# Stable chassis and jump height: bounded-exploration repair

Phase:launch. Start:2026-11-15T06:10:47.303661+08:00. Absolute deadline:2026-11-15T08:10:47.303661+08:00.
This is a fresh authorized7200s window after the previous failed run closed.
Host72 only; GPU0 training2048 environments, GPU1 independent fixed256-case evaluations.
Every300s the owner atomically saves full actor/critic/STD/Adam/RNG state. No automatic extension.

## Evidence for repair

Previous task: MOD4V3_FLAT_ACCEL_HEIGHT_2H_20261115_R1.
Final SHA:3d25b60c9925e4bdf19d4863a6c370eed715d9c224db22074e405d5e4e433204.
Final nominal evaluation:2/51 takeoffs,0 landings,0 recovered jumps; all51 failed.
Training had zero settled height events throughout645 updates. Exploration STD grew
from legs.159-.210/wheels.466-.529 to legs.823-.878/wheels1.182-1.256 by110min.
The old positive entropy bonus and unconstrained STD accompanied this growth.
All23 completed checkpoint evaluations scored below the unchanged H40 parent.
The old source, weights and failures were retained and its final trial was archived.
See evidence/DIAGNOSIS.json for exact checkpoint measurements and indexed prior reports.

## Exact repair

Restore the original H40 parent:/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V3_FORWARD_JUMP_HEIGHT_2H_20261114_R1/train7200/model_040m.pt
SHA256:43fbc78c7647ffe6dc108fd4b60dd1d986c30639ec0c59f5ac2707879621bae8; iteration27382.
Verify full PPO restore first, then retain the actor MLP exactly. Set exploration STD
to legs.035/wheels.08; bound it after every update to legs[.015,.06], wheels[.03,.15].
Clear Adam state for the changed STD and reset value output head only; retain critic
hidden layers and all remaining optimizer state. Remove entropy reward, use learning
rate3e-5, PPO clip.1 and3 learning epochs. Plant, motors and spring mechanics unchanged.

Unlike the preceding deterministic-only admission, this admission samples the same
bounded stochastic policy used for training. It must produce nominal recovered jumps
in at least25pct of cases and fullDR recoveries in at least1pct before any optimization.
Measured admission:{"passed": true, "optimizer_updates": 0, "source_archive_sha256": "8707e1fdc4d5d6fd5333e1afa7e19858a801234ed5690d3217465980e4d8bb1b", "complete_episodes": 2048, "plant_and_motor_limits_verified": true, "clocks_verified": true, "flat_ground": true, "one_flight_accounting_verified": true, "already_low_skip_cases": 1708, "interface": [35, 78, 6], "observation_schema": "MOD4V3_MOVING_JUMP_PHASE_OBS_V1", "num_envs": 2048, "physics_console_checked": true, "stochastic_rollout": true, "nominal_recovered": 333, "fullDR_recovered": 234, "exploration_STD": [0.03500000014901161, 0.03500000014901161, 0.03500000014901161, 0.03500000014901161, 0.07999999821186066, 0.07999999821186066], "note": "Runtime admission; task success is reported separately"}
First update:{"actor": true, "critic": true, "STD": true, "STD_in_bounds": true, "Adam": true}
CPU checks:11 passed.

## Retained task and comparison

Level chassis and height remain the main objectives. Lower wheel-rim clearance and
chassis rise are recorded separately. Only the first flight earns height;20pct is
incremental,80pct is settled after0.5s stable recovery and multiplied by mean flight
attitude/angular-rate quality. Flight maxima must be pitch<=10deg, roll<=5deg;
airborne>=.16s, both-wheel support duty>=80pct. High-jump reporting:rim>=.35m and
chassis rise>=.25m; continuous height reward is uncapped.

Already-low chassis(<=.275m) or both springs compressed>=30mm skips extra crouching.
Otherwise preparation ends on readiness or after.32s. Compression itself has no reward.
Actual spring stroke is upper travel stop minus slide coordinate. A<=2-point spring
potential-release bonus is paid only on stable completion; it is not exact net work.
All six motor actions are learned. No added jump impulse or scripted leg-angle target.
Physics2.5ms/TGS32/4; legs100Hz, wheels400Hz, policy50Hz; actor35/critic78/action6;
closure10mm and mimic.01rad per-episode reset. FullDR ranges and20pct nominal mixture retained.

Fixed deterministic parent baseline:{"fullDR": {"episodes": 205, "requested": 165, "takeoff": 143, "landed": 132, "sequence_complete": 32, "success": 0, "failed": 96, "prep_skipped": 158, "median_rim_m": 0.14605937898159027, "median_body_rise_m": 0.1856653392314911, "recovered_median_rim_m": 0.16792692244052887, "median_flight_quality": 0.4271087348461151, "max_air_pitch_deg": 14.08412839877497, "max_air_roll_deg": 6.351650748836025, "max_air_pitch_roll_rate_rad_s": 7.28366756439209, "median_estimated_spring_release_J": 22.299549102783203}, "nominal": {"episodes": 51, "requested": 51, "takeoff": 51, "landed": 51, "sequence_complete": 48, "success": 0, "failed": 0, "prep_skipped": 51, "median_rim_m": 0.2073194682598114, "median_body_rise_m": 0.1943386197090149, "recovered_median_rim_m": 0.20758682489395142, "median_flight_quality": 0.6121126413345337, "max_air_pitch_deg": 7.713275426861101, "max_air_roll_deg": 2.5152077703470868, "max_air_pitch_roll_rate_rad_s": 2.646928310394287, "median_estimated_spring_release_J": 22.13735580444336}}
Parent recovered-level-height score:0.03885056m.
Evaluation score averages recovered first-flight rim height times flight quality over
all256 cases; unsuccessful cases contribute zero. Training reward alone is not height.
The supervisor records every evaluation; two consecutive severe regressions trigger
a full-state save/close request without changing the original deadline.

Existing MuJoCo WASD and one-shot Space player with one visible tile is preserved.
New weights are not promoted before a compatible state-aware producer and MuJoCo replay.
End-of-run reports are collected and appended by the local finalizer.

## First checkpoint review

{
  "attempt_id": "stable-height-repair-first5min-review-01",
  "epoch": 1794694749.7971652,
  "checkpoint_sha256": "843cc8d9339fd0f1ec94d5e8ea317e07409823ff4ef0c8859d2683a0f21259c7",
  "checkpoint_job": "eval_train7200_model_005m",
  "parent_sha256": "43fbc78c7647ffe6dc108fd4b60dd1d986c30639ec0c59f5ac2707879621bae8",
  "parent_summary": {
    "fullDR": {
      "episodes": 205,
      "requested": 165,
      "takeoff": 143,
      "landed": 132,
      "sequence_complete": 32,
      "success": 0,
      "failed": 96,
      "prep_skipped": 158,
      "median_rim_m": 0.14605937898159027,
      "median_body_rise_m": 0.1856653392314911,
      "recovered_median_rim_m": 0.16792692244052887,
      "median_flight_quality": 0.4271087348461151,
      "max_air_pitch_deg": 14.08412839877497,
      "max_air_roll_deg": 6.351650748836025,
      "max_air_pitch_roll_rate_rad_s": 7.28366756439209,
      "median_estimated_spring_release_J": 22.299549102783203
    },
    "nominal": {
      "episodes": 51,
      "requested": 51,
      "takeoff": 51,
      "landed": 51,
      "sequence_complete": 48,
      "success": 0,
      "failed": 0,
      "prep_skipped": 51,
      "median_rim_m": 0.2073194682598114,
      "median_body_rise_m": 0.1943386197090149,
      "recovered_median_rim_m": 0.20758682489395142,
      "median_flight_quality": 0.6121126413345337,
      "max_air_pitch_deg": 7.713275426861101,
      "max_air_roll_deg": 2.5152077703470868,
      "max_air_pitch_roll_rate_rad_s": 2.646928310394287,
      "median_estimated_spring_release_J": 22.13735580444336
    }
  },
  "candidate_groups": {
    "fullDR": {
      "cases": 205,
      "takeoff": 151,
      "landed": 148,
      "recovered": 31,
      "high_jump": 0,
      "median_rim_m": 0.15286555886268616,
      "recovered_median_rim_m": 0.16705672442913055,
      "recovered_median_pitch_deg": 5.518897436641969,
      "recovered_median_roll_deg": 1.7771941978612789,
      "failed": 70,
      "terminal_gate_counts": {
        "no_request": 32,
        "motion_invalid": 0,
        "flight_pitch_over10deg": 16,
        "flight_roll_over5deg": 9,
        "overspeed": 58,
        "boundary": 3,
        "push_timeout": 8
      }
    },
    "nominal": {
      "cases": 51,
      "takeoff": 51,
      "landed": 51,
      "recovered": 49,
      "high_jump": 0,
      "median_rim_m": 0.20395994186401367,
      "recovered_median_rim_m": 0.20406067371368408,
      "recovered_median_pitch_deg": 5.025120863426944,
      "recovered_median_roll_deg": 1.2914340255760282,
      "failed": 0,
      "terminal_gate_counts": {
        "no_request": 0,
        "motion_invalid": 0,
        "flight_pitch_over10deg": 0,
        "flight_roll_over5deg": 1,
        "overspeed": 0,
        "boundary": 0,
        "push_timeout": 0
      }
    }
  },
  "parent_score_m": 0.03885056203157258,
  "candidate_score_m": 0.03844655615305541,
  "score_ratio_to_parent": 0.9896010287267182,
  "training_updates": 51,
  "training_recovered_counts": [
    1912,
    2107
  ],
  "exploration_STD": [
    0.03542514145374298,
    0.03603914752602577,
    0.03492880240082741,
    0.03579877316951752,
    0.08080895245075226,
    0.08080121874809265
  ],
  "recovered_events_exist": true,
  "policy_promoted_to_player": false,
  "interpretation": "Fixed independent first5min comparison, not a claim of the final two-hour result; gate counts overlap"
}
