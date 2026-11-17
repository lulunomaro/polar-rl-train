# MOD4V3_MOE_ROUTE2_ELEGANT_GATED_PPO_20261118 40分钟 PPO 启动与首轮更新核验报告

## 1. 训练时钟与进程
- **实验目录**：`MOD4V3_MOE_ROUTE2_ELEGANT_GATED_PPO_20261118`
- **远端路径**：`/home/egde/rl_candidates/mod4v3_moe_route2_elegant_gated_ppo_20261118_r1`
- **训练任务**：`train_elegant_gated_40m`
- **远端训练 PID / 截止守护 PID**：`3722817` / `3722818`
- **实际 PPO 计时起点**：`2026-11-18T02:42:27.974920+08:00`（epoch `1794940947.9749203`）
- **停算保存点（`2340s`）**：`2026-11-18T03:21:27.974920+08:00`
- **硬截止时间（`2400s`）**：`2026-11-18T03:22:27.974920+08:00`
- **预算与策略**：独立 2400 秒预算，无自动延长、无自动重启、无自动晋升默认模型。

## 2. 600步 0-PPO 原生预检（`native_elegant_gated_probe_r1`）
- **状态**：`passed = True`，`PPO_updates = 0`，`optimizer_updates = 0`，安全关闭并释放显存。
- **0 更新原生 Isaac Sim 实测完成**：仅 600 步（12 秒仿真）即完成 **`6` 次完整 20cm 攀爬 + 1.0 秒 `v=0, h=0.20m` 台顶驻车**（参考 DR 组 4 次、nominal 组 2 次），验证了接触门控攀爬头 + 台顶驻车头在 PhysX `TGS32/4` 下的跨仿真一致性。
- **隔离核验**：`normal_action_max_error = 0.0`、`normal_STD_max_error = 0.0`、`Isaac_MuJoCo_forward_max_error < 2e-5`、`history_queue_max_error = 0.0`。

## 3. 首轮真实 PPO 更新核验（`FIRST_UPDATE.json`）
- **检查点**：`model_first_complete.pt`（SHA256 `ea8cf42a7c13ffe1a45e0b30ac8a50f92c642fa9f64f00d7d3aa0472d266f09d`），`iteration = 1`，`actual_Adam_steps = 12`。
- **`E1` 五组可训练参数均实际更新**：
  - `E1_head`：`0.0008555`
  - `E1_top_head`：`0.0008493`
  - `E1_encoder`：`0.0008568`
  - `E1_STD`：`0.0009360`
  - `E1_critic`：`0.0009565`
- **冻结隔离严格为 0**：
  - `E0_actor_STD_max_change = 0.0`
  - `E0_critic_max_change = 0.0`
  - `E0_gradient_norm = 0.0`（含 `E1.approach_base` 与 `E1.gate` 零变化、零梯度）

## 4. 本地监测守护
- `monitor_run.py` 后台守护已启动，已自动同步校验 `model_first_complete.pt`；将按 5~35m 每 5 分钟收集检查点并执行独立 `evaluate_student200.py --video` + `flat60`，收尾自动执行全部 5 项冻结回归与最终报告。
