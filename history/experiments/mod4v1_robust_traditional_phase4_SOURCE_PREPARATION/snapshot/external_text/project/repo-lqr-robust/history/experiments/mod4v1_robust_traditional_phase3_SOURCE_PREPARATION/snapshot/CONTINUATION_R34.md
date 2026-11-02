# 接续R34 / 自动Goal round3

先读[此前R28](<CONTINUATION_R28.md>)及其上游，以下为新权威补充。cwd仍F:/RMPOLAR-RL；root=本目录。Goal id`goal-4d4bef80-e614-432d-a8cd-8f385ef2dd7d`最新get为**revision7、roundsStarted3、max12、active/armed**。18:29宿主重启导致两个child在封存前中断、后台jobs清空，之后自动round1/2/3；当前不要用旧revision4改Goal、更不要complete/blocked。无匹配机器人skill，Office/ACL不适，CLI/文件工具；不要碰另一RL会话/原expert树index，不用GPU/SSH/PPO/新agent。

## 当前C完整host接口已sealed并实际物理闭环

[HOST_CLOSED_LOOP_IO_V1](<SPR_AUDIT/HOST_CLOSED_LOOP_IO_V1/README.md>)在重启前真正封存，INDEX`6f123646715090474cc49e33f8b2f2827afd113133fc6cf1e2281f9e1bd097ef`；exe150280B SHA`d32f7b04c4c6f03c8e5a64a38addf87cdbced67b99c96c90fea882bc8bba8c2b`、SDK`e854a2f52dd0b53a35f0bb4fdd30b370ee1aaf3a181ca5f232c6302886645ef1`。

- Python64 subprocess→resident MinGW32 PE32(不是ctypes32DLL)，init once、typed ASCII version/count/seq；41632checks/0，3200fixturestate14/mathτ float32bit0差，9fault类零回包锁存、截短EOF exit2不挂、uint64>2^53保持exact。
- **MATH_TAU**是P25前DC数学请求，**GUARDED_TAU**是最终point-sensor-DC guarded；原fixture两者可差4.53119Nm，非舍入误差。父原inversePD→D4→随机PD/motorGain→逐physics signedDC仍在，所以两域物理cohort分开，不宣称MATH cohort是最终C enqueue实际执行。
- SDK`from_v4_packet`要显式mean metadata。父当前epoch先存collector20×.5ms/count/window/seq，然后按D3返回sampled_us选**原epoch**metadata。Boot instant seq1/count1/window0；D3重复首包仍用原instant/seq1，不能假装当前mean20。Drivevel全由同packet qd4/spin2拼row6。
- clockbefore/after/TTL都是模拟逻辑us，记录hostRPCwall另列，**不是ARM/WCET/BSP/HIL**。No CAN/network/realhardware。

[R29](<batches/r29_c_closedloop4/BATCH_RESULT.json>)新nominal math/guard×stand8s/fwd12s四轨全完整过筛；fwd真实v1.92133、RMS.07872。此批pointguard差0，不能否定fixture边界4.53Nm。完整当前C链+PythonSHADOW只diagnostic，truth仅grade，rootassist0。

[每列QA](<reports/R29_C_LOOP_NUMERIC_QA.json>)：standmathτ误差4.64e−6Nm；fwd末端12s最大.003164Nm（比旧3200fixture.000201大），pitch差7.94e−7rad/vx2.72e−6m/s仍小。可能f32绝对ref积分20m积累，未武断修旧C3；每列有单位，不拿mixed scalar state error当同物理单位。

[R31 fullDR TRAIN18](<batches/r31_c_fullDR18/BATCH_RESULT.json>)全部rc0完整，含10ms重复首包，无Cfault。GUARDED stand4/4、forward3/4、brake按原R26drive+stop综合3/4；MATH stand2/2、forward1/2、brake2/2。102fwd真实1.84251、RMS.158711，确实未过.15，不能用rc0当通过。

## 速度标定诊断 → 新H4独立C留出128

[TRAIN诊断](<DATA_DIAGNOSTIC/FORWARD_DEFICIT_V1/RESULT.json>)先看误差而非盲加FF：nominal估计vx2.00098而真1.92133；101估计2.00925真1.93193；102估计1.97083真1.84251。名义wheel viscous torque约.47Nm，而实际common约.79Nm，**不是简单没加阻尼FF**。速度观测/微滑等偏差仍在。

[R33](<batches/r33_spec_radius6/BATCH_RESULT.json>)只改调用者**kinematic rolling radius为既有公开规格.0625**，实际CAD碰撞轮仍.06369999796、模型/电机/DR未改、没有拟合每episode radius或真值scale。C GUARD新六轨TRAIN全过：nominal v.5→.50755、1→.99914、2→1.96908、−2→−2.00420；101/102正2分别1.97481/1.88925(RMS.0353/.1120)。不是硬件实测标定，两个radius分支都保留。

于是**先冻结再跑**[C_P25_SPEC625_H4_V1/PROTOCOL](<C_P25_SPEC625_H4_V1/PROTOCOL.json>)，源闭包/SDK/exe/旧plant/主模型SHA固定，profileGUARDED、supported-upright、radius.0625，**新独立50000..50063**，stand20s额外xy<.3、fwd12s2m/s，原H1速度/姿态/支撑/非轮接触门槛保留，未读旧H1/H2选参。

[R34 H4](<batches/r34_c_h4_128/BATCH_RESULT.json>)全128rc0完整，独立结果：
- **stand60/64**，Wilson95[.850025,.975429]。4败仅xy超.3：50028 .315934、50035 .307094、50036 .387956、50062 .327787；不四舍五入过关。
- **forward64/64速度/姿态等原gate通过**，Wilson95[.943376,1]，并不证明95%可靠下界。真v范围1.87515–2.00844m/s、RMS.01364–.12608。
- **不叫直线车道资格**：记录secondary峰|worldy|.03499–2.83986m，52/64超过.3m；旧H1/H4无此gate，不能事后改gate掩盖，也不能只报64/64宣称路径好。
- 不覆盖brake/spin/rough/jump/board realtime，全Goal未毕业。

[H4聚合事实](<reports/R34_C_H4_INDEPENDENT_FACTS.json>)小result聚合，无raw复跑；旧H1/H2保持原freeze。

## 真RM派生地形新因果证据

[R30 namedcontact](<batches/r30_rm_blocker4/BATCH_RESULT.json>)主材料与低guidepriority显式分支各4/6cm固定P25；全部完整但仍失败。**6cm第一hard blocker是chassis_core在rm_bar_011顶面**，2.680s、峰12780.99N；轮先接bar2.564s。Guide首次ground稍后2.7435s。低guide摩擦也不解决，故不能把6cm卡阻全怪guide摩擦。主分支后有chassis_rear长期挂bar。

注意R30 stats的`tick`是**每pair每contact-point样本数**，不是去重physics step；chassis_core52575可以大于总26000，不能叫52575个不同physics ticks。第一time/力/identity与积分有意义，所有原字段不回写。

[R32慢速可行域](<batches/r32_rm_crawl6/BATCH_RESULT.json>)保持主模型材料和P25，真实4/6cm v.25/.4/.6各一nominal，延长命令时间给7.5m路径，**六条全部失败**。4cm .25/.4只进.949m，.6进2.786m；6cm均.933m左右。不能说降速就过坎，仍需主动障碍/腿策略/感知，不靠平地/删导轮/改软接触刷分。

## 传感器投影、动态COM与积分窗口

[SENSOR_CAPTURE_CLOOP_V1 manifest](<SENSOR_CAPTURE_CLOOP_V1/MANIFEST.json>)由父从R29/R31选4TRAIN轨生成4400行allowlist projection：packet/command/drive(enc速度)与时序而已，无root/contact/DR/真实pose。producerSHA全在manifest，原raw SHA引用，不为归档重读。只有这些给COM子任务。

[DYNAMIC_COM_MOTION_V1](<DYNAMIC_COM_MOTION_V1/README.md>)已sealed：完整rCOM/rdot/rddot项、23单测/12publicstatic0Step；缺wheelphase有界/未知降conf，不假balancedwheel。输出cue不是contact identity/allair。

[COM_SENSOR_CAPTURE_AUDIT_V1](<COM_SENSOR_CAPTURE_AUDIT_V1/README.md>)已sealed，14单测0失败、4400projection核验，strict-unbound可信cue0；条件4390/4400可算但radius约12.16–12.53m/s²，所有仍UNKNOWN。均值center=epoch−5.25ms、qendepoch、相邻差分名义epoch−10.25ms；60ms LPalpha实际70.25/80.25ms年龄，不能装瞬时。PUBLICD1aftermean噪声不÷sqrt20，未反推具体DR。

[INTEGRATED_COM_WINDOW_V1](<INTEGRATED_COM_WINDOW_V1/README.md>)在18:29中断前未seal，**18:45恢复后已真正seal**：核心SHAe167d5c3...，INDEX d1dd312faa0f9184fbe308cbe596f9e24b5f6e0c3a4b6c454c2490f16862da4f。恢复只核对已有15/15synthetic、4400shadow/producers/执行前sourceSHA，未重跑旧测试/物理。
恒等式u=omega×(rCOM−rIMU)+rdot，平均properCOM=平均(R properIMU)+(Rend*uend−Rstart*ustart)/T，不补g、不显式alpha/qdd。SO3相对frame/解析bin transport，不装midpoint精确。50/100/150ms p50 radius约9.2/5.2/4.0m/s²；全部可信cue仍0。150ms有1300个条件nonfreefall区间只diagnostic。输出是norm(固定frame内窗口平均vector)，不是平均norm/当前点，age T/2+queue；cap.50/冻结门槛.60未改。2k噪声共同offset方案只是信息增强/相关噪声新分支提案，尚未父实施/物理验证。

## 两个复用agent现状

`abf2088f-af10-479a-9108-202785031447`当前继续新`SPR_AUDIT/ACTIVE_BOX_QP_V3`。oldC3/HOST/H2全sealed不要改。[portable_spin_h2_v1](<SPR_AUDIT/portable_spin_h2_v1/README.md>)新H2nominalK/leash.2纯数学port已seal，5418checks0、5400vectorsτ误差2.075e−4、CPP+M4/M7 math4objects；actuation_qualified恒0，没借P25dispatcher，正4π物理范围未扩大。后续MPC使用feasibleprimalactive-set、真H15cond2426、tol.002、固定budget/earlyclock；最新磁盘02结构修复warm64真实18/18(8active最坏54pivot)、coldactive25pivot、75stresscold/warm全过。原01warm14/18/CYCLE等全保留。531内部earlyabort0fail已落盘（full factor只执行1/120cell等），当前还在未做过的CPP/M4M7和封存，**ASQP尚未sealed，不归PH3当前cutoff**。0physics，不冒3ms/ARM运行。

`e4e6c8f2-f08d-4df1-9150-945c804e8c2a`刚把INTEGRATED真正seal，等父书面PH3SOURCE cutoff。拟只snapshot准备先不commit，throughR34+sealedC3/HOST/H2/DYNAMICCOM/CAPTURE/INTEGRATED，排除ASQP/FRONT_RANGE/heading/R35+及所有活跃文件。Phase2 commit02b5ff84.../tag保持；别重record Phase1/2、别碰原expertindex/main、raw仅已有producerSHAmetadata。

## 前测距proposal与最新heading尝试（PH4pending，不归当前PH3）

[FRONT_RANGE_PROPOSAL_V1](<FRONT_RANGE_PROPOSAL_V1/>)只是新外部ToF模拟/纯几何proposal，没有安装/硬件binding/actuation资格。Sensor facade只输出range/时钟，不给root/terrain id；纯detector用sensor姿态/q和声明flat支持假设。原静态001因LinkageGeometry side传int而KeyError，0Step原失败留；002修pose('left/right')292checks0；003另改proposedmount(.30,0,.10)、加robot-self-occlusion（故不透过chassis看到地形）**293checks0、135static mj_forward、0Step**，2/4/6cmheight误差约1.38e−5m，保守bound下candidate0/8/9。源/attempt旧版保留。目前README/index尚未seal，勿宣称已接FSM/跳跃。

[heading_hold_controller_v1](<heading_hold_controller_v1.py>)是新PythonTRAIN外环relativeheadingP，依据[旧TRAIN诊断](<DATA_DIAGNOSTIC/TRAIN_HEADING_V1/RESULT.json>)，没读H4选增益：101/102漂移约+2.57/−2.46m，主要forward×真实yaw(终角+.145/−.186rad)，body侧滑积分仅cm；估计yaw已大部分测到，因此PIrate需angle-offset抵消motor差异，外环可让Irate持有偏置而heading归零。没有worldXY输入，默认spin/用户转向不作本profile资格。

**R35实际新失败，务必保留**：[batches/r35_heading27/SOFTWARE_ABORT](<batches/r35_heading27/SOFTWARE_ABORT.json>)前4baseline k0/seed0,201,202,203跑完physical后，写trace时heading_log.active是NumPybool(JSON2.4称bool)，json序列化失败；except再次序列化也失败，**没有ERROR.json/没有有效result，trace/partial为空**。日志清晰双TypeError。没有持久controls/physics计数，故**精确消费数未知，不能凭12s配置伪造24000；只能配置上限24000/episode**。其余23未启动。不要为补档重跑这4物理。

父已新建[streamed_trace_rows_v1](<streamed_trace_rows_v1.py>)：每新row先写文件/producerhash再存memory，default只支持numpy scalar.item，非finite仍错，防postproc丢整轨。拟R36做纯bool v2+序列化preflight+流式logger，新ID；baseline用204..211八DR以避重放失去的0/201..203，k2/k4用原未消费nominal+201..208各9，共26。配对比较仅共同TRAIN204..208五个，其余分母显式；不偷补R35成绩。

## Jobs/下一步

重启后get joblist无背景；之前R29/R30/R31/R32/R33/R34、QA/projection/诊断均完成且收过。最新R35 `pwsh-83dd16f1992540b2`已collect exit1，原因已读；无父物理running。agents仍各自数学/归档准备。先修R35 logger类型并做无物理序列化/partial保存preflight，再新R36；ToFproposal补README/index后才算sealed；PH3cutoff先父书面发给Modelagent。全Goal仍很多技能未过/board未绑定，不complete、不因研究难标blocked。
