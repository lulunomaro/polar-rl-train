# Typed wire serialization：独立 SOURCE 审计与 NEW V2 最小设计

## 结论与证据边界

**真实三 BIG writer 已确认；仅改 runtime writer 会遗漏两个。** 最小 NEW V2 是：worker 的 CASE FINAL 调用增加一个明确 keyword；runtime helper 的新增 keyword 默认保持 pretty；NEW parent 仅改本地 `put` helper，使精确两个根级 BIG 名称 compact。旧 9336-byte parent 与全部旧封件封存，未修改生产代码。

本轮仅 FS/read/glob/grep、Python 3.14 `-I -S -B` stdlib AST/hash/JSON 与小标量检查。技能 catalog 的 Office/ACL 与本任务无 RL 匹配。**9 项 NEW SOURCE/ownScalar 检查 PASS**；旧 tests、旧 size fixture、项目 import/entry、Torch/SDK、SSH、GPU、PT/raw、actualreports、C/锁/账本/Git 操作均为 0。未读取实际 SimulationApp SDK 源码或实际数据文件。Stage1/Gate1 `UNKNOWN`，Stage2 `False`，actual native size/qualification `UNKNOWN`。

21 件明确小源码/源码元数据：15 个完整 Python AST、6 个 JSON；三封件的声明 root 已认证，未声称重验每件封件的全部 leaf。固定 before inventory SHA256：`5f511bb08c2072cc19230010b01f9b371cd74ef4dcdf5b9a9d957059de43aa97`。逐件 bytes/SHA、protected function source SHA 和报告后复核在 [JSON 报告](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_typed_wire_serialization_audit_v1/WIRE_SERIALIZATION_AUDIT.json>)。

## 1. 三个实际入口，不是单一 writer

| BIG | 真实调用与发布路径 | 当前编码 |
|---|---|---|
| CASE FINAL | [worker:225–226][worker] → [runtime:79–86][runtime] `put_json` | UTF-8、indent=2、allow_nan=False、默认 ensure_ascii=True / sort_keys=False，无尾 LF；dict 的 epoch 原逻辑保留 |
| TERMINAL_ROWS | [parent:59][parent] 的 **本地** `put` → [parent:7–8][parent] | 同一 pretty JSON；无自动 epoch；不经过 runtime writer |
| GROUP FINAL | [parent:60][parent] `put(...batch_result(...))` → 同一本地 helper | 完整嵌入 terminal.data 的 CASE；同一 pretty，无自动 epoch |

[parent:84][parent] 的原 entry → 完整 `capture_parent_entry` → 完整 `main`；worker 也由原完整 main 进入。parent 的唯一子进程、readiness、资源条件、实际 `p.wait()`、TERM/KILL/wait/finally、both-EX release 不属于格式修改面。CASE fit 不推出缩进后 GROUP fit；parent writer 当前本身未显式设 64MiB，但后续 GROUP reader 有同一 64MiB 上限。

## 2. 精确 NEW V2 设计；本报告没有实现它

仅允许以下源码差异，其余保持原完整 source/code：

1. [worker:226][worker] 的正常 CASE FINAL 发布增加一个 keyword，例如 `typed_case_final=True`；不用于其它 metadata 或 incomplete 路径。原 sensor/C2/codec/loop/RNG/pending/恢复顺序不动。
2. [runtime:79–86][runtime] helper 增加 keyword-only `typed_case_final=False`。默认仍走原 pretty；仅显式 CASE 选择 `indent=None, separators=(',', ':')`。保留原 epoch 插入、`allow_nan=False`、`ensure_ascii=True`、`sort_keys=False`、UTF-8、无尾 LF、原 64MiB、partial/fsync/replace。
3. NEW [parent:7–8][parent] helper 仅对 `n in ('FINAL.json', 'TERMINAL_ROWS.json')` 选 compact；其它精确名称继续原 pretty。完整 `main`、`nvidia`、`capture_parent_entry` 逐字/AST 保留。parent 不新增 epoch，不把 basename 模式扩展到嵌套或其它 metadata。

格式分支的含义仅为：

```python
# NEW V2 设计片段；不是生产补丁，也不在本轮执行。
json_options = dict(allow_nan=False)
if exact_typed_big_selection:
    json_options.update(indent=None, separators=(',', ':'))
else:
    json_options.update(indent=2)
# ensure_ascii=True、sort_keys=False 仍用原默认；其余发布逻辑保持原样。
```

保留所有 decoded 字段/unknown、原 dtype metadata、整数/bool/float、N80、controls 64|128、teacher/actor/物理/DR/预算。无 floatcast、drop、truncate、切片换值、cap raise 或额外审批门。小标量已覆盖大于 2**53 的整数、bool≠int、负零 float bits、Unicode/转义、未来未知字段、finite/非有限值校验及三种嵌套容器；这是格式等价检查，不是 Torch/native 证明。

`TYPED_CAPTURE_INCOMPLETE` 不是当前 collector 的三 BIG 之一；其错误路径、pending/provenance 与默认 writer 不暗中纳入这次成功路径格式差异。

## 3. actual raw SHA/bytes 与关闭语义

[runtime:318–324][runtime] 在发布之后读取真实 CASE raw bytes，再生成 fast-close intent 的 `final_SHA/final_bytes`；[runtime:329][runtime] 仍恰好调用原 App.close。该完整函数、waited evaluator 与 grade 函数无需格式逻辑差异。

- [runtime:227–229][runtime] 校验 intent 对真实 raw；binding 发布的 `add_capture_epoch=False` 保留。
- [reader:303–327][reader] 对 original raw SHA/bytes 校验，不是 projection 或重编码 hash。
- [typed consumer:744–818][consumer] 区分 whole original provenance 与 decoded canonical，并把 intent 绑定 original bytes/SHA。
- [App helper:100–224][app] 的 generic class/source/MRO/config/binding 条件和原 [canonical binder][core] 不需要修改；这里没有实际 SDK/MRO 已通过的主张。

compact 后 raw SHA/bytes 应自然改变，并由原发布后读取逻辑取得；沿用旧 pretty SHA 或把 canonical SHA 当 raw SHA，会破坏现有 provenance。ownScalar 131-byte pretty / 95-byte compact 已确认同 decoded 内容而 raw hash 不同；未执行项目 validator。

## 4. collector 与 science 的完整消费者边界

[reader:26,156–184][reader] 精确读取三个 BIG：根 GROUP FINAL、TERMINAL_ROWS、CASE FINAL。每个仍是 67,108,864-byte 上限、max+1、read-once/cache/不可变 stat、完整 raw hash，然后才按原七条精确路径做 payload projection；未知字段不额外裁剪。

[reader:367–369][reader] 的 stdout packet 本来就是 sorted compact、ensure_ascii=False、UTF-8 **加一个尾 LF**，总计 ≤16,777,216 bytes；[collector:207–216][collector] 的远端包读取也保留该上限。输入三 BIG compact 不保证投影后的 stdout 包 fit，尤其保留的未知字段仍可很大；本设计不改变这条边界。

[science:48–74,99–111][science] 消费 CASE/GROUP 两个 **whole** 64MiB JSON，先 raw size/SHA，后 decode；用 [pure typed_equal:74][pure] 确认 `group.terminal[0].data == worker`，再给原完整 typed consumer。projection 不是 whole-science provenance。状态报告的 pretty+尾 LF 不属于三 BIG 格式，本设计保持它。

## 5. NEW source identity 必须贯穿，不假装旧 hardpin 兼容

| NEW 发布面 | 必要身份差异 | 必须保留 |
|---|---|---|
| producer | 三 active aliases：worker/runtime/parent 的真实新 bytes/SHA；重新生成 source index、finite bundle、SOURCE_PINS、receipt/seal/root；source kind/revision 用 NEW V2 | decoded wire ABI/kind 仍 V1；原 17、9 deps、2 bootstrap、ABI 不换；旧 root 不热改 |
| outer | [outer:9][outer] `PARENT=(9336,d557...)` 改为 NEW parent 实际 bytes/SHA；重新量 NEW outer 自身 bytes/SHA | [outer:28–38][outer] parent gate、Popen/wait/except/finally 完整函数原字节/AST |
| collector | [reader:20,24,245][reader] PARENT_SHA / CONTROLLER_SHA / 实际 controller bytes；[collector contract:23–36,95–103][contract] producer/index/finite/root/三 active rows；NEW source root/修订声明及对应 metadata gate 一致传播；[source pins][sourcepins] 的路径/manifest/mirror 声明重新生成并封 NEW root | 原 64MiB/16MiB 与 read-once/projection/terminal 条件；不得把旧 3824 或旧 parent SHA 当新值 |
| science app | [science:12,54][science] MANIFEST34；[science pins][sciencepins] normalized34 和引用；NEW app/source seal | 完整 reader/apply 函数、原 typed consumer 和 pure verifier 字节不变；原 owner/value equality 不改 |

当前 normalized34 已独立重算为 `6de25a76b3d2d5a1fb13f9f80daa1669cf02fb81d602220db6a47a6c3a1ef315`。三 active rows 改变后必须用新实际源重新算，绝不从旧 root 推测新 SHA。NEW outer 即使仍可能是 3824 bytes，也要量，不预设。历史 materializer B2 / active B4 source metadata 差异与格式问题分开，不借此修改 deps 或宣称整套未来装配已合格。

## 6. 只作设计参照的精确 reduced-synthetic 计数

父报告同一 materialized component 的 canonical byte lengths：sensor **25,716,274**，C2 **15,716,009**。没有读取实际 receipt，也没有重新跑旧 fixture。相同 finite ASCII/number 配置下 key 排序只换顺序，不改长度；literal string algebra 得：

| reduced synthetic object | compact bytes | literal overhead |
|---|---:|---:|
| `{'sensor':S,'actuation':C}` | **41,432,307** | S+C+24 |
| `[{'data':CASE}]` | **41,432,318** | CASE+11 |
| `{'terminal':[{'data':CASE}]}` | **41,432,331** | CASE+24 |

这三项均小于原 64MiB，仅为 `PARENT_REPORTED_LENGTHS_PLUS_LITERAL_ALGEBRA_NOT_FULL_NATIVE_BOUND`。长度不决定 SHA；未涵盖完整 setup/DR/metadata/epoch 等全部实际 CASE，未证明 native 64 或 128 的完整体积。父此前 pretty reduced-synthetic CASE 112,407,978 / GROUP 130,455,062 bytes 也仅保留父报告归属，不当作本轮实测。

## 7. 最小后续验证，不添加新的科学审批条件

若父另开 NEW V2 实现：先对允许差异做完整函数 bytes/AST 对照、传播全部新 pin，再用小标量验证三 writer decoded 等价和 actual published raw intent 绑定。若复用未来 functional-volume CPU payload，只作原有完整三 BIG / 原七投影 / 原 exporter 的体积与一致性测量；旧 14/7 资格不因统计重跑而改写。源报告不要求再次运行旧体积 fixture，也不把纯计数式升级成 native 保证或新的 SDK 门。

本轮最终范围：**2 件 NEW 审计报告，9 项小检查，21 输入 before/after PIN，0 生产修改/运行。**

[worker]: <F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_typed_native_capture_v1/worker_passive_interface_v1.py#L225-L226>
[runtime]: <F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_typed_native_capture_v1/phase1_capture_runtime.py#L79-L329>
[parent]: <F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_typed_native_capture_v1/single_gpu_passive_capture_parent_v1.py#L7-L84>
[reader]: <F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_typed_capture_result_collector_v1/remote_metadata_reader.py#L20-L369>
[collector]: <F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_typed_capture_result_collector_v1/collect_capture_result.py#L35-L216>
[contract]: <F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_typed_capture_result_collector_v1/typed_collector_contract.py#L23-L152>
[consumer]: <F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_typed_capture_consumer_v1/typed_capture_consumer.py#L744-L818>
[science]: <F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_typed_science_cache_application_v1/typed_science_cache_apply_v1.py#L12-L131>
[sciencepins]: <F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_typed_science_cache_application_v1/SOURCE_PINS.json#L10-L34>
[outer]: <F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_capture_controller_v1/phase1_capture_parent_actual_wait_controller_v1.py#L9-L38>
[sourcepins]: <F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_typed_capture_result_collector_v1/source_pins.py#L185-L259>
[core]: <F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_a1_frozen_eval_integration_v2/a1_frozen_eval_runtime_v2.py#L491-L513>
[app]: <F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_app_close_runtime_compat_v6/app_close_semantics_v6.py#L100-L224>
[pure]: <F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_capture_evidence_verifier_v1/capture_evidence_verifier_v1.py#L74-L85>
