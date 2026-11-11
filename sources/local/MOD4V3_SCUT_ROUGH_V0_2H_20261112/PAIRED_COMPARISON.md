# 统一 SCUT Rough-v0 两小时：固定权重对照

同批比较R1父模型、名义MuJoCo原六项筛选的中间候选及120m保存点。MuJoCo筛选不等于PhysX或完整DR成绩。Flat沿用原判据；穿越和旋转分别统计首次物理episode，重置后的表现不补入首次成绩。

| 模型 | 名义Flat /60 | 完整DR Flat /60 | 完整DR Flat原六项重置 |
|---|---:|---:|---:|
| parent | 58 | 42 | 2 |
| roughv0_100m | 36 | 35 | 1 |
| roughv0_120m | 30 | 38 | 0 |

## 统一地形：±1 m/s穿越与±14.137 rad/s旋转

旋转同时列首次6秒存活和有效窗口角速度MAE，避免只看幸存样本的误差。该MAE单位rad/s，不额外套用新的毕业容差。

| 条件 | level | 模型 | 首次穿越 /160 | 旋转首次6秒存活 /160 | 旋转MAE rad/s | 对齐正负方向平均转速 rad/s |
|---|---:|---|---:|---:|---:|---:|
| nominal0 | 0 | parent | 160 | 160 | 0.5633 | 13.9064 |
| nominal0 | 0 | roughv0_100m | 160 | 160 | 0.5843 | 14.0731 |
| nominal0 | 0 | roughv0_120m | 160 | 160 | 0.5682 | 14.1287 |
| nominal0 | 5 | parent | 159 | 160 | 0.6793 | 13.7152 |
| nominal0 | 5 | roughv0_100m | 159 | 160 | 0.7926 | 13.6814 |
| nominal0 | 5 | roughv0_120m | 159 | 160 | 0.7835 | 13.6792 |
| nominal0 | 9 | parent | 158 | 158 | 0.8167 | 13.6031 |
| nominal0 | 9 | roughv0_100m | 156 | 159 | 0.9831 | 13.5344 |
| nominal0 | 9 | roughv0_120m | 157 | 160 | 1.0708 | 13.4651 |
| Step7_all_remaining_DR | 0 | parent | 155 | 157 | 0.9647 | 13.1939 |
| Step7_all_remaining_DR | 0 | roughv0_100m | 156 | 160 | 1.3978 | 12.7832 |
| Step7_all_remaining_DR | 0 | roughv0_120m | 157 | 159 | 1.3524 | 12.8330 |
| Step7_all_remaining_DR | 5 | parent | 147 | 155 | 1.5822 | 12.5685 |
| Step7_all_remaining_DR | 5 | roughv0_100m | 144 | 158 | 1.8394 | 12.3259 |
| Step7_all_remaining_DR | 5 | roughv0_120m | 143 | 158 | 1.9032 | 12.2679 |
| Step7_all_remaining_DR | 9 | parent | 134 | 153 | 1.7066 | 12.4490 |
| Step7_all_remaining_DR | 9 | roughv0_100m | 133 | 158 | 1.8705 | 12.3024 |
| Step7_all_remaining_DR | 9 | roughv0_120m | 131 | 156 | 1.8548 | 12.3192 |

## 最高代表档：±2.2 m/s穿越

| 条件 | 模型 | 首次穿越 /160 | 首次episode终止 |
|---|---|---:|---:|
| nominal0 | parent | 158 | 1 |
| nominal0 | roughv0_100m | 156 | 1 |
| nominal0 | roughv0_120m | 158 | 2 |
| Step7_all_remaining_DR | parent | 145 | 3 |
| Step7_all_remaining_DR | roughv0_100m | 148 | 2 |
| Step7_all_remaining_DR | roughv0_120m | 144 | 3 |

各地形、方向、初态及保护原因见[PAIRED_SUMMARY.json](PAIRED_SUMMARY.json)和evidence内原始RESULT/INITIAL_DR/trajectory；全部保存点的名义MuJoCo筛选另见CHECKPOINT_COMPARISON.md。最终接续选择另见DECISION。

高速表表示±2.2m/s指令下的实际穿越，不代表全过程实速达到2.2。越障后有效窗口MAE与恢复到±0.2m/s并持续0.5秒的数量另见PAIRED_SUMMARY；完整DR的父/100m/120m越障后MAE分别0.7494/0.8478/0.7300m/s。
