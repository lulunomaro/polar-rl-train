# MoE路线2固定200mm：实测收尾

默认模型未晋升；本目录仅记录本次独立实验。

训练安全关闭：True；训练报错：False。
实际训练计时 326.837s；完整PPO更新 20；实际Adam小批次 247。
最终SHA 3d2c7de9e07755545f3e07ec9d4b115094bd392c87df3adb498d567542920022。

最终PT准确训练计数：{"heights_m": [0.2], "height_population": [819], "attempts_DR_then_nominal": [[548], [352]], "completions_DR_then_nominal": [[0], [0]], "true_top_completion_events_DR_then_nominal": [0, 0], "offset_completion_events_DR_then_nominal": [[0, 0, 0, 0, 0], [0, 0, 0, 0, 0]], "speed_limits_m_s": [1.5, 1.2000000476837158, 0.8999999761581421, 0.800000011920929, 0.699999988079071, 0.6000000238418579], "speed_stage_population": [819, 0, 0, 0, 0, 0], "speed_completions": [0, 0, 0, 0, 0, 0], "strict_completions_all_heights": 0}

|检查点|flat60|200mm正式低速|真实越边|物理稳态事件|
|---|---:|---:|---:|---:|
|model_final|60 / 60|0 / 5|0 / 5|0 / 5|

200mm正式成绩要求纯E1、整程实际水平峰速≤0.6m/s、真实双轮台顶支撑、车身越边和末端连续稳态≥0.4s。物理事件与正式通过分开，MuJoCo名义回放不能当full-DR毕业。

完整原始成绩：evidence/checkpoint_evals/；最终1倍速视频：evidence/checkpoint_evals/model_final/single_step/STUDENT_CENTER_1X.mp4。

E0/STD/critic冻结核验、逐高度DR与nominal完成计数及速度档见evidence/training/FINAL.json和每份完整PT。
