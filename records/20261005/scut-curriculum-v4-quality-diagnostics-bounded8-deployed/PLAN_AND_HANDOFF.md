# 华南虎课程思路全面对齐候选 v4

用户明确要求对齐华南虎门槛，避免自设过严质量线无限卡升档。依据固定公开提交 b8ff79f3df855faf9dc92f4a282bd80c42649466 的 V14 Flat：速度/转速/高度/动作和静止平移通过连续奖励优化，没有本项目的15秒数值毕业合同；高转命令按训练迭代启用。不是其机器人/任务/重置或奖励的一比一移植。

scut_curriculum_v4_performance_diagnostic 取消有限的跟踪误差、姿态均值/峰值质量、高度、动作差分、轮载均值、低载时长、网格gap、停车、裁剪使用率和所有滑移数值的课程硬否决。所有原始指标、原flat/mesh/legacy/loaded015/旧版本布尔继续并列。真实任务终止/重置、NaN/Inf、MOD4闭链2mm/mimic.01rad、参数/接触数据一致性和完整性仍硬检查。硬件转矩转速限幅始终由现有任务执行；使用率不是越界。现有MOD4训练总倾角.75rad/底盘地面50N等真实重置规则不改，不冒充SCUT的40deg+20控制步。

课程改为完成有界45分钟有效PPO暴露后，以最新正式完整策略做真实站跑/自转及两个seed nominal/white配对的故障/完整性回归，通过即允许下一档学习；取消两份正式策略连续通过和80%质量数值毕业关卡。双seed初态/参数检查是模型及DR正确性证据，不是性能数值线。下一档短3秒/20k物理和128完整PPO仍检查实际故障/模型/材料/完整性，旧短检15deg/高度/clip等不会暗中再次否决。当前8档已经通过旧预检并正式PPO，迁移复用预检，继承45分钟剩余，不重发探针或预检。

允许学习/课程晋级不是宣称目标能力已成熟。2rev/s=4π最终需左右实测signed yaw，双seed和最终报告各方向>=80%样本距指令<=.2rad/s才写实际目标确认。该目标事实核验只在4π终点，不能卡中间档。目标未实测达到则继续当前终点学习到授权预算，不用cap登记宣布120rpm已达。

代码C=/home/egde/rl_candidates/MOD4_SPIN_ROLLING_REPAIR_20261004；status/log/canonical ownerP=/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002。新入口supervise_scut_curriculum_v4.py和SCUT_CURRICULUM_V4_STATE将是阶段依据；旧v3及所有旧入口历史化。当前准备阶段尚未部署；实际部署以HANDOVER/MIGRATION.completed、真实PID和run freeze为准。

预算唯一canonical仍/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json，324000秒90h/四登记扩展各一次，不新增/复制/清零。迁移在已核验父的账本写入外睡眠边界暂停启动权限，trainer仅自身STOP_AFTER_SAVE完整保存退出，退出证据及CPU68浮点完整后退休旧父/guardian、取得原锁、结真实尾段一次、保留所有策略并安装新文件。新父/guardian独立session、trainer deadline<=2h，PPO预检加载保存退出计同账本，冻结/迁移停机不计。不得重跑旧事务或这次已执行的entry/migration。

原地spin优先，moving/FPS/地形/云台/MoE仍延期；white_v2/rolling_v1/任务/物理/硬件/PPO/reset/网络字节不改。每2小时线程巡检、健康静默和原Rich5s本地刷新继续。预算/真实目标终验后finished/AUTONOMY_FINISHED才能删除mod4-10；repair_hold不等于finished。

来源：[公开V14配置](https://github.com/scutrobotlab/wheeled-legged_RL/blob/b8ff79f3df855faf9dc92f4a282bd80c42649466/source/agent_tasks/agent_tasks/direct/wheelbipe/wheelbipe_V14/env_cfg.py)。详细逐项语义和继承源见此前MOD4_SCUT_GATE_DIFF_AUDIT_20261005/REPORT.md。
