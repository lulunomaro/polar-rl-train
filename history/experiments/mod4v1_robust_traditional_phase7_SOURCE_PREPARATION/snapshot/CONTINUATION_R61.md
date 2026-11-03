# R61接续：局部越杆新16仅10/16；spin单因素仍0/3；新空中参考候选尚零步开发

## 当前goal/工具与不变量

原goal-4d4bef80-e614-432d-a8cd-8f385ef2dd7d最近实际get revision9、roundsStarted6/max12，active/armed。勿重建/重复resume/complete/blocked。完整旧背景见[本轮R60](<CONTINUATION_R60.md>)及其旧R55/R38/H5接续。cwd F:/RMPOLAR-RL；任务本目录；Python C:/Users/lulu/AppData/Local/Programs/Python/Python314/python.exe -B、BLAS/OMP/MKL1，<=4物理CPU，无GPU/SSH/PPO/专家canonical/worktree/index/新agent/Mnemon写。Office/ACL无robotics，fs+CLI/read-before-edit/glob/grep；approvaldisabled不escalate。

所有父job现已collect：R60 pwsh-40a42e43ba144f99、R61 pwsh-841f21eade34435f均exit0，无父PHY运行。约9h消息间隔不是R60物理运行时长（实际case wall~32s）；R61每case wall约11.5–12s，不是ARM/WCET证书。

原完整接触/闭链/model_SHA0e9ca685...、.0005物理/.01控制/原100Hz boxcar→D1→D3/inversePD→D4→randomPD/gain→signedDC、全部D0–D7保持。控制无root truth/外力/中途reset；nominal init准入不冒硬件arbitrary-pose。旧H1/H2/H4/H5/Stage1/source seal不改。PH6已真实commit4e7a3fb.../tagtrial-20261103-mod4v1-robust-traditional-phase6，正式phase7_PENDING postreceipt父已read，**不要重复record/push**。所有R54+现在PH7pending。

## 已关闭R59/R60事实，不把拟合8例当泛化

[通用小result汇总](<record_local_bar_train_v1.py>)真实只读小result，不hash大raw。R59 paired同4501..4508只替existing δ0 landing K/ff/eq/ref profile：原local7/8、firstflight mainrear7/8、联合6/8，唯一4504 guide2仍失败。不是新的8独立样本，也不是纯几何高度单变量。

R60冻结后fresh TRAIN4601..4616：**16/16complete、12800controls/256000步，原local10/16**，firstflight mainrear16/16而联合只有10。guide失败4601/03/05/06/09/14，4606另hard5；所有endstable>=2/两个scopebbox True也不抵消碰触。peakmesh约.17957..26130m，仍非270。见[R60事实](<reports/R60_TALL0_FRESH16_TRAIN_FACTS.md>)、[JSON](<reports/R60_TALL0_FRESH16_TRAIN_FACTS.json>)。保留这一负泛化证据，不推广原paired7/8。

[R60两型审计](<R60_FRESH_CONTACT_AUDIT_V1/REPORT.md>)/[机制说明](<R60_FRESH_CONTACT_AUDIT_V1/MECHANISM_NOTE.md>)/[receipt](<R60_FRESH_CONTACT_AUDIT_V1/RECEIPT.json>)父已read：4raw各单pass，仅TRAIN4605/06；0PHY/Git/编译/H5/DR控制/大rawhash、未积分D1/D2真q。

- 4605 decision1.99→push2.00；air2.1225/confirmedPOST2.1425，mainrear2.446；firstlanding2.4765左轮GROUND/7286.79N，随后2.497guide05→bar011顶6330N，pitch−11.96deg、rootPREz.260676；guide05两ticks+07两ticks，hard0。
- 4606 decision1.85→push1.86；air1.9915/confirmedPOST2.0115，mainrear2.218；**firstlanding/首次ANYbar2.3385是chassis_front→bar后侧上棱17782.78N**，pitch已−49.50deg、两主轮0、rootPREz.337598；hard5ticks，后2.3885guide07→GROUND10659.69N、pitch−39deg，guide3+2ticks。
- 两案都在actual capture开始之后、observer恢复/2.50刹车之前；因此后者不是初事件前因，但不据先后证明某K/ref唯一原因。2k q未知，100Hz真实landing_ref/weight只bracket，不用legacytarget冒当前ref。主轮净跨不是整机净跨。

## AIR_PITCH静态查询已seal；frame陷阱不是旧控制器bug

C agent已完成[38行报告](<AIR_PITCH_AUTHORITY_V1/REPORT.md>)/[response](<AIR_PITCH_AUTHORITY_V1/RESPONSES.json>)/[receipt](<AIR_PITCH_AUTHORITY_V1/RECEIPT.json>)，父read。原首query因BODY/regular frame比较错误在保存数字前失败，值unknown保留。父明确批准一次修订，总13forward=旧失败1+新有效12、2boot/13RNE/0integrator；新基线先落盘并过原1e−8/1e−14 gate才做余11。没有扩solver/模型/门槛，所有有效ncon0/time0、原8小源+3安装API SHA不变。

关键：mjOBJ_BODY/local是惯性i-frame；mjOBJ_XBODY/local是regular chassis frame。新crouch0 BODY Y−4.9770 vsXBODY Y+4.9789，使用ximat转world后吻合；原失败值不retrofill。全12角acc交叉差max4.26e−14、rootJac误差0。**这是新诊断API frame修订，不撤销旧基准或宣称旧gyro用了错frame。**

三existing pose（crouch/pushendδ+.2/landingδ0）各0、双hip+1Nm EACH、双crank+1、双wheel+1，共12有效query。名义瞬时Δrootpitch系数全负：crouch双hip−3.5522、crank−3.1227、wheel−2.1886 rad/s² /共同每轴+1Nm（一对2Nm）。所以恢复正θ的小扰动torque符号是正号，但未验证大姿态/负方向/持续速度/D4；不能直接以此选稳定gain。wheel自acc约573rad/s²/Nm，每点原soft-eq混合单位acc残差max.467，非理想刚性投影或持续动量证书。

## R61 spin：单因素stop gate实际3例已关闭，仍无通过

新[controller](<SPIN_CENTER_DECEL_GATE_V1/controller.py>)默认False exactlegacy。只在旧centering已active、operator yaw=0、forward<.1、previous own shaper.w有限非零时保持旧target；Base仍收到真实0yaw。旧K/kt20/cap1.8/lead/半径/observer0/无capture切换全保留。release是previous-shaper状态可晚当前zero一tick，非测得停止/接触。

首[preparer v1](<prepare_r61_spin_decel_gate_v1.py>)假定4-space indent失败在生成阶段，0unit/0PHY，[ERROR](<SPIN_CENTER_DECEL_GATE_V1/preflight001/ERROR.json>)保留；[retry02](<prepare_r61_spin_decel_gate_retry02.py>)AST span导出[v2](<prepare_r61_spin_decel_gate_v2.py>)后第一次真正[零步24657/0](<SPIN_CENTER_DECEL_GATE_V1/preflight002/RESULT.json>)：2600synthetic disabled math/state位同、enabled首1000同、shaper2600同；不是机器人trials或2k prefix证明。

[实际runner](<run_spin_decel_gate_v1.py>)从oldR26复制仅newimport/去truth控制分支/StreamedRows，apply调用AST同。异常只记已写prefix/hash/actualcallbacks，不再serialize坏row。model agent独立[review](<SPIN_CENTER_DECEL_GATE_V1/preflight002/PRE_EXEC_REVIEW.md>)/[20源锁JSON](<SPIN_CENTER_DECEL_GATE_V1/preflight002/PRE_EXEC_REVIEW.json>) ready true/issues[]，父read后运行[launcher](<launch_r61_spin_decel_gate_v1.py>)。

3cfg来自旧R26 seeds0/201/202，仅新caseID和flag、首PHY前全freeze。名义admission只是26s完整无health/software，不冒原skill composite。实际**3/3complete、7800controls/156000物理步，原composite0/3（DR0/2）**。旧baseline只读小result、未重跑，旧heldout不动。

[R61新分析](<record_r61_spin_decel_facts_v1.py>)只读三新trace各一次，原strictscreen重新计算逐项对账；[报告](<reports/R61_SPIN_DECEL_GATE_FACTS.md>)/[JSON](<reports/R61_SPIN_DECEL_GATE_FACTS.json>)父已read。

|seed|最终XY old→new m|finalstop v RMS old→new|原失效|
|---|---:|---:|---|
|0|.053797→.284652|.008939→.023206|whole yawtrackingRMS .1413>.1；firststop hold.49<.50|
|201|.347337→.076392|.037740→.029648|两个stop相位hold虽达标，whole yawtrackingRMS .14617>.1仍失败|
|202|1.503513→.844841|.505538→.421364|whole v/yawtracking与最终stop/XY仍失败|

原H2未推广；名义漂移退化，2DR部分指标改善不是泛化。新variant维持默认off，不作为替换包。positive首相位保存指标与old两DR精确相同、DR receipt相同，但不是每物理state bit证明。实际第二stop请求22.01附近、retained至24.10、下一tick24.11释放；不能把synthetic22.00..24.09写成真实clock。两stop均210 controlticks。

## 当前agent任务/下一步

仅复用两个原agent，无新增；idleMnemon不动：

- C abf2088f-af10-479a-9108-202785031447：AIR已seal只读后，新MINIHOP_AIR_PITCH_REF_V1正在architecture/纯Python零步开发。父预设TRAIN假说：预测flight common绝对legref offset h=clip(.25*estimatedθ+.04*estimatedθdot,±.10rad)，rate1rad/s、默认False exactdelegate、δ与左右对称；firstcapture冻结lasth为position anchor、随原landing_weight桥接到eq1，K/ff不改，防u0 ref跳变。没有physical/gain稳定/force许可；这是手选实验幅值，不能说由unitqacc得出稳定gain。要求源前锁、disabled/approach/push math位同、FK/limits/phase/finite/anchor/final目标及真实新entry0step。**此候选尚未准入；无R62 PHY/新H6。** 不填未见的实现/结果。
- model e4e6c8f2-f08d-4df1-9150-945c804e8c2a：已完成R60审计/R61静态review，接着可按父书面PH7 cutoff做SOURCE_PREPARATION only；**未批准record/commit/push**。严格截止R61+sealedAIR，排除active AIR_PITCH_REF/R62+。需先交小handoff/index/gaps/case reconciliation供父review。旧PH6不可重记；原大raw只producer metadata/unknown留unknown，不重hash补空缺。

后续可先收air-ref零步实质结果/独立review，再严格名义flat/RM准入及新TRAIN；不要无限增加旧8seed拟合或把mainclear当整机clear。自转stop根因还含观测偏差/物理漂移，R61不足；若改新stop-shaper需新单因素profile/判据不动，不以.49舍入过关。整个9m/其他地形/270mm/接触FSM/driver-rate实际Power/actualheld+unique-send/双板BSP/HIL/WCET仍未毕业，goal active。
