# MINIHOP_AIR_PITCH_REF_V1 — 001反证保留；002仅零步prototype ready

## 版本与预锁，不改旧结果/模型
- [001原架构](<attempt001/ARCHITECTURE.md>) / [原参数](<attempt001/METHOD.json>) / [原小源锁](<attempt001/SOURCE_LOCK.json>)在code前固定±.10；实际[51点](<attempt001/LIMITS_RESULT.json>)得到**14点超限、FK失败0、NOT_READY_DOMAIN**，[exit1原log](<limits_001.log>)保留，不以FK通过冒称READY。首超限h=0.048000，最大超出原上限0.054174124rad。
- 父随后仅授权[002新架构](<attempt002/ARCHITECTURE.md>) / [METHOD](<attempt002/METHOD.json>) / [新锁](<attempt002/SOURCE_LOCK.json>)：hGoal=clip(.25*estimated14[2]+.04*estimated14[9], **[-.10,+.03]rad**)，100Hz、rate1rad/s。kp/kd/rate、既有gain/时序/observer/轮公式均不改；这是公开crouch/机械model上限修domain，不从DR/GT或unitddot拟gain。没有第三版。
- 002实际[51点gate](<attempt002/LIMITS_RESULT.json>)：0超限/FK0失败，共旋转误差2.29e-16m，delta误差0，左右reference对称；正端名义hip余量15.825876039mrad。**参考在名义限位内，不证明DR实际关节/动态跟踪也在限位内。**

## 实际prototype语义
- [002 controller](<attempt002/controller.py>)继承原Position→Landing V3→Observer V2→V1。air_pitch_ref_enable缺省False时literal delegate原prepare/command；operator缺省仍False，没有新接触/air/世界位置/许可。启用要求显式原V3 landing_transition_enable，不偷偷开启它。
- flight仅super前临时q_start=original+h*ones4，finally恢复原对象；super实际算原140/3腿PD和25*pitch+4*pitchrate wheel项。没有在super后改tau，目标日志来自实际super。delta与L/R对称保持；仅16种坏输入提前INHIBIT/fault，不把NaN带入h/anchor。
- 首timedcapture冻结last h，eq0仅hip indices3/5平移，delta4/6不动；**super前**真实ctrl.eq/ref[3:7]设anchored eq0，覆盖V3首capture u=0不写ref陷阱。K0/K1/ff0/ff1/eq1不变，原landing_weight自然到eq1，h不突然清零。
- 这是air-ref反馈+连续capture anchor，不只是改空中τ。capture应看真实landing_position_ref4/ctrl.ref，不拿旧legacy target_q4冒充。flight轮τ位同结论不外推capture：新ref可能经原P25 LQR耦合影响capture轮输出；轮公式、K/ff没有改，也不事后补偿。

## 一次预声明synthetic验证，不是旧QA/PHY
- [原始UNIT_RESULT](<attempt002/UNIT_RESULT.json>) / [执行前source snapshot](<attempt002/unit_attempt001/PREEXEC.json>) / [log](<attempt002/unit_001.log>)：436620结构/数值断言0fail（含294198legacy节点比较，不是这么多个独立case）。
- **缺省off600tick**与原Position全部legacy math/state及log逐bit相同。仅harness将非控制的perf_counter_ns固定0以比对wall诊断；未替换任何控制数学。
- **enabled600tick**中approach/push 184tick逐bit同；预测flight 26tick的wheel τ逐bit同，h独立clip/rate oracle通过。最大每tickΔh=0.010000000000000002rad，原1e−14容差未动。
- 实际416行flight/capture reference均做双腿公开pure FK/原XML限位，0violation；16 finite/type/clock故障均先于ref/scheduler mutation锁存，异常finally恢复亦通过。0模型/forward/integrator/线性化；unit连MuJoCo模块也未导入。
- 真实首capture 2.10s、V3 landing_weight=0，anchor=-0.1rad；进入实际GroundController.command前ref已偏移，非补造log。与末flight4-ref最大差2.78e-17rad，保留浮点运算次序差，不宣称逐bit连续；原1e−12预算内。最后eq1/K1/ff1及leg目标逐bit正确。

## 新entry与受控零步入场
- [新entry仍在attempt002树内](<attempt002/run_manual_air_pitch_ref_v1.py>) / [AST receipt](<attempt002/ENTRY_AST.json>)：由原run_manual_position_v4派生，constructor call/control loop完全AST同，完整main仅3个result元数据字段差；另改package bootstrap/import/source manifest，未改actuator/grade。未做generic basename launcher兼容，父独立集成。
- [ENTRY_RESULT](<attempt002/ENTRY_RESULT.json>)：实际main() flagFalse/True各一次，真实新controller、geometry、StateEstimator、loaders和StreamedRows初始化；plant/DR/bounds/上游大asset-manifest明确受控fake，在首for-loop body前停止。实际model/forward/6integrator/其它dyn/packet/actuator/loop-body尝试全0。
- [OFF预期stop ERROR](<attempt002/entry_attempt001/actual_main_off/ERROR.json>) / [ON预期stop ERROR](<attempt002/entry_attempt001/actual_main_on/ERROR.json>)及空trace/physics prefix SHA原样保留：这是预期的controlled stop，不是PHY失败补档或成功trial；无result.json。**完整model boot/大asset复核、动态/driver准入均UNKNOWN。**

## 交付资格
- [小SUMMARY](<SUMMARY.json>)和本报告是**READY_FOR_PARENT_INDEPENDENT_REVIEW，ZERO_STEP_ONLY**；001仍NOT_READY_DOMAIN。26个旧小源最终SHA不变，原模型上限、gain/observer/grade/旧结果/H5/R60 raw均未动；无新PHY/编译/Git/agent/旧QA/模型线性化。
- 没有从本结果选择稳定gain、证明闭环稳定或DR安全，没有新contact/FSM/MPC许可。父R62尚为独立DRAFT/后续审查与PHY决定，本任务未读该计划或R60raw，不代执行。**PH7 pending，整个候选树不扩大既有cutoff。**
