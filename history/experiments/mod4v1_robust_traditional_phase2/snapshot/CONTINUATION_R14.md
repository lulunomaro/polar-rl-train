# 接续R14：Goal仍进行中，真实留出与跳阶新进展

工作目录F:/RMPOLAR-RL；独立任务root为本目录。Goal `goal-4d4bef80-e614-432d-a8cd-8f385ef2dd7d` revision4/active/armed，最近get仍roundsStarted0/max12；勿重建或提前complete。人类最后实质指令继续任务。Office/ACL技能均不匹配本机器人任务，文件/CLI执行。

## 模型/隔离底线

沿用[NEXT_ROUND](<NEXT_ROUND.md>)的全部模型、DR、15.8总传动比、板卡与物理证据边界。主MJCF SHA`0e9ca6854285dc73465a198656fdedd992ffbf205c4ea9ed9d3ce88b905bf324`，完整31体/6接点4mimic/279mesh、14.29414kg、.5ms隐式Newton100/100Hzcontrol。轮mesh实际支持包络用于reset/grade，绝无runtime rootZ修正/外部推力。独立两CPUagent复用，无新GPU/SSH/PPO/PT/其它会话改动。

## 独立评测已真实闭合，禁止以H1/H2再调参

- 正常LQR P25（位置权重25/leash1、fixedleg120/4、yawPI.8/.5/I15/rateFF.052）TRAIN201..208站立/前进各8/8，实际K已导出[CONTROLLER_PACK](<NORMAL_P25_HOLDOUT_V1/CONTROLLER_PACK.json>)，`K_6x14`不是nominal默认K。已在评测前冻结[H1协议](<NORMAL_P25_HOLDOUT_V1/PROTOCOL.json>)。
- H1新seeds10000..10063、全D0–D7：20s站立60/64，4个xy>.3m失败；12s2m前进63/64，仅10060真速度RMSE.1599309>.15失败。完成均64/64。D3=0组33个：站32/33/前32/33；D3=10ms组31个：站28/31/前31/31。Wilson95：站[.850025,.975429]、前[.916659,.997236]；不是证明真实可靠率95%。[报告](<reports/R07_INDEPENDENT_NORMAL_AND_MPC.md>)，[JSON](<reports/R07_INDEPENDENT_NORMAL_AND_MPC.json>)。
- 相同R07中MPC16只TRAIN：stand/fwd各8/8；共12631tick MPC /169LQR回退（167模型域外、2QP迭代不收敛），接受率98.6797%。stress最大solver5.0494ms，maxKKT.30597来自失败候选；最初nominal.48ms不可冒最差值。未做MPC独立holdout或ARMWCET。
- 自转R04旧gyro仅3/8，R08内部vref经过/旁路driverfilter的2Hz跟踪失败；R09改只经真实两轮的bounded common torque，未放宽任何物理/DC界限。R10k16cap1.6=7/8，R11k18cap1.8和k20cap1.8各8/8。仅依据TRAIN选k20，nominal零yaw小信号phase guide约.0083901s，正式高spin模型并未被证明。
- 冻结[H2协议](<SPIN_H2_K20_V1/PROTOCOL.json>)后freshseeds20000..20063、每条12s：综合56/64(87.5%)，Wilson[.772254,.935278]，D3zero29/30，10ms27/34。全部64真正持续自身yaw4π，目标转速与姿态连续保持9.03–9.10s，实际累计19.7356–19.8403圈；yawmean12.5202–12.6059rad/s。8个综合失败=4漂移>.3m+4bodyvxRMS>.15；不改门槛不把角速度64/64称完整通过。[H2报告](<reports/R12_SPIN_H2_FACTS.md>)，[JSON](<reports/R12_SPIN_H2_FACTS.json>)。任何下一variant需新TRAIN决定/冻结/新独立seed段，H1/H2不再优化。

## 实际MPC与C数值证据

- 新[scalar_ground_mpc_v1](<scalar_ground_mpc_v1.py>)：fixedleg闭环Acl=A14+B14L；对称8state[x,pitch,hipavg,crank−hipavg,v,pitchdot,hipdotavg,deltadotavg]，input每轮共同Nm(BLwheel+BRwheel)，nominal半步lag扩9state，N15 scalarboxQP，terminalDARE。无sim/controllertruth。高yaw>2rad/s/|pitch|>.25切原LQR，明确不称MPC自转。只box torque、未做contact/state/powercoupled约束。
- [MPC模型/20数学检查](<MPC8_V1/MODEL_AND_QP_CHECKS.json>)与[首物理R06](<batches/r06_mpc_and_p25_remaining/BATCH_RESULT.json>)：nomstand800/800MPC、fwd799/800MPC，v1.937/RMSE.063。
- Python优化有free=-invH@g shortcut；constrained CCD80sweep只在结束后检查3ms deadline，这不是硬实时保证；仍需新的per-sweep提前预算/独立LQR实时tick。新版本勿改封存V1文件。
- C包[QPv1](<SPR_AUDIT/portable_mpc_qp_v1/README.md>)4166/0hostchecks，C++externCsmoke过；2448Bworkspace。实际H cond≈2426.684(f32≈2426.698)，eigmin.416/max1009.89，不能只用dyadic轻题。
- [真实H C1公平对照](<SPR_AUDIT/C_MPC8_NUMERIC_V1/README.md>)：18问题(10free/8active)，cold64只有2/18收敛，256只有7/18；扩4096/20000全收敛但最坏539/551sweep仅诊断，所有144run feasible，预算不足诚实MAX。保留NumPyJSON序列化原错/所有日志，不重跑C隐藏错误。
- agent`abf2088f-af10-479a-9108-202785031447`正封存[QPv2fast](<SPR_AUDIT/portable_mpc_qp_v2_fast/>)：保留ABI/baseCCD，加bqp_solve_fast；Choleskyfree快捷成功80个free组合全0sweep，active64组合与C1逐bit相同，仍21次MAX不可掩盖；新kernel disabled/base4166/0，enabled1110/0；host均值中位free4.39us vs64sweep86us，active不变，绝非ARM WCET。
- 父新找到真实已安装ARM工具：`C:/Keil_v5/ARM/ARMCLANG/bin/armclang.exe --version`实际exit0＝MDKPlus5.26/ARMCompiler6.10.1[5d143200]；armcc也存在未运行，非PATH。已交此agent在fast封存后做ARM_OBJECT_BUILD_V1：M4F/fpv4-sp-d16与M7 conservativefpv5-sp-d16 compile-only纯C模块，留版本/cmd/宏/object/hash/错误，不BSP/链接BIN/板/flash，不放宽license，不下载包。原C1估计器对应R00不是现V4，不能冒已完整移植。

## ODOM和状态机/接触模型

- agentabf完成[ODOM2D](<SPR_AUDIT/ODOM2D_DIAGNOSTIC/README.md>)，4个R04trace3200行SHA/producer源全核：lateral proxy −cross(gyro,wheelmidFK)_y捕获主几何侧速但无独立真侧滑观测；forward v误差是主要剩余，yaw很准，换trueyaw无改善，换truevx可大降积分误差。不是轮一致就无滑/不是只调heading。
- [FSM原型](<FSM_DETECTOR_V1/fsm_detector.py>)已由agent`e4e6c8f2-f08d-4df1-9150-945c804e8c2a`封存，63/63合成tests/1042syntheticcalls/11mode；C只有proposal header语法过，无C FSM实现。48/49首次边界失败、后61/63等全留。入口DetectorFSM(Config).step(SensorFrame,now)，模式DISARMED/ARMING/BALANCE/DEGRADED/RECOVERY/STEP_APPROACH/PRELOAD/PUSH_OFF/FLIGHT/LANDING/FAULT_LATCH；只姿态/gyro/proper(必须ref)/q4绝对hipcrank/qd/有效/时序/命令，可选ForceProxy/MotorFeedback/FrontObservation，绝无contacts/rootXYZ/toptruth。
- 跳/恢复默认disable未绑定；properORIGIN即0g也不直接判freefall，COM证据需显式置信/enable；未知force不填0，故障latch立即INHIBIT/qNone/硬return。全部阈值proposed非用户验收，物理集成还没过。默认低launch速度限制需要父按270真实profile显式绑定不能暗改。
- 该agent现做CONTACT_PROXY_NOMINAL_V1：只nominalmodel常量+τ4/encoders/properRoot/ωα，gas虚功/J/nomleg势能有效载荷代理、解JᵀF，动态未知降confidence。可staticMjData/mj_forward对照0Step，但不读随机runtime接触/COM/GT抵消DR。完成后再查exactRM起伏来源，当前父read的e1_chunked_terrain只有trianglepartition，不是spec。所有task只新目录无新agent/物理/原源/Git。

## 270mm已开始，仍TIMED原型而非FSM资格

- [新bank](<JUMP270_V1/GAIN_BANK.json>)仅静态约2.95s/0Step：crouchδ−.495684 →h.454174/τ[3.523,−4.567]；landingδ−.4→h.385910/τ[4.614,−5.658]，当前新完整模型DARE，不旧MCI。旧hybridcontrollers参数仅参考。
- [sensor_core_jump_v1](<sensor_core_jump_v1.py>)由V4新建，wheelKalman/groundnoslip可禁，Joseph协方差保留预测；flight用gyro姿态+originproper世界加速度积分，push时初verticalV假设0明确；landing后恢复wheelKF，非真实COM/足力全观测器。
- [jump runner](<run_jump270_timed_v1.py>)只sensor/timer/localodom触发；approach1.4、estimateddistance.3/ .4触发、push.090896、tuckδ−.964、extend_after.3395、定时recover.72或.55；所有wheel/DC/leg40Nm真实链不变；无rootforce/poseoverwriteafterreset。grade用独立gd.qpos+ mj_kinematics算当前exactmesh，contact只用于grade。每行log完整qpos可后续静态重建视频，勿为归档回放物理。
- [R13四轨](<batches/r13_jump270_timed_proto4/BATCH_RESULT.json>)全部7s完整，但仅d30r72名义实际越沿2.02s、top双轮承载425/700、endstable1.79s(预定2sFAIL、旧ever.5指标PASS)，nonwheel1；d30r55虽clear但后坏，两个d40均不clear且大量非轮接触，失败保留。
- launcher首次缺引号ParseError，0imports/0case/0Step，已[原错](<errors/R13_LAUNCHER_PARSE_ATTEMPT01.txt>)留，修正后AST检查，重用的是未消费case IDs非回放。无需重复运行这些once。
- 当前正在后台`pwsh-7ded641f409c4bc3`：[R14](<launch_r14_jump_pressure12.py>)12轨9s：2名义(原recover.72与later.85)＋fullDR101/102/201..208 10轨。新目的长时间落台保持/首次jumpDR，不是bookkeeping延长旧日志；需collect结果。仍定时状态，勿把它说成接触FSM/270鲁棒毕业。

## Git与当前jobs

- Phase1真实独立branch`mod4v1-lqr-mpc-robust`commit`93e0814f5d4dc165dda1f85f8ee12bc35be04d2f`，annotated tag`trial-20261102-mod4v1-robust-traditional-phase1`object`1064f48cc077fdd3eb6c89e554b58f5d82ee5980`，remotepeeled同commit，atomic仅ownbranch/tag。458paths全新增blobSHA精确，436源text/30R00–R03case/41raw metadata/283externmetadata；[回执](<ARCHIVE_PHASE1_RECEIPT.json>)。
- 原专家会话一直活跃，原index/main并发前进不归因不回滚。我方push紧邻mainpre/post均f0705ed2，早期938→f070变化已留。永不commit/checkout该专家branch或pushmain。Phase1工具原recordhelper未改，用窄addadapter/memoryargv避Win长参。禁止再次record同ID/tag。
- Phase2至今所有R04..R14代码/结果/失败/新报告/回执/CQP/ODOM/FSM等仍需补档；原raw/大USD/ZIP/STL不为归档重读hash，V5后producerstreamSHA可直接索引，Cobject小构建QAhash可。
- 到R12共397物理case约8,896,000steps，R13再4个完整14k步，各数字不要混合不同控制版本做成功率。R14待结算。
- 最新父job只有R14`pwsh-7ded641f409c4bc3`仍需收；到H2summary`pwsh-e20ccf3c81ad4085`、ARMversion`pwsh-a345a13ddb7a458c`、R13修复job`pwsh-82ae77a920904218`全已finished/collected。两child正在上述不同隔离任务。Goal保持active，不blocked，不complete。
