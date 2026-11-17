# MoE路线2固定200mm：实测收尾

默认模型未晋升；本目录仅记录本次独立实验。

训练安全关闭：True；训练报错：True。
|检查点|flat60|200mm正式低速|真实越边|物理稳态事件|
|---|---:|---:|---:|---:|

200mm正式成绩要求纯E1、整程实际水平峰速≤0.6m/s、真实双轮台顶支撑、车身越边和末端连续稳态≥0.4s。物理事件与正式通过分开，MuJoCo名义回放不能当full-DR毕业。

完整原始成绩：evidence/checkpoint_evals/；最终1倍速视频：evidence/checkpoint_evals/model_final/single_step/STUDENT_CENTER_1X.mp4。

E0/STD/critic冻结核验、逐高度DR与nominal完成计数及速度档见evidence/training/FINAL.json和每份完整PT。
