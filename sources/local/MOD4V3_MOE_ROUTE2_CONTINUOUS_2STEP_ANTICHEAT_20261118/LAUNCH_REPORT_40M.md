# MOD4V3_MOE_ROUTE2_CONTINUOUS_2STEP_ANTICHEAT_20261118 40分钟反作弊+连续二级台阶 PPO 开训报告

## 1. 训练时钟与进程契约

- **实验目录**：`MOD4V3_MOE_ROUTE2_CONTINUOUS_2STEP_ANTICHEAT_20261118`
- **远端作业**：`/home/egde/rl_candidates/mod4v3_moe_route2_continuous_2step_anticheat_20261118_r1/train_2step_anticheat_40m`
- **训练 / 截止守护 PID**：`3888967` / `3888968`
- **实际 PPO 起点**：`2026-11-18T09:28:04.448554+08:00`
- **停算保存时间（`2340s`）**：`2026-11-18T10:07:04.448554+08:00`
- **硬截止时间（`2400s`）**：`2026-11-18T10:08:04.448554+08:00`
- **父权重（`model_step000.pt`）SHA256**：`274a134a4289a829f45888843ce2deac572687cf9deee0b289453da39b510c25`

## 2. 零更新预检（`native_2step_anticheat_probe_r2`）与首轮更新核验

1. **远端 600 步 `0-PPO` 预检通过并释放显存**：
   - 环境分层：`height_population = [246, 573]`（`30%` 单阶 `20 cm` + `70%` 连续二级台阶 `20+20=40 cm`，`1.50 m` 踏面，Warp 射线实测烘焙高度误差 `< 1e-5`）。
   - `0` 更新实测：首秒塌腿 `0.00%`，`12 s` 内完成 `95` 次双轮登上一级台阶（`[83, 12]`）及 `12` 次完整登顶+`1.0 s` 驻车（`[[7, 0], [5, 0]]`），`SAFE_CLOSED.json` 落盘，GPU 释放至 `110 MiB`。
   - 注：`probe_r1` 因初始二级台阶总跨度使起点 `4.10 m > 4.00 m` 触发 `r1_boundary` 超界超时已在 `0-PPO` 预检拦截并完整保留证据，缩减顶台至 `2.2 m`（保持 `1.50 m` 踏面与 `1.20 m` 助跑距不变，起点 `3.80 m < 4.00 m`）后 `probe_r2` 一次通过。
2. **双阶段首轮更新核验通过**：
   - `iteration == 1`（`FIRST_UPDATE.json`，SHA `4ce1ee7e`）：15 轮 Critic-Only 预热生效，`E1_critic` 更新 `1.18e-3`，Actor 全部五组变化严格为 `0.0`。
   - `iteration == 16`（`FIRST_ACTOR_UPDATE.json`）：Critic 预热结束首轮联合更新，`E1_head / E1_standup_head / E1_top_head / E1_encoder / E1_STD / E1_critic` 六组全部非零有限更新（`2.08e-4 ~ 2.90e-4`）。
   - `E0`（真 `c874`）Actor / STD / Critic 参数变化与梯度严格全 `0.0`。
3. **本地监控流水线**：`monitor_run.py` 已后台运行，每 `5` 分钟自动拉取完整检查点并执行独立 `single_step`（`20 cm` + 1x 视频）、`two_step`（连续 `20+20=40 cm` + 1x 视频）与 `flat60` 回归。
