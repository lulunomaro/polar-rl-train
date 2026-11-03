# Phase1首个队列矛盾已定位：观察器writer时钟/作用域需区分

## 实际测得，不是推测

[独立功能诊断回执](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/reports/PHASE1_V4_A2_ACTUAL_QUEUE_SCALAR_DIAGNOSTIC_V1.json>)在已完整关闭的同一个E3/N80/64-control capture上，仅重新打开own worker FINAL一次，原bytes SHA、JSON decode均一次；不读group FINAL、不重跑SDK、不打开模型。输入canonical在调用前后均为 `87b9360fbf7988f46cb3d8fbc801e6d768fcf3deab14c2dd5987131ce61eebca`，原pure对象/函数不改，原actuation_component实际只调用一次。

| 原异常上下文 | 实际值 |
|---|---|
| retained control_index | `int 0` |
| event.seq | `int 0` |
| event.kind / group | `target_write / legs` |
| event.tick | **`int -1`** |
| 原异常位置 | [actuation_component:381](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_capture_evidence_verifier_v1/capture_evidence_verifier_v1.py#L379-L381>) |
| 原predicate | [integer:54–56](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_capture_evidence_verifier_v1/capture_evidence_verifier_v1.py#L54-L56>)，`type(x) is int`且`x >= low=0` |
| 原结果 | `ValueError: typed integer/range`，CONTRADICTED保留 |

这不是一个float/bool被误当int的情形，而是一个**真正的int -1**遇到要求非负的通用event时钟规则。

## 原源码能支持的解释边界

1. [原C1观察器:149–164](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_actuation_capture_v1/actuation_tap.py#L149-L164>)对所有`target_write`都用存储的`_sim_step_counter - 1`，没有先判断是否实际处于`term_apply`调用栈内；只按asset setter方法名把位置writer标成legs、速度writer标成wheels。
2. 同一原代码在callback进入时先预留seq、sequence从0开始；若此前进入过term_apply，它已先占据更小seq。因此在未修改C1实现下，**这个seq0 writer没有更早的term_apply父调用**。结合`tick`分支的严格int判断，源码还可推出该callback捕获的存储counter为0。这是有源的逻辑推导，不是把未导出的parent字段冒称直接测量。
3. 原[SDK action-delay adapter:38–46](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/reward_command_audit_v1/E3/runtime/isaac/mod4/action_delay_sdk_adapter.py#L38-L46>)只在真正的term apply中将counter减1，明确依赖原SDK已先递增counter的时序。把该公式无条件套到所有asset setter超出了这个适用域。
4. [原skills:452–474](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/reward_command_audit_v1/E3/runtime/isaac/mod4/skills_isaac.py#L452-L474>)确实存在其他同asset位置setter路径`gas_spring_preload`。其真正活动注册和事件顺序正独立核对；**当前actual caller/joint_ids仍为UNKNOWN，本次seq0的具体调用者尚待证据，gas preload只保留为源码候选路径**。

所以，当前直接确认的是**captured writer event与原通用非负clock schema的首个矛盾**，不是PhysicsActionQueue实际执行了tick=-1，也不是“机器人物理系统坏了”。这一次locator只揭示首个异常，后续队列检查尚未走完。

## 下一步最小修复原则

- NEW C2观察器区分父term apply内的腿/轮writer，与其他初始化/step/reset等非term setter；所有原调用与捕获事件保留。
- 非physics writer保留原stored counter和setter/joint-id来源；physical tick标NOT_APPLICABLE/UNKNOWN，不把-1钳成0，不伪造一次queue apply。
- 真正queue issue/apply和父term writer继续严格验证非负physics tick、原8个apply、源group/parent seq以及实际target写入链。
- 不把旧validator普遍改成允许负tick，不删gas/其他合法writer，不改动作、物理、DR、接受阈值或RNG；旧C1、pure、CONTRADICTED报告和所有失败保持。
- 先NEW source差异和合成/真实CPU不变性测试，再决定是否需要新的原门控有界capture；未取得新证据前，**Gate1 UNKNOWN，Stage2未放行**。

[定位器封存](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_queue_failure_locator_v1/SOURCE_SEAL.json>)及[父11项验证](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/reports/PHASE1_QUEUE_LOCATOR_PARENT_SOURCE_VERIFY_V1.json>)均已实核；原输入与10个旧pure/application封存成员不变。实际capture的64/512/128和完整关闭PASS仍成立，但它与全接口科学通过、技能通过是三件不同的事。
