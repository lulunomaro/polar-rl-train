# B3 独立 STATIC SOURCE 复核

**结论：`STATIC_REVIEW_TWO_BINDING_CONTRACT_GAPS_NOT_INTEGRATED`。** 固定源码、完整 diff、类型角色与回调保留检查通过；确认两项依赖绑定契约缺口。现有冻结 V4 尚未接入 B3，README 示例不构成 installed binding。未发现第三项已确认的 B3 回调/数学/物理源码缺陷；实际 Torch CPU、SDK/native 绑定及 Gate1 仍为 UNKNOWN。

## 1. 边界与证据等级

- catalog 仅 Office/ACL，无 RL 匹配技能；采用 read/glob/grep 与显式 Python 3.14 `-I -S -B` 的 stdlib 哈希、JSON、完整 AST 比对。
- 本轮 **项目模块执行 0、测试执行 0、worker/stager/native 执行 0**；无 SSH、SDK/Torch 导入、PT/raw、GPU、C、锁/账本、actual reports、Git 操作。未装 profiler/audit hook，因此不声称存在动态 audit 覆盖或动态零事件 receipt。
- 已有作者 SOURCE 30/30 来自[固定测试 receipt](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_passive_sensor_capture_v3/STDLIB_FAKE_TEST_RECEIPT.json>)，只读核对；其 fake attach 显式绕过 native preflight。父报告的 codec CPU 565 项仅证明 codec 本身，二者均不等于 B3 Torch CPU/SDK 接入证明。
- **PARENT_REPORTED，未读取实际报告：** 父另行报告其独立 stdlib V2 已复现：默认 published 检查 22 functions/3 classes；public override 四集合全空仍 accepted/checked0；live `_metadata` default int0→False 或 0.0 仍被默认 PIN 接受，随后 finally 恢复。父称 27 SOURCE 成员与两 seal 未变、旧30未跑；父 V1 的 StopIteration 发生于首 case 前（0 cases），不当作通过。本轮只保留此归属声明，不转成本轮动态证据，也不读取父 actual report。
- 仅新建本报告及[机器清单](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_b3_parent_source_review_v1/SOURCE_REVIEW.json>)；旧封件不改、不重封。H1、原物理/DR、接受阈值和预算锁保持原状；未增加 native approval boolean。

## 2. 两项已确认的 SOURCE 契约缺口

### G1：public override 缺少固定键集与 PIN 权威绑定

[dependency_contract:43–44](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_passive_sensor_capture_v3/dependency_contract.py#L43-L44>) 在 `dependency_pins is None` 时读固定 JSON，否则直接采用 caller 字典；[73–103 行](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_passive_sensor_capture_v3/dependency_contract.py#L73-L103>) 遍历 supplied constants/classes/functions/field_functions 的 `.items()`，未先核固定键集、数量或与封存权威表的一致性。

- **默认 sealed 路径：** 当前固定 JSON 确实含 17 codec、5 Field 方法、3 codec class、3 constants；独立 AST/PIN 核对全部相符，正常路径会执行这些检查。
- **public override 路径：** 即使 kind/publisher/module/source/Field class 与结构条件都满足，传入空的函数/类集合也使对应循环执行零次。缺失顶层键可能直接抛错，但保留键、仅删减其内容的字典没有 required-keyset 检查。这不是默认封存 JSON 已经缺项的指控。
- [seal verifier:82](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_passive_sensor_capture_v3/verify_seal.py#L82>) 的 17/5 长度断言不在 public install 调用链，未补上此处缺口。

仅供控制流说明的 builtin 字典源码；本轮未执行项目反例：

```python
caller_pins = dict(sealed_pins)
caller_pins.update(codec_functions={}, codec_classes={}, field_functions={})
# 三个 supplied .items() 循环均迭代零次。
# 这段代码不调用项目验证器，也不宣称一次实际 runtime exploit。
```

### G2：默认路径也存在 literal default 类型宽松等值

[dependency_contract:29–31](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_passive_sensor_capture_v3/dependency_contract.py#L29-L31>) 用普通 list/dict `!=` 比较 live positional/keyword defaults。Python 的 `[False] == [0]`、`{'n': 80.0} == {'n': 80}` 均为 True。当前固定源码默认值本身与 PIN 一致；缺口是验证算法未严格区分这些 live default 的类型。

[source_api:170–194](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_passive_sensor_capture_v3/source_api.py#L170-L194>) 另核 module/qualname/source SHA/line/完整 code key/parameters，signature 仅返回 receipt，未与 expected literal types 比对，故不补救 G2。修改函数的 defaults 本身也不改变其 code object 或源码 SHA。本轮没有修改任何项目 defaults。

仅 builtin 函数的源码示意，未作为项目动态测试执行：

```python
def positional(value, depth=0): return value
positional.__defaults__ = (False,)
assert list(positional.__defaults__) == [0]   # 普通等值，类型不同

def keyword(*, n=80): return n
keyword.__kwdefaults__ = {'n': 80.0}
assert keyword.__kwdefaults__ == {'n': 80}   # 普通等值，类型不同
```

**NEW 版本建议：** 仅在独立 NEW B4 绑定层固定完整键集及 PIN 权威；public override 要么与固定权威严格相符，要么仅留为隔离的负例入口；literal defaults 递归核类型和值。新增缺键/空集合/删减/改权威/False↔0/80↔80.0 的 own fixture。保持原 preflight、MDP、六原回调与封存 B3/codec 不动；不降低 guard、不新增 parent approval 门。

## 3. 已通过的静态保留检查

- 完整阅读主要生产源码、README/SCHEMA、643 行测试及 668 行 diff；独立重建完整 diff 字节内容相符。10 个 immutable AST 与 B2 完全相同；继承 source API 与 fake runtime 字节相同。22 个新组件 PIN，以及 17+5 函数、4 class、3 constants 的 SHA/qualname/行号/参数/默认值静态元数据相符。
- [install:651–657](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_passive_sensor_capture_v3/passive_capture.py#L651-L657>) 顺序为 typed dependency → 原 preflight → 构造并 attach 六钩；没有 parent_approved 新门。
- 六个 original callback 的调用点、参数转发、原返回对象及原异常传播结构保留。feedback 两个 AST 调用点属于 foreign-env 直接返回与正常路径，互斥；其余五个各一次。未见回调中额外 step/observe/compute/RNG/CPU materialize 调用。
- 元数据在选择 witness 前取得。ENV_ROWS_WITNESS 为 axis0/N80/W1..8；ENV_IDS_FULL 完整 K=0..80，保留原整数 dtype、clone、不筛 witness、不强转 long；TERMINAL_BOOL_FULL 保留全 80 位含非 witness 79/78。行号映射仅 caller 声明，不是 GPU readback。
- clean16 仅 3+3+4+4+2；五通道 normal MID/END，原 tick×2500us、MID `%8==4`、END `>0 && %8==0`、scene_update/非 reset/原 100Hz 语义保持。noise 来自实际已有缓存而非相减推导，delay 保留原队列前后；同 tick 缓存不冒充新 draw，无 C2 重放。
- debug rings 与 64/128-control ledger、1280 normal cap 独立。物理 MID 其余 19/full35/actor/clean0 等仍 UNKNOWN；outside-loop materialize 不前移进 callback。
- 原 reset RAISED 保留同一异常、完整 owned IDs、before 与实际 partial after；pending INCOMPLETE，`original_post_return=NOT_OBSERVED`、post=None，无补 observe/假 post。IDs 元数据失败仍转发一次原 reset：codec 可为 NOT_OBSERVED，但 B3 实际 count=1、OBSERVED_METADATA_FAILED、INCOMPLETE 及两项 missing 标记避免当作自然无 callback。重复 callback 原样各转发一次、计数 2、保留首个 owned 事件并判不完整。end 先保存 owned post context，只有完整 end 才清 pending。

## 4. 当前 worker 接缝：有原 buffers，尚无 B3 installed binding

父已确认仅冻结 V4。静态查得 [V4 worker:127–138](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_capture_worker_v4/worker_passive_interface_v1.py#L127-L138>) 仍为 B2 generic snapshot/install，无 B3 witness/ledger 参数，直接替换组件并不形成完整接入。

[V4 worker:153–164](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_capture_worker_v4/worker_passive_interface_v1.py#L153-L164>) 原控制顺序：157 boundary.for_action → 158 唯一 bridge.step → 159 after_original_step(state.terminated,state.truncated) → 161 原 `state.obs['policy']` actor buffer。现有 B3 begin/end 调用数为 0。

[原 bridge:141–144](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_runtime/native_supermimic_bridge.py#L141-L144>) 中 step 定义位于 141，**真实 `self.real.step(applied)` 调用位于 142**，唯一一次；144 返回原 flags 与 obs。未来 NEW caller 只围住原一次 step/严格 boundary，end 使用这些现成 flags 与原 policy buffer，不取 masked xi1、不捏造 pre-reset actor、不加 action/observe/reset/getter。

[V4 index:651–666](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_capture_worker_v4/CAPTURE_SOURCE_INDEX.json#L651-L666>) 实际映射物理 [phase1_capture_observer](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_capture_worker_v4/phase1_capture_observer.py>)，不是猜测 alias。仅核此 observer、worker、index 三个 V4 成员及其 seal；不声称已审完 V4 13-member 闭包。旧 manifest 的 legacy BPTT worker 另列元数据核对，不拿其零 begin/end 作为当前接入失败证据。

## 5. Inventory、方法纠错与仍待证明

47 个当前小 SOURCE 实际 bytes/SHA 见机器清单：原三包 41 + 补充 seam 6；22 Python 完整 AST、16 JSON。41 的审计前 digest 与当前相同；补充 6 在父扩展 scope 后才形成首个完整 baseline，未冒称初始 41 的一部分。

| 身份集合/固定根 | SHA256 |
|---|---|
| core41 前/当前 identity | `e83cc1e7a8b8eb8ad78d11c629a4943b2188ff74be7417f1c8c02fb870141a11` |
| supplemental6 首次完整 identity | `784cdb5fe2143f567aad15943855bf8d116288920da93149a5c669ecabd344ed` |
| all47 报告前 identity | `58f3a8f7c82b3d402f961f6d106a86a8f014d302738162a72484675f2a9df553` |
| B3 18-member content root | `084b507cd460909abb03a241860595d6c93cf66a30ac2f05c775d0827a202692` |
| codec 7-member content root | `4ceeeda60cde6f8ca6cc496b8d299e5ea3b4ff2770b707f84898f06c1b75eec8` |

identity 算法：按绝对 POSIX path 排序，将 `path<TAB>bytes<TAB>SHA256<LF>` 拼接取 SHA256。B2 seal 没有 content-root 字段，不虚构一个。

自身 stdlib locator 曾把 bridge step 定义行 141 误当实际 call 行，触发一次 AssertionError；read 原源码确认 call=142 后，仅修正 own locator 并完成检查。非项目源码失败、非项目测试失败，源码和旧测试均未改变。NEW 目录初次 glob 报 os error 2，是尚不存在的输出目录，并非 ACL 问题。

**未来独立 NEW CPU fixture 优先级（本轮执行 0）：**
1. G1 完整/删减/空/额外键与权威替换，证明在原 preflight 和六 hook 之前 fail-closed；G2 用 bool/int/float 类型变换及 wrapper/default 变换。
2. 真 Torch CPU 全 IDs 0/1/79/80、多整数 dtype、非 witness 全 bool flags、owned clone、W1/W8/行映射声明；不引 SDK。
3. 原 reset RAISED 后 partial state、IDs 元数据失败、IDs 成功但 boundary tree 失败、重复 callback、end 错形状及 pending 完整性；同一原异常/返回对象/回调数。
4. 64/128 ledger 与 debug=0/2、same-tick/no-draw/no-replay、原 tick 与原队列差分；CPU materialize 只在 loop 外。
5. 仅在独立 NEW caller 集成后，再分别证明真实 MRO/source live binding、原一次 step/严格 boundary/现成 flags 与 actor、物理 DR/接受和预算条件。当前无该证明，SOURCE label、作者30及父 codec565 均不替代它。
