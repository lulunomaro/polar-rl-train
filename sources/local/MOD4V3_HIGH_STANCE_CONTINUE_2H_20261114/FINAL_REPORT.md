# 高站姿追加两小时接训：结果

实际PPO 7205.240秒；计划7200秒。综合父db6e9ccf保持冻结，实际接续权重和SHA见PLAN；教师715c只提供运动后成功示范。没有自动延长或新科目。

实验候选：high_stance_continue_20261114_035m，SHA 5fa22340107fe72987ba5537138f15ecc96c985d016481ae6d81fd5f2eb4b9ae。完整PT见weights/selected_specialist_student.pt。

| 保存点 | 平地/60 | 正向/5 | 真实斜向/20 | 下阶/5 | 前进MAE(m/s) |
|---|---:|---:|---:|---:|---:|
|model_005m.pt|60|4|3|5|0.106940|
|model_010m.pt|50|4|0|5|0.128808|
|model_015m.pt|60|4|2|5|0.022777|
|model_020m.pt|60|3|1|5|0.065163|
|model_025m.pt|60|3|0|5|0.075324|
|model_030m.pt|60|4|1|5|0.045675|
|model_035m.pt|60|4|7|5|0.032266|
|model_040m.pt|60|2|1|5|0.081373|
|model_045m.pt|60|3|0|5|0.043164|
|model_050m.pt|60|2|1|5|0.042179|
|model_055m.pt|60|4|0|5|0.025126|
|model_060m.pt|60|3|1|5|0.052047|
|model_065m.pt|60|4|2|5|0.039904|
|model_070m.pt|60|2|1|5|0.047197|
|model_075m.pt|60|4|5|5|0.022675|
|model_080m.pt|60|4|2|5|0.022594|
|model_085m.pt|60|4|1|5|0.066670|
|model_090m.pt|60|4|2|5|0.051704|
|model_095m.pt|60|3|1|5|0.101978|
|model_100m.pt|60|4|1|5|0.055999|
|model_105m.pt|60|2|1|5|0.063610|
|model_110m.pt|60|4|1|5|0.021589|
|model_115m.pt|60|2|0|5|0.076446|
|model_120m.pt|60|3|0|5|0.051082|
|model_final.pt|60|3|0|5|0.051082|

父既有同SHA基线为平地60/60、正向4/5、真实斜向0/20、下阶5/5。全部失败和训练保护保留；实验候选不自动替代综合父。

## 原生复核

|科目|模型|条件|数量|
|---|---|---|---:|
|stairs|parent|fullDR|0/100|
|stairs|parent|nominal0|14/100|
|stairs|student|fullDR|0/100|
|stairs|student|nominal0|16/100|
|retained_traverse|parent|Step7_all_remaining_DR|173/200|
|retained_traverse|parent|nominal0|178/200|
|retained_traverse|student|Step7_all_remaining_DR|173/200|
|retained_traverse|student|nominal0|177/200|
|retained_gyro|parent|Step7_all_remaining_DR|99/100|
|retained_gyro|parent|nominal0|100/100|
|retained_gyro|student|Step7_all_remaining_DR|99/100|
|retained_gyro|student|nominal0|100/100|
|retained_landing|parent|Step7_all_remaining_DR|79/80|
|retained_landing|parent|nominal0|80/80|
|retained_landing|student|Step7_all_remaining_DR|79/80|
|retained_landing|student|nominal0|80/80|

两引擎协议分别解释。原生台阶精确逐环境成绩以post_native/stairs/RESULT.json为准；rough穿越、首6秒旋转存活、落地指令恢复沿用原L9协议，不混作完整地图或主动跳跃毕业。

修改范围：4433帧运动后成功示范按阶段/角度/引擎均衡；高站姿腿部单独保留；单轮真实台面落地各0.15+双轮0.2，总0.5不变；在线池新轮重建且占比0.25。原40/35/25配比、速度奖励、完整DR、35/78/6、MOD4电机与时序不变。每5分钟完整保存及检查记录在evidence/inspections。
