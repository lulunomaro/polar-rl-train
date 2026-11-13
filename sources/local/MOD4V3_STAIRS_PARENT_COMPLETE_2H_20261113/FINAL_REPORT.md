# 完整示范与上阶约束修复：两小时结果

实际PPO 7204.531秒；计划7200秒。父db6e9ccf保持冻结，教师715c只提供完整成功示范。没有自动延长或新科目。

实验候选：stairs_parent_complete_20261113_095m，SHA de57c6dc9ef2bee303b9e2e91c314e76bdf7e336cc66043cf02660bb8f0446d0。完整PT见weights/selected_specialist_student.pt。

| 保存点 | 平地/60 | 正向/5 | 真实斜向/20 | 下阶/5 | 前进MAE(m/s) |
|---|---:|---:|---:|---:|---:|
|model_005m.pt|50|4|7|5|0.020766|
|model_010m.pt|50|4|4|5|0.026108|
|model_015m.pt|50|3|3|5|0.044000|
|model_020m.pt|50|2|1|5|0.075937|
|model_025m.pt|50|2|2|5|0.032663|
|model_030m.pt|50|1|3|5|0.033538|
|model_035m.pt|50|2|3|5|0.030999|
|model_040m.pt|50|1|4|5|0.044457|
|model_045m.pt|50|3|6|5|0.026244|
|model_050m.pt|50|2|3|5|0.030512|
|model_055m.pt|50|4|5|5|0.021969|
|model_060m.pt|50|3|5|5|0.061185|
|model_065m.pt|50|3|4|5|0.025908|
|model_070m.pt|50|3|5|5|0.051952|
|model_075m.pt|50|4|6|5|0.027134|
|model_080m.pt|50|3|6|5|0.022921|
|model_085m.pt|50|4|6|5|0.023231|
|model_090m.pt|50|5|6|5|0.048636|
|model_095m.pt|50|4|8|5|0.024607|
|model_100m.pt|50|4|6|5|0.059480|
|model_105m.pt|50|4|3|5|0.065182|
|model_110m.pt|50|4|6|5|0.029264|
|model_115m.pt|50|5|7|5|0.038282|
|model_120m.pt|50|4|5|5|0.021921|
|model_final.pt|50|4|5|5|0.021921|

父既有同SHA基线为平地60/60、正向4/5、真实斜向0/20、下阶5/5。全部失败和训练保护保留；实验候选不自动替代综合父。

## 原生复核

|科目|模型|条件|数量|
|---|---|---|---:|
|stairs|parent|fullDR|0/100|
|stairs|parent|nominal0|14/100|
|stairs|student|fullDR|0/100|
|stairs|student|nominal0|14/100|
|retained_traverse|parent|Step7_all_remaining_DR|173/200|
|retained_traverse|parent|nominal0|178/200|
|retained_traverse|student|Step7_all_remaining_DR|174/200|
|retained_traverse|student|nominal0|176/200|
|retained_gyro|parent|Step7_all_remaining_DR|99/100|
|retained_gyro|parent|nominal0|100/100|
|retained_gyro|student|Step7_all_remaining_DR|100/100|
|retained_gyro|student|nominal0|100/100|
|retained_landing|parent|Step7_all_remaining_DR|80/80|
|retained_landing|parent|nominal0|80/80|
|retained_landing|student|Step7_all_remaining_DR|78/80|
|retained_landing|student|nominal0|80/80|

两引擎协议分别解释。原生台阶精确逐环境成绩以post_native/stairs/RESULT.json为准；rough穿越、首6秒旋转存活、落地指令恢复沿用原L9协议，不混作完整地图或主动跳跃毕业。

修改范围：完整示范8933帧/30次成功含准备；所有上台阶解除旧父动作保留，平地/rough/下台阶仍保留。原40/35/25配比、奖励、完整DR、35/78/6、MOD4电机与时序不变。每5分钟完整保存及检查记录在evidence/inspections。
