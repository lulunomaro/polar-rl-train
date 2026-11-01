# MOD4 traditional control workspace

本目录是 2026-11-01 新建的独立调试工程。原项目、源 STEP、旧 MJCF/USD、旧训练与预算文件保持原样。

远端任务根：`/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_MUJOCO_LQR_MPC_STEP270_20261101`。

- 物理：MuJoCo 3.12.0；31 个机器人刚体、30 个关节、6 个真实电机；400 N 工程弹簧参数；物理步长 0.5 ms，反馈/传统控制 100 Hz。模型源与导出 SHA 见 `MODEL_PROVENANCE.json`。
- `full_lqr.py`：14 状态、6 输入、闭链与圆轮支撑降阶线性化后的离散 LQR。
- `linear_mpc.py`：带转矩约束的凝聚有限时域 QP；15 步地面预测，接近与落台恢复在线滚动求解。腾空仍由分相位关节控制与俯仰反馈负责；MPC 地面预测没有显式建模 D4 目标队列。
- `hybrid_trial.py`：接近、蹬伸、收腿、展腿、落台与恢复；所有状态推进来自完整 MuJoCo，根部没有外加力或轨迹位置覆盖。
- `dr_components.py`：D0–D7 按已核实工程范围；每回合固定物理参数、偏置和延迟，每反馈 tick 采样噪声，每物理 tick 应用处理后目标队列。
- `run.sh`：远端固定 GPU 0，复用原隔离 Python；所有缓存沿原启动器写回 zonglin2 根。MuJoCo 刚体求解运行在 CPU，CUDA CEM 用于参数候选采样/排序；不声称 GPU 刚体大规模仿真。

## 单次运行

在远端使用：

```bash
TASK='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_MUJOCO_LQR_MPC_STEP270_20261101'
bash "$TASK/run.sh" "$TASK/run_case.py" \
  --controller mpc --full-dr --seed 5063 \
  --out NEW_UNIQUE_CASE_ID
```

输出目录必须使用新名字。结果 JSON、真实 qpos/qvel 轨迹和源码快照保留原件。

## 验收与解释

真实竖直 0.27 m 箱形台阶；双轮在同一次腾空中完整越过边缘；顶面法向接触力每轮超过 1 N；随后双轮完整脚印在台顶、无非轮承载、姿态直立余弦大于 0.95、线速度低于 0.3 m/s、角速度低于 0.5 rad/s，连续至少 0.5 秒。跨沿后掉回下层地面或退回台边的候选不得凭后续动作补算成功。接触回弹与非轮接触次数逐次记录。闭链误差终止 10 mm，mimic 终止 0.01 rad，非有限或大角度姿态事件终止。

结果中的 `success` 是曾完成稳定窗口的记录；还要同时看 `stable_at_end`、`stop_reason`、接触回执及真实轨迹。早期宽松验收命名含 success 的目录仅保留为历史试错，以最新验收版本为准。

D0–D7 范围是工程压力分布，非实物标定。最终版本的 roll/pitch 导数和 yaw 导数使用采样后的重力/IMU，腿反馈也经过噪声、偏置和队列。控制仍使用仿真真实平移位置/速度、yaw 角及接触相位；实机状态估计和全反馈延迟尚未验证。名义或全 DR 仿真通过均不等同实机就绪。名义候选在落台转换有 1 个控制采样的短暂非轮接触；单独提供的全 DR 成功示例在 100 Hz 记录中全程非轮接触为 0。

本轮保留源 MJCF 的被动电机关节阻尼（腿 0.2、轮 0.015 N·m·s/rad），另外执行 60/2 与轮速度 0.6 的显式 PD；它与最近 PhysX 文件的被动电机 damping=0 存在差异。气弹簧 400 N 指上限行程静态力，原 preload reference 保留，q=0 时约 441.28 N，工程质量惯性尚未实物标定。

最终结果和 128 条完整 DR 回执以 `results/FINAL_FULLDR_MATCHED_V2/summary.json` 为准；两套策略使用相同 64 种子，MPC 另有固定 5 ms 一阶反馈预测，LQR 无此预测。`FINAL_DR_TRIALS.csv` 提供逐种子摘要，`FINAL_METRICS.json` 和 `summarize_final.py` 提供独立保存轨迹验收。完整说明见 `RESULTS_20261101.md`。

本机渲染使用已保存 qpos/qvel 和 MuJoCo 3.14 `mj_forward`，没有重新积分；物理结果来自远端 MuJoCo 3.12。

Git 归档要求已查到，当前未执行提交或推送；新增代码、配置、失败、结果应作为一个独立阶段后续归档，凭据不进入文件或索引。
