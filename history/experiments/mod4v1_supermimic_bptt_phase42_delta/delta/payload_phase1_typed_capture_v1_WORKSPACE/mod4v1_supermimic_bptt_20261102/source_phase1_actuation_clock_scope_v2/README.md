# C2：独立时钟/作用域 SOURCE 候选

`enabled:false`；仅 NEW 源码与 stdlib fakes，未接 worker、未执行实际采集、未修改任何旧源/测试/封件。技能 catalog 为 Office/ACL，无本任务 RL 匹配；采用 read/glob/grep 与本地 stdlib。入口是 [actuation_tap_v2.py](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_actuation_clock_scope_v2/actuation_tap_v2.py>)，完整差异仅供参考：[C1_TO_C2_SOURCE_DIFF.patch](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_actuation_clock_scope_v2/C1_TO_C2_SOURCE_DIFF.patch>)；未应用到 C1。

## 1. 独立推导，而非真实物理 cause

限定小聚合 [scalar diagnostic:61–128](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/reports/PHASE1_V4_A2_ACTUAL_QUEUE_SCALAR_DIAGNOSTIC_V1.json#L61-L128>) 给出原 pure 首异常：control 0、event seq 0、`target_write/legs/tick=int(-1)`，`integer(event.tick,0)` 抛 `typed integer/range`；未读取实际 whole/trace。

[C1:89–108](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_actuation_capture_v1/actuation_tap.py#L89-L108>) 初始化 sequence=0/context=[]，通过 setter 方法名固定 discovery group；[C1:149–181](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_actuation_capture_v1/actuation_tap.py#L149-L181>) 进入时先预留 seq，term 原调用前先压 context，而所有 setter 无条件使用 `counter-1`；[C1:189–193](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_actuation_capture_v1/actuation_tap.py#L189-L193>) drain 不重置 sequence。因此，在该源码、未外改状态、单线程调用假设下，seq0 setter 之前没有 term_apply 进入；观察到 int(-1) 由该分支可推出 stored counter 为 int(0)。这不是 `queue.apply(-1)` 的证据，也未识别真实调用者或目标 DOF。

[pure:379–411](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_capture_evidence_verifier_v1/capture_evidence_verifier_v1.py#L379-L411>) 的全事件 group/tick 检查早于 parented writer 联结。首异常暴露的是采集 scope/clock 域混用；后续队列、写入、reset、全 pipeline 尚待分别证明。旧 `CONTRADICTED`、旧输入、所有旧源保持原样；Gate1=`UNKNOWN`、exact=false、Stage2=false。

## 2. NEW schema 的最小契约

[C2:149–212](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_actuation_clock_scope_v2/actuation_tap_v2.py#L149-L212>) 使用 `capture_schema=ACTUATION_CLOCK_SCOPE_V2_SOURCE_DISABLED`：

- `issue` 保留原 counter；queue submit/apply 保留原实参 tick；term_apply 保留原 entry counter−1。均为未裁决的源值；负数、float、bool 不转换、不钳位。
- 原 term_apply context 保存 `{seq,group,tick,asset}`。setter 仅在 **top context 的 stored 原 term._asset 与实际被 hook owner 同一对象**时，继承 parent 的 group/tick/seq，scope=`SAME_ASSET_TERM_APPLY_CONTEXT`。nested 调用使用当前 top，finally 恢复。
- 无 parent：group=`UNKNOWN`、physics tick=`NOT_APPLICABLE`、scope=`NON_TERM_SETTER`；active parent 但 asset 不同：group/tick=`UNKNOWN`、scope=`ACTIVE_TERM_ASSET_MISMATCH`。两者 parent seq 均 None，保留 raw stored counter 和 active context 来源。不删 auxiliary/preload/non-parent setter。
- 保留 method、owner stored binding、非权威 discovery hint、joint-id 来源和值。kwargs.joint_ids 明示来源；positional[1] 标记 `UNQUALIFIED_SDK_SIGNATURE`；遗漏不猜默认。joint-id 元数据复用已冻结 args/kwargs，无额外 clone。
- 同 asset 动态 context **不证明** joint 子集、queued target 身份、真实物理 readback，亦不证明同一 context 内每个辅助 setter 均是最终执行命令。多写/缺写保留，后续严格约束有歧义仍为 UNKNOWN。只覆盖 C1 既有 hook 上实际到达的调用，不声称覆盖所有 SDK 路径。

**nested 测试的精确边界：** case04 仅断言动态 context 为 wheels，且观察到 position 方法；它不证明该 setter 是 wheels2 物理写入。未来 NEW verifier 还须结合实际 setter method、原 term._joint_ids 的已存储绑定/source IDs、原 kwargs/位置参数的 joint-id 记录，独立判断 DOF 与 target 组身份。当前 C2 未完成该 join，context labels 不是 direct-DOF 证据；缺项保持 UNKNOWN。不添加 SDK getter，不读取或比较 GPU 数据补这个未知，亦不拿不兼容的旧 offline/pure 给 NEW schema 出 PASS。

## 3. 保留与边界

仅 `_patch` 及 module docstring 改动；其他 20 个完整函数 AST 与 C1 相同，包括 freeze_memory/stored、guards/overflow、close 冲突保护、8-tick/4+2/episode/reset 原离线 helper。无新增 imports、SDK getter、CPU 同步、RNG、reset/sensor/termination hook；原 setter 实参、返回对象、原异常各一次。

采集不是有效性验证。NEW 消费器尚未实现：自然 issue/queue/term 与 qualified physics tick 必须继续 `type(x) is int` 且 `x>=0`，4+2 形状、原 issue/due/apply、8 apply、episode/reset 等约束全部保留。非物理 setter 是独立证据域，不是普遍放行负 physics tick。旧 pure 原样保留且不认识 NEW 的 N/A tick，**不把 C2 冒充旧 schema 输入**；复制的局部离线 helper 也不替代 pure 完整验收。

## 4. NEW synthetic 验证与下一步

[test_actuation_clock_scope_v2.py](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_actuation_clock_scope_v2/test_actuation_clock_scope_v2.py>)：12/12 PASS，Python 3.14.3 `-I -S -B`，用时见结果，Torch 未导入。覆盖 counter0/正 counter 外部 setter、仅 synthetic gas/preload 样式、nested wheels-position 不按方法硬归 legs、原 8 ticks/4+2、parent tick 与后变 counter 分离、wrong asset、原 exception identity/once、reset 邻界、restore 冲突、overflow UNKNOWN、负/float/bool physics 原 predicate 继续抛错、20 函数 AST 与完整 diff。结果见 [TEST_RESULTS_V2.json](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_actuation_clock_scope_v2/TEST_RESULTS_V2.json>)；不是实际 runtime/技能/收益证据，也未运行旧测试。case03/08 使用的复制 helper 仅核对受控 fake 中 reset-free、已 parented 的局部队列子流；case11 调用旧 integer 仅作原严格反例。它们均未给含非物理 setter 的完整 NEW schema 签发 verifier PASS。

唯一行动下一步：先由父的独立 SOURCE 调用路径归因及证据审查确认语义边界，再决定是否另开 NEW schema consumer/小段观测任务；本候选保持 disabled，不重采、不热补丁、不修旧状态。精确 bytes/SHA、来源行号、AST 相等项与内容根统一在 [SOURCE_SEAL.json](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_actuation_clock_scope_v2/SOURCE_SEAL.json>)。
