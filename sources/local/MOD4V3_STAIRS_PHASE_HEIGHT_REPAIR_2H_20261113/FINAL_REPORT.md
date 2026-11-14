# 高站姿保留与阶段均衡/单轮落地反馈：两小时结果

实际PPO 7206.380秒；计划7200秒。综合父db6e9ccf保持冻结，实际接续权重和SHA见PLAN；教师715c只提供运动后成功示范。没有自动延长或新科目。

实验候选：stairs_phase_height_repair_20261114_015m，SHA 3b20e4f0cf03251fc82abb260fda2fa2f6ac12be2e341479eb834766e4a41b1f。完整PT见weights/selected_specialist_student.pt。

| 保存点 | 平地/60 | 正向/5 | 真实斜向/20 | 下阶/5 | 前进MAE(m/s) |
|---|---:|---:|---:|---:|---:|
|model_005m.pt|60|4|6|5|0.077014|
|model_010m.pt|60|4|4|5|0.049175|
|model_015m.pt|60|4|7|5|0.049464|
|model_020m.pt|60|4|3|5|0.050305|
|model_025m.pt|60|4|2|5|0.018553|
|model_030m.pt|60|4|0|5|0.020851|
|model_035m.pt|60|4|1|5|0.058160|
|model_040m.pt|60|4|6|5|0.048652|
|model_045m.pt|60|4|1|5|0.020995|
|model_050m.pt|60|4|1|5|0.062488|
|model_055m.pt|60|4|1|5|0.085930|
|model_060m.pt|60|4|0|5|0.063269|
|model_065m.pt|60|4|7|5|0.104076|
|model_070m.pt|60|4|0|5|0.113651|
|model_075m.pt|60|4|2|5|0.129177|
|model_080m.pt|60|4|1|5|0.074309|
|model_085m.pt|60|4|4|5|0.029630|
|model_090m.pt|60|4|3|5|0.067321|
|model_095m.pt|60|4|0|5|0.073021|
|model_100m.pt|60|4|3|5|0.065045|
|model_105m.pt|60|4|1|5|0.083810|
|model_110m.pt|60|4|7|5|0.052513|
|model_115m.pt|60|4|6|5|0.044487|
|model_120m.pt|60|4|3|5|0.062124|
|model_final.pt|60|4|3|5|0.062124|

父既有同SHA基线为平地60/60、正向4/5、真实斜向0/20、下阶5/5。全部失败和训练保护保留；实验候选不自动替代综合父。

## 原生复核

|科目|模型|条件|数量|
|---|---|---|---:|
|stairs|parent|fullDR|0/100|
|stairs|parent|nominal0|14/100|
|stairs|student|fullDR|1/100|
|stairs|student|nominal0|14/100|
|retained_traverse|parent|Step7_all_remaining_DR|173/200|
|retained_traverse|parent|nominal0|178/200|
|retained_traverse|student|Step7_all_remaining_DR|174/200|
|retained_traverse|student|nominal0|176/200|
|retained_gyro|parent|Step7_all_remaining_DR|99/100|
|retained_gyro|parent|nominal0|100/100|
|retained_gyro|student|Step7_all_remaining_DR|99/100|
|retained_gyro|student|nominal0|99/100|
|retained_landing|parent|Step7_all_remaining_DR|79/80|
|retained_landing|parent|nominal0|80/80|
|retained_landing|student|Step7_all_remaining_DR|80/80|
|retained_landing|student|nominal0|80/80|

两引擎协议分别解释。原生台阶精确逐环境成绩以post_native_recovery_r2/stairs/RESULT.json为准；rough穿越、首6秒旋转存活、落地指令恢复沿用原L9协议，不混作完整地图或主动跳跃毕业。

修改范围：4433帧运动后成功示范按阶段/角度/引擎均衡；高站姿腿部单独保留；单轮真实台面落地各0.15+双轮0.2，总0.5不变；在线池新轮重建且占比0.25。原40/35/25配比、速度奖励、完整DR、35/78/6、MOD4电机与时序不变。每5分钟完整保存及检查记录在evidence/inspections。
