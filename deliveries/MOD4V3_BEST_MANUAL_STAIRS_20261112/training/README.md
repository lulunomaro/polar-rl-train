# 华南虎 Rough-v1：统一跑场两小时

**PPO已完成7206.600秒，26份完整训练PT已核验；PhysX收齐5/10组，其余因目标机SSH超时待收齐。** 本轮实际父为Rough-v0 100m，未回退R1。原实车调试包保留，暂未晋升新模型。

| 用途 | 文件 | iteration | SHA256 |
|---|---|---:|---|
| 本轮真实父、Rough线保留基座 | [Rough-v0 100m](../MOD4V3_SCUT_ROUGH_V0_2H_20261112/weights/model_100m.pt) |23665|`001028396205e7d44d69ac5af36cdbb638cc26b97daeea29439f84952a58f6e9`|
| 本轮正式比较候选 | [105m完整PPO](weights/model_105m.pt) |24380|`43eb5ab733f426f61b9fc963703c5114a4c837c53219d7e6042892b0325bd4bd`|
| 本轮末点、实验权重 | [120m完整PPO](weights/model_120m.pt) |24482|`7cc1fc6deeee3d3aba8ae8d2da31dce200079fb229a145f1cbb1cd3bfabea103`|

11类地形/10级统一训练，不拆短课；保持完整DR、20%名义与20%平地独立交叉、35/78/6、2.5/10/20ms、TGS32/4、2mm单env保护、−1.5e²/指数1.2和2.2m/s上限。LR3e-5 fixed、clip.1、3epochs、rollout24、seed66。内部腾空落地开启，主动跳跃关闭。

每五分钟完整保存/下载SHA核验/实际Torch读回/名义MuJoCo筛查；24定时点、首次和final共26份PT，25种字节。全部PT本体随阶段Git归档，完整SHA/bytes/iteration见evidence/MODEL_ARCHIVE_INDEX.json。短探针原件另存，原始恢复训练盘、读回器修复和SSH读者错误均保留。

完整DR最高档穿越父/105m/120m=170/162/169（各200）；高速162/154/154（各180）；宽阶上行仍未掌握。原始逐地形结果在同批报告中，不把旋转/落地未收齐项写成通过。

[最终报告](FINAL_REPORT.md) · [模型选择](DECISION.md) · [同批结果](PAIRED_COMPARISON.md) · [全部保存点](CHECKPOINT_COMPARISON.md) · [实际配方](EFFECTIVE_RECIPE.json) · [复现](TRAINING_RECIPE.md)。

[前一轮Rough-v0行走与小陀螺分项报告](../MOD4V3_SCUT_ROUGH_V0_2H_20261112/COURSE_COMPLETION_REPORT.md)。Git同步回执另见SYNC_REPORT；当前无新PPO。
