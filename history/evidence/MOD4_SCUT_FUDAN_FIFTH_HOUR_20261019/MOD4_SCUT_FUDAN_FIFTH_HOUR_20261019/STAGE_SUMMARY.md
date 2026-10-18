# Fourth reward-hour closure, fifth-hour continuation and local recovery residuals

{
  "closed": {
    "h1": {
      "final": {
        "path": "/home/lc01/Zonglin Li/zonglin2/tasks/T3sf4_1910v9/h1/job0/production/model_update73.pt",
        "bytes": 16646963,
        "SHA": "133847baef60d16a9c2c286b7d2dbde3c1b54cd097fe29d529441bd40fb5c5d4",
        "key": "h1",
        "local_path": "C:\\Users\\lulu\\Desktop\\claude\\mjcf\\MOD4_SCUT_FUDAN_FOURTH_HOUR_20261019\\actual_closed_three_finals\\h1\\model_update73.pt",
        "twohost_complete_SHA": true
      },
      "updates": 73,
      "Adam": 662640,
      "tensor_counts": [
        199,
        105
      ]
    },
    "e2": {
      "final": {
        "path": "/mnt/mod4_linux_durable_20261013/T3sf4_1910v9/e2/job0/production/model_update237.pt",
        "bytes": 14615528,
        "SHA": "94ca10b629fd413065124076cac290ca8b35bfc55bfe13e87ed1853b13d77b15",
        "key": "e2",
        "local_path": "C:\\Users\\lulu\\Desktop\\claude\\mjcf\\MOD4_SCUT_FUDAN_FOURTH_HOUR_20261019\\actual_closed_three_finals\\e2\\model_update237.pt",
        "twohost_complete_SHA": true
      },
      "updates": 237,
      "Adam": 710020,
      "tensor_counts": [
        175,
        98
      ]
    },
    "recovery": {
      "final": {
        "path": "/home/lc01/Zonglin Li/zonglin2/tasks/T3sf4_1910v9/recovery/job0/production/final_valid_update97.pt",
        "bytes": 14715349,
        "SHA": "b9444feaba2e816de36ecd2a138f1de38b8a625a7b883e4e9ffdb5f748ec25f7",
        "key": "recovery",
        "local_path": "C:\\Users\\lulu\\Desktop\\claude\\mjcf\\MOD4_SCUT_FUDAN_FOURTH_HOUR_20261019\\actual_closed_three_finals\\recovery\\final_valid_update97.pt",
        "twohost_complete_SHA": true
      },
      "updates": 97,
      "Adam": 674800,
      "tensor_counts": [
        173,
        96
      ]
    }
  },
  "cost_once": 10909.122479200363,
  "remaining_snapshot": 394943.3422162533,
  "new_dispatch": {
    "epoch": 1792357509.434765,
    "owner": {
      "detached_pid": 246762,
      "root": "/mnt/mod4_linux_durable_20261013/T3sf5_1910v10/owner",
      "role": "owner"
    },
    "nodes": {
      "e2": {
        "detached_pid": 246767,
        "root": "/mnt/mod4_linux_durable_20261013/T3sf5_1910v10/e2",
        "role": "node"
      },
      "h1": {
        "detached_pid": 53980,
        "root": "/home/lc01/Zonglin Li/zonglin2/tasks/T3sf5_1910v10/h1",
        "role": "node"
      },
      "recovery": {
        "detached_pid": 53997,
        "root": "/home/lc01/Zonglin Li/zonglin2/tasks/T3sf5_1910v10/recovery",
        "role": "node"
      }
    },
    "source_root": "/mnt/mod4_linux_durable_20261013/T3sf5_1910v10/owner",
    "roots": {
      "h1": "/home/lc01/Zonglin Li/zonglin2/tasks/T3sf5_1910v10/h1",
      "e2": "/mnt/mod4_linux_durable_20261013/T3sf5_1910v10/e2",
      "recovery": "/home/lc01/Zonglin Li/zonglin2/tasks/T3sf5_1910v10/recovery"
    },
    "specs": {
      "h1": {
        "key": "h1",
        "GPU_UUID": "GPU-16828f91-2b45-b646-8dc0-9481138e2842",
        "max_parent_seconds": 3900,
        "exit_headroom_seconds": 300,
        "source_SHA": "133847baef60d16a9c2c286b7d2dbde3c1b54cd097fe29d529441bd40fb5c5d4",
        "source_filename": "H1_closed_hour73.pt",
        "source_Adamstep": 662640,
        "manifest_SHA": "5e805cb0edef829226a119ce885647bad2c6baedacf4cc981731a4a27c2d0144",
        "native_controls": 180,
        "native_script": "h1_ground_prelaunch_v2_native_worker_v1.py",
        "native_CPU_script": "review_H1_prelaunch_v2_native_allrows_CPU_v1.py",
        "production_script": "h1_prelaunch_v2_production_worker_v1.py",
        "execution_backend": "target72",
        "python": "/home/lc01/Zonglin Li/zonglin2/run-python.sh",
        "previous_runtime_root": "/home/lc01/Zonglin Li/zonglin2/tasks/T3sf4_1910v9/h1",
        "previous_exit_kind": "node",
        "private_lock": "/home/lc01/Zonglin Li/zonglin2/state/three_expert_v2_GPU-16828f91-2b45-b646-8dc0-9481138e2842.lock",
        "reuse_completed_native": false,
        "closed_production_continuation": true,
        "reward_migration": false
      },
      "e2": {
        "key": "e2",
        "GPU_UUID": "GPU-937bdb0b-0d8f-aa3d-a10e-1b24969a5d4e",
        "max_parent_seconds": 3900,
        "exit_headroom_seconds": 300,
        "source_SHA": "94ca10b629fd413065124076cac290ca8b35bfc55bfe13e87ed1853b13d77b15",
        "source_filename": "E2_closed_hour237.pt",
        "source_Adamstep": 710020,
        "manifest_SHA": "cff06b0851a2f67b3e94fff3d3d42d34765b42955641e5dbe3093ab3fae37ea3",
        "native_controls": 144,
        "native_script": "native_admission_worker.py",
        "native_CPU_script": "native_CPU.py",
        "production_script": "native_admission_worker.py",
        "execution_backend": "source210",
        "python": "/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python",
        "previous_runtime_root": "/mnt/mod4_linux_durable_20261013/T3sf4_1910v9/e2",
        "previous_exit_kind": "node",
        "private_lock": "/mnt/mod4_linux_durable_20261013/H125_1710n1/OWN_SOURCE_GPU_NATIVE_ONLY.lock",
        "reuse_completed_native": false,
        "closed_production_continuation": true,
        "reward_migration": false
      },
      "recovery": {
        "key": "recovery",
        "GPU_UUID": "GPU-c27eecbd-6838-7290-1cd2-37e34522213d",
        "max_parent_seconds": 3900,
        "exit_headroom_seconds": 300,
        "source_SHA": "b9444feaba2e816de36ecd2a138f1de38b8a625a7b883e4e9ffdb5f748ec25f7",
        "source_filename": "RECOVERY_closed_hour97.pt",
        "source_Adamstep": 674800,
        "manifest_SHA": "424c2d0d0aa8b04e03f9a202b7f422057a534c41a928000e8daada8a7c429c27",
        "native_controls": 336,
        "native_script": "recovery_worker.py",
        "native_CPU_script": "native_CPU.py",
        "production_script": "recovery_worker.py",
        "execution_backend": "target72",
        "python": "/home/lc01/Zonglin Li/zonglin2/run-python.sh",
        "previous_runtime_root": "/home/lc01/Zonglin Li/zonglin2/tasks/T3sf4_1910v9/recovery",
        "previous_exit_kind": "node",
        "private_lock": "/home/lc01/Zonglin Li/zonglin2/state/three_expert_v2_GPU-c27eecbd-6838-7290-1cd2-37e34522213d.lock",
        "reuse_completed_native": false,
        "closed_production_continuation": true,
        "reward_migration": false
      }
    },
    "all_three_direct_full_production_source_not_native_replay": true,
    "one_original_writer_independent_intervals_once": true,
    "all_GO_save3600_lifecycle3900_exit300": true,
    "no_total_budget_PPO_reward_LR_STD_physics_threshold_change": true,
    "not_actual_learning_claim_before_GO": true
  },
  "actual_learning": {
    "epoch": 1792358012.4080603,
    "three_actual_PPO_learning_verified": true,
    "experts": {
      "h1": {
        "actual_GO": true,
        "actual_production_log_positive": true,
        "actual_matching_GPU_worker_compute": true,
        "worker": {
          "pid": 54002,
          "creation": 1792357512.27,
          "argv": [
            "/home/lc01/Zonglin Li/zonglin2/compat/glibc240/ld-linux-x86-64.so.2",
            "--library-path",
            "/home/lc01/Zonglin Li/zonglin2/compat/glibc240:/home/lc01/Zonglin Li/zonglin2/envs/mod4/lib",
            "/home/lc01/Zonglin Li/zonglin2/envs/mod4/bin/python",
            "-B",
            "-u",
            "-B",
            "/home/lc01/Zonglin Li/zonglin2/tasks/T3sf5_1910v10/h1/h1_prelaunch_v2_production_worker_v1.py",
            "--phase",
            "production"
          ],
          "root": "/home/lc01/Zonglin Li/zonglin2"
        },
        "latest_complete": {
          "epoch": 1792357998.565706,
          "path": "/home/lc01/Zonglin Li/zonglin2/tasks/T3sf5_1910v10/h1/job0/production/model_update1.pt",
          "bytes": 16646758,
          "SHA": "9d3cbb1f203a483db2ec46fdc598ef1a6d55ae0d01a0e0fa725e97d047cf5333",
          "phase": "production",
          "updates": 1,
          "actual17Adam_steps": [
            662660
          ],
          "failed_partial_prefix": false
        },
        "GO": {
          "learning_started_epoch": 1792357510.9703183,
          "save_deadline": 1792361110.9703183,
          "nominal_end_epoch": 1792361410.9703183,
          "max_parent_seconds": 3900,
          "exit_headroom_seconds": 300,
          "source_SHA": "133847baef60d16a9c2c286b7d2dbde3c1b54cd097fe29d529441bd40fb5c5d4",
          "source_native_CPU_SHA": null,
          "source_CPU_SHA": "b9e73d9c6ba0ac91b4b445bb2a372bb9fdb3d70a599dbcca978992e198de895a",
          "source_qualification_kind": "closed_same_backend_production",
          "original_owner_pid": 246762,
          "original_owner_creation": 1792357507.17,
          "run_id": "THREE_NEXT_CLOSED_HOUR_1792357507814237900",
          "actual_H1_prelaunch_v2_scope_admitted": true
        }
      },
      "recovery": {
        "actual_GO": true,
        "actual_production_log_positive": true,
        "actual_matching_GPU_worker_compute": true,
        "worker": {
          "pid": 54011,
          "creation": 1792357512.86,
          "argv": [
            "/home/lc01/Zonglin Li/zonglin2/compat/glibc240/ld-linux-x86-64.so.2",
            "--library-path",
            "/home/lc01/Zonglin Li/zonglin2/compat/glibc240:/home/lc01/Zonglin Li/zonglin2/envs/mod4/lib",
            "/home/lc01/Zonglin Li/zonglin2/envs/mod4/bin/python",
            "-B",
            "-u",
            "-B",
            "/home/lc01/Zonglin Li/zonglin2/tasks/T3sf5_1910v10/recovery/recovery_worker.py",
            "--job",
            "0",
            "--phase",
            "production"
          ],
          "root": "/home/lc01/Zonglin Li/zonglin2"
        },
        "latest_complete": {
          "epoch": 1792357952.624392,
          "path": "/home/lc01/Zonglin Li/zonglin2/tasks/T3sf5_1910v10/recovery/job0/production/model_update1.pt",
          "bytes": 14714032,
          "SHA": "b6019cb540b09cbc519023ed7397e3b3b3b0346bfd4f9d1d1e7c98caa5a7da90",
          "updates": 1,
          "Adam_step": 674820,
          "phase": "production"
        },
        "GO": {
          "learning_started_epoch": 1792357510.9915593,
          "save_deadline": 1792361110.9915593,
          "nominal_end_epoch": 1792361410.9915593,
          "max_parent_seconds": 3900,
          "exit_headroom_seconds": 300,
          "source_SHA": "b9444feaba2e816de36ecd2a138f1de38b8a625a7b883e4e9ffdb5f748ec25f7",
          "source_native_CPU_SHA": null,
          "source_CPU_SHA": "dd3bca72d71bfb10b5a084444b7ff5f137592297e2e24a234dc3b9c926afc33c",
          "source_qualification_kind": "closed_same_backend_production",
          "original_owner_pid": 246762,
          "original_owner_creation": 1792357507.17,
          "run_id": "THREE_NEXT_CLOSED_HOUR_1792357507814237900",
          "actual_H1_prelaunch_v2_scope_admitted": false
        }
      },
      "e2": {
        "actual_GO": true,
        "actual_production_log_positive": true,
        "actual_matching_GPU_worker_compute": true,
        "worker": {
          "pid": 246793,
          "creation": 1792357510.56,
          "argv": [
            "/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python",
            "-u",
            "-B",
            "/mnt/mod4_linux_durable_20261013/T3sf5_1910v10/e2/native_admission_worker.py",
            "--job",
            "0",
            "--phase",
            "production"
          ],
          "root": "/mnt/mod4_linux_durable_20261013/T3sf5_1910v10/e2"
        },
        "latest_complete": {
          "epoch": 1792357709.081301,
          "path": "/mnt/mod4_linux_durable_20261013/T3sf5_1910v10/e2/job0/production/model_update1.pt",
          "bytes": 14615166,
          "SHA": "746abddf25f8d6a7b989efba093cc3895458707ab05b44185a51fa5134eb8a8f",
          "phase": "production",
          "updates": 1,
          "Adam_step": 710040,
          "kind": "E2_WORLD_MOVING_SIGNED4"
        },
        "GO": {
          "learning_started_epoch": 1792357510.9811845,
          "save_deadline": 1792361110.9811845,
          "nominal_end_epoch": 1792361410.9811845,
          "max_parent_seconds": 3900,
          "exit_headroom_seconds": 300,
          "source_SHA": "94ca10b629fd413065124076cac290ca8b35bfc55bfe13e87ed1853b13d77b15",
          "source_native_CPU_SHA": null,
          "source_CPU_SHA": "57ba0cad222bc66a2e9563bda619f5620c58a9a7b79a0612a2cde1b536869c6a",
          "source_qualification_kind": "closed_same_backend_production",
          "original_owner_pid": 246762,
          "original_owner_creation": 1792357507.17,
          "run_id": "THREE_NEXT_CLOSED_HOUR_1792357507814237900",
          "actual_H1_prelaunch_v2_scope_admitted": false
        }
      }
    },
    "H1_loaded_SCUT_Fudan_recipe": {
      "profile": {
        "version": "scut_fudan_jump_reward_v1",
        "tuck_leg_length_m": 0.22,
        "extend_leg_length_m": 0.31,
        "leg_exp_l1_gain": 4.0,
        "zero_wheel_torque_sigma": 1.5,
        "Fudan_weighted_rate_clip": 2.5,
        "weights": {
          "push_vz": 1.0,
          "flight_vz": 6.0,
          "flight": 0.15,
          "leg_tuck": 1.7,
          "takeoff_extend": 0.5,
          "wheel_below_base": 2.0,
          "air_wheel_zero_torque": 20.0,
          "orientation": -25.0,
          "angular_velocity_xy": -0.1
        },
        "geometry_adaptation": "body-to-wheel 3D lengths from actual MOD4 link poses; tuck .22 SCUT default, extend .31 Fudan target",
        "no_assist_force_or_air_reset_or_privileged_actor_observation": true,
        "flight_mask": "existing H1 air_ticks>0; measured both-wheel clearance, all34 clearance, nonwheel clean and positive-vz history; no new success threshold",
        "active_scope": "H1 public4 request rows with an actual ready attempt; every normal action row retains its original reward"
      },
      "actual_loaded_terms": [
        {
          "name": "ang_vel_xy",
          "weight": -0.05,
          "func": "h1_scut_fudan_jump_reward_v1.mask_replaced_jump_cost",
          "params": "{'original_func': <function ang_vel_xy_jump_exempt at 0x7f69744ee340>, 'original_params': {}}"
        },
        {
          "name": "flat_orientation_y",
          "weight": -1.0,
          "func": "h1_scut_fudan_jump_reward_v1.mask_replaced_jump_cost",
          "params": "{'original_func': <function orientation at 0x7f69744eed40>, 'original_params': {'mode': 'pitch'}}"
        },
        {
          "name": "flat_orientation_y_v",
          "weight": -1.0,
          "func": "h1_scut_fudan_jump_reward_v1.mask_replaced_jump_cost",
          "params": "{'original_func': <function orientation at 0x7f69744eed40>, 'original_params': {'mode': 'pitch_velocity'}}"
        },
        {
          "name": "flat_orientation_x_v",
          "weight": -1.0,
          "func": "h1_scut_fudan_jump_reward_v1.mask_replaced_jump_cost",
          "params": "{'original_func': <function orientation at 0x7f69744eed40>, 'original_params': {'mode': 'roll_velocity'}}"
        },
        {
          "name": "h1_scut_fudan_push_vz",
          "weight": 1.0,
          "func": "h1_scut_fudan_jump_reward_v1.measured_reward",
          "params": "{'name': 'push_vz'}"
        },
        {
          "name": "h1_scut_fudan_flight_vz",
          "weight": 6.0,
          "func": "h1_scut_fudan_jump_reward_v1.measured_reward",
          "params": "{'name': 'flight_vz'}"
        },
        {
          "name": "h1_scut_fudan_flight",
          "weight": 0.15,
          "func": "h1_scut_fudan_jump_reward_v1.measured_reward",
          "params": "{'name': 'flight'}"
        },
        {
          "name": "h1_scut_fudan_leg_tuck",
          "weight": 1.7,
          "func": "h1_scut_fudan_jump_reward_v1.measured_reward",
          "params": "{'name': 'leg_tuck'}"
        },
        {
          "name": "h1_scut_fudan_takeoff_extend",
          "weight": 0.5,
          "func": "h1_scut_fudan_jump_reward_v1.measured_reward",
          "params": "{'name': 'takeoff_extend'}"
        },
        {
          "name": "h1_scut_fudan_wheel_below_base",
          "weight": 2.0,
          "func": "h1_scut_fudan_jump_reward_v1.measured_reward",
          "params": "{'name': 'wheel_below_base'}"
        },
        {
          "name": "h1_scut_fudan_air_wheel_zero_torque",
          "weight": 20.0,
          "func": "h1_scut_fudan_jump_reward_v1.measured_reward",
          "params": "{'name': 'air_wheel_zero_torque'}"
        },
        {
          "name": "h1_scut_fudan_orientation",
          "weight": -25.0,
          "func": "h1_scut_fudan_jump_reward_v1.measured_reward",
          "params": "{'name': 'orientation'}"
        },
        {
          "name": "h1_scut_fudan_angular_velocity_xy",
          "weight": -0.1,
          "func": "h1_scut_fudan_jump_reward_v1.measured_reward",
          "params": "{'name': 'angular_velocity_xy'}"
        }
      ],
      "no_new_actor_input": true
    },
    "H1_actual_SCUT_Fudan_public4_rows_readout": {
      "epoch": 1792357998.0873446,
      "completed": 1,
      "active_rows": 0,
      "airborne_rows": 0,
      "unweighted_rate_means": {
        "push_vz": 0.0,
        "flight_vz": 0.0,
        "flight": 0.0,
        "leg_tuck": 0.0,
        "takeoff_extend": 0.0,
        "wheel_below_base": 0.0,
        "air_wheel_zero_torque": 0.0,
        "orientation": 0.0,
        "angular_velocity_xy": 0.0
      },
      "not_skill_or_final_model_audit": true
    },
    "current_metadata_not_whole_model_CPU_or_skill_qualification": true,
    "no_heavy_mid_hour_checkpoint_or_behavior_audit": true,
    "no_runtime_stop_or_canonical_write": true,
    "actual_finite_transport_returned": true
  },
  "local_recovery": {
    "epoch": 1792357597.8012378,
    "trial_id": "fourth-reward-hour-new-source-local-recovery-and-rate-diagnostic",
    "rows": [
      {
        "source_SHA": "133847baef60d16a9c2c286b7d2dbde3c1b54cd097fe29d529441bd40fb5c5d4",
        "public4_requested": false,
        "yaw": 0.0,
        "ready_before_request": true,
        "prepared_longest_callbacks": 372,
        "strict_counts": {
          "takeoff": 0,
          "landing": 0,
          "recovery": 0
        },
        "event_callback_rows": {
          "takeoff": [],
          "landing": [],
          "recovery": []
        },
        "survived15s": true,
        "duration_s": 15.00000000000684,
        "first_failure": null,
        "request_both_wheel_min_peak_m": -2.2526993798122064e-07,
        "actual_phase_recovery_ticks_max": 0,
        "original_required_recovery_callbacks": 200,
        "longest_readonly_recovery_condition_callbacks": 0,
        "segments": {
          "public4_attempt": {
            "callbacks": 0,
            "failed_recovery_condition_callbacks": {
              "both_wheel_support": 0,
              "nonwheel_clean": 0,
              "geometry_clear": 0,
              "vertical_speed": 0,
              "planar_speed": 0,
              "roll": 0,
              "pitch": 0,
              "yaw": 0
            },
            "all_recovery_conditions_callbacks": 0,
            "pitch_range": null,
            "planar_speed_max": null,
            "weighted_rate_mean": null
          },
          "landed_still_public4": {
            "callbacks": 0,
            "failed_recovery_condition_callbacks": {
              "both_wheel_support": 0,
              "nonwheel_clean": 0,
              "geometry_clear": 0,
              "vertical_speed": 0,
              "planar_speed": 0,
              "roll": 0,
              "pitch": 0,
              "yaw": 0
            },
            "all_recovery_conditions_callbacks": 0,
            "pitch_range": null,
            "planar_speed_max": null,
            "weighted_rate_mean": null
          },
          "landed_normal": {
            "callbacks": 0,
            "failed_recovery_condition_callbacks": {
              "both_wheel_support": 0,
              "nonwheel_clean": 0,
              "geometry_clear": 0,
              "vertical_speed": 0,
              "planar_speed": 0,
              "roll": 0,
              "pitch": 0,
              "yaw": 0
            },
            "all_recovery_conditions_callbacks": 0,
            "pitch_range": null,
            "planar_speed_max": null,
            "weighted_rate_mean": null
          },
          "last_second": {
            "callbacks": 401,
            "failed_recovery_condition_callbacks": {
              "both_wheel_support": 0,
              "nonwheel_clean": 0,
              "geometry_clear": 0,
              "vertical_speed": 0,
              "planar_speed": 401,
              "roll": 0,
              "pitch": 0,
              "yaw": 401
            },
            "all_recovery_conditions_callbacks": 0,
            "pitch_range": [
              -0.011842012399222127,
              -0.01137066812429355
            ],
            "planar_speed_max": 0.056182701591403365,
            "weighted_rate_mean": {
              "push_vz": 0.0,
              "flight_vz": 0.0,
              "flight": 0.0,
              "leg_tuck": 0.0,
              "takeoff_extend": 0.0,
              "wheel_below_base": 0.0,
              "air_wheel_zero_torque": 0.0,
              "orientation": 0.0,
              "angular_velocity_xy": 0.0
            }
          }
        },
        "samples": {
          "request_start": {
            "time_s": 0.9999999999999453,
            "control": 99,
            "mode": 0,
            "pitch": -0.012207324117306304,
            "roll": 0.06964250298927904,
            "planar_speed": 0.04962938564691259,
            "vz": 0.0024886753547323347,
            "world_angular_velocity": [
              -0.0014363326355431045,
              0.002096728586784584,
              0.05435970256654595
            ],
            "body_angular_velocity": [
              -0.0007169120710929047,
              0.005912252623803571,
              0.05409221655030002
            ],
            "policy_action": [
              -6.0,
              1.7114276885986328,
              -0.6281654238700867,
              1.3568397760391235,
              -0.13375182449817657,
              -0.02747437357902527
            ],
            "actuator_torque_hip_crank_wheel_left_right": [
              21.360764302810836,
              -17.454229514904355,
              -0.2255586109827461,
              10.70958230735687,
              -8.694333881017101,
              0.20835852312023787
            ],
            "wheel_support_N": [
              82.56291093410464,
              83.3660805769076
            ],
            "wheel_clearance": [
              -3.575229534771851e-06,
              -9.254955777721063e-07
            ],
            "active": false,
            "airborne": false,
            "recovery_ticks": 0,
            "weighted_rate": {
              "push_vz": 0.0,
              "flight_vz": 0.0,
              "flight": 0.0,
              "leg_tuck": 0.0,
              "takeoff_extend": 0.0,
              "wheel_below_base": 0.0,
              "air_wheel_zero_torque": 0.0,
              "orientation": -0.0,
              "angular_velocity_xy": -0.0
            }
          },
          "request_end": {
            "time_s": 1.7999999999998573,
            "control": 179,
            "mode": 0,
            "pitch": -0.011867762440751568,
            "roll": 0.06923506823487337,
            "planar_speed": 0.05474273995060747,
            "vz": 0.0009225343891846173,
            "world_angular_velocity": [
              0.0009428314552898656,
              0.000581668035540309,
              0.049439991439655696
            ],
            "body_angular_velocity": [
              0.0015650797237399213,
              0.003937537409841935,
              0.04927054238603746
            ],
            "policy_action": [
              -6.0,
              1.7173300981521606,
              -0.6140373349189758,
              1.3583319187164307,
              -0.1375911682844162,
              -0.03415684401988983
            ],
            "actuator_torque_hip_crank_wheel_left_right": [
              21.533999976480352,
              -17.457399565244025,
              -0.2213458299117804,
              10.750691009286149,
              -8.501893779099298,
              0.2088008798465761
            ],
            "wheel_support_N": [
              83.08783071191046,
              84.55684000134923
            ],
            "wheel_clearance": [
              -3.0080565913276347e-06,
              -1.1233902147272934e-06
            ],
            "active": false,
            "airborne": false,
            "recovery_ticks": 0,
            "weighted_rate": {
              "push_vz": 0.0,
              "flight_vz": 0.0,
              "flight": 0.0,
              "leg_tuck": 0.0,
              "takeoff_extend": 0.0,
              "wheel_below_base": 0.0,
              "air_wheel_zero_torque": 0.0,
              "orientation": -0.0,
              "angular_velocity_xy": -0.0
            }
          },
          "one_second_after_request": {
            "time_s": 2.8000000000001024,
            "control": 279,
            "mode": 0,
            "pitch": -0.011732816445318548,
            "roll": 0.06911670540984108,
            "planar_speed": 0.05568412979833096,
            "vz": 0.000389204620650284,
            "world_angular_velocity": [
              0.002055531066922437,
              0.0007520583786043682,
              0.048958958414617317
            ],
            "body_angular_velocity": [
              0.0027007926143388246,
              0.003896346443044991,
              0.04877801361747158
            ],
            "policy_action": [
              -6.0,
              1.718121886253357,
              -0.6128617525100708,
              1.3599019050598145,
              -0.13852886855602264,
              -0.0351107120513916
            ],
            "actuator_torque_hip_crank_wheel_left_right": [
              21.558026678062227,
              -17.46755129469568,
              -0.2238752454516439,
              10.797771000055834,
              -8.516387412909062,
              0.2070888830296549
            ],
            "wheel_support_N": [
              87.71219839450826,
              93.74282218169218
            ],
            "wheel_clearance": [
              -2.99626096002259e-06,
              -8.037422930401439e-07
            ],
            "active": false,
            "airborne": false,
            "recovery_ticks": 0,
            "weighted_rate": {
              "push_vz": 0.0,
              "flight_vz": 0.0,
              "flight": 0.0,
              "leg_tuck": 0.0,
              "takeoff_extend": 0.0,
              "wheel_below_base": 0.0,
              "air_wheel_zero_torque": 0.0,
              "orientation": -0.0,
              "angular_velocity_xy": -0.0
            }
          },
          "final": {
            "time_s": 15.00000000000684,
            "control": 1499,
            "mode": 0,
            "pitch": -0.011472447146926747,
            "roll": 0.06916975871211915,
            "planar_speed": 0.054426180893934466,
            "vz": 0.00019781641002095135,
            "world_angular_velocity": [
              0.00497532847072933,
              -7.77029771841355e-05,
              0.0456539206385232
            ],
            "body_angular_velocity": [
              0.004332950573664167,
              -4.14724098449417e-05,
              0.04571940747842529
            ],
            "policy_action": [
              -6.0,
              1.7158265113830566,
              -0.6112812757492065,
              1.3631248474121094,
              -0.1362125426530838,
              -0.02764517068862915
            ],
            "actuator_torque_hip_crank_wheel_left_right": [
              21.48255041137864,
              -17.557440547144342,
              -0.21771033390853695,
              10.89452062569232,
              -8.460730440475917,
              0.24086915353500907
            ],
            "wheel_support_N": [
              85.79561026733339,
              86.84940765033335
            ],
            "wheel_clearance": [
              -1.9319750126228774e-06,
              -2.479607552757779e-07
            ],
            "active": false,
            "airborne": false,
            "recovery_ticks": 0,
            "weighted_rate": {
              "push_vz": 0.0,
              "flight_vz": 0.0,
              "flight": 0.0,
              "leg_tuck": 0.0,
              "takeoff_extend": 0.0,
              "wheel_below_base": 0.0,
              "air_wheel_zero_torque": 0.0,
              "orientation": -0.0,
              "angular_velocity_xy": -0.0
            }
          }
        },
        "previous_source_SHA": "330220514b9bcf5f5bdf3e8b1280b08932bb4d8e58adeee33ee1b9a5281c8801",
        "previous_counts": {
          "takeoff": 0,
          "landing": 0,
          "recovery": 0
        },
        "previous_duration_s": 15.00000000000684,
        "previous_first_failure": null,
        "raw": {
          "path": "C:\\Users\\lulu\\Desktop\\claude\\mjcf\\MOD4_SCUT_FUDAN_FIFTH_HOUR_20261019\\local_fourth_reward_hour_new_source_trajectories\\after_reward_hour4_normal_0.0.npz",
          "bytes": 1714140,
          "SHA": "35fc624550a85616fcb0a607b3282546a6566256b9884034ac56a83332a3c16f"
        }
      },
      {
        "source_SHA": "133847baef60d16a9c2c286b7d2dbde3c1b54cd097fe29d529441bd40fb5c5d4",
        "public4_requested": false,
        "yaw": 3.141592653589793,
        "ready_before_request": true,
        "prepared_longest_callbacks": 372,
        "strict_counts": {
          "takeoff": 0,
          "landing": 0,
          "recovery": 0
        },
        "event_callback_rows": {
          "takeoff": [],
          "landing": [],
          "recovery": []
        },
        "survived15s": true,
        "duration_s": 15.00000000000684,
        "first_failure": null,
        "request_both_wheel_min_peak_m": -2.2526993785632055e-07,
        "actual_phase_recovery_ticks_max": 0,
        "original_required_recovery_callbacks": 200,
        "longest_readonly_recovery_condition_callbacks": 0,
        "segments": {
          "public4_attempt": {
            "callbacks": 0,
            "failed_recovery_condition_callbacks": {
              "both_wheel_support": 0,
              "nonwheel_clean": 0,
              "geometry_clear": 0,
              "vertical_speed": 0,
              "planar_speed": 0,
              "roll": 0,
              "pitch": 0,
              "yaw": 0
            },
            "all_recovery_conditions_callbacks": 0,
            "pitch_range": null,
            "planar_speed_max": null,
            "weighted_rate_mean": null
          },
          "landed_still_public4": {
            "callbacks": 0,
            "failed_recovery_condition_callbacks": {
              "both_wheel_support": 0,
              "nonwheel_clean": 0,
              "geometry_clear": 0,
              "vertical_speed": 0,
              "planar_speed": 0,
              "roll": 0,
              "pitch": 0,
              "yaw": 0
            },
            "all_recovery_conditions_callbacks": 0,
            "pitch_range": null,
            "planar_speed_max": null,
            "weighted_rate_mean": null
          },
          "landed_normal": {
            "callbacks": 0,
            "failed_recovery_condition_callbacks": {
              "both_wheel_support": 0,
              "nonwheel_clean": 0,
              "geometry_clear": 0,
              "vertical_speed": 0,
              "planar_speed": 0,
              "roll": 0,
              "pitch": 0,
              "yaw": 0
            },
            "all_recovery_conditions_callbacks": 0,
            "pitch_range": null,
            "planar_speed_max": null,
            "weighted_rate_mean": null
          },
          "last_second": {
            "callbacks": 401,
            "failed_recovery_condition_callbacks": {
              "both_wheel_support": 0,
              "nonwheel_clean": 0,
              "geometry_clear": 0,
              "vertical_speed": 0,
              "planar_speed": 401,
              "roll": 0,
              "pitch": 0,
              "yaw": 401
            },
            "all_recovery_conditions_callbacks": 0,
            "pitch_range": [
              -0.011842010474083875,
              -0.011370667155583635
            ],
            "planar_speed_max": 0.05618269068563791,
            "weighted_rate_mean": {
              "push_vz": 0.0,
              "flight_vz": 0.0,
              "flight": 0.0,
              "leg_tuck": 0.0,
              "takeoff_extend": 0.0,
              "wheel_below_base": 0.0,
              "air_wheel_zero_torque": 0.0,
              "orientation": 0.0,
              "angular_velocity_xy": 0.0
            }
          }
        },
        "samples": {
          "request_start": {
            "time_s": 0.9999999999999453,
            "control": 99,
            "mode": 0,
            "pitch": -0.012207324117593794,
            "roll": 0.06964250298929955,
            "planar_speed": 0.049629385647180536,
            "vz": 0.0024886753546785783,
            "world_angular_velocity": [
              0.001436332635565164,
              -0.0020967285854556084,
              0.05435970256668646
            ],
            "body_angular_velocity": [
              -0.0007169120711326215,
              0.005912252622489816,
              0.05409221655053344
            ],
            "policy_action": [
              -6.0,
              1.7114276885986328,
              -0.6281654238700867,
              1.3568397760391235,
              -0.13375182449817657,
              -0.02747437357902527
            ],
            "actuator_torque_hip_crank_wheel_left_right": [
              21.36076430281084,
              -17.454229514910413,
              -0.22555861098503854,
              10.70958230735718,
              -8.694333881018917,
              0.20835852311939468
            ],
            "wheel_support_N": [
              82.56291093407644,
              83.36608057679221
            ],
            "wheel_clearance": [
              -3.5752295349383845e-06,
              -9.254955776749618e-07
            ],
            "active": false,
            "airborne": false,
            "recovery_ticks": 0,
            "weighted_rate": {
              "push_vz": 0.0,
              "flight_vz": 0.0,
              "flight": 0.0,
              "leg_tuck": 0.0,
              "takeoff_extend": 0.0,
              "wheel_below_base": 0.0,
              "air_wheel_zero_torque": 0.0,
              "orientation": -0.0,
              "angular_velocity_xy": -0.0
            }
          },
          "request_end": {
            "time_s": 1.7999999999998573,
            "control": 179,
            "mode": 0,
            "pitch": -0.011867761664826906,
            "roll": 0.06923506816644788,
            "planar_speed": 0.054742745295951974,
            "vz": 0.0009225384652162644,
            "world_angular_velocity": [
              -0.000942817940841839,
              -0.0005817276959077548,
              0.04943998089484793
            ],
            "body_angular_velocity": [
              0.00156506992668333,
              0.003937596948848106,
              0.049270527803725615
            ],
            "policy_action": [
              -6.0,
              1.7173300981521606,
              -0.6140373349189758,
              1.3583319187164307,
              -0.1375911980867386,
              -0.0341569185256958
            ],
            "actuator_torque_hip_crank_wheel_left_right": [
              21.533999975928857,
              -17.457399653186172,
              -0.22134581333386869,
              10.750691011906852,
              -8.501893902519708,
              0.20880068716137265
            ],
            "wheel_support_N": [
              83.08782979028308,
              84.55684031368604
            ],
            "wheel_clearance": [
              -3.0080563050705056e-06,
              -1.1233908756014266e-06
            ],
            "active": false,
            "airborne": false,
            "recovery_ticks": 0,
            "weighted_rate": {
              "push_vz": 0.0,
              "flight_vz": 0.0,
              "flight": 0.0,
              "leg_tuck": 0.0,
              "takeoff_extend": 0.0,
              "wheel_below_base": 0.0,
              "air_wheel_zero_torque": 0.0,
              "orientation": -0.0,
              "angular_velocity_xy": -0.0
            }
          },
          "one_second_after_request": {
            "time_s": 2.8000000000001024,
            "control": 279,
            "mode": 0,
            "pitch": -0.011732820341260988,
            "roll": 0.06911670889357253,
            "planar_speed": 0.055684111850570504,
            "vz": 0.0003892160445875253,
            "world_angular_velocity": [
              -0.0020555813776630895,
              -0.0007520064965766383,
              0.048958924880357586
            ],
            "body_angular_velocity": [
              0.0027008366241224042,
              0.003896287237620091,
              0.0487779835715187
            ],
            "policy_action": [
              -6.0,
              1.718121886253357,
              -0.6128617525100708,
              1.359901785850525,
              -0.13852886855602264,
              -0.03511075675487518
            ],
            "actuator_torque_hip_crank_wheel_left_right": [
              21.5580266755856,
              -17.46755187957349,
              -0.2238753111696496,
              10.797767419466751,
              -8.516387104055068,
              0.2070884481502732
            ],
            "wheel_support_N": [
              87.71219412196474,
              93.74282283316346
            ],
            "wheel_clearance": [
              -2.9962621516527177e-06,
              -8.037461992488337e-07
            ],
            "active": false,
            "airborne": false,
            "recovery_ticks": 0,
            "weighted_rate": {
              "push_vz": 0.0,
              "flight_vz": 0.0,
              "flight": 0.0,
              "leg_tuck": 0.0,
              "takeoff_extend": 0.0,
              "wheel_below_base": 0.0,
              "air_wheel_zero_torque": 0.0,
              "orientation": -0.0,
              "angular_velocity_xy": -0.0
            }
          },
          "final": {
            "time_s": 15.00000000000684,
            "control": 1499,
            "mode": 0,
            "pitch": -0.01147244354547452,
            "roll": 0.06916976325297779,
            "planar_speed": 0.05442616964332756,
            "vz": 0.00019783591963020325,
            "world_angular_velocity": [
              -0.004975294594468627,
              7.775135049122636e-05,
              0.04565396004969453
            ],
            "body_angular_velocity": [
              0.0043328940575953455,
              -4.1485518571852086e-05,
              0.04571944857312646
            ],
            "policy_action": [
              -6.0,
              1.7158265113830566,
              -0.6112812757492065,
              1.3631248474121094,
              -0.13621260225772858,
              -0.027645155787467957
            ],
            "actuator_torque_hip_crank_wheel_left_right": [
              21.48255041269024,
              -17.55744063038576,
              -0.21771062467309166,
              10.89452062213294,
              -8.460729911806137,
              0.24086936994792965
            ],
            "wheel_support_N": [
              85.79561669466399,
              86.84941099219381
            ],
            "wheel_clearance": [
              -1.931974507624057e-06,
              -2.479545592737331e-07
            ],
            "active": false,
            "airborne": false,
            "recovery_ticks": 0,
            "weighted_rate": {
              "push_vz": 0.0,
              "flight_vz": 0.0,
              "flight": 0.0,
              "leg_tuck": 0.0,
              "takeoff_extend": 0.0,
              "wheel_below_base": 0.0,
              "air_wheel_zero_torque": 0.0,
              "orientation": -0.0,
              "angular_velocity_xy": -0.0
            }
          }
        },
        "previous_source_SHA": "330220514b9bcf5f5bdf3e8b1280b08932bb4d8e58adeee33ee1b9a5281c8801",
        "previous_counts": {
          "takeoff": 0,
          "landing": 0,
          "recovery": 0
        },
        "previous_duration_s": 15.00000000000684,
        "previous_first_failure": null,
        "raw": {
          "path": "C:\\Users\\lulu\\Desktop\\claude\\mjcf\\MOD4_SCUT_FUDAN_FIFTH_HOUR_20261019\\local_fourth_reward_hour_new_source_trajectories\\after_reward_hour4_normal_3.1416.npz",
          "bytes": 1711420,
          "SHA": "137fa2dda8b979a09a99412c1a7d0a3478b2c9d0d6f5c47b77a0a83380ac9663"
        }
      },
      {
        "source_SHA": "133847baef60d16a9c2c286b7d2dbde3c1b54cd097fe29d529441bd40fb5c5d4",
        "public4_requested": true,
        "yaw": 0.0,
        "ready_before_request": true,
        "prepared_longest_callbacks": 372,
        "strict_counts": {
          "takeoff": 1,
          "landing": 1,
          "recovery": 0
        },
        "event_callback_rows": {
          "takeoff": [
            {
              "time_s": 1.129999999999931,
              "control": 112,
              "mode": 4,
              "pitch": -0.069728927994574,
              "roll": 0.035429769905166754,
              "planar_speed": 0.04530668499057865,
              "vz": 0.47768040092564246,
              "world_angular_velocity": [
                0.050329312919808286,
                0.016541503616101065,
                0.3931387362253626
              ],
              "body_angular_velocity": [
                0.07797270092305654,
                0.029108693614057806,
                0.38786295114200176
              ],
              "policy_action": [
                -6.0,
                1.8671658039093018,
                -0.3188243508338928,
                2.0857110023498535,
                -0.4461216926574707,
                2.390836000442505
              ],
              "actuator_torque_hip_crank_wheel_left_right": [
                31.605205503625438,
                -40.0,
                -0.019860475028562696,
                30.702224952945702,
                -37.94647830279369,
                -0.0037577595396420804
              ],
              "wheel_support_N": [
                0.0,
                0.0
              ],
              "wheel_clearance": [
                0.026822466559672437,
                0.029245375286479414
              ],
              "active": true,
              "airborne": true,
              "recovery_ticks": 0,
              "weighted_rate": {
                "push_vz": 0.0,
                "flight_vz": 2.5,
                "flight": 0.15000000596046448,
                "leg_tuck": 0.5124275088310242,
                "takeoff_extend": 0.0,
                "wheel_below_base": 0.6132673025131226,
                "air_wheel_zero_torque": 19.99649429321289,
                "orientation": -0.15257252752780914,
                "angular_velocity_xy": -0.0006927057984285057
              }
            }
          ],
          "landing": [
            {
              "time_s": 1.3224999999999099,
              "control": 132,
              "mode": 4,
              "pitch": 0.07497762815390635,
              "roll": -0.015261209323992922,
              "planar_speed": 0.09427812380622287,
              "vz": -0.7526709225914786,
              "world_angular_velocity": [
                -0.4108368543302323,
                0.1633418210469152,
                0.5584967806347161
              ],
              "body_angular_velocity": [
                -0.4402935394818834,
                0.18115195080671748,
                0.5298223241499573
              ],
              "policy_action": [
                -6.0,
                1.0177226066589355,
                -0.172902911901474,
                0.6725587844848633,
                1.120356559753418,
                1.628174066543579
              ],
              "actuator_torque_hip_crank_wheel_left_right": [
                19.602792455875417,
                -10.678349005615493,
                -4.512485732781795,
                -1.1189653610948853,
                2.167503046781615,
                -2.1662356640450757
              ],
              "wheel_support_N": [
                117.62723544928458,
                205.41311783324986
              ],
              "wheel_clearance": [
                4.526402142462915e-06,
                2.9725084904896892e-06
              ],
              "active": true,
              "airborne": false,
              "recovery_ticks": 0,
              "weighted_rate": {
                "push_vz": 0.0,
                "flight_vz": -0.0,
                "flight": 0.0,
                "leg_tuck": 0.0,
                "takeoff_extend": 0.0,
                "wheel_below_base": 0.0,
                "air_wheel_zero_torque": 0.0,
                "orientation": -0.14606745541095734,
                "angular_velocity_xy": -0.02266744337975979
              }
            }
          ],
          "recovery": []
        },
        "survived15s": true,
        "duration_s": 15.00000000000684,
        "first_failure": null,
        "request_both_wheel_min_peak_m": 0.048889612569783455,
        "actual_phase_recovery_ticks_max": 110,
        "original_required_recovery_callbacks": 200,
        "longest_readonly_recovery_condition_callbacks": 110,
        "segments": {
          "public4_attempt": {
            "callbacks": 320,
            "failed_recovery_condition_callbacks": {
              "both_wheel_support": 191,
              "nonwheel_clean": 0,
              "geometry_clear": 0,
              "vertical_speed": 315,
              "planar_speed": 317,
              "roll": 0,
              "pitch": 0,
              "yaw": 0
            },
            "all_recovery_conditions_callbacks": 0,
            "pitch_range": [
              -0.069728927994574,
              0.11827910079112473
            ],
            "planar_speed_max": 0.4423646764960691,
            "weighted_rate_mean": {
              "push_vz": 0.22642782527254895,
              "flight_vz": 0.34609528733417394,
              "flight": 0.06234375247731805,
              "leg_tuck": 0.24288323074579238,
              "takeoff_extend": 0.10332431914284826,
              "wheel_below_base": 0.33497700206935405,
              "air_wheel_zero_torque": 7.289072331786156,
              "orientation": -0.11944348087713479,
              "angular_velocity_xy": -0.12122313742515871
            }
          },
          "landed_still_public4": {
            "callbacks": 192,
            "failed_recovery_condition_callbacks": {
              "both_wheel_support": 95,
              "nonwheel_clean": 0,
              "geometry_clear": 0,
              "vertical_speed": 189,
              "planar_speed": 190,
              "roll": 0,
              "pitch": 0,
              "yaw": 0
            },
            "all_recovery_conditions_callbacks": 0,
            "pitch_range": [
              -0.034485009654785036,
              0.11827910079112473
            ],
            "planar_speed_max": 0.4423646764960691,
            "weighted_rate_mean": {
              "push_vz": 0.23383641336113214,
              "flight_vz": 0.2423879106839498,
              "flight": 0.04531250180055698,
              "leg_tuck": 0.17723649895439544,
              "takeoff_extend": 0.11165728280320764,
              "wheel_below_base": 0.24684215368082127,
              "air_wheel_zero_torque": 5.152618057094514,
              "orientation": -0.14781237794106042,
              "angular_velocity_xy": -0.15975152312360782
            }
          },
          "landed_normal": {
            "callbacks": 5280,
            "failed_recovery_condition_callbacks": {
              "both_wheel_support": 74,
              "nonwheel_clean": 0,
              "geometry_clear": 0,
              "vertical_speed": 124,
              "planar_speed": 5170,
              "roll": 0,
              "pitch": 0,
              "yaw": 3926
            },
            "all_recovery_conditions_callbacks": 110,
            "pitch_range": [
              -0.012019267814745632,
              0.09465827704611803
            ],
            "planar_speed_max": 0.20662896765536534,
            "weighted_rate_mean": {
              "push_vz": 0.0,
              "flight_vz": 0.0,
              "flight": 0.0,
              "leg_tuck": 0.0,
              "takeoff_extend": 0.0,
              "wheel_below_base": 0.0,
              "air_wheel_zero_torque": 0.0,
              "orientation": 0.0,
              "angular_velocity_xy": 0.0
            }
          },
          "last_second": {
            "callbacks": 401,
            "failed_recovery_condition_callbacks": {
              "both_wheel_support": 0,
              "nonwheel_clean": 0,
              "geometry_clear": 0,
              "vertical_speed": 0,
              "planar_speed": 401,
              "roll": 0,
              "pitch": 0,
              "yaw": 401
            },
            "all_recovery_conditions_callbacks": 0,
            "pitch_range": [
              -0.011842008330531919,
              -0.011433579365383742
            ],
            "planar_speed_max": 0.05618269110118894,
            "weighted_rate_mean": {
              "push_vz": 0.0,
              "flight_vz": 0.0,
              "flight": 0.0,
              "leg_tuck": 0.0,
              "takeoff_extend": 0.0,
              "wheel_below_base": 0.0,
              "air_wheel_zero_torque": 0.0,
              "orientation": 0.0,
              "angular_velocity_xy": 0.0
            }
          }
        },
        "samples": {
          "request_start": {
            "time_s": 0.9999999999999453,
            "control": 99,
            "mode": 0,
            "pitch": -0.012207324117306304,
            "roll": 0.06964250298927904,
            "planar_speed": 0.04962938564691259,
            "vz": 0.0024886753547323347,
            "world_angular_velocity": [
              -0.0014363326355431045,
              0.002096728586784584,
              0.05435970256654595
            ],
            "body_angular_velocity": [
              -0.0007169120710929047,
              0.005912252623803571,
              0.05409221655030002
            ],
            "policy_action": [
              -6.0,
              1.7114276885986328,
              -0.6281654238700867,
              1.3568397760391235,
              -0.13375182449817657,
              -0.02747437357902527
            ],
            "actuator_torque_hip_crank_wheel_left_right": [
              21.360764302810836,
              -17.454229514904355,
              -0.2255586109827461,
              10.70958230735687,
              -8.694333881017101,
              0.20835852312023787
            ],
            "wheel_support_N": [
              82.56291093410464,
              83.3660805769076
            ],
            "wheel_clearance": [
              -3.575229534771851e-06,
              -9.254955777721063e-07
            ],
            "active": false,
            "airborne": false,
            "recovery_ticks": 0,
            "weighted_rate": {
              "push_vz": 0.0,
              "flight_vz": 0.0,
              "flight": 0.0,
              "leg_tuck": 0.0,
              "takeoff_extend": 0.0,
              "wheel_below_base": 0.0,
              "air_wheel_zero_torque": 0.0,
              "orientation": -0.0,
              "angular_velocity_xy": -0.0
            }
          },
          "request_end": {
            "time_s": 1.7999999999998573,
            "control": 179,
            "mode": 4,
            "pitch": 0.020127131596394413,
            "roll": -0.04174841864256764,
            "planar_speed": 0.20937373165095166,
            "vz": 0.9921023659413148,
            "world_angular_velocity": [
              0.23502815253660536,
              -0.7431682360145129,
              0.0749491588860334
            ],
            "body_angular_velocity": [
              0.20096190467256114,
              -0.7553212256944514,
              0.04752677991642132
            ],
            "policy_action": [
              -6.0,
              2.1864688396453857,
              0.42697858810424805,
              1.5439029932022095,
              -1.632226586341858,
              -1.4917364120483398
            ],
            "actuator_torque_hip_crank_wheel_left_right": [
              39.16565029394562,
              -32.26971173298885,
              0.07497721904279828,
              28.804065584005862,
              -17.088299456177484,
              1.7058430971687435
            ],
            "wheel_support_N": [
              0.0,
              46.67776224738291
            ],
            "wheel_clearance": [
              0.0029943733294894997,
              5.900390825895607e-05
            ],
            "active": true,
            "airborne": false,
            "recovery_ticks": 0,
            "weighted_rate": {
              "push_vz": 0.9921023845672607,
              "flight_vz": 0.0,
              "flight": 0.0,
              "leg_tuck": 0.0,
              "takeoff_extend": 0.3958728611469269,
              "wheel_below_base": 0.0,
              "air_wheel_zero_torque": 0.0,
              "orientation": -0.053656481206417084,
              "angular_velocity_xy": -0.06108958274126053
            }
          },
          "one_second_after_request": {
            "time_s": 2.8000000000001024,
            "control": 279,
            "mode": 0,
            "pitch": -0.0119434722700827,
            "roll": 0.07065431253829466,
            "planar_speed": 0.04450089157043322,
            "vz": 0.0008572655786570777,
            "world_angular_velocity": [
              -0.010226860919856652,
              -0.0020757022320013275,
              0.056047824519223494
            ],
            "body_angular_velocity": [
              -0.009698265610709574,
              0.0027876179836506115,
              0.05611086069103775
            ],
            "policy_action": [
              -6.0,
              1.710036277770996,
              -0.6214011311531067,
              1.341524362564087,
              -0.12352176010608673,
              -0.01826229691505432
            ],
            "actuator_torque_hip_crank_wheel_left_right": [
              21.303358937546754,
              -17.44899356946861,
              -0.23936481674633,
              10.254388714849863,
              -8.269155803846289,
              0.1964377681327987
            ],
            "wheel_support_N": [
              80.9362221911772,
              84.8113607991068
            ],
            "wheel_clearance": [
              5.69565219488144e-07,
              -4.809384970411168e-06
            ],
            "active": false,
            "airborne": false,
            "recovery_ticks": 0,
            "weighted_rate": {
              "push_vz": 0.0,
              "flight_vz": 0.0,
              "flight": 0.0,
              "leg_tuck": 0.0,
              "takeoff_extend": 0.0,
              "wheel_below_base": 0.0,
              "air_wheel_zero_torque": 0.0,
              "orientation": -0.0,
              "angular_velocity_xy": -0.0
            }
          },
          "final": {
            "time_s": 15.00000000000684,
            "control": 1499,
            "mode": 0,
            "pitch": -0.011657822234743657,
            "roll": 0.06933572004913838,
            "planar_speed": 0.05511820945849278,
            "vz": 0.0012331937867363797,
            "world_angular_velocity": [
              -0.00033168183229106757,
              0.0014245773389915993,
              0.047532122809359985
            ],
            "body_angular_velocity": [
              0.0011627735651042802,
              0.004619126631872877,
              0.047315470609428936
            ],
            "policy_action": [
              -6.0,
              1.7175171375274658,
              -0.6081097722053528,
              1.3595494031906128,
              -0.14164124429225922,
              -0.035237714648246765
            ],
            "actuator_torque_hip_crank_wheel_left_right": [
              21.536389916647117,
              -17.463024496882845,
              -0.23247084477434385,
              10.787496011554314,
              -8.31571657084687,
              0.22232555240806054
            ],
            "wheel_support_N": [
              86.88160825271034,
              88.77411468404047
            ],
            "wheel_clearance": [
              -2.3214363117501913e-06,
              -4.455008893594625e-07
            ],
            "active": false,
            "airborne": false,
            "recovery_ticks": 0,
            "weighted_rate": {
              "push_vz": 0.0,
              "flight_vz": 0.0,
              "flight": 0.0,
              "leg_tuck": 0.0,
              "takeoff_extend": 0.0,
              "wheel_below_base": 0.0,
              "air_wheel_zero_torque": 0.0,
              "orientation": -0.0,
              "angular_velocity_xy": -0.0
            }
          }
        },
        "previous_source_SHA": "330220514b9bcf5f5bdf3e8b1280b08932bb4d8e58adeee33ee1b9a5281c8801",
        "previous_counts": {
          "takeoff": 1,
          "landing": 1,
          "recovery": 0
        },
        "previous_duration_s": 1.4924999999998911,
        "previous_first_failure": {
          "time": 1.4924999999998911,
          "control": 149,
          "kind": "bad_orientation_local_tilt_0.75",
          "mode": 4,
          "roll": 0.14703802228378335,
          "pitch": -0.7511251431698834
        },
        "raw": {
          "path": "C:\\Users\\lulu\\Desktop\\claude\\mjcf\\MOD4_SCUT_FUDAN_FIFTH_HOUR_20261019\\local_fourth_reward_hour_new_source_trajectories\\after_reward_hour4_jump_0.0.npz",
          "bytes": 1719933,
          "SHA": "e69fb5df852029c04462c75f53a18c4360df9fad5e5df27414e8acdbacb55cf0"
        }
      },
      {
        "source_SHA": "133847baef60d16a9c2c286b7d2dbde3c1b54cd097fe29d529441bd40fb5c5d4",
        "public4_requested": true,
        "yaw": 3.141592653589793,
        "ready_before_request": true,
        "prepared_longest_callbacks": 372,
        "strict_counts": {
          "takeoff": 1,
          "landing": 1,
          "recovery": 0
        },
        "event_callback_rows": {
          "takeoff": [
            {
              "time_s": 1.129999999999931,
              "control": 112,
              "mode": 4,
              "pitch": -0.06972892799505688,
              "roll": 0.03542976990525395,
              "planar_speed": 0.045306684990896726,
              "vz": 0.47768040092597247,
              "world_angular_velocity": [
                -0.050329312920146085,
                -0.016541503615420578,
                0.39313873622636414
              ],
              "body_angular_velocity": [
                0.07797270092363578,
                0.02910869361343435,
                0.38786295114296265
              ],
              "policy_action": [
                -6.0,
                1.8671658039093018,
                -0.3188243508338928,
                2.0857110023498535,
                -0.4461216926574707,
                2.390836000442505
              ],
              "actuator_torque_hip_crank_wheel_left_right": [
                31.605205503627175,
                -40.0,
                -0.019860475029256006,
                30.702224952943144,
                -37.94647830278632,
                -0.0037577595393308624
              ],
              "wheel_support_N": [
                0.0,
                0.0
              ],
              "wheel_clearance": [
                0.026822466559672214,
                0.029245375286464703
              ],
              "active": true,
              "airborne": true,
              "recovery_ticks": 0,
              "weighted_rate": {
                "push_vz": 0.0,
                "flight_vz": 2.5,
                "flight": 0.15000000596046448,
                "leg_tuck": 0.5124275088310242,
                "takeoff_extend": 0.0,
                "wheel_below_base": 0.6132673025131226,
                "air_wheel_zero_torque": 19.99649429321289,
                "orientation": -0.15257252752780914,
                "angular_velocity_xy": -0.0006927057984285057
              }
            }
          ],
          "landing": [
            {
              "time_s": 1.3224999999999099,
              "control": 132,
              "mode": 4,
              "pitch": 0.07497762815303415,
              "roll": -0.015261209323908733,
              "planar_speed": 0.09427812380662627,
              "vz": -0.7526709225917682,
              "world_angular_velocity": [
                0.4108368543311401,
                -0.16334182104270228,
                0.5584967806398347
              ],
              "body_angular_velocity": [
                -0.4402935394829231,
                0.18115195080264943,
                0.5298223241552835
              ],
              "policy_action": [
                -6.0,
                1.0177226066589355,
                -0.172902911901474,
                0.6725587844848633,
                1.120356559753418,
                1.628174066543579
              ],
              "actuator_torque_hip_crank_wheel_left_right": [
                19.602792455908773,
                -10.678349005616091,
                -4.5124857327727765,
                -1.118965361091516,
                2.1675030467703795,
                -2.166235664051616
              ],
              "wheel_support_N": [
                117.62723544913533,
                205.4131178332945
              ],
              "wheel_clearance": [
                4.526402143018027e-06,
                2.9725084904896892e-06
              ],
              "active": true,
              "airborne": false,
              "recovery_ticks": 0,
              "weighted_rate": {
                "push_vz": 0.0,
                "flight_vz": -0.0,
                "flight": 0.0,
                "leg_tuck": 0.0,
                "takeoff_extend": 0.0,
                "wheel_below_base": 0.0,
                "air_wheel_zero_torque": 0.0,
                "orientation": -0.14606745541095734,
                "angular_velocity_xy": -0.02266744337975979
              }
            }
          ],
          "recovery": []
        },
        "survived15s": true,
        "duration_s": 15.00000000000684,
        "first_failure": null,
        "request_both_wheel_min_peak_m": 0.048889612569815694,
        "actual_phase_recovery_ticks_max": 110,
        "original_required_recovery_callbacks": 200,
        "longest_readonly_recovery_condition_callbacks": 110,
        "segments": {
          "public4_attempt": {
            "callbacks": 320,
            "failed_recovery_condition_callbacks": {
              "both_wheel_support": 191,
              "nonwheel_clean": 0,
              "geometry_clear": 0,
              "vertical_speed": 315,
              "planar_speed": 317,
              "roll": 0,
              "pitch": 0,
              "yaw": 0
            },
            "all_recovery_conditions_callbacks": 0,
            "pitch_range": [
              -0.06972892799505688,
              0.11827910078764979
            ],
            "planar_speed_max": 0.442364676495399,
            "weighted_rate_mean": {
              "push_vz": 0.22642782527254895,
              "flight_vz": 0.34609528733417394,
              "flight": 0.06234375247731805,
              "leg_tuck": 0.24288323074579238,
              "takeoff_extend": 0.10332431914284826,
              "wheel_below_base": 0.33497700206935405,
              "air_wheel_zero_torque": 7.289072331786156,
              "orientation": -0.11944348087713479,
              "angular_velocity_xy": -0.12122313742515871
            }
          },
          "landed_still_public4": {
            "callbacks": 192,
            "failed_recovery_condition_callbacks": {
              "both_wheel_support": 95,
              "nonwheel_clean": 0,
              "geometry_clear": 0,
              "vertical_speed": 189,
              "planar_speed": 190,
              "roll": 0,
              "pitch": 0,
              "yaw": 0
            },
            "all_recovery_conditions_callbacks": 0,
            "pitch_range": [
              -0.03448500965691688,
              0.11827910078764979
            ],
            "planar_speed_max": 0.442364676495399,
            "weighted_rate_mean": {
              "push_vz": 0.23383641336113214,
              "flight_vz": 0.2423879106839498,
              "flight": 0.04531250180055698,
              "leg_tuck": 0.17723649895439544,
              "takeoff_extend": 0.11165728280320764,
              "wheel_below_base": 0.24684215368082127,
              "air_wheel_zero_torque": 5.152618057094514,
              "orientation": -0.14781237794106042,
              "angular_velocity_xy": -0.15975152312360782
            }
          },
          "landed_normal": {
            "callbacks": 5280,
            "failed_recovery_condition_callbacks": {
              "both_wheel_support": 74,
              "nonwheel_clean": 0,
              "geometry_clear": 0,
              "vertical_speed": 124,
              "planar_speed": 5170,
              "roll": 0,
              "pitch": 0,
              "yaw": 3926
            },
            "all_recovery_conditions_callbacks": 110,
            "pitch_range": [
              -0.012019265201900171,
              0.09465827702969858
            ],
            "planar_speed_max": 0.20662896764497976,
            "weighted_rate_mean": {
              "push_vz": 0.0,
              "flight_vz": 0.0,
              "flight": 0.0,
              "leg_tuck": 0.0,
              "takeoff_extend": 0.0,
              "wheel_below_base": 0.0,
              "air_wheel_zero_torque": 0.0,
              "orientation": 0.0,
              "angular_velocity_xy": 0.0
            }
          },
          "last_second": {
            "callbacks": 401,
            "failed_recovery_condition_callbacks": {
              "both_wheel_support": 0,
              "nonwheel_clean": 0,
              "geometry_clear": 0,
              "vertical_speed": 0,
              "planar_speed": 401,
              "roll": 0,
              "pitch": 0,
              "yaw": 401
            },
            "all_recovery_conditions_callbacks": 0,
            "pitch_range": [
              -0.011842011681648276,
              -0.011433578903369703
            ],
            "planar_speed_max": 0.05618270584550545,
            "weighted_rate_mean": {
              "push_vz": 0.0,
              "flight_vz": 0.0,
              "flight": 0.0,
              "leg_tuck": 0.0,
              "takeoff_extend": 0.0,
              "wheel_below_base": 0.0,
              "air_wheel_zero_torque": 0.0,
              "orientation": 0.0,
              "angular_velocity_xy": 0.0
            }
          }
        },
        "samples": {
          "request_start": {
            "time_s": 0.9999999999999453,
            "control": 99,
            "mode": 0,
            "pitch": -0.012207324117593794,
            "roll": 0.06964250298929955,
            "planar_speed": 0.049629385647180536,
            "vz": 0.0024886753546785783,
            "world_angular_velocity": [
              0.001436332635565164,
              -0.0020967285854556084,
              0.05435970256668646
            ],
            "body_angular_velocity": [
              -0.0007169120711326215,
              0.005912252622489816,
              0.05409221655053344
            ],
            "policy_action": [
              -6.0,
              1.7114276885986328,
              -0.6281654238700867,
              1.3568397760391235,
              -0.13375182449817657,
              -0.02747437357902527
            ],
            "actuator_torque_hip_crank_wheel_left_right": [
              21.36076430281084,
              -17.454229514910413,
              -0.22555861098503854,
              10.70958230735718,
              -8.694333881018917,
              0.20835852311939468
            ],
            "wheel_support_N": [
              82.56291093407644,
              83.36608057679221
            ],
            "wheel_clearance": [
              -3.5752295349383845e-06,
              -9.254955776749618e-07
            ],
            "active": false,
            "airborne": false,
            "recovery_ticks": 0,
            "weighted_rate": {
              "push_vz": 0.0,
              "flight_vz": 0.0,
              "flight": 0.0,
              "leg_tuck": 0.0,
              "takeoff_extend": 0.0,
              "wheel_below_base": 0.0,
              "air_wheel_zero_torque": 0.0,
              "orientation": -0.0,
              "angular_velocity_xy": -0.0
            }
          },
          "request_end": {
            "time_s": 1.7999999999998573,
            "control": 179,
            "mode": 4,
            "pitch": 0.020127131588595106,
            "roll": -0.041748418642757294,
            "planar_speed": 0.20937373164033332,
            "vz": 0.9921023659457305,
            "world_angular_velocity": [
              -0.23502815254716244,
              0.7431682360661291,
              0.07494915887449095
            ],
            "body_angular_velocity": [
              0.20096190468319525,
              -0.7553212257455045,
              0.047526779901224156
            ],
            "policy_action": [
              -6.0,
              2.1864688396453857,
              0.42697858810424805,
              1.5439029932022095,
              -1.632226586341858,
              -1.4917364120483398
            ],
            "actuator_torque_hip_crank_wheel_left_right": [
              39.16565029384157,
              -32.26971173277367,
              0.07497721904452063,
              28.80406558391347,
              -17.08829945611031,
              1.7058430971718472
            ],
            "wheel_support_N": [
              0.0,
              46.67776224850728
            ],
            "wheel_clearance": [
              0.0029943733295124814,
              5.900390824170598e-05
            ],
            "active": true,
            "airborne": false,
            "recovery_ticks": 0,
            "weighted_rate": {
              "push_vz": 0.9921023845672607,
              "flight_vz": 0.0,
              "flight": 0.0,
              "leg_tuck": 0.0,
              "takeoff_extend": 0.3958728611469269,
              "wheel_below_base": 0.0,
              "air_wheel_zero_torque": 0.0,
              "orientation": -0.053656481206417084,
              "angular_velocity_xy": -0.06108958274126053
            }
          },
          "one_second_after_request": {
            "time_s": 2.8000000000001024,
            "control": 279,
            "mode": 0,
            "pitch": -0.01194347296356856,
            "roll": 0.07065431208126101,
            "planar_speed": 0.044500892905393455,
            "vz": 0.0008572312999406479,
            "world_angular_velocity": [
              0.010226808620558804,
              0.00207564323949553,
              0.05604786657728418
            ],
            "body_angular_velocity": [
              -0.009698207849630217,
              0.0027876749478500523,
              0.05611089814086698
            ],
            "policy_action": [
              -6.0,
              1.710036277770996,
              -0.6214011907577515,
              1.341524362564087,
              -0.12352178990840912,
              -0.018262207508087158
            ],
            "actuator_torque_hip_crank_wheel_left_right": [
              21.30335893853901,
              -17.448993253820426,
              -0.23936508781477023,
              10.254388689721557,
              -8.26915702351745,
              0.19643784466698141
            ],
            "wheel_support_N": [
              80.93622259279265,
              84.81135538761049
            ],
            "wheel_clearance": [
              5.695633878144424e-07,
              -4.809383678805457e-06
            ],
            "active": false,
            "airborne": false,
            "recovery_ticks": 0,
            "weighted_rate": {
              "push_vz": 0.0,
              "flight_vz": 0.0,
              "flight": 0.0,
              "leg_tuck": 0.0,
              "takeoff_extend": 0.0,
              "wheel_below_base": 0.0,
              "air_wheel_zero_torque": 0.0,
              "orientation": -0.0,
              "angular_velocity_xy": -0.0
            }
          },
          "final": {
            "time_s": 15.00000000000684,
            "control": 1499,
            "mode": 0,
            "pitch": -0.011657821846998703,
            "roll": 0.06933571985748636,
            "planar_speed": 0.05511821031982922,
            "vz": 0.0012331818163900143,
            "world_angular_velocity": [
              0.0003316838511418633,
              -0.0014246116896858346,
              0.047532134670347476
            ],
            "body_angular_velocity": [
              0.0011627930462291172,
              0.004619155795583981,
              0.04731548024728602
            ],
            "policy_action": [
              -6.0,
              1.7175171375274658,
              -0.6081097722053528,
              1.3595495223999023,
              -0.14164124429225922,
              -0.035237640142440796
            ],
            "actuator_torque_hip_crank_wheel_left_right": [
              21.536389917301506,
              -17.463024489466243,
              -0.23247086219115876,
              10.787499594751049,
              -8.315716447489478,
              0.22232584329483834
            ],
            "wheel_support_N": [
              86.8816063652359,
              88.77411231318955
            ],
            "wheel_clearance": [
              -2.321437429952944e-06,
              -4.455003044523398e-07
            ],
            "active": false,
            "airborne": false,
            "recovery_ticks": 0,
            "weighted_rate": {
              "push_vz": 0.0,
              "flight_vz": 0.0,
              "flight": 0.0,
              "leg_tuck": 0.0,
              "takeoff_extend": 0.0,
              "wheel_below_base": 0.0,
              "air_wheel_zero_torque": 0.0,
              "orientation": -0.0,
              "angular_velocity_xy": -0.0
            }
          }
        },
        "previous_source_SHA": "330220514b9bcf5f5bdf3e8b1280b08932bb4d8e58adeee33ee1b9a5281c8801",
        "previous_counts": {
          "takeoff": 1,
          "landing": 1,
          "recovery": 0
        },
        "previous_duration_s": 1.4924999999998911,
        "previous_first_failure": {
          "time": 1.4924999999998911,
          "control": 149,
          "kind": "bad_orientation_local_tilt_0.75",
          "mode": 4,
          "roll": 0.14703802228739857,
          "pitch": -0.7511251431779435
        },
        "raw": {
          "path": "C:\\Users\\lulu\\Desktop\\claude\\mjcf\\MOD4_SCUT_FUDAN_FIFTH_HOUR_20261019\\local_fourth_reward_hour_new_source_trajectories\\after_reward_hour4_jump_3.1416.npz",
          "bytes": 1717455,
          "SHA": "adb2cc737f3088315ccccdb901a2844d31ba418cac315bf5e9ba1b7f7d05ec56"
        }
      }
    ],
    "original_thresholds_and_external_request_clock_unchanged": true,
    "all_normal_rows_new_reward_terms_zero": true,
    "weighted_Fudan_rate_limit_verified": true,
    "rate_evidence": "Read-only evaluation of installed formula on current local MuJoCo callback state; not an actual PhysX RewardManager/PPO reward readback. Callback rates are not summed as training return.",
    "no_old_case_replay": true,
    "not_PhysX_or_statistical_or_unique_causal_result": true,
    "no_live_player_GPU_reward_LR_STD_physics_or_budget_change": true
  },
  "normal_drift": {
    "epoch": 1792357680.265142,
    "rows": [
      {
        "yaw": 0.0,
        "new": {
          "source_SHA": "133847baef60d16a9c2c286b7d2dbde3c1b54cd097fe29d529441bd40fb5c5d4",
          "survived15s": true,
          "duration_s": 15.00000000000684,
          "final_speed_m_s": 0.054426180893934466,
          "last_second_mean_speed_m_s": 0.054908466756760435,
          "final_yaw_drift_rad": 0.683186169831631,
          "net_planar_displacement_m": 0.803559701097908,
          "planar_path_length_m": 0.8364675857379932,
          "raw": {
            "path": "C:\\Users\\lulu\\Desktop\\claude\\mjcf\\MOD4_SCUT_FUDAN_FIFTH_HOUR_20261019\\local_fourth_reward_hour_new_source_trajectories\\after_reward_hour4_normal_0.0.npz",
            "bytes": 1714140,
            "SHA": "35fc624550a85616fcb0a607b3282546a6566256b9884034ac56a83332a3c16f"
          }
        },
        "previous": {
          "source_SHA": "330220514b9bcf5f5bdf3e8b1280b08932bb4d8e58adeee33ee1b9a5281c8801",
          "survived15s": true,
          "duration_s": 15.00000000000684,
          "final_speed_m_s": 0.014072830421317153,
          "last_second_mean_speed_m_s": 0.022219254350633006,
          "final_yaw_drift_rad": 0.6671696075911129,
          "net_planar_displacement_m": 0.28937822829158927,
          "planar_path_length_m": 0.40028702235430375,
          "raw": {
            "path": "C:\\Users\\lulu\\Desktop\\claude\\mjcf\\MOD4_SCUT_FUDAN_FOURTH_HOUR_20261019\\local_third_reward_hour_new_source_trajectories\\after_reward_hour3_normal_0.0.npz",
            "bytes": 1370930,
            "SHA": "b583329cef3fea0a10182dfbc610ae4f0677c43c4dd3bda3c288dd70b8981bc7"
          }
        },
        "final_speed_increase_m_s": 0.040353350472617316
      },
      {
        "yaw": 3.141592653589793,
        "new": {
          "source_SHA": "133847baef60d16a9c2c286b7d2dbde3c1b54cd097fe29d529441bd40fb5c5d4",
          "survived15s": true,
          "duration_s": 15.00000000000684,
          "final_speed_m_s": 0.05442616964332756,
          "last_second_mean_speed_m_s": 0.05490846598444366,
          "final_yaw_drift_rad": 0.6831861688906042,
          "net_planar_displacement_m": 0.8035597019763773,
          "planar_path_length_m": 0.8364675872780538,
          "raw": {
            "path": "C:\\Users\\lulu\\Desktop\\claude\\mjcf\\MOD4_SCUT_FUDAN_FIFTH_HOUR_20261019\\local_fourth_reward_hour_new_source_trajectories\\after_reward_hour4_normal_3.1416.npz",
            "bytes": 1711420,
            "SHA": "137fa2dda8b979a09a99412c1a7d0a3478b2c9d0d6f5c47b77a0a83380ac9663"
          }
        },
        "previous": {
          "source_SHA": "330220514b9bcf5f5bdf3e8b1280b08932bb4d8e58adeee33ee1b9a5281c8801",
          "survived15s": true,
          "duration_s": 15.00000000000684,
          "final_speed_m_s": 0.01402193909576142,
          "last_second_mean_speed_m_s": 0.02215763693531063,
          "final_yaw_drift_rad": 0.6668645620472167,
          "net_planar_displacement_m": 0.2894318549119527,
          "planar_path_length_m": 0.40017851748292,
          "raw": {
            "path": "C:\\Users\\lulu\\Desktop\\claude\\mjcf\\MOD4_SCUT_FUDAN_FOURTH_HOUR_20261019\\local_third_reward_hour_new_source_trajectories\\after_reward_hour3_normal_3.1416.npz",
            "bytes": 1368490,
            "SHA": "b4cb5838af1a3f6e608e2d1e1093a89d186d7d6d42387162980ebd861cef3b08"
          }
        },
        "final_speed_increase_m_s": 0.040404230547566145
      }
    ],
    "only_existing_local_raw_read_no_case_replay": true,
    "interpretation": "Both normal traces still survive15s, but zero-command final planar speed increases from about.014 to.054m/s. This is a local residual/regression in stopping, alongside yaw drift in both generations. Do not describe these survival results as complete normal nonregression. No statistical, PhysX or unique causal claim.",
    "no_new_threshold_or_training_player_GPU_account_change": true
  },
  "readout_limits": {
    "epoch": 1792357648.249579,
    "rows": [
      {
        "source_SHA": "133847baef60d16a9c2c286b7d2dbde3c1b54cd097fe29d529441bd40fb5c5d4",
        "public4_requested": false,
        "yaw": 0.0,
        "strict_counts": {
          "takeoff": 0,
          "landing": 0,
          "recovery": 0
        },
        "duration_s": 15.00000000000684,
        "first_failure": null,
        "previous_duration_s": 15.00000000000684,
        "previous_first_failure": null,
        "final_planar_speed_m_s": 0.054426180893934466,
        "final_yaw_error_rad": 0.683186169831631,
        "actual_phase_recovery_ticks_max": 0,
        "required_recovery_callbacks": 200
      },
      {
        "source_SHA": "133847baef60d16a9c2c286b7d2dbde3c1b54cd097fe29d529441bd40fb5c5d4",
        "public4_requested": false,
        "yaw": 3.141592653589793,
        "strict_counts": {
          "takeoff": 0,
          "landing": 0,
          "recovery": 0
        },
        "duration_s": 15.00000000000684,
        "first_failure": null,
        "previous_duration_s": 15.00000000000684,
        "previous_first_failure": null,
        "final_planar_speed_m_s": 0.05442616964332756,
        "final_yaw_error_rad": 0.6831861688906042,
        "actual_phase_recovery_ticks_max": 0,
        "required_recovery_callbacks": 200
      },
      {
        "source_SHA": "133847baef60d16a9c2c286b7d2dbde3c1b54cd097fe29d529441bd40fb5c5d4",
        "public4_requested": true,
        "yaw": 0.0,
        "strict_counts": {
          "takeoff": 1,
          "landing": 1,
          "recovery": 0
        },
        "duration_s": 15.00000000000684,
        "first_failure": null,
        "previous_duration_s": 1.4924999999998911,
        "previous_first_failure": {
          "time": 1.4924999999998911,
          "control": 149,
          "kind": "bad_orientation_local_tilt_0.75",
          "mode": 4,
          "roll": 0.14703802228378335,
          "pitch": -0.7511251431698834
        },
        "final_planar_speed_m_s": 0.05511820945849278,
        "final_yaw_error_rad": 0.657909618123722,
        "actual_phase_recovery_ticks_max": 110,
        "required_recovery_callbacks": 200
      },
      {
        "source_SHA": "133847baef60d16a9c2c286b7d2dbde3c1b54cd097fe29d529441bd40fb5c5d4",
        "public4_requested": true,
        "yaw": 3.141592653589793,
        "strict_counts": {
          "takeoff": 1,
          "landing": 1,
          "recovery": 0
        },
        "duration_s": 15.00000000000684,
        "first_failure": null,
        "previous_duration_s": 1.4924999999998911,
        "previous_first_failure": {
          "time": 1.4924999999998911,
          "control": 149,
          "kind": "bad_orientation_local_tilt_0.75",
          "mode": 4,
          "roll": 0.14703802228739857,
          "pitch": -0.7511251431779435
        },
        "final_planar_speed_m_s": 0.05511821031982922,
        "final_yaw_error_rad": 0.6579095836508815,
        "actual_phase_recovery_ticks_max": 110,
        "required_recovery_callbacks": 200
      }
    ],
    "interpretation": "Both new-source local jump traces take off and land under the original phase protocol and survive15s, compared with the prior source failing near1.4925s. Recovery remains0; the longest actual stable recovery run is110 callbacks, below200. Post-landing speed and yaw remain outside the original recovery conditions. These two yaw variants are deterministic small-sample MuJoCo evidence, not independent statistical trials, PhysX qualification or unique reward causality.",
    "torque_readout_limitation": "The existing46-column callback array stores the controller torque sent to MuJoCo d.ctrl, in actuator order hip,crank,wheel for each side. The added local reward-formula diagnostic uses those wheel command torques at indices2,5. It does not separately read d.actuator_force and must not be called a measured actuator-force or PhysX applied_torque readback. All original trace/code/report bytes remain retained.",
    "rate_readout_limit": "Added9-term callback rates are a read-only local formula diagnostic; they neither change control nor measure the production RewardManager/PPO return. Normal-mode extra terms are zero by the same request/attempt mask. This is not proof of full normal-behavior nonregression.",
    "response": "Continue the healthy unchanged production hour; next new source review should inspect recovery planar/yaw residuals and post-landing action/torque timeline. Do not tune the heldout set, alter phase/thresholds/request clock, add correction forces, or blindly change reward/LR/STD/physics.",
    "no_replay_or_GPU_player_account_mutation": true
  },
  "scope": "Unchanged SCUT+Fudan/PPO/physics/STD/LR/budget; new-source local diagnostics do not qualify PhysX or course graduation."
}