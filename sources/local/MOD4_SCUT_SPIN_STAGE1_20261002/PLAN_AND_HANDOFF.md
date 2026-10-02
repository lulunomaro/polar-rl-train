# MOD4 首档小陀螺：给接手 AI 的执行说明

> 最新移动需求：2026-10-02用户明确小陀螺时0.5 m/s足够。下一阶段以0.15→0.3→0.5 m/s世界定向移动为目标；当前原地自转/独立站跑生产不变。详见SPIN_TRANSLATION_0P5_REQUIREMENT_20261002.md；并非已实现边转边移动。

> 最新预算：2026-10-02用户再次明确追加20小时，canonical总有效预算现为180000秒（50小时）。扩展USER_ADD20H_20261002_1520已应用；下文原108000秒/30小时是部署时历史值，以MOD4_BUDGET_ADD20H_20261002_HANDOFF.md为准。当前45分钟试训与其验收时间不变，PPO未中断。

用户于 2026-10-02 明确授权：先做偏航短物理验收，完整保存边界切换，从成熟策略训练左右持续自转 1–2 rad/s；保留站立、走跑；以后再自转定向平移、启停反转、地形与更高转速。

## 本阶段与授权预算

隔离根目录 `/home/egde/rl_candidates/MOD4_scut_spin_stage1_20261002`。原轻 DR 根目录 `/home/egde/rl_candidates/MOD4_mild_dr_trial_20261001` 保留。唯一预算仍为 `/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json` 的180000秒有效PPO（50小时），包含已应用的两条明确扩展USER_ADD20H_20261001_2341及USER_ADD20H_20261002_1520；不得重复应用，不复制账本、不清零charged。冻结评测在无 trainer 时不计 PPO；128 环境预检 PPO 计入同一账本，预检权重弃用。

保持 20000 env×24、solver16/4、原生 Plane、详细 MOD4 USD、真实 root 目标 .25m、3500 N/m 预载弹簧、六电机硬件限制、white_v1 轻 DR、35/38 维观测、6 动作、256/128/64 网络、奖励和 PPO 系数。完整恢复 actor、critic、optimizer、std、iteration。实物 300–700N 弹簧曲线仍未标定。

## 唯一允许的新课程差异

`spin_commands.py` 显式关闭 heading correction 和旧 gyro_window。指令重采样 4–8 秒：预期站立10%、直线60%、纯自转30%；自转左右均衡，绝对角速度均匀 1–2 rad/s，约9.55–19.10 rpm。纯自转时 vx=vy=0；直线样本 yaw=0、vx仍在±1.5m/s。观测维度不变。不启用旧±13rad/s的课程，不直接加速度上限或新的硬件随机化。

这是 MOD4 的可控课程适配，不能称 SCUT 全套配置字节一致。world 定向平移尚未实现：后续必须用明确的固定/世界方向速度，经机身 yaw 变换到策略 body-frame 指令；同时核验轮腿的侧向非完整约束、跟踪奖励与可行性。直接 constant body vx+constant yaw 会画圈，不能当作定向平移通过。

## 执行顺序和证据

1. 现有生产继续时，只在无现存自动回放时做18env×300步冻结短验收；程序错误保留日志后修复，不影响原训练。左右±1/±2 rad/s、直线、停车分组，物理安全与未训练的新 yaw 技能分别报告。
2. `supervise_spin.py` 验证源指纹、短验收后暂停经 /proc 确认的旧 supervisor 启动权限，STOP_AFTER_SAVE 请求 trainer 完整原子保存，验证 latest_complete 与完整有限 checkpoint 后退出旧父、结清同一账本，取得原 canonical lock。禁止双开。
3. 旧20k生产完全退出后，20k×1.2s冻结混合 yaw 原始接触/法向/有限数/闭链/材料验收；128env×2轮完整 PPO；同权重80env×15s旧站跑回归。短时高度警告和技能是否通过分别保留，不用未学会 yaw 否定物理可以训练。
4. 从交接的正式完整权重开始45分钟试训；从未用预检 PPO 权重开始生产。结束后依次同权重冻结15s旧站跑与72env左右 yaw/启停/反转回放。旧站跑实验准入+自转物理安全通过才继续学习；新 yaw 跟踪未达标并不等于应该从零重训。
5. 剩余时间按最长两小时 PPO 段继续，保存后冻结检查。同一 canonical 有效时间预算逐段结清。出现物理/旧站跑真实退化，保留所有自转权重，从交接前成熟完整 checkpoint 用原轻 DR 直线配方恢复剩余预算。
6. 到预算结束保存停止，分别报告 flat、nominal spin、mild spin 的15秒结果；不凭训练 success、reward 或积分接触100%宣布毕业。下一课程只有在这些结果支持时实施。

核心报告：`reports/spin_small_baseline.json`、`SHORT_ACCEPTANCE.json`、`handover_completed.json`、`spin_fullscale_20k.json`、`FULLSCALE_ACCEPTANCE.json`、`PPO_PREFLIGHT_128.json`、`handover_flat15s.json`、`spin_production_started.json`、`trial45_decision.json`。一切实际进展以这些文件、status、日志和真实进程为准。

## 检查口径

自转回放同时给目标/实际 yaw、角速度误差、signed 与 absolute turns、XY 漂移、停车角速度、倾角/真高度、动作 delta/d2、逐环境存活、闭链/mimic、电机实际裁剪、导轮/底盘载荷。保留 .5ms 卸载时长与载荷冲量、10ms输入轮网格间隙和最低支撑点滑移近似。间隙/力矩不是子步峰值，滑移不是 PhysX 流形；低力不是腾空。旧端点窗口只是影子口径，不把更换统计当作学习。

物理烟雾验收不是15秒技能毕业；新 yaw 技能必须明确15秒，组通过≥80%，方向正确、误差≤max(.2rad/s,.2|cmd|)，倾角/高度/平滑/接触物理限制与旧能力保留。这些是本项目条件，不是 SCUT 或赛场官方标准。

## 重启与可视化

入口 `isaac/mod4/supervise_spin.py` 是一次性接管程序。已有 handover 或 production receipt 后不可盲跑 main。突然重启先核对真实 PID/cwd/cmdline/start_ticks、checkpoint、关机证据与 active_segment，结清上次实际运行时间，保留 charged；再写安全续训入口，不重复扩预算或接管。监督器出错但 trainer 仍运行时不可双开。

新 Ubuntu Rich 终端 `isaac/mod4/tui_spin.py --interval 5`：读本目录 status/active_log 和同一 canonical 账本；5秒只刷新本地文件。区分在线探索统计、冻结直线回归、自转15秒验收。线程自动巡检每两小时一次，健康无实质变化安静。

## 后续任务（本阶段没有冒称已实现）

稳定左右持续自转 → 独立角速度启停/反向课程与恢复 → 可行的世界定向平移命令转换/跟踪 → 现有 SCUT Rough v1 隔离适配坡/起伏/台阶并保留平地 → 自转与地形混合 → 更高转速/正弦转速。Rough adapter 仍在 `MOD4_SCUT_ROUGH_V1_ADAPTER_20261002`，不能直接切 flat-only reset 或加载 RMUC。MoE、负载云台适配与实物弹簧 DR 仍是独立后续事项。
