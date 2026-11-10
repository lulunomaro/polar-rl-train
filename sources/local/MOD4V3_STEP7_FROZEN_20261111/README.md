# Step7 模型与训练配方冻结

冻结当前已完成独立质量 DR 适应的最终检查点，iteration 21754，SHA `23c112b16e9629215c7265124925daaf0f9b6bbbb62be61689c714ba1fc7a772`。完整模型保存在本地 `D:/claude2/fangzhen/frozen_models/step7_20261111_mass_final/model_final.pt` 和 RECIPE 指定的远端冻结目录，二进制不入 Git。源码、PLAN、实际 STARTUP/PPO/恢复及完成回执在本目录固定保存，逐文件 SHA 见 MANIFEST。

后续 DR 使用新目录，从本模型继续。此冻结保留当前能力基线，全部 DR 与 Rough 仍按仓库计划推进；不修改已冻结的 Step6 和历史模型。
