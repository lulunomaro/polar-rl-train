# Stage1首个真实合格捕获：执行已闭合，科学接口仍有一项矛盾

## 已实际完成

| 项目 | 实际结果 |
|---|---|
| 独立purpose | V4 DEVICE_BINDING Admission2；旧零准入V4未重放 |
| 资源释放 | 先取得原权威锁/finite/私锁和硬件真实只读正见证；原父重新走准入 |
| SDK被动捕获 | E3 / N80 / 64 controls / 512 physics callbacks / 128 feedback sample时隙 |
| 动作/模型 | 原合成zero6 tape；模型PT读取0；训练/optimizer更新0 |
| 终末 | worker、原父及外层actual Popen.wait均RC0；原child wait已完成；双EX释放；errors=[] |
| 父实际窗口 | wall39.5837562084198秒，绝非SDK零成本 |
| 执行结论 | PASS_CLOSED_CAPTURE_EXECUTION_METADATA_ONLY |

[原合格终末](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/reports/PHASE1_E3_CAPTURE_V4_ADMISSION2_ACTUAL_CLOSED_20261104_012804/CLOSED_RESULT.json>)保留source checks、原wait、原close及EX证据。原父PID1554911、controller1554903、worker1554920；父exit epoch1793726913.8108263。

这验证了V4调用组合能实际完成原SDK控制循环及终末边界检查。历史V3没有记录原flags/device实际类型，因此仍不据此宣称已证明其唯一根因。

## 独立whole-FINAL科学应用

[实际科学receipt](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/reports/PHASE1_V4_ADMISSION2_ACTUAL_SCIENTIFIC_CAPTURE_APPLICATION_V1.json>)只为保留窗口科学分析而读取自己的整份worker/group FINAL，各自严格1次read、1次原始bytes SHA、1次decode，再复用同一对象缓存。输入canonical digest前后相同，没有导出原始trace payload、读取模型或执行SDK/C/锁。旧V1分析SOURCE保持未执行；V2只是原始bytes checksum复用及显式计数，不改变pure verifier/application封件。

| 组件 | 结果 | 作用域 |
|---|---|---|
| retention schema | CONSISTENT | 72个独立保留event |
| clean16 / used noise+bias / delay / episode clock | CONSISTENT | 56条保留feedback，38个normal channel slot，144个同episode MID/END行见证对 |
| pre-reset与partial-reset资料结构 | CONSISTENT | 6个pre-reset端点、4条保留reset；没有连上的自然terminal/reset边证明 |
| 原actor同buffer sanity | CONSISTENT | 6条；不是未打tap的反事实逐位比较 |
| 执行队列issue/apply/write/reset | **CONTRADICTED** | 当前只报告原严格校验器泛型错误 `typed integer/range`，尚未定位字段、类型和边界 |
| stored RNG/DR资料及源码声明 | CONSISTENT | 仅储存计数顺序/80x4与80x2 motor资料形状；不是物理readback或全私有RNG比较 |

**执行通过与科学接口通过是两件事。整体科学应用仍为CONTRADICTED，Gate1=UNKNOWN、exact=false、Stage2_GO=false。**

当前队列异常既未定位到实际标量，也未区分验证器schema/合法初值哨兵/捕获资料或真实队列行为，不归因为物理错误、不修改原验证器让结果通过。A194正准备小型纯SOURCE locator，未来独立科学purpose只读自己的同一worker FINAL一次，以原异常traceback给出严格字段/值上下文；不重新跑SDK复现，不编辑旧receipt。

仍缺的证据包括：实际per-tensor row/dtype、未打tap反事实位等、完整自然terminal/partial-reset跨边、SDK DR物理readback和全private/global RNG实际比对；保留窗口内一致不代表整个64步全部字段、八角色覆盖或技能通过。

## 与质量目标的关系

本次不是E3恢复技能评测，也不是E0新结果，更没有新BPTT更新。原H1/母模型/Registryv12、物理/DR/速度/阈值/资源权威/预算保持。Stage1实际执行闭环取得实质进展，接下来先定位队列科学异常和覆盖缺口；不把SOURCE、RC0或512 callbacks当作Stage2训练放行。
