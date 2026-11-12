# 华南虎训练方法核对与本轮适配（2026-11-13）

直接核对本机参考仓库保存的实际env.yaml、agent.yaml、初始model_0.pt、训练入口和训练链README；没有把参考机器人的权重或资产装入MOD4。原件副本在reference，原始初始优化器读回在evidence/SCUT_REFERENCE_INITIAL_OPTIMIZER.json。

| 项目 | 实际华南虎证据 | 此前实验 | 新轮执行 |
|---|---|---|---|
| 训练分支 | rough_rotation_stair/2026-07-23_16-23-21被作者标注登阶好；rough_dash是另一个跑场分支 | 腾空跑场奖励与自定义登阶叠在50%专项环境 | 宽阶采用成功登阶分支普通奖励；其余原rough/平地保留原目标 |
| 检查点接续 | 当前train.py默认finetune只载匹配网络；显式resume_training才恢复优化器；三个保存的model_0均为Adam step20（5epochs×4minibatches） | 恢复父完整Adam、RNG和迭代计数 | actor/critic/STD权重从iter24692载入，Adam/seed/计数新建，迭代从0起；之后每份保存仍是完整PPO |
| PPO | LR1e-4 adaptive、clip0.2、5epochs、4batches、value2、entropy.005、KL.01、rollout24 | LR3e-5 fixed、clip.1、3epochs、value4 | 对齐上述实际PPO参数 |
| 数据分布 | 原Rough-v1宽阶5+5、其余非平地50、平地15，总75；旋转登阶分支另有小地形配比 |50%固定200mm专项/30%原rough/20%平地 | 沿用原Rough-v1比例：273宽阶、1365其余rough、410平地；保留完整DR和十级其他地形 |
| 宽阶奖励 | 成功分支无腾空、无新增抬腿/落轮奖励；速度平方-0.1×(0.25e)²，指数1.0 | 自定义进展/收腿/落轮/完成/阶间耗时参与PPO；全环境采用跑场奖励 | 宽阶用保存的普通SCUT奖励；自定义分数仅统计；其余环境保持原-1.5e²及落地奖励 |
| 地形识别 | 原状态机通过地形名筛选 | MOD4桥接仍用旧单地形mod4_step270占位方法 | 将奖励对象地形查询接到真实terrain_family，宽阶排除腾空状态机 |
| 完成事件 | 原任务按边界/20秒及原终止处理 | 到顶保持.3秒便提前timeout | 到顶事件只统计，一episode只计一次；按原边界/时长和保护终止 |

两个边界必须说清：成功旋转登阶参考保存的地形主要为5–40mm密阶，并非本项目200mm连续宽阶的成功验收。200mm高度、1.5m踏面、两级以及可行底部/中间平台起点，是我们的任务扩展；没有据此宣称原模型已证明200mm必过。其余Rough-v1地形和适用地形腾空落地采样继续训练。

本轮保留MOD4 R3资产和部署35actor/78critic/6action、电机包络、2.5ms物理/400Hz轮/100Hz腿/50Hz策略、TGS32/4、2mm单环境闭链保护；参考4096环境和5ms物理步适配为本项目已用2048环境与物理频率。速度上限保持2.2m/s。旧任务奖励保持原配方，宽阶奖励采用参考配方，这是明确的任务适配，不是整套参考机器人的原样复制。

[实际父与本轮计划](PLAN.json) · [成功登阶env原件](reference/scut_successful_stair_env.yaml) · [agent原件](reference/scut_successful_stair_agent.yaml) · [训练入口原件](reference/scut_train.py) · [作者训练链说明](reference/SCUT_PRETRAINED_README.md)。
