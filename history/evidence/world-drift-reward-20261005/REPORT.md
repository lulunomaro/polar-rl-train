# 世界定向横向净漂移奖励

用户授权：2026-10-05“你觉得需要加上吗？按照你想法来吧”。

原训练仅有 BODY 前向速度和 yaw 跟踪奖励，没有完整 yaw 圈的世界横向净漂移奖励。新增单项 `phase_compensated_cycle_cross_v1`，只作用于世界定向边走边转。原地、站跑、loaded_rolling_v1、white_v2、物理、硬件限幅、观察与动作、PPO和闭链 reset 不变。

用实际 heading 和位置累计圈。完整 2π 圈采用插值边界的真实横向净位移/时长；未完成圈减去理想轨迹本来就有的周期横向位移 `-V/(2ω)·(cos(2φ)-cos(2φ0))`。最近完整圈和当前余段提供连续净横向速度估计，初始分母至少四分之一请求圈时长。成本为 `clamp((estimate/.10)^2,0,4)`，权重 `-.3`，额外每秒惩罚上限1.2；.10只是连续优化尺度，没有新增课程硬否决。参数重采样和实际 episode reset 清空累计；站跑、原地模式成本严格为零。

这一余圈修正假设请求的恒定 signed yaw，属于工程奖励估计，不是直接材料点测量、完整位置纠偏或实车认证。完整圈真实方向指标、全窗口和所有旧质量布尔继续单列，不能把新奖励保存或课程接受当成能力改善。

72组精确运动学测试覆盖 V=.15/.3/.5、yaw左右1/2、不同世界方向和初始相位；正常周期摆动最大估计残差7.94e-6m/s，注入±.06m/s世界横向漂移均正确识别。重采样、reset、非移动模式和成本上界通过。已有22589轨迹离线重算完整圈横向速度与原测量最大差2.38e-9m/s，非移动成本全零；±1与±2样本的平均额外惩罚预览分别约-.0147和-.1667/s。这是旧轨迹上的离线计算，未证明新策略学习效果。

保存边界迁移已经将原 trainer311263 的正式22775完整保存并正常退出。SHA ca24f9f30216d43558e2c7ab9839d5f1c3f4b0b791218cd3940df5dd4cf2667a；CPU68浮点有限，actor/critic/optimizer/std/iter完整保留。唯一canonical尾段96.94167160987854秒只结一次，退出观测上界.25秒。旧父213707/guardian213749已退休，不恢复旧入口。没有追加预算。

新监督器首次在任何worker/PPO启动前因比较两个保存记录字典的元数据键不同而拒绝启动。实际路径、SHA、iteration、68有限tensor完全相同；错误完整保留为 INITIAL_SOURCE_RECORD_ERROR.txt。已改为比较这四个实质来源字段，唯一 SOURCE_RECORD_REVIEW_CONTINUATION 继续；没有重复迁移或结账。实际奖励开关回读、模型/旧能力/完整PPO及正式部署结果见后续 ACTUAL_VERIFIED.json，不能用本文预先声称通过。


实际部署核验 2026-10-05T22:05:02.243540+08:00：奖励off/on实际通过，动作/指令/rootXY/heading/q完整bit-exact，reward差公式最大误差 9.31322574615e-10/step。auto0233独立20k1.2s检查terminations=0、finite与材料/闭链通过v4，原combined=False、短高差0.06269720196723938m继续保留。auto0234/0235/0236原站跑/4pi/world各15秒分别80/88/88全存活、任务/模型/数据准入通过。固定旧22775世界事实16/64，不是新奖励已学效果。

128env2轮和20kenv4轮完整PPO预检通过，均扣原canonical、预检权重弃用；20k吞吐28660.99环境策略步/s。正式从精确完整22775恢复，KEEP_STD1/white_v2/world_v1/rolling_v1/goal.5/纯spin cap4pi，新term cycle_v1。实际run /home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/logs/2026-10-05_22-03-39_auto_0239_world_drift_learning_cap12.5664_white_v2。新PID330317/start36402806自己的22775 SHA737a8ce92a8647994e6684487917df7083c59574e1081cfbbcc4eff9b6eae7d3已CPU68浮点有限；这是新run初始保存，未做该策略15秒回放或宣称改善。

实际独立parent325437/start36271233、guardian325476/start36271298，唯一trainer的cwd/argv/session和账本PID一致；candidate164冻结与run完全相同、原P104精确核查。首段deadline 2026-10-05T22:45:49.269821+08:00，随后已有顺序flat/spin/world及双seed nominal/white十二份回归，不重复probe。预算总90h不变，本核验实时剩49126.871s，后续扣active尾段。世界完成后按授权再独立扩大物理DR，当前不混入；两小时监控保持。
