# Rough-v1 两小时：固定权重实测对照

当前只收齐5/10组结果。目标机SSH超时；旋转、落地及新模型的Rough-v0保留测量待收齐，不记作0或通过。训练7206.600秒和26份完整PT已在本机核验。

parent为本轮真实Rough-v0 100m父；候选由全部定时点的MuJoCo筛查选来做进一步比较，不预先称为综合最优。以下成绩全部来自实际同批PhysX。

## 平地原六项保留

| 模型 | 名义Flat /60 | 完整DR Flat /60 | 名义vx@2.0 / vx@2.2 |
|---|---:|---:|---:|
| parent | 34 | 35 | 1.6963 / 1.8207 |
| scutroughv1_105m | 41 | 32 | 1.7878 / 1.9224 |
| scutroughv1_120m | 40 | 34 | 1.8643 / 2.0177 |

## Rough-v1 实际地形穿越

10类非平地×两方向×10初态，分母200；常规地形±1，高速宽阶/反高浅阶±1.5、落差族±2.0 m/s，遵守本轮按地形指令范围。宽阶每方向5个进阶、5个出阶初态，穿越要求实际高度变化和两轮清障，平平台上走够距离不算过阶。

| 条件 | 难度 | 模型 | 地形指定速度穿越 /200 | 越障后恢复指令 /200 |
|---|---:|---|---:|---:|
| nominal0 | 0 | parent | 180 | 145 |
| nominal0 | 0 | scutroughv1_105m | 180 | 147 |
| nominal0 | 0 | scutroughv1_120m | 180 | 144 |
| nominal0 | 5 | parent | 179 | 132 |
| nominal0 | 5 | scutroughv1_105m | 179 | 138 |
| nominal0 | 5 | scutroughv1_120m | 179 | 137 |
| nominal0 | 9 | parent | 177 | 106 |
| nominal0 | 9 | scutroughv1_105m | 177 | 128 |
| nominal0 | 9 | scutroughv1_120m | 178 | 123 |
| Step7_all_remaining_DR | 0 | parent | 180 | 102 |
| Step7_all_remaining_DR | 0 | scutroughv1_105m | 178 | 97 |
| Step7_all_remaining_DR | 0 | scutroughv1_120m | 178 | 104 |
| Step7_all_remaining_DR | 5 | parent | 176 | 78 |
| Step7_all_remaining_DR | 5 | scutroughv1_105m | 171 | 85 |
| Step7_all_remaining_DR | 5 | scutroughv1_120m | 171 | 86 |
| Step7_all_remaining_DR | 9 | parent | 170 | 65 |
| Step7_all_remaining_DR | 9 | scutroughv1_105m | 162 | 64 |
| Step7_all_remaining_DR | 9 | scutroughv1_120m | 169 | 74 |

## 宽台阶：上行与下行分别计数

以下为完整DR，每类宽阶各10个接近中央高平台的上行初态、10个离开平台的下行初态；两方向合计。不能用下行成绩替代上行能力。

| 难度 | 模型 | 低速宽阶上行 /10 | 低速宽阶下行 /10 | 高速宽阶上行 /10 | 高速宽阶下行 /10 |
|---:|---|---:|---:|---:|---:|
| 0 | parent | 0 | 10 | 0 | 10 |
| 0 | scutroughv1_105m | 0 | 10 | 1 | 10 |
| 0 | scutroughv1_120m | 0 | 10 | 0 | 10 |
| 5 | parent | 0 | 10 | 0 | 10 |
| 5 | scutroughv1_105m | 0 | 10 | 0 | 9 |
| 5 | scutroughv1_120m | 0 | 10 | 0 | 9 |
| 9 | parent | 0 | 10 | 0 | 10 |
| 9 | scutroughv1_105m | 0 | 8 | 0 | 10 |
| 9 | scutroughv1_120m | 0 | 9 | 0 | 10 |

## 最高档高速穿越与旋转

高速2.2仅检查9个允许该速度的非平地族（180例）；旋转只检查5个训练角速范围含14.137的非平地族（100例）。宽台阶、指定高速下阶和落差族按参考为直行科目，不用其未训练高速陀螺组合作毕业条件。

| 条件 | 模型 | ±2.2指令穿越（完成/请求） | 旋转首6秒保持（完成/请求） | 旋转MAE rad/s |
|---|---|---:|---:|---:|
| nominal0 | parent | 167/180 | 待收齐 | 待收齐 |
| nominal0 | scutroughv1_105m | 166/180 | 待收齐 | 待收齐 |
| nominal0 | scutroughv1_120m | 167/180 | 待收齐 | 待收齐 |
| Step7_all_remaining_DR | parent | 162/180 | 待收齐 | 待收齐 |
| Step7_all_remaining_DR | scutroughv1_105m | 154/180 | 待收齐 | 待收齐 |
| Step7_all_remaining_DR | scutroughv1_120m | 154/180 | 待收齐 | 待收齐 |

## 腾空落地

4个参考允许地形×两方向×10初态，分母80。真正离地、接触、姿态恢复和指令恢复分别计数；后两项要求首次episode内连续保持.5秒，不用重置后的表现补分。

| 条件 | 难度 | 模型 | 观测离地 /80 | 接触 /80 | 姿态恢复 /80 | 指令恢复 /80 |
|---|---:|---|---:|---:|---:|---:|
| nominal0 | 0 | parent | 待收齐 | 待收齐 | 待收齐 | 待收齐 |
| nominal0 | 0 | scutroughv1_105m | 待收齐 | 待收齐 | 待收齐 | 待收齐 |
| nominal0 | 0 | scutroughv1_120m | 待收齐 | 待收齐 | 待收齐 | 待收齐 |
| nominal0 | 9 | parent | 待收齐 | 待收齐 | 待收齐 | 待收齐 |
| nominal0 | 9 | scutroughv1_105m | 待收齐 | 待收齐 | 待收齐 | 待收齐 |
| nominal0 | 9 | scutroughv1_120m | 待收齐 | 待收齐 | 待收齐 | 待收齐 |
| Step7_all_remaining_DR | 0 | parent | 待收齐 | 待收齐 | 待收齐 | 待收齐 |
| Step7_all_remaining_DR | 0 | scutroughv1_105m | 待收齐 | 待收齐 | 待收齐 | 待收齐 |
| Step7_all_remaining_DR | 0 | scutroughv1_120m | 待收齐 | 待收齐 | 待收齐 | 待收齐 |
| Step7_all_remaining_DR | 9 | parent | 待收齐 | 待收齐 | 待收齐 | 待收齐 |
| Step7_all_remaining_DR | 9 | scutroughv1_105m | 待收齐 | 待收齐 | 待收齐 | 待收齐 |
| Step7_all_remaining_DR | 9 | scutroughv1_120m | 待收齐 | 待收齐 | 待收齐 | 待收齐 |

## Rough-v0 旧科目保留

| 条件 | 模型 | 原最高档±1穿越 /160 | 原小陀螺首6秒保持 /160 | 原旋转MAE rad/s |
|---|---|---:|---:|---:|
| nominal0 | parent | 待收齐 | 待收齐 | 待收齐 |
| nominal0 | scutroughv1_105m | 待收齐 | 待收齐 | 待收齐 |
| nominal0 | scutroughv1_120m | 待收齐 | 待收齐 | 待收齐 |
| Step7_all_remaining_DR | parent | 待收齐 | 待收齐 | 待收齐 |
| Step7_all_remaining_DR | scutroughv1_105m | 待收齐 | 待收齐 | 待收齐 |
| Step7_all_remaining_DR | scutroughv1_120m | 待收齐 | 待收齐 | 待收齐 |

## 原始证据与限制

逐地形/方向结果及第一episode终止原因见PAIRED_SUMMARY.json和evidence/paired_*_RESULT.json；按模型配对的DR、延迟、噪声、外力和推扰原件在INITIAL_DR/trajectory中。每一组实际numerical、动作槽误差、电机包络与是否构建优化器见PAIRED_SUMMARY.checks。没有将少量保护事件改成全程0。

这是一组固定初态和代表难度的实测，不把训练奖励、纯6秒旋转保持、触地或名义MuJoCo精度合并成全面毕业结论。新科目与旧R1模型的历史分数不作异批直接排名。
