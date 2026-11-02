# 接续R16 — 当前权威补充（覆盖R14旧进度）

继续原active Goal，读[上段完整上下文](<CONTINUATION_R14.md>)。Goal id`goal-4d4bef80-e614-432d-a8cd-8f385ef2dd7d`revision4/active/armed/max12；未complete/blocked。工作cwd F:/RMPOLAR-RL，独立root即本目录；模型SHA`0e9ca6854285dc73465a198656fdedd992ffbf205c4ea9ed9d3ce88b905bf324`不变。所有旧失败/快照保留，不改H1/H2冻结源、不再拿H1/H2调参。

## 已闭合的独立证据

- 正常LQR_P25 H1：20s站立60/64；12s2m/s前进63/64；详细[报告](<reports/R07_INDEPENDENT_NORMAL_AND_MPC.md>)。均complete64/64不等于均pass。前唯一失败10060 vRMS.15993>.15；站4漂移>.3；全部不删、不改阈值。
- SpinH2：k20cap1.8 boundedcommonwheeltorque、sensor-only2Drelativeodom；12s×64新seed20000..20063，综合56/64，4漂移+4vRMS失败。所有64真实持续自身4π目标转速与姿态9.03–9.10s、累计19.74–19.84圈；[报告](<reports/R12_SPIN_H2_FACTS.md>)。角速度64/64≠完整复合56/64。仅正转，不含停止/反转/复合2m+4pi包络。
- MPC16只TRAIN，stand8/8/forward8/8；12631MPC/169LQR，maxsolver5.05ms/2个QP_MAX，非ARMdeadline资格。新局部8+lag9状态模型和boxQP详见旧接续。

## R13/R14/R15/R16跳阶事实

- 公共nominal蹲伏/落台bank已重建，源[GAIN_BANK](<JUMP270_V1/GAIN_BANK.json>)；父不读runtime root/contact给controller。controller依赖IMU/encoder/timer/localodom，**当前仍TIMED-profile，不是contactFSM资格**。起跳时禁加速度姿态修正、预测flight禁wheel-KF/groundnoslip，push开始properIMU世界加速度积分替代飞行轮测速；当前惯性假设/着陆timer未对任意失败验证。
- R13首launcher缺引号ParseError0steps留[原错](<errors/R13_LAUNCHER_PARSE_ATTEMPT01.txt>)，修后4条7s试验：d30r72真越沿2.02s/上台425controls/结束稳定1.79s，预定2s失败；其它3轨失败保留。
- [R14 9s首次DR压力](<batches/r14_jump9s_pressure12/BATCH_RESULT.json>)：2nominal均endstable3.79/3.82s通过end2；10DR中6真meshclear、5end2s；201/202发生roll~±1.07rad健康停止，204pitch1.11rad停止，205撞墙未越沿，207end稳定1.11s未达2s，全部记录。不能称270鲁棒holdout。
- 父新增groundroll20/2、push保留8Nm余量、AHRSrollmoment虚功Jᵀ分配、groundedpush yaw抑制、push.11s等训练假设，物理峰/DC不变。首次R15软件错：误调用不存在LinkageGeometry.jacobian，ALL33子process exit1在push前缀停止。**不把batch打印0/10当机器人分数**，参[勘误](<reports/R15_SOFTWARE_FAILURE_ERRATUM.md>)。已有33error/counts/source全部原留，前缀trace旧handler未写不能重建假装有。
- 新V3改用[现有wheel_kinematics API](<sensor_core_v4.py#L53-L59>)result[2]的3x2J，0step数学APIpreflight，错误写partialtrace；R16全新ID，4casechunk快停以免再消耗一整批程序错误。
- [R16实际33轨](<batches/r16_jump_roll_train33/BATCH_RESULT.json>)全rc0：
  - roll(原push.0909)：10DR clear6/end2=5，仍201/202roll倒下。
  - roll_long(push.11)：10DR **clear9/end2=7**，201/204结束稳定不足，205pitch倒下；nominalend4.08s。
  - roll_long_pitchD(将push_pitchD升10)：10DR clear1/end2=1，9个pitch恶化；明显退化，不继续盲加D。
- 真实RM起伏尚未运行；父只read冻源e1_chunked_terrain.py(仅partition)和eval_terrain_mod4.py，后者显示mod4_task.attach_rmuc2026_terrain为入口。别执行PPO/eval脚本/读PT/动另一会话预算。

## 导轮接触分类：重要新诊断，不事后掩盖

[静态接触候选诊断](<DATA_DIAGNOSTIC/JUMP_CONTACT_IDENTITY_V1/RESULT.json>)，仅已记录qpos的mj_kinematics+mj_collision **0step**：R14nominal仅1个nonwheel控制采样t2.16，currentpose候选为guide_wheel_03碰step270；101多次候选guide01/05/07；R16nominalt2.10候选guide01/03。部分.5msbackproject候选一致/有些为空，原force没有geomName，所以仅“几何候选”，不伪称精确原接触身份。

导轮可能是有意的过坎/落台支撑，因此主驱动轮离地≠全机器人离地，导轮承载时leg forceproxy可off、IMU proper仍非自由落体。现有FSM也明确FLIGHT不是所有表面truth。旧严格nonwheel零指标保留，不能事后改pass；未来新protocol应预先区分允许导轮/硬车身/轮先落台，并用physics-rate namedcontact评分，不反馈给controller。当前jump属于可能guide-assisted landing，勿叫clean ballistic wheel-first。

## 两个复用child正在做什么（不要新增agent）

1. `abf2088f-af10-479a-9108-202785031447`：QP1/ODOM/真实H V1/QP2fast/**ARM_OBJECT_BUILD_V1已全部封存**。真实armclang路径C:/Keil_v5/ARM/ARMCLANG/bin/armclang.exe，MDKPlus5.26/Compiler6.10.1。M4fpv4-sp-d16/M7fpv5-sp-d16 hardfloat×C1obs/C2FK/QPfast共6/6object compile-only，fromelf/宏全0。对象M4=22172/10940/6892B，M7=22228/10904/6924B，各SHA在[summary](<SPR_AUDIT/ARM_OBJECT_BUILD_V1/OBJECT_SUMMARY.json>)；[README](<SPR_AUDIT/ARM_OBJECT_BUILD_V1/README.md>) SHA5d02ae5b...，INDEXc0721a94...。无BSP链接/BIN/ARM运行/flash/WCET/数值结论。M7FPattr8是FPU属性非CPUv8-A。
   - 当前新任务`SPR_AUDIT/portable_control_v3_current/` ACTIVE：port当前sensorV4 packet数学/innovation gate/uprightprior+normalP25 actualK/legPID/yawPI，若体量可做H2sensor2D torque；fixedsizeC，FK复用C2，schema crank−hip≠passiveknee、6row顺序不暗改，当前C1仍R00旧算法。100Hz packet先port，2k frontend与真实CAN同步未绑不冒称2k实物采样。host向量/TRAIN同包数学对照、M4/M7对象可；不新physics/board/Git/agent。默认所有fault/age/invalid硬返回零，不发未知DM3519帧。
2. `e4e6c8f2-f08d-4df1-9150-945c804e8c2a`：FSM已sealed63/63 synthetic/1042call/11mode，C仅header；当前CONTACT_PROXY_NOMINAL_V1 ACTIVE，SDK-free nominal31body/30joint FK与旧闭链公式。首nomEq algebra已得Fz[70.057416,70.168100]、Fx~0，Σ140.225516=14.29414g，非硬填mg/2；气簧virtualτ[-16.2963,+16.2963]、leg有效load[2.6456,-1.2931]，Jcond1.363，residual1.78e-15。runtime仅public常量+τ4/q/qd/properRoot/ωα；output扭矩域/符号/标定强制声明，wheel反作用/动态RNE未全观、起伏真实normal不冒chassis-Z，未知降conf/None，不取消DR。静态forward对照可0step，不读runtimecontacts/rootGT。
   - CONTACT封存之后优先PHASE2 Git归档，再查terrain来源。已授权沿现独立worktree/branch新unique trial mod4v1-robust-traditional-phase2；包括截至R16全部source/报告/失败/实际case/H1/H2protocol/Cseals/CONTACT及ARM若sealed，exclude activeportable_control_v3及未来。raw只producerSHA索引，不为归档重读；旧recordhelper+窄adapter/expectedblob核验，只ownbranch/tagatomic，不pushmain/不改原expert工作树。R15软件33与R16物理分母分开；并发main变化如实pre/post不回滚。随后terrain只读入口再MuJoCo port规划。

## Git与文件/运行边界

Phase1已真实commit93e0814f5d4dc165dda1f85f8ee12bc35be04d2f、annotated trial-20261102-mod4v1-robust-traditional-phase1，回执[ARCHIVE_PHASE1_RECEIPT](<ARCHIVE_PHASE1_RECEIPT.json>)；勿重record。所有新R04..R16/错误/回执/新C阶段需Phase2补档。独立gitworktreeF:/RMPOLAR-RL/repo-lqr-robust branchmod4v1-lqr-mpc-robust，另一repo-lqr专家会话活跃，别checkout/commit/恢复其index或main。

[硬件绑定清单](<HARDWARE_BINDING_CHECKLIST.md>)新增：板/CAN/零位/方向/Nm↔A/IMU/母线/温度/队列真实门控均待绑定；电机达妙不变，轮15.8不重复19.2032。机械功率不是电功率。无额外Office/GUI/网络安装工作。

最后父job`pwsh-5cb6ea74778b4d05`(R16)与`pwsh-08e7ec1f365d4118`(staticcontact)、H2summary等均已finished/collected；**当前无running父pwshjob**，两child仍各自工作。所有nonzero均读过/有原错，没未处理job。保持Goalactive，不blocked。下一应integrate可靠proxy/FSM与currentC、推进真实RM与jump takeoff/landing；先做TRAIN再新独立holdout，H1/H2保持只读。
