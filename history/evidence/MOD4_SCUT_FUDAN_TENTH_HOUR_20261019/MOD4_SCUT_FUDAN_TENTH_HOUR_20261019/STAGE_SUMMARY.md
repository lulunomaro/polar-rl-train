# Ninth-hour full closure and tenth-hour resource admission pending

{
  "closed": {
    "h1": {
      "final": {
        "path": "/home/lc01/Zonglin Li/zonglin2/tasks/T3sf9_1910v14/h1/job0/production/model_update62.pt",
        "bytes": 16646963,
        "SHA": "8d0ce2a098af591524e4a4e7379189f21b8c55ffc47eef8b6bd8f3fa3db56d97",
        "key": "h1",
        "local_path": "C:\\Users\\lulu\\Desktop\\claude\\mjcf\\MOD4_SCUT_FUDAN_NINTH_HOUR_20261019\\actual_closed_three_finals\\h1\\model_update62.pt",
        "twohost_complete_SHA": true
      },
      "updates": 62,
      "Adam": 669640,
      "tensor_counts": [
        199,
        105
      ]
    },
    "e2": {
      "final": {
        "path": "/mnt/mod4_linux_durable_20261013/T3sf9_1910v14/e2/job0/production/model_update241.pt",
        "bytes": 14615528,
        "SHA": "5bee3dee41de4a29d4903ccff03f622c1d32de228ed4782e6ecf5927a158666e",
        "key": "e2",
        "local_path": "C:\\Users\\lulu\\Desktop\\claude\\mjcf\\MOD4_SCUT_FUDAN_NINTH_HOUR_20261019\\actual_closed_three_finals\\e2\\model_update241.pt",
        "twohost_complete_SHA": true
      },
      "updates": 241,
      "Adam": 734060,
      "tensor_counts": [
        175,
        98
      ]
    },
    "recovery": {
      "final": {
        "path": "/home/lc01/Zonglin Li/zonglin2/tasks/T3sf9_1910v14/recovery/job0/production/final_valid_update93.pt",
        "bytes": 14715349,
        "SHA": "749267e9ffc593fc1054921bd942cde4d7bdcca7737bbb81e2d4cecc1b47ccd4",
        "key": "recovery",
        "local_path": "C:\\Users\\lulu\\Desktop\\claude\\mjcf\\MOD4_SCUT_FUDAN_NINTH_HOUR_20261019\\actual_closed_three_finals\\recovery\\final_valid_update93.pt",
        "twohost_complete_SHA": true
      },
      "updates": 93,
      "Adam": 684180,
      "tensor_counts": [
        173,
        96
      ]
    }
  },
  "original_cost_once": 10929.569695949554,
  "remaining_snapshot": 340361.3840699196,
  "resource_hold": {
    "epoch": 1792376900.2760339,
    "status": "three_expert_continuation_prepared_but_not_dispatched_target_GPU_admission_pending",
    "previous_owner": 293563,
    "previous_actual_closed": true,
    "whole_CPU_passed": true,
    "actual_local_transport_returned_error": true,
    "fresh_local_CIM_no_own_finite": [],
    "observations": 10,
    "observation_Beijing_range": [
      "2026-10-19T10:21:22.012132+08:00",
      "2026-10-19T10:25:56.146724+08:00"
    ],
    "last_observed_target_resources": {
      "epoch": 1792376756.146724,
      "previous_nodes": {
        "h1": {
          "root": "/home/lc01/Zonglin Li/zonglin2/tasks/T3sf9_1910v14/h1",
          "actual_own_processes": [],
          "previous_final_SHA": "8d0ce2a098af591524e4a4e7379189f21b8c55ffc47eef8b6bd8f3fa3db56d97",
          "matches_complete_source": true,
          "actual_closed": true
        },
        "recovery": {
          "root": "/home/lc01/Zonglin Li/zonglin2/tasks/T3sf9_1910v14/recovery",
          "actual_own_processes": [],
          "previous_final_SHA": "749267e9ffc593fc1054921bd942cde4d7bdcca7737bbb81e2d4cecc1b47ccd4",
          "matches_complete_source": true,
          "actual_closed": true
        }
      },
      "actual_locks": [
        {
          "path": "/home/lc01/Zonglin Li/zonglin2/state/three_expert_v2_GPU-16828f91-2b45-b646-8dc0-9481138e2842.lock",
          "actual_fcntl_free": true
        },
        {
          "path": "/home/lc01/Zonglin Li/zonglin2/state/three_expert_v2_GPU-c27eecbd-6838-7290-1cd2-37e34522213d.lock",
          "actual_fcntl_free": true
        },
        {
          "path": "/home/lc01/Zonglin Li/zonglin2/state/finite_environment_validation.lock",
          "actual_fcntl_free": true
        }
      ],
      "compute_snapshot": "GPU-16828f91-2b45-b646-8dc0-9481138e2842, 66633, 8526\n",
      "target_GPU_empty": {
        "h1": false,
        "recovery": true
      },
      "durable_free_bytes": 98571862016,
      "RAM_available_bytes": 529423056896,
      "non_GPU_original_admission_ready": true,
      "target_admission_snapshot_ready": false,
      "no_peer_identity_or_workload_inference": true,
      "no_process_signal_lock_delete_PT_or_account_write": true
    },
    "actual_10054_then_SSH_session_not_active_retained": true,
    "original_keepalive15_already_present": true,
    "not_GPU_failure_or_network_repaired_claim": true,
    "no_new_owner_nodes_workers_GO": true,
    "original_one_writer_three_expert_accounting_contract_unchanged": true,
    "E2_and_E3_idle_reason": "The original three-expert handoff requires all assigned GPUs to pass admission before dispatch; no new two-card/concurrent accounting contract was introduced.",
    "no_PT_raw_native_Task_or_charge_replay": true,
    "no_peer_signal_lock_delete_or_identity_assumption": true
  },
  "local_new_source_feedback": {
    "epoch": 1792376424.9652197,
    "rows": [
      {
        "source_SHA": "8d0ce2a098af591524e4a4e7379189f21b8c55ffc47eef8b6bd8f3fa3db56d97",
        "public4_requested": false,
        "yaw": 0.0,
        "strict_counts": {
          "takeoff": 0,
          "landing": 0,
          "recovery": 0
        },
        "event_times_s": {
          "takeoff": [],
          "landing": [],
          "recovery": []
        },
        "survived15s": true,
        "duration_s": 15.00000000000684,
        "first_failure": null,
        "peak_both_wheel_min_clearance_m": -6.328592178084236e-07,
        "prepared_longest_callbacks": 396,
        "actual_phase_recovery_ticks_max": 0,
        "first_after_recovery_yaw_condition_breach_s": null,
        "previous_after_recovery_yaw_condition_breach_s": null,
        "final_yaw_error_rad": -0.24709239154230025,
        "previous_final_yaw_error_rad": 0.07002832212617574,
        "final_planar_speed_m_s": 0.01731535628097718,
        "previous_final_planar_speed_m_s": 0.0070548167186539066,
        "command_actual_force_max_abs_difference": [
          0.0,
          0.0,
          0.0,
          0.0,
          0.0,
          0.0
        ],
        "normal_comparison": {
          "current": {
            "source_SHA": "8d0ce2a098af591524e4a4e7379189f21b8c55ffc47eef8b6bd8f3fa3db56d97",
            "survived15s": true,
            "final_speed_m_s": 0.01731535628097718,
            "last_second_mean_speed_m_s": 0.01731536007802026,
            "final_yaw_drift_rad": -0.24709239154230025,
            "net_planar_displacement_m": 0.26352552967660264,
            "raw": {
              "path": "C:\\Users\\lulu\\Desktop\\claude\\mjcf\\MOD4_SCUT_FUDAN_TENTH_HOUR_20261019\\local_ninth_reward_hour_new_source_trajectories\\after_reward_hour9_normal_0.0.npz",
              "bytes": 1668577,
              "SHA": "ffaca8c5e4baa7dfebeef2bbac8f2336502bece9fb6bc057a1e055d8d4c6e21c"
            }
          },
          "previous": {
            "source_SHA": "1078e676ac1b4c9d03941d8f1ba177934474613fa9f31caa3db320d0a20037b3",
            "survived15s": true,
            "final_speed_m_s": 0.0070548167186539066,
            "last_second_mean_speed_m_s": 0.007054811453536241,
            "final_yaw_drift_rad": 0.07002832212617574,
            "net_planar_displacement_m": 0.11906421353484531,
            "raw": {
              "path": "C:\\Users\\lulu\\Desktop\\claude\\mjcf\\MOD4_SCUT_FUDAN_NINTH_HOUR_20261019\\local_eighth_reward_hour_new_source_trajectories\\after_reward_hour8_normal_0.0.npz",
              "bytes": 1641206,
              "SHA": "ed0e13edc4f94a6a9901edb264022355ba6c582cad34002608680cafa906dd58"
            }
          }
        },
        "raw": {
          "path": "C:\\Users\\lulu\\Desktop\\claude\\mjcf\\MOD4_SCUT_FUDAN_TENTH_HOUR_20261019\\local_ninth_reward_hour_new_source_trajectories\\after_reward_hour9_normal_0.0.npz",
          "bytes": 1668577,
          "SHA": "ffaca8c5e4baa7dfebeef2bbac8f2336502bece9fb6bc057a1e055d8d4c6e21c"
        }
      },
      {
        "source_SHA": "8d0ce2a098af591524e4a4e7379189f21b8c55ffc47eef8b6bd8f3fa3db56d97",
        "public4_requested": false,
        "yaw": 3.141592653589793,
        "strict_counts": {
          "takeoff": 0,
          "landing": 0,
          "recovery": 0
        },
        "event_times_s": {
          "takeoff": [],
          "landing": [],
          "recovery": []
        },
        "survived15s": true,
        "duration_s": 15.00000000000684,
        "first_failure": null,
        "peak_both_wheel_min_clearance_m": -6.328592177945458e-07,
        "prepared_longest_callbacks": 396,
        "actual_phase_recovery_ticks_max": 0,
        "first_after_recovery_yaw_condition_breach_s": null,
        "previous_after_recovery_yaw_condition_breach_s": null,
        "final_yaw_error_rad": -0.24709239929007154,
        "previous_final_yaw_error_rad": 0.07002830107675376,
        "final_planar_speed_m_s": 0.017315364091811964,
        "previous_final_planar_speed_m_s": 0.00705480062017302,
        "command_actual_force_max_abs_difference": [
          0.0,
          0.0,
          0.0,
          0.0,
          0.0,
          0.0
        ],
        "normal_comparison": {
          "current": {
            "source_SHA": "8d0ce2a098af591524e4a4e7379189f21b8c55ffc47eef8b6bd8f3fa3db56d97",
            "survived15s": true,
            "final_speed_m_s": 0.017315364091811964,
            "last_second_mean_speed_m_s": 0.017315362127769563,
            "final_yaw_drift_rad": -0.24709239929007154,
            "net_planar_displacement_m": 0.26352555015706713,
            "raw": {
              "path": "C:\\Users\\lulu\\Desktop\\claude\\mjcf\\MOD4_SCUT_FUDAN_TENTH_HOUR_20261019\\local_ninth_reward_hour_new_source_trajectories\\after_reward_hour9_normal_3.1416.npz",
              "bytes": 1663324,
              "SHA": "e27519d8bb3acc23dd380fec90aa7cec979268cb5d93ad65c072304f9675af50"
            }
          },
          "previous": {
            "source_SHA": "1078e676ac1b4c9d03941d8f1ba177934474613fa9f31caa3db320d0a20037b3",
            "survived15s": true,
            "final_speed_m_s": 0.00705480062017302,
            "last_second_mean_speed_m_s": 0.007054807233432099,
            "final_yaw_drift_rad": 0.07002830107675376,
            "net_planar_displacement_m": 0.11906421665497342,
            "raw": {
              "path": "C:\\Users\\lulu\\Desktop\\claude\\mjcf\\MOD4_SCUT_FUDAN_NINTH_HOUR_20261019\\local_eighth_reward_hour_new_source_trajectories\\after_reward_hour8_normal_3.1416.npz",
              "bytes": 1635291,
              "SHA": "0d52b7d33e5ff537b4b2e02d2e3d6acf3d54c9be03f876af48c2f0ec6164d416"
            }
          }
        },
        "raw": {
          "path": "C:\\Users\\lulu\\Desktop\\claude\\mjcf\\MOD4_SCUT_FUDAN_TENTH_HOUR_20261019\\local_ninth_reward_hour_new_source_trajectories\\after_reward_hour9_normal_3.1416.npz",
          "bytes": 1663324,
          "SHA": "e27519d8bb3acc23dd380fec90aa7cec979268cb5d93ad65c072304f9675af50"
        }
      },
      {
        "source_SHA": "8d0ce2a098af591524e4a4e7379189f21b8c55ffc47eef8b6bd8f3fa3db56d97",
        "public4_requested": true,
        "yaw": 0.0,
        "strict_counts": {
          "takeoff": 1,
          "landing": 1,
          "recovery": 1
        },
        "event_times_s": {
          "takeoff": [
            1.1374999999999302
          ],
          "landing": [
            1.3624999999999055
          ],
          "recovery": [
            2.562500000000023
          ]
        },
        "survived15s": true,
        "duration_s": 15.00000000000684,
        "first_failure": null,
        "peak_both_wheel_min_clearance_m": 0.0696401315911743,
        "prepared_longest_callbacks": 396,
        "actual_phase_recovery_ticks_max": 5175,
        "first_after_recovery_yaw_condition_breach_s": null,
        "previous_after_recovery_yaw_condition_breach_s": 13.422500000004913,
        "final_yaw_error_rad": -0.12389259004426,
        "previous_final_yaw_error_rad": 0.21064585391143795,
        "final_planar_speed_m_s": 0.017315361117661868,
        "previous_final_planar_speed_m_s": 0.0070548079293892415,
        "command_actual_force_max_abs_difference": [
          0.0,
          0.0,
          0.0,
          0.0,
          0.0,
          0.0
        ],
        "normal_comparison": null,
        "raw": {
          "path": "C:\\Users\\lulu\\Desktop\\claude\\mjcf\\MOD4_SCUT_FUDAN_TENTH_HOUR_20261019\\local_ninth_reward_hour_new_source_trajectories\\after_reward_hour9_jump_0.0.npz",
          "bytes": 1744405,
          "SHA": "05d8755c9f8aab264bd572699ca889b812ccd60825a89f826c85626d8189acb3"
        }
      },
      {
        "source_SHA": "8d0ce2a098af591524e4a4e7379189f21b8c55ffc47eef8b6bd8f3fa3db56d97",
        "public4_requested": true,
        "yaw": 3.141592653589793,
        "strict_counts": {
          "takeoff": 1,
          "landing": 1,
          "recovery": 1
        },
        "event_times_s": {
          "takeoff": [
            1.1374999999999302
          ],
          "landing": [
            1.3624999999999055
          ],
          "recovery": [
            2.562500000000023
          ]
        },
        "survived15s": true,
        "duration_s": 15.00000000000684,
        "first_failure": null,
        "peak_both_wheel_min_clearance_m": 0.0696401315910655,
        "prepared_longest_callbacks": 396,
        "actual_phase_recovery_ticks_max": 5175,
        "first_after_recovery_yaw_condition_breach_s": null,
        "previous_after_recovery_yaw_condition_breach_s": 13.422500000004913,
        "final_yaw_error_rad": -0.12389258129201064,
        "previous_final_yaw_error_rad": 0.2106458750987799,
        "final_planar_speed_m_s": 0.0173153647729904,
        "previous_final_planar_speed_m_s": 0.007054804170631205,
        "command_actual_force_max_abs_difference": [
          0.0,
          0.0,
          0.0,
          0.0,
          0.0,
          0.0
        ],
        "normal_comparison": null,
        "raw": {
          "path": "C:\\Users\\lulu\\Desktop\\claude\\mjcf\\MOD4_SCUT_FUDAN_TENTH_HOUR_20261019\\local_ninth_reward_hour_new_source_trajectories\\after_reward_hour9_jump_3.1416.npz",
          "bytes": 1740834,
          "SHA": "9e1aae8f70b9628c134b8c481ae048b3f5ebdaa21ee94c14f0bdd5b562ca5be7"
        }
      }
    ],
    "interpretation": "Compare each observed event, duration, clearance and late yaw/speed/displacement separately. A sticky recovery event does not establish continuous holding. These are four deterministic local MuJoCo trajectories under a different backend without the production20kDR, not PhysX qualification, statistical significance, unique reward causality or complete normal nonregression.",
    "original_physics_control_request_clock_and_thresholds_unchanged": true,
    "no_old_case_replay_or_live_player_GPU_account_change": true,
    "retained_original_yaw_objective_source_audit": "C:\\Users\\lulu\\Desktop\\claude\\mjcf\\MOD4_SCUT_FUDAN_EIGHTH_HOUR_20261019\\reports\\NORMAL_YAW_RATE_SOURCE_OBJECTIVE_CPU_ACTUAL.json"
  },
  "errors": [
    {
      "path": "C:\\Users\\lulu\\Desktop\\claude\\mjcf\\MOD4_SCUT_FUDAN_TENTH_HOUR_20261019\\reports\\LOCAL_CPU_REVIEW_STARTED_BEFORE_TRAJECTORY_RECEIPT_ORIGINAL_ERROR_ACTUAL.json",
      "bytes": 1523,
      "SHA": "c2704db53b965398e5125692c1c2403f1b8eb8314a83c7140899d43431e9e4ee"
    },
    {
      "path": "C:\\Users\\lulu\\Desktop\\claude\\mjcf\\MOD4_SCUT_FUDAN_TENTH_HOUR_20261019\\reports\\TENTH_TARGET_MISSING_RESOURCE_WAIT_ORIGINAL_ERROR_1792376786077270300.json",
      "bytes": 2087,
      "SHA": "163297f24092241e36d28a98499ee8d941fe7ba8e28a7befef62192c4a39c6b5"
    }
  ],
  "same_original_recipe_budget_and_player": true
}