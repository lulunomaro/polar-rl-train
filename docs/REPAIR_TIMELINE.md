# 修复与试错主线

这里是阅读导航，原报告保留完整指标、协议和失败样本。历史计划可能已被后续审计取代，不能按旧计划直接重启生产。

|日期|版本/问题|实际变化与边界|原证据|
|---|---|---|---|
|09-10～09-15|早期模型/场地/材料与规模试验|保存机械模型、RMUC 来源、材料合并、不同 env/solver 的运行配置与快照。后续平地阶段不因此声称在 RMUC 训练。|[ENV_SCALING_AB_20260927.md](../sources/remote/MOD4_takeover_20260914/scut_flat_repair10h_20260927/ENV_SCALING_AB_20260927.md)|
|09-16～09-18|其他 AI 的平地专项对照|收录 DEEPSEEK_V41_20260916 中延长训练、PD、动作幅度、噪声 A/B 与原总结。原文判断保留为当时主张；作者仅按证据声明，不由目录名推断。|[SUMMARY.md](../sources/remote/DEEPSEEK_V41_20260916/experiments/obs_noise_ab/SUMMARY.md)|
|09-27|完整续训、12k/16k/20k 测速与手动关机恢复|保留所有测速、完整权重恢复和监督记录。用户确认的手动关机不能归因于 20k OOM；测速临时策略不替代正式来源。|[RESUME_AFTER_MANUAL_SHUTDOWN_20260927.md](../sources/remote/MOD4_takeover_20260914/scut_flat_repair10h_20260927/RESUME_AFTER_MANUAL_SHUTDOWN_20260927.md)|
|09-27～09-28|弹簧、强姿态惩罚与高度实验|保留弹簧关/开和力曲线对照、SCUT 适配、强倾角/低高度惩罚及高度课程。旧弹簧 DR 报告不等同已标定的实物力—行程验收。|[STRONG_POSTURE_EXPERIMENT_20260928.md](../sources/remote/MOD4_takeover_20260914/scut_v14_strong_posture_20260928/STRONG_POSTURE_EXPERIMENT_20260928.md)|
|09-29|SCUT 平地移植三项修复|真实平地 z=0，纠正未加载 RMUC 射线地面扣高度；纠正指数 sigma 分母被再次平方；使用完整闭链逆解复位库。暖启动保留网络/优化器/std。|[scut_flat_rescue.py](../sources/remote/MOD4_scut_rescue_20260929/isaac/mod4/scut_flat_rescue.py)|
|09-29|接管审计与错误判断纠正|保留另一 AI 窗口判据和瞬时影子；纠正“瞬时低力=厘米腾空”的过度推断。实测 lazy 历史 10ms 不能冒称已实测 3×5ms。|[RESTART_AUDIT.md](../sources/remote/MOD4_scut_continue10h_20260929/RESTART_AUDIT.md)|
|09-30|直线课程范围修复与单因素接触诊断|关闭误覆盖的旧 gyro yaw 课程；保留 solver/轮网格/固定腿探针。对照未一致改善的方案不部署，不把相关性写成原因。|[REPAIR_PLAN.md](../sources/remote/MOD4_scut_speed_repair10h_20260930/REPAIR_PLAN.md)|
|09-30|接触采样积分修复|0.5ms 子步冲量累计，每 5ms 写均力历史。冻结物理数组对照和奖励门控验证保留；旧端点/eager/积分并列，统计变化不是学习进步。|[README.md](../sources/remote/MOD4_contact_integrated_repair_20260930/README.md)|
|09-30～10-01|原生 Plane 地板修复与续训|原 4km 薄地板失败样本的 raw 法向证据及同策略单因素对照；原生 Plane 消除该异常。不把所有失败归因于地板，保留未部署限速方案。|[FINDINGS.md](../sources/remote/MOD4_NATIVE_FLOOR_FIX_NEXT_AI_20260930/FINDINGS.md)|
|10-01|轻 DR 的实际回读、试训和配对|white_v1 只随机共同质量惯量、主轮摩擦和六电机输出；保留 nominal 配对、全量 combined 警告及独立物理验收。|[MILD_DR_HANDOVER_20261001.md](../sources/remote/MOD4_AUTO_PROGRESS_NEXT_AI_20261001/MILD_DR_HANDOVER_20261001.md)|
|10-01～10-02|执行器裁剪诊断与预算/归档程序修复|纠正策略顺序与执行器局部 gain 顺序错配；预算扩展 ID/唯一账本、SameFileError 安全归档、STOP 控制目录和孤儿预检尾段核算保留。|[MOD4_BUDGET_ADD20H_20261002_HANDOFF.md](../sources/remote/MOD4_scut_spin_stage1_20261002/MOD4_BUDGET_ADD20H_20261002_HANDOFF.md)|
|10-02～10-03|纯自转 1–2→3→4→6rad/s 阶梯|保留各档短预检、正式训练、两次技能及两 seed nominal/white 回归。4rad/s 有多 seed 成熟证据；归档时 6rad/s 仍在学习，目标 120rpm 不是已达到。|[rate4p0_model15583_multiseed.json](../sources/remote/MOD4_scut_spin_rate_20261002/reports/rate4p0_model15583_multiseed.json)|
|10-02～10-03|传感器 DR 的拒绝与隔离定位|全 sensor_v1 与 delay-only 出现真实异常，保留拒绝/回退证据；noise-only 单 seed 冻结检查不能冒称正式部署或实车适配完成。|[SENSOR_REJECTION_AND_ABLATION_20261003.md](../sources/remote/MOD4_sim2real_sensor_dr_20261002/SENSOR_REJECTION_AND_ABLATION_20261003.md)|
|10-03|本机最新策略与普通转弯候选|保存 model15600 拉取凭据、交互播放器修复、短冻结弧线检查和已有四份 15s 基线流程。未部署普通转弯 PPO，不把 3s 泛化当 15s 毕业。|[LOCAL_PLAYBACK_OPENED.json](../sources/local/MOD4_LOCAL_LATEST_SPIN_20261003/LOCAL_PLAYBACK_OPENED.json)|
|未完成|世界定向移动、Rough、云台、MoE 与实物弹簧|保留已写的数学/SDK/地面查询/来源核对代码和待办；这些准备不等同真实训练和完成验收。|[ROUGH_NEXT_TASKS_20261001.md](../sources/remote/MOD4_AUTO_PROGRESS_NEXT_AI_20261001/ROUGH_NEXT_TASKS_20261001.md)|

## 已纠正的说法

- 低力比例不是腾空比例；窗口/积分高通过率不是持续承重，也不是策略学习进步。
- 旧报告的上游/赛场标准主张原样保留为历史；当前门槛是本项目自定实验条件。
- “训练成功/奖励高”不能替代首次失败截断、逐环境和多种子确定性回放。
- 当前 3500N/m 预载弹簧不是 SCUT 240N 恒力；300–700N 实物力—行程未标定。
- 新增预算只来自明确用户授权，已应用扩展不得再次执行。
- 旧源码/评测程序有偏差或缺口时明示；不因补建标签填造历史。
