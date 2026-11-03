# NEW C2 最小 observer 规范（独立 SOURCE 审计建议，非 C2 实现）

**边界：只改 NEW observer/其匹配的 NEW schema；原队列、动作处理、SDK 调用、阈值、物理 DR、H1、mothers 与 acceptance 保持原样。** A194 独立负责 C2 源码；本目录没有安装、patch 或执行该实现。

## 1. 三种时钟分别保存

| 字段 | 来源 | 适用范围 |
|---|---|---|
| `observed_sim_counter` | 自然调用入口处 env 普通内存里已有 `_sim_step_counter`，原 Python 类型保留 | 所有事件；缺失/非精确 int 记 UNKNOWN |
| `queue_argument_tick` | 原 `submit` / `apply` 实参，保留原类型和值 | queue 事件；真实 apply/submit 的整型与非负约束维持 |
| `physical_apply_tick` | 固定原 D4 `apply` 绑定的 `counter-1`，并与其自然出现的 queue.apply 实参互证 | 已验证 term_apply 及它的 writer 子事件；无此父 context 时为 null/UNKNOWN |

另存 `control_window_index` 与入口分配的 `seq`，它们均不是上述三种时钟。global counter 的初始化、reset/rebase 语义缺失 SDK 源时保持 UNKNOWN。不要通过 control index 乘 decimation 生成全局时钟。

`target_write` 在无父 context 时只保留自然 counter，不减一、不截断为零、不取最近 queue.apply、不把上一 control 的最后 apply 关联过来。它不是 queue.apply(-1)。反之，若**真实** queue.apply 实参就是 -1，原非负验证仍应失败；本规范没有负队列 tick 豁免。

## 2. 父 context 必须来自原调用的动态范围

- term_apply 包装入口先预留 seq；context 记录 `{term_apply_seq, group, bound_term_identity, bound_asset_identity, observed_counter, physical_apply_tick}`。group 来自已源绑定的 adapter.terms 条目，不从 setter 方法名猜。
- 在调用原 term_apply **之前** push，在 `finally` 中 pop；原函数恰好一次，原返回 object identity 和原异常 object/传播保持。
- queue.apply 的自然回调保留自身入口 seq、原 group/tick；可以在当前 term context 保存它的已观察事件引用。setter 往往发生在 queue.apply **返回之后**：该引用应命名 `selected_queue_apply_seq`/因果引用，而不是伪造“当前活跃 queue.apply 父栈”。
- writer 的 `parent_term_apply_seq` 只取当前栈。没有栈就是 null。父 context group、asset、预期 writer 方法、原 joint selector/宽度仍需互证；一个不匹配 writer 留作异常/UNKNOWN，不自动当成本 term 的有效应用。
- seq 是入口顺序，事件 append 是完成顺序。原 C1 会先 append 子事件后 append 父事件；序列验证以入口 seq 排序并检查唯一性。observer 重入/线程隔离、异常清栈、restore 冲突及溢出继续 fail-closed 标记，不污染原控制流。

## 3. writer 分类分离，原始证据全部保留

建议独立事件集合或同一集合的明确 `writer_domain` 字段：

1. `term_child_writer`：在合法 term_apply 动态范围内，group/asset/method/原 joint_ids 的绑定一致。该集合才参与原 legs4 / wheels2 物理 apply 链。
2. `other_writer`：无父 term_apply 的合法调用形状也完整保存，`group=UNKNOWN`、`physical_apply_tick=null`。保留 setter 方法、同 asset 的 identity token、原位置/关键字实参、原 joint selector 和宽度、自然 counter、结果/异常、源绑定信息。不要统一硬标 `legs`，不要删除。
3. `unresolved_or_mismatched_writer`：未知 caller、opaque selector、父/asset 不一致、缺失绑定等；保留全部观察项，资格为 UNKNOWN。

气簧配置来源指向 `GAS_JOINTS`；legs 来源是 LEG_ORDER 的四个关节；wheels 来源是 WHEEL_ORDER 的两个关节。**同一个 position setter 不是腿组标识；宽度也不是充分标识。** 用原实参/原有 term._joint_ids/既有 cfg 元数据作只读对照；不新增 find_joints、SDK getter 或动作重算。SDK 内部二次调用同名 setter 等路径缺源时不预判。

可选 origin 字段只限已有自然调用的一小段 Python caller 元数据或已绑定的 callback context；源 SHA 在安装前计算，回调中不做文件 IO/全栈扫描。没有 origin 证据时 `cause=UNKNOWN`，不能仅因注册过气簧就标 `cause=gas_preload`。

## 4. 对非物理 writer 的验证并非自动放行

保留 separate counts/first/last/seq，结构、结果、边界与来源都需审核。匹配到已注册 gas callback 的实际 binding/caller/joint selector 后才可进一步确认其身份；未匹配项仍使相关完整性 gate 为 UNKNOWN。现有 actual seq0 只有四标量，身份维持 UNKNOWN。

原物理链要求原样保留：每 control 每组 8 个 apply（以原 D4 非 backend-decimated 分支为前提）、submit/apply 实参非负整数、0/1/2 tick 延迟与精确 queue transition/reset、term→queue→writer seq 因果、原数值/动作与 actor35 证据。额外 writer 与物理 target 冲突/重叠时要报告，不能靠移出队列集合掩盖冲突。

因此应有匹配 NEW event schema 的 NEW verifier：先按明确 domain 分组，再对真实 queue/term 链执行原严格检查，对 other/UNKNOWN writer 执行单独审核。不要直接改旧封件的通用 `integer(e.tick,0)` 阈值，也不要把未 parent 的事件丢掉以迁就旧 schema。

## 5. observer 的不可变约束与准入证据

- 包装实际被调用的原对象；不构造新队列、manager、policy、SDK 实例。
- 不添加 RNG draw / obs / reset / step / SDK getter / setter；不改变原参数、queue mutation、调用或随机数次序。
- 原函数一次；返回 identity、异常传播、finally cleanup、安装失败回滚和 restore ownership 保持。
- 只读已有 Python 内存/原参数的 bounded snapshot；总数与 first/last 有界，不做每 tick O(n²) 重写；无真实 PID/signal 操作。
- 默认 `native_enabled:false`、`exact:false`。SOURCE/下面 toy 只证明逻辑建议；实际 binding、actor35 bitwise、原调用/RNG/queue 数值与原资源准入小窗证据由父单独审核。

关联：[独立 SOURCE 审计](<SOURCE_AUDIT.json>)、[路径/SHA/行表](<SOURCE_PATH_SHA_LINES.md>)、[自己的时序 toy](<test_clock_context_toy.py>)。toy 不是 C1/C2 实现验证，更不是 SDK/Native receipt。
