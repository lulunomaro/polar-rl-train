# MoE路线2固定200mm：实测收尾

默认模型未晋升；本目录仅记录本次独立实验。

训练安全关闭：True；训练报错：False。
实际训练计时 2340.442s；完整PPO更新 332；实际Adam小批次 3984。
最终SHA f2f21eef616cec43590d669ab8b40806390cdcf2ec24b795250d691735e57ac7。

最终PT准确训练计数：{"heights_m": [0.2], "height_population": [819], "attempts_DR_then_nominal": [[7374], [1857]], "completions_DR_then_nominal": [[59], [19]], "true_top_completion_events_DR_then_nominal": [59, 19], "offset_completion_events_DR_then_nominal": [[0, 0, 59, 0, 0], [0, 0, 19, 0, 0]], "offset_attempts_DR_then_nominal": [[0, 0, 7374, 0, 0], [0, 0, 1857, 0, 0]], "offset_population_reference_groups": [[0, 0, 655, 0, 0], [0, 0, 164, 0, 0]], "E1_DR_curriculum": {"method": "success-gated mixture fraction; enabled DR always uses original full ranges", "target_stage": 0, "fullDR_fraction_of_reference_DR_group": 0.0, "stage_population": [819, 0, 0, 0, 0, 0, 0], "actual_fullDR_population": 0, "zeroDR_population": 819, "attempts_stage_actualDR_offset": [[[0, 0, 9231, 0, 0], [0, 0, 0, 0, 0]], [[0, 0, 0, 0, 0], [0, 0, 0, 0, 0]], [[0, 0, 0, 0, 0], [0, 0, 0, 0, 0]], [[0, 0, 0, 0, 0], [0, 0, 0, 0, 0]], [[0, 0, 0, 0, 0], [0, 0, 0, 0, 0]], [[0, 0, 0, 0, 0], [0, 0, 0, 0, 0]], [[0, 0, 0, 0, 0], [0, 0, 0, 0, 0]]], "completions_stage_actualDR_offset": [[[0, 0, 78, 0, 0], [0, 0, 0, 0, 0]], [[0, 0, 0, 0, 0], [0, 0, 0, 0, 0]], [[0, 0, 0, 0, 0], [0, 0, 0, 0, 0]], [[0, 0, 0, 0, 0], [0, 0, 0, 0, 0]], [[0, 0, 0, 0, 0], [0, 0, 0, 0, 0]], [[0, 0, 0, 0, 0], [0, 0, 0, 0, 0]], [[0, 0, 0, 0, 0], [0, 0, 0, 0, 0]]], "offsets_mm": [-60, -30, 0, 30, 60], "recent_success_rates": [0.0078125, null, null, null, null, null, null], "promotions": [], "zeroDR_results_are_not_fullDR_graduation": true}, "reset_sensor_cache": {"calls": 5080, "max_gravity_change": 1.3202695846557617, "max_body_velocity_change": 10.116262435913086, "nonreset_rows_max_change": 0.0}, "speed_limits_m_s": [1.5, 1.2000000476837158, 0.8999999761581421, 0.800000011920929, 0.699999988079071, 0.6000000238418579], "speed_stage_population": [819, 0, 0, 0, 0, 0], "speed_completions": [78, 0, 0, 0, 0, 0], "strict_completions_all_heights": 15}

|检查点|flat60|200mm正式低速|真实越边|物理稳态事件|
|---|---:|---:|---:|---:|
|model_005m|60 / 60|0 / 5|0 / 5|0 / 5|
|model_010m|60 / 60|0 / 5|0 / 5|0 / 5|
|model_020m|60 / 60|0 / 5|1 / 5|0 / 5|
|model_final|60 / 60|0 / 5|1 / 5|1 / 5|

200mm正式成绩要求纯E1、整程实际水平峰速≤0.6m/s、真实双轮台顶支撑、车身越边和末端连续稳态≥0.4s。物理事件与正式通过分开，MuJoCo名义回放不能当full-DR毕业。

完整原始成绩：evidence/checkpoint_evals/；最终1倍速视频：evidence/checkpoint_evals/model_final/single_step/STUDENT_CENTER_1X.mp4。

E0/STD/critic冻结核验、逐高度DR与nominal完成计数及速度档见evidence/training/FINAL.json和每份完整PT。
