# MOD4v3 低速助跑 + 台顶停车 + 四阶段回放修复：40分钟正式开训报告

- **实验目录**：`MOD4V3_MOE_ROUTE2_LOWSPEED_PARK_REPAIR_20261118`
- **远端作业**：`/home/egde/rl_candidates/mod4v3_moe_route2_lowspeed_park_repair_20261118_r1/train_lowspeed_park_40m`
- **父权重锁定**：原 `v1` (`a55eeaed11ed7c7471444e1369153824b3fe79544e59296c911a3235507bd7a4`)，未从旧末权重或 `025m` 续训
- **实际 PPO 起点**：`2026-11-18T01:15:23.026543+08:00`
- **停算保存点（2340s）**：`2026-11-18T01:54:23.026543+08:00`
- **硬截止时间（2400s）**：`2026-11-18T01:55:23.026543+08:00`
- **远端进程**：训练 PID `3679400`，截止守护 PID `3679401`（RTX 4090 显存占用约 `7134 MiB`，算力利用率 `76%`）
- **本地守护**：`monitor_run.py` 后台守护已启动，每 5 分钟完整拉取 PT 并自动运行独立 20cm 五起点评测（含 1x 视频）+ `flat60`，同步在线成功轨迹，收尾自动执行五项全回归

## 预检与首轮更新核验

1. **600 步 0-PPO 原生预检通过**（`native_lowspeed_park_probe_v1_r2`，`r1` 因 `float32(1.2)` 精度比较触发断言已在 0PPO 安全退出并完整保留于远端/本地记录）：
   - `PPO_updates = 0, optimizer_updates = 0`
   - `E0` 动作/STD/整网参数最大变化 `0.0`，无进展停滞样本最大净奖励 `-0.00040 < 0`
   - 同状态单轮台顶 `200` 帧净奖励 `-11.929 -> +13.387`（净正 `33 -> 174`）；双轮台顶 `560` 帧 `+39.602 -> +289.766`（净正 `441 -> 559`）
   - 预检场景正常安全关闭（`SAFE_CLOSED.json`），GPU 释放回 `110 MiB` 后再启动正式 PPO

2. **首轮真实 PPO 更新核验（`FIRST_UPDATE.json`）**：
   - `iteration = 1`，`actual_Adam_steps = 12`，首个完整检查点 `model_first_complete.pt` SHA `9d846a3f52691889bc67eb12eb3e87e375b6a5e06df90e6bd6b7b5bac735e03c`
   - `E1` 四组可训参数均实际更新（`head 1.12e-3, encoder 1.09e-3, STD 7.72e-4, critic 1.04e-3`）
   - `E0`（`c874`）actor/STD/critic 最大变化与梯度范数全为 `0.0`
   - 四阶段回放池实际载入 `5,444` 帧：`[settle_high=150 (pinned v1), approach=4753, top_climb=541, top_park=0]`
