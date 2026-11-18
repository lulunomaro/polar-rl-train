# MOD4V3_MOE_ROUTE2_CONTINUOUS_2STEP_ANTICHEAT_20261118 修复与预检报告

## 1. 上一轮（`ELEGANT_GATED_PPO`）退化根因与反作弊修复

1. **回放池峰速被 `_reset_idx` 清零漏洞修复**：
   - 根因：Isaac Lab `env.step()` 内部在回合结束时先调用 `_reset_idx` 清零 `course_speed_max`，随后 `NativeSuccessRecorder.finish()` 读到 `episode_max_speed_m_s = 0.0`，导致 `0.85 ~ 1.20 m/s` 猛冲轨迹绕过 `<= 0.60 m/s` 限速污染 BC 池。
   - 修复：在 [continuous_stair_env.py](file:///d:/claude2/fangzhen/_mod4v2_src_20261106/sources/local/MOD4V3_MOE_ROUTE2_CONTINUOUS_2STEP_ANTICHEAT_20261118/support/mod4v3_ppo_v1/continuous_stair_env.py) `_update_course_events` 内（`_reset_idx` 之前）将真实峰速锁存至 `replay_episode_max_speed_at_step`，并在 [success_replay.py](file:///d:/claude2/fangzhen/_mod4v2_src_20261106/sources/local/MOD4V3_MOE_ROUTE2_CONTINUOUS_2STEP_ANTICHEAT_20261118/support/mod4v3_ppo_v1/success_replay.py) 强断言 `ep_max_spd > 0.05`，严守低速入池。
2. **零容忍反作弊（杜绝蹭阶拿奖励再滑落）**：
   - 在 [continuous_stair_env.py](file:///d:/claude2/fangzhen/_mod4v2_src_20261106/sources/local/MOD4V3_MOE_ROUTE2_CONTINUOUS_2STEP_ANTICHEAT_20261118/support/mod4v3_ppo_v1/continuous_stair_env.py) 建立双轮上阶承诺 `s1_committed / s2_committed` 与单轮累计触阶帧监测：一旦上阶后任意轮高度跌破 `step_z + R_w - 0.035 m` 或后退越过阶沿，**立即扣除 `-25.0` 追回罚分并当场终止回合（`term |= step_regressed_now`）**。
   - 在 [dense_top_reward.py](file:///d:/claude2/fangzhen/_mod4v2_src_20261106/sources/local/MOD4V3_MOE_ROUTE2_CONTINUOUS_2STEP_ANTICHEAT_20261118/support/mod4v3_ppo_v1/dense_top_reward.py) 禁止单轮静止挂阶刷分（单轮触顶必须 `vx >= 0.05 m/s` 才有推进分，倒退 `vx < -0.02 m/s` 台顶奖严格置 `0`）。
3. **15 轮 Critic-Only 预热**：
   - 在 [route2_optimizer.py](file:///d:/claude2/fangzhen/_mod4v2_src_20261106/sources/local/MOD4V3_MOE_ROUTE2_CONTINUOUS_2STEP_ANTICHEAT_20261118/support/mod4v3_ppo_v1/route2_optimizer.py) 强制前 `15` 轮 PPO 仅更新 `critic.mlp.e1`（Actor 梯度为 `None`、参数零变化），消除冷启动 Value 误差对热启动 Actor 的冲击。
4. **连续二级台阶（`20 cm + 20 cm = 40 cm`，`1.5 m` 踏面）与不相交相平面门控**：
   - 地形配置（[single_step_geometry.py](file:///d:/claude2/fangzhen/_mod4v2_src_20261106/sources/local/MOD4V3_MOE_ROUTE2_CONTINUOUS_2STEP_ANTICHEAT_20261118/support/single_step_geometry.py)）：`30%` 环境为单阶 `20 cm`（`3.0 x 3.0 x 0.20 m`），`70%` 环境为连续二级台阶（一级 `5.2 x 5.2 x 0.20 m`、二级 `2.2 x 2.2 x 0.40 m`，踏面净深严格 `1.50 m`，起点距一级阶沿 `1.20 m` 处于 `4.0 m` 边界内）。
   - 专家结构（[route2_common.py](file:///d:/claude2/fangzhen/_mod4v2_src_20261106/sources/local/MOD4V3_MOE_ROUTE2_CONTINUOUS_2STEP_ANTICHEAT_20261118/support/mod4v3_ppo_v1/route2_common.py)）：在 `(obs[3], ext, d_ext)` 相平面无重叠路由 `approach_base`、`head`、`standup_head` 与 `top_head`。

## 2. 本地纯学生 `model_step000.pt`（SHA `274a134a`）独立实测成绩

- **常规运动保留（`E0`）**：`flat60 = 60 / 60`（相对真 `c874` 最大动作/STD/Critic 参数差严格为 `0.0`）。
- **单阶 `200 mm` 纯学生五起点（`evaluate_student200.py`）**：正式 `<= 0.60 m/s` 通过 **`3 / 5`**（`-60, 0, +30 mm`），双轮越边且稳态驻车 **`4 / 5`**，滑落 `0 / 5`；实测视频 [STUDENT_CENTER_1X.mp4](file:///d:/claude2/fangzhen/_mod4v2_src_20261106/sources/local/MOD4V3_MOE_ROUTE2_CONTINUOUS_2STEP_ANTICHEAT_20261118/evidence/preflight_step000/single_step/STUDENT_CENTER_1X.mp4)。
- **连续二级台阶 `200 + 200 = 400 mm` 纯学生五起点（`evaluate_2step400.py`）**：一级越边 **`5 / 5`**，**二级全登顶 + `<= 0.60 m/s` 正式驻车通过 `2 / 5`**（`-60 mm` 峰速 `0.5851 m/s`、`0 mm` 峰速 `0.5748 m/s`；另 `-15 mm` 峰速 `0.5039 m/s`），**滑落退阶 `0 / 5`**；实测视频 [TWO_STEP_CENTER_1X.mp4](file:///d:/claude2/fangzhen/_mod4v2_src_20261106/sources/local/MOD4V3_MOE_ROUTE2_CONTINUOUS_2STEP_ANTICHEAT_20261118/evidence/preflight_step000/two_step/TWO_STEP_CENTER_1X.mp4)。
