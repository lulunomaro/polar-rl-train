# B4 独立小范围 SOURCE 静态复核 V1

**结论：`STATIC_FIXES_MATCH_SCOPE_RUNTIME_UNQUALIFIED`。** 在固定发布 JSON 作为 expected 的实际生产调用域，B3 两项绑定缺口已按预定范围闭合；未确认新增生产 SOURCE blocker。此结论仅覆盖 NEW strict-binding 修复，不代替父完整审计、真实 Sensor/Delay CPU、NEW worker integration 或 actual capture。

## 1. 范围与实际读取

- 已检查 catalog：仅 Office/ACL，无 RL 对应；使用 read/glob/grep，以及明确的 Python314 `-I -S -B` stdlib hash/JSON/AST/diff。项目 import/test/entry 执行 **0**；旧 B3 30 tests 未重跑；无 Torch/SDK/SSH/PT/raw/actualreports/C/GPU/Git 操作，未修改旧封件，未创建大 review driver。
- 全读 NEW core 181 行、固定 authority JSON 579 行、API contract 287 行、11 tests 源码 269 行、完整 diff 151 行、README/diff 说明及两次 attempt receipt/log/failure record。其他原回调/数学与 worker 大审核不重开，只验证本轮要求的字节保全。
- [B4 SOURCE seal](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_passive_sensor_capture_v4/SOURCE_SEAL.json>)：3824B / `81fe69c8c2f2ffde98b2a5e4b03d6921207d60156dcb180ab0097aa7397813b3`；21 members 全部实际 bytes/SHA 匹配，content root 实算 `6c8cc456c752a57fd9963b919e398f3c91c0c2205c15b4d1a0dbd9b605c96107`。
- 唯一生产变化 [dependency_contract](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_passive_sensor_capture_v4/dependency_contract.py>)：9827B / `799569719f570bf94d6d9ab9fd10d4e3006471990a0a433a51a0ab16026c5f68`。其余三生产文件、fake tensor、固定 PIN 文件均与 B3 整体字节相同。source revision **4**、capture schema 仍 **V3**；没有据此声称 B3 或 native 已安装。

## 2. 两项修复的精确结论

### 固定 authority 与完整 keysets

- [core:19–33](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_passive_sensor_capture_v4/dependency_contract.py#L19-L33>) 固定 **19153B / `5cd6c770c7f3541308201389f721b43f9e7c681199443c9a2f80d2f80347e452`**，与 B3 固定 publication 实际完全相同，不从当前 imported module 推导 expected。
- [core:59–80](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_passive_sensor_capture_v4/dependency_contract.py#L59-L80>) 先验固定 raw bytes/SHA，再 parse/check。精确 **3 constants + 3 codec classes + 17 functions + 5 Field methods** 键集，非仅长度检查；顶层及集合均要求 exact dict/string keys。
- override 仅在 keysets 以及整个 tree 的递归 type/value 全同后接受；返回的是本次固定文件新 parse 的 `expected`，不是 caller-owned override。空集合、删减、额外键或改 authority 不再成为生产替代预期。

### 类型严格、明确的外层归一

- [core:36–56](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_passive_sensor_capture_v4/dependency_contract.py#L36-L56>) 首先 `type(actual) is type(expected)`；dict 的 keys 在 set/lookup 前检查 exact str，list 精确类型后递归；仅 exact JSON builtins 比值。故固定 JSON expected 域中的 False/int0/float0.0、int80/float80.0 别名不再等价，actual 任意对象或子类不会进入其自定义 equality/repr/bool。
- [core:83–101](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_passive_sensor_capture_v4/dependency_contract.py#L83-L101>) 仅 `None` 分别归一为 defaults `()` / kwdefaults `{}`；positional defaults 先要求 exact outer tuple，再 outer list 转换。没有旧的任意 falsy `or` 归一。
- [core:140–148](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_passive_sensor_capture_v4/dependency_contract.py#L140-L148>) 仅 ROLES / INTEGER_DTYPES 两个明确常量允许 exact outer tuple→JSON list；CHANNEL_WIDTHS 递归严格。嵌套 tuple 不转换，subclass 不放宽。
- 通过完整 AST 比对，原 `_function` owner/raw function/no unwrap/globals/closure guards 与最终 `verify_callable` 保留；主 verifier 在更换 fixed-pins 初始化、constants 比较和 receipt 之外的 module/source/owner、unused ledger、descriptor、17+5 检查块完全保留。公开 verifier 参数 AST 不变；原三生产文件字节不变，故原 preflight/六 hook 顺序没有因本次修复改变。

## 3. 边界：结论限定于真实 fixed-expected 调用域

这里的“无任意对象 equality”是**新 literal 比较路径 + 固定 JSON expected** 的结论，不是整个旧 metadata/object inspection 对任意恶意对象无副作用的泛化保证。内部 `_same_literal_tree` 也不是已证明的任意双输入公共比较 API：若脱离生产路径直接给 arbitrary expected/custom metaclass，末端 `kind in (...)` 的泛用行为应单独审查；本轮未执行此场景，不把它列为已确认生产 blocker。生产 expected 始终来自固定、有限 JSON tree；未用运行时对象补造 expected。

真实 Torch/Sensor/Delay CPU、live SDK/MRO/tensor provenance、caller witness index readback、NEW worker 接入及 actual capture 仍待各自证据。保持既有 H1、物理/DR、阈值及预算约束；Source11 不是这些项目的替代证明。

## 4. 11 tests 与历史失败：仅读既有记录

- [attempt1 receipt](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_passive_sensor_capture_v4/STDLIB_TEST_RECEIPT_attempt1.json>) / [attempt1 log](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_passive_sensor_capture_v4/STDLIB_TEST_LOG_attempt1.txt>)：11 tests，0 failures、**1 error**，并非 0 cases。精确错误 `TypeError: __code__ must be set to a code object` 来自 own `patch.object(function, '__code__', ...)` 清理，stdlib mock 尝试 `delattr`；原失败记录保留。
- [attempt2 receipt](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_passive_sensor_capture_v4/STDLIB_TEST_RECEIPT_attempt2.json>) / [attempt2 log](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_passive_sensor_capture_v4/STDLIB_TEST_LOG_attempt2.txt>)：既有 11 PASS / 0 / 0；NEW test 使用 explicit try/finally 恢复 code object。两 attempt 的生产 core 都是同一 9827B/SHA；变化的是 own test 清理方法，不是旧 B3 或生产热补丁。
- 已静态读到完整 keysets/tree/authority、bool-int-float defaults、outer tuple、hostile actual、wrapper/owner/source、清理恢复与 source-only 负例。receipt 中 fake operations/activity 为作者记录，不冒充本轮动态审计计数。本轮项目 tests/imports/entries 始终 **0**，不新增 CPU 数值证明。

父补充 **PARENT_REPORTED**：独立 matched stdlib 8 cases PASS，默认及完整相同 override 22+3；原四空集合、删 `_metadata` 键、positional False/0.0、keyword 80.0 均按预期失败，restore 回 22+3；父报告 B4+codec 30 members/seals 未变、defaults/kwdefaults 恢复、FakeTensor ops{}。本轮未读该 actual report、未复现这 8 cases，也未把父8、作者11或旧30并作本轮动态证明；未修改封件的 parent_review 字段。

## 5. 实际 PIN 与 before/after

63 项小 SOURCE = B4 21 members + seal **22**，以及 B2/B3/codec 历史 **41**；完整 parse **26 Python AST / 23 JSON**。旧 41 与本轮实际哈希、固定旧 seals、三份 B4 before/after table 全等；作者表 manifest `34345662be0e30cfb08d2598d7e3e36c7f11c24796805ab8ae0285444ac12fbe` 也独立重算一致，算法不同于下列路径行清单，不混同。

路径行清单算法：对 absolute POSIX path 排序，逐行 `path TAB bytes TAB SHA256 LF` 后 SHA256。

- old41：`e83cc1e7a8b8eb8ad78d11c629a4943b2188ff74be7417f1c8c02fb870141a11`
- B4 22：`8f38e102143f7add69271a0746b7bb16ae0956ba4eb816908a38f572a15e77e2`
- all63：`bc7a042d0f74a8026f05e20da0bdbc80e469f381d3d52482f584636b7e0bdf06`

机器清单及最终 post-hash 收据见 [SOURCE_REVIEW.json](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_b4_parent_static_review_v1/SOURCE_REVIEW.json>)。本轮 own CLI 最初用简称 `B3/…` / `B4/…` 生成 diff header，完整比较触发 `AssertionError`；read 确认原 patch header 是绝对 Windows 路径后，仅修正 own stdlib locator，151 行 patch 完整重建相同。没有执行项目测试，也不是生产源码失败。
