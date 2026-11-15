# Stable chassis and jump height: bounded-exploration repair

Phase:final. Start:2026-11-15T06:10:47.303661+08:00. Absolute deadline:2026-11-15T08:10:47.303661+08:00.
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

## Final evidence

{
  "phase": "final",
  "collected_at": "2026-11-15T08:15:11.096210+08:00",
  "start": "2026-11-15T06:10:47.303661+08:00",
  "deadline": "2026-11-15T08:10:47.303661+08:00",
  "fresh_authorized_seconds": 7200,
  "training_job": "train7200",
  "parent": "/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V3_FORWARD_JUMP_HEIGHT_2H_20261114_R1/train7200/model_040m.pt",
  "parent_sha256": "43fbc78c7647ffe6dc108fd4b60dd1d986c30639ec0c59f5ac2707879621bae8",
  "source_archive_sha256": "8707e1fdc4d5d6fd5333e1afa7e19858a801234ed5690d3217465980e4d8bb1b",
  "admission": {
    "passed": true,
    "optimizer_updates": 0,
    "source_archive_sha256": "8707e1fdc4d5d6fd5333e1afa7e19858a801234ed5690d3217465980e4d8bb1b",
    "complete_episodes": 2048,
    "plant_and_motor_limits_verified": true,
    "clocks_verified": true,
    "flat_ground": true,
    "one_flight_accounting_verified": true,
    "already_low_skip_cases": 1708,
    "interface": [
      35,
      78,
      6
    ],
    "observation_schema": "MOD4V3_MOVING_JUMP_PHASE_OBS_V1",
    "num_envs": 2048,
    "physics_console_checked": true,
    "stochastic_rollout": true,
    "nominal_recovered": 333,
    "fullDR_recovered": 234,
    "exploration_STD": [
      0.03500000014901161,
      0.03500000014901161,
      0.03500000014901161,
      0.03500000014901161,
      0.07999999821186066,
      0.07999999821186066
    ],
    "note": "Runtime admission; task success is reported separately"
  },
  "baseline": {
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
  "baseline_score_m": 0.03885056203157258,
  "first_update": {
    "actor": true,
    "critic": true,
    "STD": true,
    "STD_in_bounds": true,
    "Adam": true
  },
  "evaluations": [
    {
      "job": "eval_train7200_model_005m",
      "status": "complete",
      "summary": {
        "fullDR": {
          "episodes": 205,
          "requested": 173,
          "takeoff": 151,
          "landed": 148,
          "sequence_complete": 31,
          "success": 0,
          "failed": 70,
          "prep_skipped": 162,
          "median_rim_m": 0.15286555886268616,
          "median_body_rise_m": 0.18986007571220398,
          "recovered_median_rim_m": 0.16705672442913055,
          "median_flight_quality": 0.453322172164917,
          "max_air_pitch_deg": 22.70565932957592,
          "max_air_roll_deg": 7.220373971633484,
          "max_air_pitch_roll_rate_rad_s": 3.6647183895111084,
          "median_estimated_spring_release_J": 22.5725154876709
        },
        "nominal": {
          "episodes": 51,
          "requested": 51,
          "takeoff": 51,
          "landed": 51,
          "sequence_complete": 49,
          "success": 0,
          "failed": 0,
          "prep_skipped": 51,
          "median_rim_m": 0.20395994186401367,
          "median_body_rise_m": 0.1935175657272339,
          "recovered_median_rim_m": 0.20406067371368408,
          "median_flight_quality": 0.617849588394165,
          "max_air_pitch_deg": 8.791823768508644,
          "max_air_roll_deg": 5.996433954444818,
          "max_air_pitch_roll_rate_rad_s": 2.719094753265381,
          "median_estimated_spring_release_J": 21.94892120361328
        }
      },
      "checkpoint_sha256": "843cc8d9339fd0f1ec94d5e8ea317e07409823ff4ef0c8859d2683a0f21259c7",
      "recovered_level_height_score_m": 0.03844655615305541
    },
    {
      "job": "eval_train7200_model_010m",
      "status": "complete",
      "summary": {
        "fullDR": {
          "episodes": 205,
          "requested": 178,
          "takeoff": 156,
          "landed": 150,
          "sequence_complete": 33,
          "success": 0,
          "failed": 65,
          "prep_skipped": 170,
          "median_rim_m": 0.15719175338745117,
          "median_body_rise_m": 0.1903766691684723,
          "recovered_median_rim_m": 0.16763614118099213,
          "median_flight_quality": 0.4688114523887634,
          "max_air_pitch_deg": 18.927424076967476,
          "max_air_roll_deg": 6.173191566201932,
          "max_air_pitch_roll_rate_rad_s": 3.740786075592041,
          "median_estimated_spring_release_J": 22.825944900512695
        },
        "nominal": {
          "episodes": 51,
          "requested": 51,
          "takeoff": 51,
          "landed": 51,
          "sequence_complete": 49,
          "success": 0,
          "failed": 0,
          "prep_skipped": 51,
          "median_rim_m": 0.20200100541114807,
          "median_body_rise_m": 0.19856654107570648,
          "recovered_median_rim_m": 0.2028197944164276,
          "median_flight_quality": 0.6339250206947327,
          "max_air_pitch_deg": 8.189563300706308,
          "max_air_roll_deg": 4.317438560219577,
          "max_air_pitch_roll_rate_rad_s": 2.5987203121185303,
          "median_estimated_spring_release_J": 21.730318069458008
        }
      },
      "checkpoint_sha256": "80353f8d5b7ad4de715f3914e8c660d91cad26e08260e46bbaebe936997d6391",
      "recovered_level_height_score_m": 0.038579912047249545
    },
    {
      "job": "eval_train7200_model_015m",
      "status": "complete",
      "summary": {
        "fullDR": {
          "episodes": 205,
          "requested": 180,
          "takeoff": 156,
          "landed": 148,
          "sequence_complete": 35,
          "success": 0,
          "failed": 75,
          "prep_skipped": 169,
          "median_rim_m": 0.15239544212818146,
          "median_body_rise_m": 0.18713754415512085,
          "recovered_median_rim_m": 0.15975184738636017,
          "median_flight_quality": 0.44954758882522583,
          "max_air_pitch_deg": 20.275209937960458,
          "max_air_roll_deg": 6.52852319314856,
          "max_air_pitch_roll_rate_rad_s": 3.439485788345337,
          "median_estimated_spring_release_J": 22.500381469726562
        },
        "nominal": {
          "episodes": 51,
          "requested": 51,
          "takeoff": 51,
          "landed": 51,
          "sequence_complete": 50,
          "success": 0,
          "failed": 0,
          "prep_skipped": 51,
          "median_rim_m": 0.2037404477596283,
          "median_body_rise_m": 0.19934561848640442,
          "recovered_median_rim_m": 0.20402562618255615,
          "median_flight_quality": 0.607757031917572,
          "max_air_pitch_deg": 8.30532476185427,
          "max_air_roll_deg": 2.9032312439823342,
          "max_air_pitch_roll_rate_rad_s": 2.606029510498047,
          "median_estimated_spring_release_J": 22.01906967163086
        }
      },
      "checkpoint_sha256": "61e62be248e271353ef10520aff8c499613e81352e46962d36fda8e5e2e3a993",
      "recovered_level_height_score_m": 0.04013726476017971
    },
    {
      "job": "eval_train7200_model_020m",
      "status": "complete",
      "summary": {
        "fullDR": {
          "episodes": 205,
          "requested": 185,
          "takeoff": 161,
          "landed": 150,
          "sequence_complete": 29,
          "success": 0,
          "failed": 82,
          "prep_skipped": 174,
          "median_rim_m": 0.1564059555530548,
          "median_body_rise_m": 0.19393771886825562,
          "recovered_median_rim_m": 0.16798509657382965,
          "median_flight_quality": 0.4508237838745117,
          "max_air_pitch_deg": 15.510130171048354,
          "max_air_roll_deg": 7.087003002144761,
          "max_air_pitch_roll_rate_rad_s": 3.4975156784057617,
          "median_estimated_spring_release_J": 23.057571411132812
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
          "median_rim_m": 0.19778236746788025,
          "median_body_rise_m": 0.19830843806266785,
          "recovered_median_rim_m": 0.19909189641475677,
          "median_flight_quality": 0.634677529335022,
          "max_air_pitch_deg": 8.143048004911229,
          "max_air_roll_deg": 3.0405161253088866,
          "max_air_pitch_roll_rate_rad_s": 2.745177984237671,
          "median_estimated_spring_release_J": 21.776578903198242
        }
      },
      "checkpoint_sha256": "2b43b69f9680de99db7887ecc2b8b271992d17606f651fdae57a8a3679145edf",
      "recovered_level_height_score_m": 0.0384278252980324
    },
    {
      "job": "eval_train7200_model_025m",
      "status": "complete",
      "summary": {
        "fullDR": {
          "episodes": 205,
          "requested": 194,
          "takeoff": 160,
          "landed": 152,
          "sequence_complete": 34,
          "success": 0,
          "failed": 78,
          "prep_skipped": 189,
          "median_rim_m": 0.15600723028182983,
          "median_body_rise_m": 0.19477348029613495,
          "recovered_median_rim_m": 0.1800176501274109,
          "median_flight_quality": 0.49972617626190186,
          "max_air_pitch_deg": 16.693146256051243,
          "max_air_roll_deg": 7.224730778550306,
          "max_air_pitch_roll_rate_rad_s": 3.595604658126831,
          "median_estimated_spring_release_J": 23.339330673217773
        },
        "nominal": {
          "episodes": 51,
          "requested": 51,
          "takeoff": 51,
          "landed": 51,
          "sequence_complete": 49,
          "success": 0,
          "failed": 0,
          "prep_skipped": 51,
          "median_rim_m": 0.20107850432395935,
          "median_body_rise_m": 0.1998211145401001,
          "recovered_median_rim_m": 0.2037680447101593,
          "median_flight_quality": 0.6101893782615662,
          "max_air_pitch_deg": 8.902401116076566,
          "max_air_roll_deg": 5.001640380607733,
          "max_air_pitch_roll_rate_rad_s": 2.778378486633301,
          "median_estimated_spring_release_J": 22.603687286376953
        }
      },
      "checkpoint_sha256": "ad19d762d4bba599a0d5b17544e3c58cd5c012b798638e06fd0e522d8807e3fe",
      "recovered_level_height_score_m": 0.04053647513239942
    },
    {
      "job": "eval_train7200_model_030m",
      "status": "complete",
      "summary": {
        "fullDR": {
          "episodes": 205,
          "requested": 195,
          "takeoff": 167,
          "landed": 155,
          "sequence_complete": 24,
          "success": 0,
          "failed": 81,
          "prep_skipped": 183,
          "median_rim_m": 0.15254278481006622,
          "median_body_rise_m": 0.19713658094406128,
          "recovered_median_rim_m": 0.16577988862991333,
          "median_flight_quality": 0.4751940667629242,
          "max_air_pitch_deg": 21.49189714802422,
          "max_air_roll_deg": 7.322192455364511,
          "max_air_pitch_roll_rate_rad_s": 4.616404056549072,
          "median_estimated_spring_release_J": 23.34560775756836
        },
        "nominal": {
          "episodes": 51,
          "requested": 51,
          "takeoff": 51,
          "landed": 51,
          "sequence_complete": 51,
          "success": 0,
          "failed": 0,
          "prep_skipped": 51,
          "median_rim_m": 0.2001534104347229,
          "median_body_rise_m": 0.20130357146263123,
          "recovered_median_rim_m": 0.2001534104347229,
          "median_flight_quality": 0.6273666620254517,
          "max_air_pitch_deg": 9.381492782576062,
          "max_air_roll_deg": 3.6143790144198373,
          "max_air_pitch_roll_rate_rad_s": 2.7779767513275146,
          "median_estimated_spring_release_J": 22.1097469329834
        }
      },
      "checkpoint_sha256": "e27d7d9fb7abaf3b37497b95cb7d34491122c100478a5cc429dd8355f3935ebb",
      "recovered_level_height_score_m": 0.03697239105554208
    },
    {
      "job": "eval_train7200_model_035m",
      "status": "complete",
      "summary": {
        "fullDR": {
          "episodes": 205,
          "requested": 201,
          "takeoff": 168,
          "landed": 160,
          "sequence_complete": 33,
          "success": 0,
          "failed": 79,
          "prep_skipped": 191,
          "median_rim_m": 0.15641668438911438,
          "median_body_rise_m": 0.20016524195671082,
          "recovered_median_rim_m": 0.17162717878818512,
          "median_flight_quality": 0.48846036195755005,
          "max_air_pitch_deg": 16.38535914903025,
          "max_air_roll_deg": 6.465065186230441,
          "max_air_pitch_roll_rate_rad_s": 3.787966251373291,
          "median_estimated_spring_release_J": 24.982027053833008
        },
        "nominal": {
          "episodes": 51,
          "requested": 51,
          "takeoff": 51,
          "landed": 51,
          "sequence_complete": 51,
          "success": 0,
          "failed": 0,
          "prep_skipped": 51,
          "median_rim_m": 0.20183265209197998,
          "median_body_rise_m": 0.2036067247390747,
          "recovered_median_rim_m": 0.20183265209197998,
          "median_flight_quality": 0.626715362071991,
          "max_air_pitch_deg": 9.55070132775302,
          "max_air_roll_deg": 4.271920898930142,
          "max_air_pitch_roll_rate_rad_s": 2.7238919734954834,
          "median_estimated_spring_release_J": 22.563692092895508
        }
      },
      "checkpoint_sha256": "c4780a753666ddff4284f8c8f08f108bbb0d359f2b59dbf1c06612311337f88c",
      "recovered_level_height_score_m": 0.04149840278593904
    },
    {
      "job": "eval_train7200_model_040m",
      "status": "complete",
      "summary": {
        "fullDR": {
          "episodes": 205,
          "requested": 203,
          "takeoff": 173,
          "landed": 165,
          "sequence_complete": 26,
          "success": 0,
          "failed": 87,
          "prep_skipped": 194,
          "median_rim_m": 0.16249404847621918,
          "median_body_rise_m": 0.2008514553308487,
          "recovered_median_rim_m": 0.16448906064033508,
          "median_flight_quality": 0.514273464679718,
          "max_air_pitch_deg": 24.300044047910333,
          "max_air_roll_deg": 6.731094224213267,
          "max_air_pitch_roll_rate_rad_s": 3.7237167358398438,
          "median_estimated_spring_release_J": 24.046207427978516
        },
        "nominal": {
          "episodes": 51,
          "requested": 51,
          "takeoff": 51,
          "landed": 51,
          "sequence_complete": 51,
          "success": 0,
          "failed": 0,
          "prep_skipped": 51,
          "median_rim_m": 0.20043393969535828,
          "median_body_rise_m": 0.2071666270494461,
          "recovered_median_rim_m": 0.20043393969535828,
          "median_flight_quality": 0.6221579909324646,
          "max_air_pitch_deg": 9.77210703234086,
          "max_air_roll_deg": 3.165401011640692,
          "max_air_pitch_roll_rate_rad_s": 2.709815502166748,
          "median_estimated_spring_release_J": 23.81528091430664
        }
      },
      "checkpoint_sha256": "72429f79d5603044f394a90596639f4fab07516d1683b6c1440f93d7c35dc622",
      "recovered_level_height_score_m": 0.038229672187181
    },
    {
      "job": "eval_train7200_model_045m",
      "status": "complete",
      "summary": {
        "fullDR": {
          "episodes": 205,
          "requested": 203,
          "takeoff": 177,
          "landed": 174,
          "sequence_complete": 30,
          "success": 0,
          "failed": 91,
          "prep_skipped": 191,
          "median_rim_m": 0.16052433848381042,
          "median_body_rise_m": 0.20226441323757172,
          "recovered_median_rim_m": 0.1783820241689682,
          "median_flight_quality": 0.511551558971405,
          "max_air_pitch_deg": 17.015855618861423,
          "max_air_roll_deg": 10.170730532681144,
          "max_air_pitch_roll_rate_rad_s": 3.444779396057129,
          "median_estimated_spring_release_J": 24.548131942749023
        },
        "nominal": {
          "episodes": 51,
          "requested": 51,
          "takeoff": 51,
          "landed": 51,
          "sequence_complete": 51,
          "success": 0,
          "failed": 0,
          "prep_skipped": 51,
          "median_rim_m": 0.19896245002746582,
          "median_body_rise_m": 0.20990008115768433,
          "recovered_median_rim_m": 0.19896245002746582,
          "median_flight_quality": 0.6685343384742737,
          "max_air_pitch_deg": 9.528899363922338,
          "max_air_roll_deg": 3.1709601452948477,
          "max_air_pitch_roll_rate_rad_s": 2.8346080780029297,
          "median_estimated_spring_release_J": 25.766939163208008
        }
      },
      "checkpoint_sha256": "d3062755ff7bc16c6bda90c61ec15a4d6fc1ed70d4f9a199428f09cc9a19b74e",
      "recovered_level_height_score_m": 0.041693794689944816
    },
    {
      "job": "eval_train7200_model_050m",
      "status": "complete",
      "summary": {
        "fullDR": {
          "episodes": 205,
          "requested": 203,
          "takeoff": 181,
          "landed": 177,
          "sequence_complete": 23,
          "success": 0,
          "failed": 93,
          "prep_skipped": 193,
          "median_rim_m": 0.1632031351327896,
          "median_body_rise_m": 0.20354275405406952,
          "recovered_median_rim_m": 0.17148873209953308,
          "median_flight_quality": 0.4975156784057617,
          "max_air_pitch_deg": 32.034242905520124,
          "max_air_roll_deg": 7.8341450157345855,
          "max_air_pitch_roll_rate_rad_s": 6.350250720977783,
          "median_estimated_spring_release_J": 25.612693786621094
        },
        "nominal": {
          "episodes": 51,
          "requested": 51,
          "takeoff": 51,
          "landed": 51,
          "sequence_complete": 50,
          "success": 0,
          "failed": 0,
          "prep_skipped": 51,
          "median_rim_m": 0.20006534457206726,
          "median_body_rise_m": 0.21378232538700104,
          "recovered_median_rim_m": 0.2000882625579834,
          "median_flight_quality": 0.636455237865448,
          "max_air_pitch_deg": 9.283167940605498,
          "max_air_roll_deg": 5.1509649644503135,
          "max_air_pitch_roll_rate_rad_s": 2.826784133911133,
          "median_estimated_spring_release_J": 26.211254119873047
        }
      },
      "checkpoint_sha256": "51eb013ba8672c31e093a5575912c0e3b4bbbb3fb6fd1375804d08a825aca567",
      "recovered_level_height_score_m": 0.03716041996716585
    },
    {
      "job": "eval_train7200_model_055m",
      "status": "complete",
      "summary": {
        "fullDR": {
          "episodes": 205,
          "requested": 205,
          "takeoff": 181,
          "landed": 179,
          "sequence_complete": 27,
          "success": 0,
          "failed": 85,
          "prep_skipped": 192,
          "median_rim_m": 0.16159018874168396,
          "median_body_rise_m": 0.20162127912044525,
          "recovered_median_rim_m": 0.17493616044521332,
          "median_flight_quality": 0.5212242007255554,
          "max_air_pitch_deg": 21.834989502865007,
          "max_air_roll_deg": 8.137978296999787,
          "max_air_pitch_roll_rate_rad_s": 3.692020893096924,
          "median_estimated_spring_release_J": 24.789196014404297
        },
        "nominal": {
          "episodes": 51,
          "requested": 51,
          "takeoff": 51,
          "landed": 51,
          "sequence_complete": 51,
          "success": 0,
          "failed": 0,
          "prep_skipped": 51,
          "median_rim_m": 0.20053020119667053,
          "median_body_rise_m": 0.21343764662742615,
          "recovered_median_rim_m": 0.20053020119667053,
          "median_flight_quality": 0.6309561729431152,
          "max_air_pitch_deg": 9.70861188626913,
          "max_air_roll_deg": 2.645244540303786,
          "max_air_pitch_roll_rate_rad_s": 2.8108506202697754,
          "median_estimated_spring_release_J": 23.98859405517578
        }
      },
      "checkpoint_sha256": "e40ea173756868c33e25f79751ecb29d752dab27a042e49ddd8680c9c0e5d886",
      "recovered_level_height_score_m": 0.04033343184156997
    },
    {
      "job": "eval_train7200_model_060m",
      "status": "complete",
      "summary": {
        "fullDR": {
          "episodes": 205,
          "requested": 205,
          "takeoff": 181,
          "landed": 180,
          "sequence_complete": 28,
          "success": 0,
          "failed": 84,
          "prep_skipped": 193,
          "median_rim_m": 0.16232241690158844,
          "median_body_rise_m": 0.20037567615509033,
          "recovered_median_rim_m": 0.16012991219758987,
          "median_flight_quality": 0.5214875340461731,
          "max_air_pitch_deg": 20.268238022365168,
          "max_air_roll_deg": 8.735265533312708,
          "max_air_pitch_roll_rate_rad_s": 3.5250985622406006,
          "median_estimated_spring_release_J": 25.373428344726562
        },
        "nominal": {
          "episodes": 51,
          "requested": 51,
          "takeoff": 51,
          "landed": 51,
          "sequence_complete": 50,
          "success": 0,
          "failed": 0,
          "prep_skipped": 51,
          "median_rim_m": 0.19888216257095337,
          "median_body_rise_m": 0.211861714720726,
          "recovered_median_rim_m": 0.19892102479934692,
          "median_flight_quality": 0.6276059150695801,
          "max_air_pitch_deg": 10.022721187140615,
          "max_air_roll_deg": 2.5195075878730213,
          "max_air_pitch_roll_rate_rad_s": 2.721278667449951,
          "median_estimated_spring_release_J": 26.00717544555664
        }
      },
      "checkpoint_sha256": "fe3ba52088051469117adc32a0288407615b926fc5f27eaac6447ca6fd09ce66",
      "recovered_level_height_score_m": 0.04023466937861339
    },
    {
      "job": "eval_train7200_model_065m",
      "status": "complete",
      "summary": {
        "fullDR": {
          "episodes": 205,
          "requested": 205,
          "takeoff": 180,
          "landed": 180,
          "sequence_complete": 25,
          "success": 0,
          "failed": 87,
          "prep_skipped": 194,
          "median_rim_m": 0.16258679330348969,
          "median_body_rise_m": 0.2001039683818817,
          "recovered_median_rim_m": 0.167871356010437,
          "median_flight_quality": 0.525985836982727,
          "max_air_pitch_deg": 22.362636984174124,
          "max_air_roll_deg": 9.317391457215493,
          "max_air_pitch_roll_rate_rad_s": 3.7244067192077637,
          "median_estimated_spring_release_J": 26.077774047851562
        },
        "nominal": {
          "episodes": 51,
          "requested": 51,
          "takeoff": 51,
          "landed": 51,
          "sequence_complete": 51,
          "success": 0,
          "failed": 0,
          "prep_skipped": 51,
          "median_rim_m": 0.19862118363380432,
          "median_body_rise_m": 0.20662769675254822,
          "recovered_median_rim_m": 0.19862118363380432,
          "median_flight_quality": 0.6402990818023682,
          "max_air_pitch_deg": 9.841811674141779,
          "max_air_roll_deg": 2.4898227319664996,
          "max_air_pitch_roll_rate_rad_s": 2.6898698806762695,
          "median_estimated_spring_release_J": 23.835433959960938
        }
      },
      "checkpoint_sha256": "65483fa719d4e93a75230341c0c33c391883adbee3fae58c366da5acb434049f",
      "recovered_level_height_score_m": 0.03978678425216253
    },
    {
      "job": "eval_train7200_model_070m",
      "status": "complete",
      "summary": {
        "fullDR": {
          "episodes": 205,
          "requested": 205,
          "takeoff": 180,
          "landed": 179,
          "sequence_complete": 29,
          "success": 0,
          "failed": 85,
          "prep_skipped": 193,
          "median_rim_m": 0.1634347289800644,
          "median_body_rise_m": 0.20175538957118988,
          "recovered_median_rim_m": 0.18282566964626312,
          "median_flight_quality": 0.5395042896270752,
          "max_air_pitch_deg": 16.678145453086604,
          "max_air_roll_deg": 8.59774906588461,
          "max_air_pitch_roll_rate_rad_s": 3.559298276901245,
          "median_estimated_spring_release_J": 26.046371459960938
        },
        "nominal": {
          "episodes": 51,
          "requested": 51,
          "takeoff": 51,
          "landed": 51,
          "sequence_complete": 51,
          "success": 0,
          "failed": 0,
          "prep_skipped": 51,
          "median_rim_m": 0.19933027029037476,
          "median_body_rise_m": 0.21123848855495453,
          "recovered_median_rim_m": 0.19933027029037476,
          "median_flight_quality": 0.6445086002349854,
          "max_air_pitch_deg": 9.662916213174451,
          "max_air_roll_deg": 3.222702456795691,
          "max_air_pitch_roll_rate_rad_s": 2.656064510345459,
          "median_estimated_spring_release_J": 23.77362823486328
        }
      },
      "checkpoint_sha256": "1d36b9dbf636f4e81fd5fd55c1d5fa0233c87ab97e401422817d659bbc9c5d33",
      "recovered_level_height_score_m": 0.04198718271531912
    },
    {
      "job": "eval_train7200_model_075m",
      "status": "complete",
      "summary": {
        "fullDR": {
          "episodes": 205,
          "requested": 205,
          "takeoff": 180,
          "landed": 180,
          "sequence_complete": 35,
          "success": 0,
          "failed": 111,
          "prep_skipped": 191,
          "median_rim_m": 0.16594518721103668,
          "median_body_rise_m": 0.2018127143383026,
          "recovered_median_rim_m": 0.17634756863117218,
          "median_flight_quality": 0.5414960980415344,
          "max_air_pitch_deg": 17.97653367845476,
          "max_air_roll_deg": 8.594208466573605,
          "max_air_pitch_roll_rate_rad_s": 3.7756989002227783,
          "median_estimated_spring_release_J": 25.42286491394043
        },
        "nominal": {
          "episodes": 51,
          "requested": 51,
          "takeoff": 51,
          "landed": 51,
          "sequence_complete": 50,
          "success": 0,
          "failed": 0,
          "prep_skipped": 51,
          "median_rim_m": 0.19710302352905273,
          "median_body_rise_m": 0.21359242498874664,
          "recovered_median_rim_m": 0.19728447496891022,
          "median_flight_quality": 0.6739131212234497,
          "max_air_pitch_deg": 9.438314833828692,
          "max_air_roll_deg": 5.465658673382658,
          "max_air_pitch_roll_rate_rad_s": 2.6662471294403076,
          "median_estimated_spring_release_J": 24.512216567993164
        }
      },
      "checkpoint_sha256": "6fdd840455d2abcc29472b846b0672fa9c7481ad272a2e89b2d65d67c791672f",
      "recovered_level_height_score_m": 0.04436008406226476
    },
    {
      "job": "eval_train7200_model_080m",
      "status": "complete",
      "summary": {
        "fullDR": {
          "episodes": 205,
          "requested": 205,
          "takeoff": 180,
          "landed": 180,
          "sequence_complete": 25,
          "success": 0,
          "failed": 95,
          "prep_skipped": 191,
          "median_rim_m": 0.16354861855506897,
          "median_body_rise_m": 0.2003345489501953,
          "recovered_median_rim_m": 0.1610628068447113,
          "median_flight_quality": 0.5162718892097473,
          "max_air_pitch_deg": 20.111309303542246,
          "max_air_roll_deg": 8.49724539356881,
          "max_air_pitch_roll_rate_rad_s": 3.2729437351226807,
          "median_estimated_spring_release_J": 26.004432678222656
        },
        "nominal": {
          "episodes": 51,
          "requested": 51,
          "takeoff": 51,
          "landed": 51,
          "sequence_complete": 51,
          "success": 0,
          "failed": 0,
          "prep_skipped": 51,
          "median_rim_m": 0.19923824071884155,
          "median_body_rise_m": 0.21291834115982056,
          "recovered_median_rim_m": 0.19923824071884155,
          "median_flight_quality": 0.6659408211708069,
          "max_air_pitch_deg": 9.548887058754735,
          "max_air_roll_deg": 3.4248393439612794,
          "max_air_pitch_roll_rate_rad_s": 2.6949169635772705,
          "median_estimated_spring_release_J": 26.244518280029297
        }
      },
      "checkpoint_sha256": "0313415c8090d6345d238294a20122fa3d18a72804ec7c1adaeeb1527e15c3c9",
      "recovered_level_height_score_m": 0.03936196613501393
    },
    {
      "job": "eval_train7200_model_085m",
      "status": "complete",
      "summary": {
        "fullDR": {
          "episodes": 205,
          "requested": 205,
          "takeoff": 184,
          "landed": 183,
          "sequence_complete": 30,
          "success": 0,
          "failed": 94,
          "prep_skipped": 191,
          "median_rim_m": 0.16619090735912323,
          "median_body_rise_m": 0.2002042531967163,
          "recovered_median_rim_m": 0.16904006153345108,
          "median_flight_quality": 0.5427035689353943,
          "max_air_pitch_deg": 18.50014110286982,
          "max_air_roll_deg": 9.779418749847359,
          "max_air_pitch_roll_rate_rad_s": 3.6896309852600098,
          "median_estimated_spring_release_J": 26.058855056762695
        },
        "nominal": {
          "episodes": 51,
          "requested": 51,
          "takeoff": 51,
          "landed": 51,
          "sequence_complete": 51,
          "success": 0,
          "failed": 0,
          "prep_skipped": 51,
          "median_rim_m": 0.19707843661308289,
          "median_body_rise_m": 0.21032001078128815,
          "recovered_median_rim_m": 0.19707843661308289,
          "median_flight_quality": 0.6690828800201416,
          "max_air_pitch_deg": 9.551960643881241,
          "max_air_roll_deg": 2.3161075425978037,
          "max_air_pitch_roll_rate_rad_s": 2.618267059326172,
          "median_estimated_spring_release_J": 24.11985969543457
        }
      },
      "checkpoint_sha256": "e55d7e65abee8d1ddf33738fb95b4fdf08c05bde12610efa261140e7cfa22b40",
      "recovered_level_height_score_m": 0.042839850863998885
    },
    {
      "job": "eval_train7200_model_090m",
      "status": "complete",
      "summary": {
        "fullDR": {
          "episodes": 205,
          "requested": 205,
          "takeoff": 181,
          "landed": 180,
          "sequence_complete": 27,
          "success": 0,
          "failed": 95,
          "prep_skipped": 192,
          "median_rim_m": 0.1663566678762436,
          "median_body_rise_m": 0.2001829445362091,
          "recovered_median_rim_m": 0.18111780285835266,
          "median_flight_quality": 0.5456715822219849,
          "max_air_pitch_deg": 25.876764189503806,
          "max_air_roll_deg": 8.127307833968933,
          "max_air_pitch_roll_rate_rad_s": 3.2044928073883057,
          "median_estimated_spring_release_J": 25.909940719604492
        },
        "nominal": {
          "episodes": 51,
          "requested": 51,
          "takeoff": 51,
          "landed": 51,
          "sequence_complete": 51,
          "success": 0,
          "failed": 0,
          "prep_skipped": 51,
          "median_rim_m": 0.19528251886367798,
          "median_body_rise_m": 0.2134721875190735,
          "recovered_median_rim_m": 0.19528251886367798,
          "median_flight_quality": 0.6781831979751587,
          "max_air_pitch_deg": 9.47723410549307,
          "max_air_roll_deg": 2.2235053319346516,
          "max_air_pitch_roll_rate_rad_s": 2.585266590118408,
          "median_estimated_spring_release_J": 24.25617218017578
        }
      },
      "checkpoint_sha256": "e7d647a580af1fc1d6433dc88e1c35c385f10c1307e4e6b0e1ee0c708de3a253",
      "recovered_level_height_score_m": 0.041063213385900466
    },
    {
      "job": "eval_train7200_model_095m",
      "status": "complete",
      "summary": {
        "fullDR": {
          "episodes": 205,
          "requested": 205,
          "takeoff": 179,
          "landed": 178,
          "sequence_complete": 29,
          "success": 0,
          "failed": 109,
          "prep_skipped": 192,
          "median_rim_m": 0.16521085798740387,
          "median_body_rise_m": 0.20420262217521667,
          "recovered_median_rim_m": 0.16961808502674103,
          "median_flight_quality": 0.539367139339447,
          "max_air_pitch_deg": 20.140216371657033,
          "max_air_roll_deg": 9.649943122619659,
          "max_air_pitch_roll_rate_rad_s": 3.558971881866455,
          "median_estimated_spring_release_J": 26.148244857788086
        },
        "nominal": {
          "episodes": 51,
          "requested": 51,
          "takeoff": 51,
          "landed": 51,
          "sequence_complete": 51,
          "success": 0,
          "failed": 0,
          "prep_skipped": 51,
          "median_rim_m": 0.19647502899169922,
          "median_body_rise_m": 0.21042077243328094,
          "recovered_median_rim_m": 0.19647502899169922,
          "median_flight_quality": 0.6613451242446899,
          "max_air_pitch_deg": 9.586384797298106,
          "max_air_roll_deg": 3.1270123602974587,
          "max_air_pitch_roll_rate_rad_s": 2.6332807540893555,
          "median_estimated_spring_release_J": 23.220394134521484
        }
      },
      "checkpoint_sha256": "696831f78326f575352d2515d946f87329d08908321d4b0658fd9ed589b67886",
      "recovered_level_height_score_m": 0.042175968159929425
    },
    {
      "job": "eval_train7200_model_100m",
      "status": "complete",
      "summary": {
        "fullDR": {
          "episodes": 205,
          "requested": 205,
          "takeoff": 184,
          "landed": 184,
          "sequence_complete": 36,
          "success": 0,
          "failed": 102,
          "prep_skipped": 193,
          "median_rim_m": 0.16560585796833038,
          "median_body_rise_m": 0.20476332306861877,
          "recovered_median_rim_m": 0.1719653308391571,
          "median_flight_quality": 0.5492455363273621,
          "max_air_pitch_deg": 18.66137454841714,
          "max_air_roll_deg": 10.309279212447562,
          "max_air_pitch_roll_rate_rad_s": 4.283921241760254,
          "median_estimated_spring_release_J": 25.985408782958984
        },
        "nominal": {
          "episodes": 51,
          "requested": 51,
          "takeoff": 51,
          "landed": 50,
          "sequence_complete": 50,
          "success": 0,
          "failed": 0,
          "prep_skipped": 51,
          "median_rim_m": 0.1974986493587494,
          "median_body_rise_m": 0.21092891693115234,
          "recovered_median_rim_m": 0.19754180312156677,
          "median_flight_quality": 0.6703210473060608,
          "max_air_pitch_deg": 9.525106047612043,
          "max_air_roll_deg": 3.058419118340548,
          "max_air_pitch_roll_rate_rad_s": 2.584392786026001,
          "median_estimated_spring_release_J": 23.676496505737305
        }
      },
      "checkpoint_sha256": "4b9bfd9a7065652e3e6e514973d4fe9ba0215ee1f9042848d3acb27cfc27cb9d",
      "recovered_level_height_score_m": 0.045850771071230645
    },
    {
      "job": "eval_train7200_model_105m",
      "status": "complete",
      "summary": {
        "fullDR": {
          "episodes": 205,
          "requested": 205,
          "takeoff": 183,
          "landed": 183,
          "sequence_complete": 32,
          "success": 0,
          "failed": 108,
          "prep_skipped": 194,
          "median_rim_m": 0.16454873979091644,
          "median_body_rise_m": 0.20071116089820862,
          "recovered_median_rim_m": 0.18748155236244202,
          "median_flight_quality": 0.5437014102935791,
          "max_air_pitch_deg": 19.752353834354103,
          "max_air_roll_deg": 9.88221309685605,
          "max_air_pitch_roll_rate_rad_s": 3.5911262035369873,
          "median_estimated_spring_release_J": 25.727466583251953
        },
        "nominal": {
          "episodes": 51,
          "requested": 51,
          "takeoff": 51,
          "landed": 51,
          "sequence_complete": 50,
          "success": 0,
          "failed": 0,
          "prep_skipped": 51,
          "median_rim_m": 0.19620752334594727,
          "median_body_rise_m": 0.21021918952465057,
          "recovered_median_rim_m": 0.19695937633514404,
          "median_flight_quality": 0.679908812046051,
          "max_air_pitch_deg": 9.522270665332842,
          "max_air_roll_deg": 6.462793721444588,
          "max_air_pitch_roll_rate_rad_s": 2.6539955139160156,
          "median_estimated_spring_release_J": 23.82953643798828
        }
      },
      "checkpoint_sha256": "fbd970bd442390d9b6074c25bf36ecafbfc03163b622eb57edbfb9064f473f5d",
      "recovered_level_height_score_m": 0.04400888524818008
    },
    {
      "job": "eval_train7200_model_110m",
      "status": "complete",
      "summary": {
        "fullDR": {
          "episodes": 205,
          "requested": 205,
          "takeoff": 185,
          "landed": 183,
          "sequence_complete": 24,
          "success": 0,
          "failed": 118,
          "prep_skipped": 193,
          "median_rim_m": 0.16588373482227325,
          "median_body_rise_m": 0.2039901316165924,
          "recovered_median_rim_m": 0.1754966750741005,
          "median_flight_quality": 0.5474407076835632,
          "max_air_pitch_deg": 25.82702675196777,
          "max_air_roll_deg": 7.831088506081005,
          "max_air_pitch_roll_rate_rad_s": 3.6224772930145264,
          "median_estimated_spring_release_J": 26.29888343811035
        },
        "nominal": {
          "episodes": 51,
          "requested": 51,
          "takeoff": 51,
          "landed": 51,
          "sequence_complete": 51,
          "success": 0,
          "failed": 0,
          "prep_skipped": 51,
          "median_rim_m": 0.19846829771995544,
          "median_body_rise_m": 0.21533535420894623,
          "recovered_median_rim_m": 0.19846829771995544,
          "median_flight_quality": 0.6838575005531311,
          "max_air_pitch_deg": 9.889140616221736,
          "max_air_roll_deg": 2.460128697993281,
          "max_air_pitch_roll_rate_rad_s": 2.623807191848755,
          "median_estimated_spring_release_J": 26.66919708251953
        }
      },
      "checkpoint_sha256": "d257142f749faebea661ce6b154376644b87df0d5823e525ecc190bc5818dea2",
      "recovered_level_height_score_m": 0.04069037117287365
    },
    {
      "job": "eval_train7200_model_115m",
      "status": "complete",
      "summary": {
        "fullDR": {
          "episodes": 205,
          "requested": 205,
          "takeoff": 187,
          "landed": 186,
          "sequence_complete": 19,
          "success": 0,
          "failed": 129,
          "prep_skipped": 191,
          "median_rim_m": 0.16650672256946564,
          "median_body_rise_m": 0.20563636720180511,
          "recovered_median_rim_m": 0.16650672256946564,
          "median_flight_quality": 0.5598472356796265,
          "max_air_pitch_deg": 19.646670317326496,
          "max_air_roll_deg": 8.233377256684646,
          "max_air_pitch_roll_rate_rad_s": 3.8233566284179688,
          "median_estimated_spring_release_J": 26.435665130615234
        },
        "nominal": {
          "episodes": 51,
          "requested": 51,
          "takeoff": 51,
          "landed": 50,
          "sequence_complete": 50,
          "success": 0,
          "failed": 0,
          "prep_skipped": 51,
          "median_rim_m": 0.1989164650440216,
          "median_body_rise_m": 0.21315868198871613,
          "recovered_median_rim_m": 0.19878746569156647,
          "median_flight_quality": 0.6682215929031372,
          "max_air_pitch_deg": 9.325253004950177,
          "max_air_roll_deg": 2.5880254843056507,
          "max_air_pitch_roll_rate_rad_s": 2.662418842315674,
          "median_estimated_spring_release_J": 25.35673713684082
        }
      },
      "checkpoint_sha256": "91e0d00db6a2be474f902781739c6d2100efcc6730cea9a3f0948ac5a52281bb",
      "recovered_level_height_score_m": 0.03767410677367293
    },
    {
      "job": "eval_train7200_model_120m",
      "status": "complete",
      "summary": {
        "fullDR": {
          "episodes": 205,
          "requested": 205,
          "takeoff": 186,
          "landed": 186,
          "sequence_complete": 17,
          "success": 0,
          "failed": 138,
          "prep_skipped": 190,
          "median_rim_m": 0.1666581928730011,
          "median_body_rise_m": 0.20628690719604492,
          "recovered_median_rim_m": 0.1610022783279419,
          "median_flight_quality": 0.5644673109054565,
          "max_air_pitch_deg": 20.704082638587437,
          "max_air_roll_deg": 9.58452271697563,
          "max_air_pitch_roll_rate_rad_s": 3.6165037155151367,
          "median_estimated_spring_release_J": 26.113420486450195
        },
        "nominal": {
          "episodes": 51,
          "requested": 51,
          "takeoff": 51,
          "landed": 51,
          "sequence_complete": 51,
          "success": 0,
          "failed": 0,
          "prep_skipped": 51,
          "median_rim_m": 0.200399249792099,
          "median_body_rise_m": 0.21730396151542664,
          "recovered_median_rim_m": 0.200399249792099,
          "median_flight_quality": 0.6781240105628967,
          "max_air_pitch_deg": 9.9446563937956,
          "max_air_roll_deg": 2.1506159009898025,
          "max_air_pitch_roll_rate_rad_s": 2.668367385864258,
          "median_estimated_spring_release_J": 24.847557067871094
        }
      },
      "checkpoint_sha256": "e2a205978fdbebae2f37eead3ab7636c593eb86ebc81d64965b4a71ffd59a32f",
      "recovered_level_height_score_m": 0.03733309595053885
    },
    {
      "job": "eval_train7200_model_final",
      "status": "complete",
      "summary": {
        "fullDR": {
          "episodes": 205,
          "requested": 205,
          "takeoff": 186,
          "landed": 186,
          "sequence_complete": 17,
          "success": 0,
          "failed": 138,
          "prep_skipped": 190,
          "median_rim_m": 0.1666581928730011,
          "median_body_rise_m": 0.20628690719604492,
          "recovered_median_rim_m": 0.1610022783279419,
          "median_flight_quality": 0.5644673109054565,
          "max_air_pitch_deg": 20.704082638587437,
          "max_air_roll_deg": 9.58452271697563,
          "max_air_pitch_roll_rate_rad_s": 3.6165037155151367,
          "median_estimated_spring_release_J": 26.113420486450195
        },
        "nominal": {
          "episodes": 51,
          "requested": 51,
          "takeoff": 51,
          "landed": 51,
          "sequence_complete": 51,
          "success": 0,
          "failed": 0,
          "prep_skipped": 51,
          "median_rim_m": 0.200399249792099,
          "median_body_rise_m": 0.21730396151542664,
          "recovered_median_rim_m": 0.200399249792099,
          "median_flight_quality": 0.6781240105628967,
          "max_air_pitch_deg": 9.9446563937956,
          "max_air_roll_deg": 2.1506159009898025,
          "max_air_pitch_roll_rate_rad_s": 2.668367385864258,
          "median_estimated_spring_release_J": 24.847557067871094
        }
      },
      "checkpoint_sha256": "1a05effc86cfe93ac2e13e12eb9437bb0d2d3c65bb415659258af9d66c676374",
      "recovered_level_height_score_m": 0.03733309595053885
    }
  ],
  "best_evaluated_candidate": {
    "job": "eval_train7200_model_100m",
    "status": "complete",
    "summary": {
      "fullDR": {
        "episodes": 205,
        "requested": 205,
        "takeoff": 184,
        "landed": 184,
        "sequence_complete": 36,
        "success": 0,
        "failed": 102,
        "prep_skipped": 193,
        "median_rim_m": 0.16560585796833038,
        "median_body_rise_m": 0.20476332306861877,
        "recovered_median_rim_m": 0.1719653308391571,
        "median_flight_quality": 0.5492455363273621,
        "max_air_pitch_deg": 18.66137454841714,
        "max_air_roll_deg": 10.309279212447562,
        "max_air_pitch_roll_rate_rad_s": 4.283921241760254,
        "median_estimated_spring_release_J": 25.985408782958984
      },
      "nominal": {
        "episodes": 51,
        "requested": 51,
        "takeoff": 51,
        "landed": 50,
        "sequence_complete": 50,
        "success": 0,
        "failed": 0,
        "prep_skipped": 51,
        "median_rim_m": 0.1974986493587494,
        "median_body_rise_m": 0.21092891693115234,
        "recovered_median_rim_m": 0.19754180312156677,
        "median_flight_quality": 0.6703210473060608,
        "max_air_pitch_deg": 9.525106047612043,
        "max_air_roll_deg": 3.058419118340548,
        "max_air_pitch_roll_rate_rad_s": 2.584392786026001,
        "median_estimated_spring_release_J": 23.676496505737305
      }
    },
    "checkpoint_sha256": "4b9bfd9a7065652e3e6e514973d4fe9ba0215ee1f9042848d3acb27cfc27cb9d",
    "recovered_level_height_score_m": 0.045850771071230645
  },
  "candidate_beats_parent": true,
  "automatic_training_extension": false,
  "old_player_preserved": true,
  "policy_promoted_to_player": false,
  "final": {
    "epoch": 1794701456.2802727,
    "checkpoint": {
      "path": "/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V3_FLAT_ACCEL_STABLE_HEIGHT_REPAIR_2H_20261115_R1/train7200/model_final.pt",
      "bytes": 6353789,
      "sha256": "1a05effc86cfe93ac2e13e12eb9437bb0d2d3c65bb415659258af9d66c676374",
      "iteration": 28087,
      "elapsed_seconds": 7208.976531803026
    },
    "last_progress": {
      "epoch": 1794701456.0658095,
      "iteration": 28087,
      "new_updates": 705,
      "training_elapsed_seconds": 7208.762148857117,
      "segment_training_elapsed_seconds": 7208.762143912027,
      "target_seconds": 7200,
      "reward_mean": 0.01463255228009075,
      "losses": {
        "value": 18.461315472920734,
        "surrogate": 0.0011413176713782984,
        "entropy": -10.660556157430014
      },
      "task": {
        "counts": {
          "episodes": [
            113790,
            35604
          ],
          "crouched": [
            107836,
            34980
          ],
          "extended": [
            107655,
            34974
          ],
          "takeoff": [
            99749,
            34970
          ],
          "retracted": [
            98327,
            34965
          ],
          "upright_flight": [
            0,
            0
          ],
          "landed": [
            97049,
            34901
          ],
          "success": [
            0,
            0
          ],
          "sequence_complete": [
            20627,
            33256
          ]
        },
        "grouping": [
          "fullDR",
          "nominal"
        ],
        "rim_peak_max_m": 0.30086469650268555,
        "body_rise_peak_max_m": 0.28888970613479614,
        "max_takeoffs_per_episode": 1,
        "reward_components": {
          "height": 0.04716965928673744,
          "dense": -0.005529710091650486,
          "failure": 0.00244140625
        },
        "closure_peak_m": 0.0017015545163303614,
        "done_totals": {
          "episodes": 145298,
          "closure": 0,
          "mimic": 0,
          "numerical": 0,
          "timeout": 52471,
          "fall": 0,
          "closure_catastrophic": 0
        }
      },
      "exploration_STD": [
        0.028867853805422783,
        0.03510462865233421,
        0.02789304032921791,
        0.03051702119410038,
        0.0748228132724762,
        0.07291724532842636
      ],
      "total_env_steps": 34652160
    },
    "elapsed_seconds": 7208.976629646029,
    "target_training_seconds": 7200.0,
    "original_start_epoch": 1794694247.3036613,
    "original_deadline_epoch": 1794701447.3036613,
    "automatic_extension": false,
    "request_stop": false
  },
  "closed": {
    "epoch": 1794701460.2599404,
    "scene_closed": true,
    "outcome": "complete"
  },
  "error": null,
  "progress": {
    "epoch": 1794701456.0658095,
    "iteration": 28087,
    "new_updates": 705,
    "training_elapsed_seconds": 7208.762148857117,
    "segment_training_elapsed_seconds": 7208.762143912027,
    "target_seconds": 7200,
    "reward_mean": 0.01463255228009075,
    "losses": {
      "value": 18.461315472920734,
      "surrogate": 0.0011413176713782984,
      "entropy": -10.660556157430014
    },
    "task": {
      "counts": {
        "episodes": [
          113790,
          35604
        ],
        "crouched": [
          107836,
          34980
        ],
        "extended": [
          107655,
          34974
        ],
        "takeoff": [
          99749,
          34970
        ],
        "retracted": [
          98327,
          34965
        ],
        "upright_flight": [
          0,
          0
        ],
        "landed": [
          97049,
          34901
        ],
        "success": [
          0,
          0
        ],
        "sequence_complete": [
          20627,
          33256
        ]
      },
      "grouping": [
        "fullDR",
        "nominal"
      ],
      "rim_peak_max_m": 0.30086469650268555,
      "body_rise_peak_max_m": 0.28888970613479614,
      "max_takeoffs_per_episode": 1,
      "reward_components": {
        "height": 0.04716965928673744,
        "dense": -0.005529710091650486,
        "failure": 0.00244140625
      },
      "closure_peak_m": 0.0017015545163303614,
      "done_totals": {
        "episodes": 145298,
        "closure": 0,
        "mimic": 0,
        "numerical": 0,
        "timeout": 52471,
        "fall": 0,
        "closure_catastrophic": 0
      }
    },
    "exploration_STD": [
      0.028867853805422783,
      0.03510462865233421,
      0.02789304032921791,
      0.03051702119410038,
      0.0748228132724762,
      0.07291724532842636
    ],
    "total_env_steps": 34652160
  }
}
