# 11月16日俯仰较低模型

MuJoCo交互播放入口：[play_mujoco.py](play_mujoco.py)。沿用WASD面板，额外显示机身俯仰/角速度；松键硬停车，P暂停，R复位。运行输出隔离于playback_runtime。

用户于2026-11-16明确采用的当前综合默认模型。后续综合回放和续训从本目录完整PT进入；统一指针见[CURRENT_COMPREHENSIVE_MODEL.json](../CURRENT_COMPREHENSIVE_MODEL.json)。

- 模型：`scut_pitch_brake_2h_20261116_005m`，iteration **25362**；两小时轮次第5分钟完整检查点，实际305.428秒。
- 完整权重：[model_full_ppo.pt](model_full_ppo.pt)，6,678,211字节，普通Git二进制；SHA256 `c874a1afa9adc33c3fa806d098fc135a76d3e9ecdf411d0ca4ab879696b18617`。
- 名称固定指向上述SHA，不随最后检查点变化。actor35、critic78、6动作；完整PPO与17项优化器状态。
- Git名称：`11月16日俯仰较低模型`；ASCII别名：`best-20261116-low-pitch-c874a1af`。
- 原机体：MOD4V3_HW300N60_R3；MJCF77904c00、USDe057969b；不替换资产、电机或控制时序。

| 固定MuJoCo名义回放 | 11月13日父db6 | 本模型 |
|---|---:|---:|
| 难度9崎岖急停俯仰峰值 |22.645°|13.562°|
| 平地急停俯仰峰值 |18.673°|13.370°|
| 平地综合 |60/60|60/60|
| 正向连续两阶 |4/5|5/5|
| 实际斜向 |1/20|1/20|
| 下阶 |5/5|5/5|

采用依据是已完成的固定协议改善与用户明确指令。完整DR训练不等于此SHA已通过完整DR验收；父模型的原生成绩不能直接记入本模型。原[11月13日db6](../MOD4V3_BEST_COMPREHENSIVE_20261113/README.md)权重保留回退。

[身份](MODEL_IDENTITY.json) · [采用记录](ADOPTION.json) · [训练配方](TRAINING_RECIPE.json) · [评测快照](EVALUATION_SNAPSHOT.json) · [两小时报告](TRAINING_FINAL_REPORT.md) · [华南虎奖励差距分析](../../sources/local/MOD4V3_LOW_PITCH_ADOPTION_AUDIT_20261116/REPORT.md)

快照中的实验候选/未晋升措辞记录自动筛选时刻；本目录ADOPTION.json记录用户随后明确采用。此次采用没有进行PPO更新、ONNX导出或真机部署。
