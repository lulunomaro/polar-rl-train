# 接续 R36 — Goal round3后段

上游详见[CONT_R34](<CONTINUATION_R34.md>)→[CONT_R28](<CONTINUATION_R28.md>)；模型/全DR/H1/H2/H4/Git边界全部仍有效。最新get_goal仍revision7、roundsStarted3/max12、active/armed，id`goal-4d4bef80-e614-432d-a8cd-8f385ef2dd7d`，未调用complete/blocked。cwd F:/RMPOLAR-RL，danger-full-access且approval disabled，别加sandbox_permissions。可用skill仍Office/ACL，无机器人匹配。Python3.14、-B、BLAS/OMP/MKL1、≤4物理CPUworker，无GPU/SSH/PPO/新agent/原expertindex修改。

## R36 航向外环 TRAIN 已完成

R35四条k0/0,201,202,203 postprocessing丢记录不回放，精确物理计数仍unknown，上限24000/条只是配置，不补成绩。

- [R36第一次launcher](<launch_r36_heading_train.py>)在[PREP.log](<batches/r36_heading26/PREP.log>)捕获生成except块缩进错误；AST阶段、**0物理/0cases启动**，原源码/日志留存。
- [新02生成器](<prepare_r36_retry02.py>)生成[preparer v3](<prepare_r36_heading_v3.py>)和[新launcher](<launch_r36b_heading_train.py>)；只把except生成缩进3→2、adopt原已生成且字节相同的bool-only controller，不改控制公式。原v1/v2失败源保留。
- [heading controller v2](<heading_hold_controller_v2.py>)只把heading_log.active显式Python bool，控制公式同v1。[stream recorder](<streamed_trace_rows_v1.py>)每row先写/hash后入memory，NumPy标量.item只处理数值/布尔，非finite仍错误；新except不重新序列化坏row，保存prefix与真实physics计数。
- [02 precheck](<batches/r36b_heading26/preflight/PRECHECK_RESULT.json>)纯控制符号、JSON/NumPy类型、坏字段/NaN不损前缀、sourceSHA等检查通过，0physics。unit prefix文件单独留存。

[物理BATCH_RESULT](<batches/r36b_heading26/BATCH_RESULT.json>)：**26/26 rc0完整，各1200controls/24000steps，共31200/624000**，原速度/姿态/支撑/无非轮接触筛选26/26。baseline k0 seeds204..211八DR，k2/k4各nominal+201..208九条，所有全DR路径不变、传感器控制、truth只grade、无root assist。旧R35基线四条没有借分。

同种子204..208只有5组三方配对：

|heading K|原筛选|侧向峰值<.3m车道筛选|峰值中位数|最坏峰值|
|---|---:|---:|---:|---:|
|0|5/5|1/5|.848840m|.982171m|
|2|5/5|4/5|.098359m|.359249m|
|4|5/5|4/5|.110169m|.354493m|

整组k0车道2/8，k2/k4各6/8；整体分母不是八组完全配对，不能拿2/8→6/8冒作8对数据。k2/k4失败仍201/205，名义均过。这个是新Python TRAIN，不是新C holdout，不改H4。证据：[事实JSON](<reports/R36_HEADING_TRAIN_FACTS.json>)、[说明](<reports/R36_HEADING_TRAIN_FACTS.md>)、[残差](<DATA_DIAGNOSTIC/R36_HEADING_RESIDUAL_V1/RESULT.json>)。

## 剩余漂移诊断：不要盲加横向积分反馈

201 k2末端真实y=+.370279m，估计vx/yaw推算y=−.111702m；205真实+.359249m，推算仅+.004865m。因此除了历史侧移未回收，还有真实/估计航向积分误差。**尚未实现/运行cross-track controller，下一步不要直接加这个错误位置的增益。**

只读公共[DR源码](<../traditional_control_20261101/dr_components.py>)确认D1 gyro每轴均匀±.125rad/s，100Hz mean后加噪，不÷sqrt20。简化gyro-only白噪声/2m/s/10s横移尺度约.2635m，仅解释数量级，不是普适可靠性下界或实测独立sigma。

[离线轮差yaw feasibility脚本](<analyze_r36_yaw_fusion_v1.py>)在201..208 k2八TRAIN上0physics：公开半径.0625、两侧FK/J、gyro z置0求vL0/vR0，条件纯滚动wz=(vR0−vL0)/track，再Euler转换。权重0/.25/.5/.75/1全预列，truth只评分。结果**固定轮差融合整体恶化**：yawRMS中位.011997/.029292/.054606/.080086/.105627rad；最坏末端误差.034486/.078813/.171796/.264780/.357763rad。没有据此开新物理批次；不把条件滚动当独立滑移检测，不武断归因全是轮滑或D2。

证据：[结果](<DATA_DIAGNOSTIC/R36_YAW_FUSION_V1/RESULT.json>)、[解释](<DATA_DIAGNOSTIC/R36_YAW_FUSION_V1/README.md>)。已知q endpoint、gyro/qd mean、age-view姿态时域差异仍在，这不是完整同步融合器。H1/H2/H4/C3不改。

## ACTIVE_BOX_QP_V3 已真正封存

复用C agent发到磁盘的[README](<SPR_AUDIT/ACTIVE_BOX_QP_V3/README.md>)与[INDEX](<SPR_AUDIT/ACTIVE_BOX_QP_V3/INDEX.json>)已读：92文件/57links，旧530+5实际MPC引用SHA不变。core`b726c0acf09a13fe0114da1e1161fb2a7f57a4e138c7caf239c5fdd157ec653e`，header`e8b52347608370314dff3e48d5b4de1f4821b7b0e5f978a2ffae66958a0f8cba`，INDEX`dac32d84d2d4bf0c27b73ef4f8860661b0030874ca52d9b91f486317fa562fbc`。

- 真H15、64全局pivot、同一f32绝对tol=.002：cold18/18、shifted-warm18/18；active8/8各mode，最坏25/54pivots。
- 75独立stress cold/warm64分别75/75；实际active最大zerr6.416e−5、costgap3.307e−9、doubleKKT5.673e−5。
- 531 earlyabort检查0fail，full H15 factor只1/120cell即停、face/gradient/triangular/line/iteration/exit、rollback/UINT64均有证据；不是算完再看时钟。
- CPP active smoke及M4/M7 compile-only2/2，14684/13472B，无BSP/ARM运行/WCET。
- 原01 warm64 14/18、warm25616/18、MAX/CYCLE、402失败与trace/source/binary全保留；02低budget392失败valid0零z保留，不是抹去首轮。
- ASQP相对时间从START开始，前置固定准备不算；全周期deadline仍caller负责，不冒3ms。

## 两个agent当前继续，未增child

C child `abf2088f-af10-479a-9108-202785031447` **running**：新[HOST_ACTIVE_QP_IO_V1](<SPR_AUDIT/HOST_ACTIVE_QP_IO_V1/>)，刚报告设计执行中：resident MinGW32PE32+Py64 stdio，直接链接sealed ASQP源，不改kernel；seq/count/warm/uint64严格协议，真实QPC商余数安全us。计划93组cold+warm186新接口帧对直接C +fault/truncated/nonfinite/cleanup；确定性earlydeadline独立TEST_CLOCK构建，不用随机hostwall作固定断言。**尚未收到seal，不要抢读活跃源或当已完成。** 19:21 child新消息：SDK返回合同已匹配valid/status(int0成功)/z list/kkt_upper；clock换算254大整数向量/2514检查0fail。但生产exe遇到link返回0/map完整、文件Created后Deleted的异常，FileSystemWatcher已证实，其他小test exe存在；两轮build/probes保留，首轮缺产物被guard拦住，未当成功。父要求仅做与完整目标exe路径/构建时间相关的只读Windows事件及自身cleanup/fixture生命周期核查，**不改AV设置/排除/关闭防护、不改名/混淆绕删除、不为同源无止境重编译**。归因尚未知，IO未seal，R37尚未物理。19:27 [一次事件核查](<SPR_AUDIT/HOST_ACTIVE_QP_IO_V1/EVENT_CHECK_01.json>)仅匹配本次prod/harness/已有诊断exe完整路径、19:11:28–19:25:05；Defender1116/1117与Application1000/1001无匹配。源码静态无删除调用，fixture/SDK/build生命周期亦未发现actor；Watcher只证实Created→Deleted而不含actor。**归因仍未知，不能写成AV处置或sandbox denial。** child停止同源碰运气编译/改名，仅整理证据及不依赖prod的SDK编码/生命周期测试。IO组件NOT SEALED/R37不要接draft；sealedASQP核仍有效。这是局部产物问题，整个Goal继续active，未标blocked。

Model/archive child `e4e6c8f2-f08d-4df1-9150-945c804e8c2a`：**PH3 SOURCE snapshot已真正完成并由父读收据核对**。[最终交接](<../repo-lqr-robust/history/experiments/mod4v1_robust_traditional_phase3_SOURCE_PREPARATION/FINAL_HANDOFF.md>)、[完成收据](<../repo-lqr-robust/history/experiments/mod4v1_robust_traditional_phase3_SOURCE_PREPARATION/COMPLETION_VERIFICATION_RECEIPT.json>)、[FINAL_INDEX](<../repo-lqr-robust/history/experiments/mod4v1_robust_traditional_phase3_SOURCE_PREPARATION/FINAL_INDEX.json>)为主。3229源条目=2119新text/15,173,369B+441PH1/2引用+669rawmetadata(665已知SHA/4unknown)，2560text SHA配对验证通过，270物理result/4R25软件ERROR/22batch报告；actual in-scope source缺口0，source capture期间变化0。两次admin实现错误和关联erratum均追加留存，不算机器人失败。

cutoff仍固定R34：纳入R17–R34小result/source/errors与sealedC3/HOST-P25/H2/DYNAMICCOM/CAPTURE/INTEGRATED等闭包；ASQP(虽现在sealed仍postcutoff)、FRONT_RANGE、heading、R35+、streamer/new supervisor共145排除paths/whole trees。Root explicit allowlist63，无mtime全树或active替换；raw不重hash、unknown不补造。

19:26父收到repo AGENTS，已读[全部Git政策](<../repo-lqr-robust/docs/ALL_TRIALS_AND_REPORTS_GIT_POLICY.md>)与[既有流程](<../repo-lqr-robust/docs/NEXT_AI_GIT_WORKFLOW.md>)；按本任务原批准Git策略，书面批准同child执行下一唯一`mod4v1-robust-traditional-phase3` record/commit/annotated tag`trial-20261102-mod4v1-robust-traditional-phase3`及atomic **own branch+new tag** push。child现running该归档，尚未收到commit/push receipt；不能先叫已入Git。使用原helper SHA b2fd15...不改源码，仅显式PH3目录+新record/cover allowlist，旧PH1/2/main/原expertindex不写，不扩cutoff。commit若成但push失败只续objects不重record/force。后生成receipt与R35+等**PH4pending**，不造无限验证trial。

## 父新MPC supervisor 仅预检，未物理

新[supervisor.py](<C_ACTIVE_MPC_SUPERVISOR_V1/supervisor.py>)与[README](<C_ACTIVE_MPC_SUPERVISOR_V1/README.md>)，状态UNSEALED/await sealed SDK。无MuJoCo/DR/truth读取，消费C3 STATE14/REF14/MATH/GUARDED/SHAPER_V+同packet drive6，**独立C3 GUARDED LQR回退**，不另算PythonLQR。

- 旧8+lag9/N15模型，H32逐bit等于sealed实际H15，梯度/参考和mux仍Python；仅QP C，不冒全嵌入式MPC。
- 当前两轮signed四象限DC与LQRyawdiff求common交集，向内量化f32，整个N15冻结当前点box，**非未来状态/接触/功率约束**。保留overspeed只能制动的非对称情形，不用旧abs(v/r)对称cap。
- 全周期wall起点应在C3 RPC前；剩余整数us传QP，前/回包/证书后/mux查截止。所有failure/MAX/domain/deadline→已算好的C3 GUARDED；协议/证书fault锁存worker；warm仅最终接受才更新。
- MPC输出标签C_ASQP_SEQUENCE_PYTHON_MUX，**不是原C3最终guarded enqueue**；原C3 enqueue只证明P25分支。新物理runner必须分清，不沿用H4完整C dispatch标签。
- [preflight](<C_ACTIVE_MPC_SUPERVISOR_V1/preflight.py>)执行一次[42/0、0physics](<C_ACTIVE_MPC_SUPERVISOR_V1/attempts/001/RESULT.json>)，仅fake callback验证模型H32、禁用/domain、前/后deadline、remainingbudget、clockrollback、MAX/坏证书锁存、无效C基线、overspeed冲突与JSON，不是C IO/物理证明。
- core SHA`f50f8b7e97142ec280842fea8fab362a57a62e67cb6bb0e654e8cc33ae307927`。

**待集成的小项**：当前supervisor的`whole_cycle_observed_ns`实际是最后一个cooperative poll到cycle_start的差；disabled/domain等未进入QP的路径可能记0，不是各路径完整wall时间。下一版应改名/补最终只读采样，并保留001源码/新attempt验证；runner必须独立记录完整wall及最终提交前deadline，勿直接拿该字段作时延资格。

**下一步**：等child SDK真正seal，父做薄callback bridge+新零物理C IO/MPC一致性预检，再新R37 TRAIN(原C-LQR作独立基线，C3半径.0625、fullDR/原plant保持)。不要先消费新R37 physics。若IO产物问题仍在，可优先做R22/R30旧TRAIN的几何/姿态/扭矩因果分析或可靠contact/FSM准备，不盲加航向增益/重复编译/重跑旧once。全周期绝对wall只observed host，非ARM实时资格。最终移植完整gradient/mux/board仍待后续。

## 前测距静态proposal现已封存（PH3依然排除）

[README](<FRONT_RANGE_PROPOSAL_V1/README.md>)、[VALIDATION](<FRONT_RANGE_PROPOSAL_V1/VALIDATION.json>)、[INDEX](<FRONT_RANGE_PROPOSAL_V1/INDEX.json>)已整理，0测试/物理重跑。293checks/135静态forward/0steps，2/4/6cm候选0/8/9，13.82µm静态高度误差。安装(.30,0,.10)、−40°、noise±5mm/10ms是提案不是已有器件；静态几何测试本身noise0，公开误差预算10mm/5mrad未降。未绑定sensor/支架质量/线束/BSP/真实光学误差，未闭合FSM/动作。**早期测试没有执行前SHA收据，INDEX只能说明seal-time字节，不追认preexec源码证明**。actuation_qualified/hardware_binding恒false。

## Jobs与后续

本段全部父job已collect：R36a`pwsh-f40a9d21eb0f4e7c`exit1 AST/0physics；R36b`pwsh-c083e1b30e1c4aaf`exit0；yaw诊断`pwsh-1ae84b53db0242a7`exit0；其他记录/预检foreground exit0，无父physics running。两个child任务继续，别另开agent或碰Mnemon idle children。

已向用户阶段说明R36配对漂移改善、估计侧移错号、固定轮差融合负面证据与ASQP数值通过；没有宣称整个Goal或实机完成。停转/换向、4–6cm地形主动策略、270mm独立holdout、可靠contact/FSM/功率/板级HIL仍待，不complete/blocked。
