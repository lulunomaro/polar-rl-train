# MINIHOP_AUDIT_V2 — attempts 与诚实修订

## 已执行 attempts

| attempt | 实际结果 | 留存 |
|---|---|---|
| freeze01 | hash-only 成功，1078旧/26源/279实际mesh | [冻结源脚本](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/MINIHOP_AUDIT_V2/freeze_v2.py>)、[log](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/MINIHOP_AUDIT_V2/freeze_01.log>)、[清单](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/MINIHOP_AUDIT_V2/SOURCE_FREEZE.json>) |
| bridge01 / runner01 | 两完整actuator AST与完整control-loop AST证明成功；0step | [桥证明](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/MINIHOP_AUDIT_V2/BRIDGE_AST.json>)、[runner证明](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/MINIHOP_AUDIT_V2/RUNNER_AST.json>) |
| unit01 | 917 checks/0，覆盖当时声明测试；未发现 cache 位置问题 | [原源快照目录](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/MINIHOP_AUDIT_V2/unit_attempt_01/contact_grade_v2.py>)、[原回执](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/MINIHOP_AUDIT_V2/UNIT_RESULT_01.json>) |
| manual cache review | 发现私有 R/COM 在 capture 读取会早一个 dynamics cache；非 executed-test failure | 只把这两个 read 移到 post-grade；没有改normal阈值、hooks参数、controller/driver |
| unit02 | 当前源 **936 checks/0**；新添cache刷新与对应非finite/时标测试 | [当前源快照](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/MINIHOP_AUDIT_V2/unit_attempt_02/contact_grade_v2.py>)、[回执](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/MINIHOP_AUDIT_V2/UNIT_RESULT_02.json>) |
| boot01 | 当前unit源校验后，flat/rm真实fullmodel 0step，**39 checks/0** | [boot源快照](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/MINIHOP_AUDIT_V2/boot_attempt_01/boot_admission_v2.py>)、[回执](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/MINIHOP_AUDIT_V2/BOOT_ADMISSION_01.json>) |

原 unit01 的 source/log/receipt 和 synthetic ERROR/prefix 都保留。没有把其 cache 字段冒充当前源的资格证据；其 force aggregation 测试仍是实际发生的初轮记录。当前 canonical source 对应 unit02 + boot01。

## 非finite 是明确错误，不是 air

当前新unit的每个 instrumentation fault 都保存 code/field/observed_repr/good_rows/last_good_stage；NaN/Inf 用错误对象中的 repr 保留，不写进成功样本，不改成0。force6（含friction/torque）、ct.pos/frame、mesh、dq/tau、root、mass、rotation/COM、clock、shape、overflow、schema 与stream append故障均有新测试。首错锁存，后续hook报 INSTRUMENTATION_LATCHED。

[synthetic ERROR](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/MINIHOP_AUDIT_V2/unit_attempt_02/synthetic_ERROR.json>)保留一条成功physics-prefix，然后在下一个合成tick的 NaN force 处停止。成功行数与 tick 不强凑相等；实际 raw bytes/SHA 与原 producer 均记录，不重建prefix，不制造补行。append失败时 observer air/landing state不提交。这个fixture不是机器人episode或旧R39错误补档。

## 准入边界

Boot的60次 `mj_forward` 是初始构造/reset/FK chart所需初始化，六种 integration入口的调用都是0。未运行新runner、旧preflight、旧physics/成绩重评；没有未来DR4221..4224 episode。真实boot本次 actual/cached mass相同，只有synthetic故意设置actual20/cached999证明选择了actual读取；二者不能混说。

本次没有编译/运行/修复 blocked IO，也没有 AV 设置、Git、GPU、agent、goal 或 active ROOT world_leg 改动。这里只准入新的只读grading代码；不是新contact sensor、true COM proper、jump/flight控制许可、实机/BSP/WCET或阶段成绩。PH4 cutoff排除v2；PH5/后续pending。
