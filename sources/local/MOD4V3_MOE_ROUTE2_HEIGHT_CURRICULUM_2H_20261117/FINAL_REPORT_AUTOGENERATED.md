# MoE路线2逐环境高度课程：实测收尾

默认模型未晋升；本目录仅记录本次独立实验。

训练安全关闭：True；训练报错：False。
实际训练计时 7140.047s；完整PPO更新 855；实际Adam小批次 10260。
最终SHA a20ae89b3180c507e31ad0f21a23c55a46381c48e17c74a33a800dffb926408f。

|检查点|flat60|200mm正式低速|真实越边|物理稳态事件|
|---|---:|---:|---:|---:|
|model_010m|60 / 60|0 / 5|0 / 5|0 / 5|
|model_020m|60 / 60|0 / 5|0 / 5|0 / 5|
|model_040m|60 / 60|0 / 5|0 / 5|0 / 5|
|model_060m|60 / 60|0 / 5|0 / 5|0 / 5|
|model_090m|60 / 60|0 / 5|0 / 5|0 / 5|
|model_final|60 / 60|0 / 5|0 / 5|0 / 5|

200mm正式成绩要求纯E1、整程实际水平峰速≤0.6m/s、真实双轮台顶支撑、车身越边和末端连续稳态≥0.4s。物理事件与正式通过分开，MuJoCo名义回放不能当full-DR毕业。

完整原始成绩：evidence/checkpoint_evals/；最终1倍速视频：evidence/checkpoint_evals/model_final/single_step/STUDENT_CENTER_1X.mp4。

E0/STD/critic冻结核验、逐高度DR与nominal完成计数及速度档见evidence/training/FINAL.json和每份完整PT。
