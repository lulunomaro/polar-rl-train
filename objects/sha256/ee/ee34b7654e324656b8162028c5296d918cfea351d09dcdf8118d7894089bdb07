# 接管任务清单

## 0. 保留现有工作

- [ ] 先读 `CURRENT_STATUS.md` 和基线哈希；不要停止当前进程来跑本包。
- [ ] 用 `stage_candidate.py` 做只读核对。有源码漂移就审阅 diff 并重新合并，不跳过哈希检查。补丁绑定 Isaac Lab 3.0.0-beta2.patch1 的实际 `ManagerBasedRLEnv.step`；运行库变化必须重审步进循环。
- [ ] 运行单元测试，创建独立候选；保留当前训练结果及原 `model_16295.pt`。工作目录没有 Git，不能依赖 `git reset` 回滚。
- [ ] 本包传感器修复只适用于 8 个导轮各有独立刚体/被动 revolute 的 rolling USD。核对资产哈希及 30 个运动关节；保留 6 条闭链和 4 条 mimic。

## 1. 先验控制接口，再跑训练

- [ ] 环境空闲时，在候选上按 1→16→64 环境分别运行受限烟测，输出源码、USD、PhysX 版本、真实 action/observation 顺序和物理参数。不要先开 1024 环境。
- [ ] 核对策略动作仍是 `[left_crank,left_hip,right_crank,right_hip,left_wheel_spin,right_wheel_spin]`。记录实际 24 V 电压约束、DM8009P 腿电机及 DM3519/总减速比 15.8 的速度—力矩裁剪，不用 PhysX 表格中的原始 effort 上限代替外部电机模型。
- [ ] 验证事件顺序：驱动随机化/气弹簧预载→physics→地面/路线/离地/落地状态→termination/reward→完整回合计数和终态快照→reset→下一次观测。每步状态机只能推进一次；先更新离地状态，再处理落地缓冲。
- [ ] 强制一个 env 成功、下回合碰撞失败，确认日志记为 2 次尝试/1 次成功；同一步 goal+安全失败只能算失败。改变 reset 子集，确认其他 env 的历史、路线、着陆计时未被清空。
- [ ] 至少完成计划的全部烟测迭代；任意缺指标、NaN、异常退出必须失败。闭链最大残差 ≤2 mm，mimic 最大残差 ≤0.01 rad；同时检查姿态、关节范围、力矩限幅和未被传感器覆盖的接触。阈值通过只是该烟测范围内健康。

## 2. 修复评测与自动晋级

- [ ] 运行 `eval_episodes_mod4.py`，不用旧 `eval_terrain_mod4.py` 的跨回合 OR 标志当通过率。每个 env 的终态必须在 reset 前保存，保留 route_id、episode_id、失败原因和进度证据。
- [ ] 完整回合是分母，末尾未结束回合单列 censored；每个种子都要有目标地形完成回合。至少 3 个固定种子、每类合计 ≥20 回合只是最低证据门槛，正式报告建议每类每种子 ≥100 回合并报告置信区间。
- [ ] 用同一套修复后的任务、名义参数、路线长度、随机种子评估原基线和候选。不要把旧评测器的百分数当成新基线。
- [ ] `tools/run_nominal_suite.sh` 会在检测到 RL 进程时拒绝启动。其默认 9000 步覆盖两个 45 s 回合时长；失败退出不会被吞掉。输出目录必须全新。
- [ ] 将当前链脚本里的评测 `|| true`、自动生成 retention 基线、缺指标 WARNING 放行全部移除。所有 gate 的非零退出码都必须阻止晋级；加入“缺文件/损坏 JSON/某种地形缺失”的负向验收。
- [ ] 保持 run/ramp_up/step_up/rough_cross/slope_spin 等已会技能的独立验收。包内 gate 默认绝对通过率 ≥0.60、相对基线下降 ≤0.10；run 如沿用原标准须单独用 `--bar 0.8`。这些是候选工程门槛，不是比赛通过率保证。

```bash
# 两次分别评估 baseline 和 candidate；必须等现有 RL 工作空闲。
bash "$PKG/tools/run_nominal_suite.sh" "$CANDIDATE" "$BASE_CKPT" "$BASE_REPORTS" 64 9000
bash "$PKG/tools/run_nominal_suite.sh" "$CANDIDATE" "$NEW_CKPT" "$NEW_REPORTS" 64 9000
"$PY" "$CANDIDATE/isaac/mod4/repair_gate.py" \
  --baseline "$BASE_REPORTS"/seed_*.json --candidate "$NEW_REPORTS"/seed_*.json \
  --kinds run,ramp_up,step_up,rough_cross,slope_spin
```

## 3. 狗洞物理验收，不能只改奖励权重

- [ ] 以用户已经展示的“腿收到身体中间、触及限位、底盘导轮蹭地”作为姿态目标。原参考 `hip=+0.45029, crank=-0.63603 rad`，差值 `-1.08632 rad`；腿高约 **223.53 mm**。另一个有小余量的候选是 `hip=+0.470170, crank=-0.595844 rad`。这是姿态参考，不能直接当成当前 PhysX 资产已经通过的测量。
- [ ] 对当前 rolling USD 复测完整刚体/关节状态、左右硬限位余量、主轮和每个导轮的接地力、导轮角速度、主轮牵引、底盘接触。先证明低姿态可以受控前进/滑行，再做完整过洞；不能从旧固定导轮模型推断目前一定没有牵引。
- [ ] 净高使用当前地图测量的 **247.2 mm**，明确局部洞底坐标。每步计算全部启用的碰撞体与完整训练视觉/CAD 包络的上缘，按关节姿态和姿态角变换。不能用“腿最高点”、root 高度加常数或主轮最低点替代实际接地后的整机包络。
- [ ] 同时核对身体前后突出部分的进洞和出洞时刻；root 离开顶板范围不等于整机出洞。输出最小净空、发生时刻、零件名、左右轮载荷、车体 pitch/roll、最差样本；完整轨迹必须跨过出口。
- [ ] 从静止、低速、合理助跑速度分别测试，保留失败样本。胎面压缩/接触柔度只有在实测或材料数据支持时建模，不能调小轮径、删除碰撞、增大洞口或凭空加柔度让指标通过。
- [ ] 完整包络和牵引未验收前，`repair_gate.py` 对 tunnel 晋级保持失败。当前新评测器只记录行为完成率，`physical_clearance_verified=false` 是有意保留的待办状态。完成独立 envelope/traction 报告后，接入有资产/路线/轨迹哈希的验证器，再解开这一条 gate；禁止直接改布尔值放行。
- [ ] 拆分参数：`RM_TUNNEL_PRECROUCH_LEAD_M` 只控制提前蹲下；`RM_TUNNEL_SPAWN_LEAD_M` 只控制训练出生点前移，验收必须 0。旧 `RM_TUNNEL_LEAD_M` 仅作为前者兼容回退，不再改变出生点。

## 4. 编码器和课程单独恢复

- [ ] 先保持当前 plain actor、DR 关闭，完成上面控制与评测验收，再单独开启路线课程；不要在同一轮同时改 reward、模型、编码器和随机化。
- [ ] 课程按终止回合计数，用 route_id→kind 映射；禁止 `clamp(0,K-1)` 把后面的路线塞进 tunnel 桶。检查窗口不足 40 回合时不升降级，且“无样本”不记为 0% 成功。
- [ ] 开启序列编码前，用带唯一数值的每项历史向量验证 175 维布局，确认提取出的当前帧正好 35 维；同时测训练、TorchScript、ONNX 路径。新 gather 不改变原 observation 排列，encoder 仍接收 term-major 历史。
- [ ] 用纯 35 维基线做 35→38 的受控迁移：新增 head 列为 0、encoder 保持非零随机初始化。迁移初始动作与基线一致；一次更新后新增 head 列有梯度，后续 encoder 有梯度。旧序列检查点不能只因 shape 相同就当作等价恢复。
- [ ] 检查 jump curriculum：最新日志 jump 奖励全为 0，而 target/reach 仍变化；分别按 jump_in_place 和 fly_jump 统计真实起跳、升高、着陆及目标达成，核对不同任务是否混用一组达成率。该项需要新的运行轨迹，不能仅凭聚合日志定因。
- [ ] 最后逐项恢复随机化，记录质量/COM/摩擦/执行器误差/电压/延迟分布与最坏净空、技能保留率。1024 环境吞吐需独立 benchmark，当前 512 环境正常运行并不能证明 1024 达标。

## 5. 交付验收

- [ ] 输出 `runtime_smoke.json`、`episode_eval_*.json`、`retention_gate.json`、`tunnel_envelope_traction.json`、`reward_budget_by_kind.csv` 和视频。
- [ ] 按地形列正奖励、负奖励和成功奖励占比，比较站着不动、倒退、撞墙、完整通过的回报，确认没有奖励停滞或短程假成功。不要因总 reward 上升就晋级。
- [ ] 将所有报告绑定源码、资产、检查点 SHA256 和真实 runtime 参数；`run_manifest.effective` 原来是正则抓取的字符串提示，不能视为完整参数审计。
- [ ] 在接管 AI 确定切换窗口后才使用候选；回退方法是回到原工作目录和原启动配置，本包没有覆盖原文件。
