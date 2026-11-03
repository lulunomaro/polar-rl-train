# Good-expert holdout materializer — NEW SOURCE D6

**SOURCE_READY_FOR_PREFLIGHT_NOT_NATIVE**。`enabled=False`、`source_native_enabled=False`、`staged=False`、`dispatched=False`，actual native binding **UNKNOWN**。本轮只派生源码、运行八项 NEW 小 SOURCE/AST/三 dict 内存测试并封存新组件；没有实际 prepare、metadata_validate、preflight、stage、parent/worker、guard derive、SSH、SDK/Torch、PT/raw/bank、GPU、预算 C、锁或 Git 操作。Office/ACL catalog 无匹配 RL 技能，使用 FS read/glob/grep 与 Python314 `-B` stdlib。

## 1. 原问题及最小闭合修复

[父 actual teacher identity 诊断 V2](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/reports/GOOD_HOLDOUT_ACTUAL_TEACHER_IDENTITY_SCHEMA_DIAGNOSIS_V2.json>) 记录两角色原 FINAL 各一次读字节/hash/decode，模型访问为 0。CURB_PROTECTED878/SLOPE135 的 `FINAL.teacher == checkpoint.teacher_source` 都有完整 9 keys。D5 row 仅保存 `teacher_identity` 的 4-field projection，因此在原 runtime 完整相等断言失败。

只把 row 改为 9 keys 仍会在活跃原 guard 的 `row == mother_projection4` 断言失败。已先只读复现两种失败组合并交父确认，再经父明确范围派生以下 NEW 源码：

| 层次 | 实际差分 | 保持项 |
|---|---|---|
| [D6 entry](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_stage_good_expert_holdout_v6/stage_good_expert_holdout_v6.py>) | prepare 的一处 `copy.deepcopy(producers[role]['FINAL']['teacher'])`；global INDEX_PIN；V6 SOURCE 标签 | 其余 **28 个完整函数**源码/AST 不变，含完整 metadata_validate / source_mappings / copy-fsync / typed publication / main |
| [NEW 完整 guard](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_holdout_teacher_schema_v2/producer_teacher_guard_v1.py>) | 仅 `validate_reference_row` 的 raw 完整身份/schema predicate | 其他 **6 个完整函数**不变；derive / allstate / source pins / 原 IO / evidence / return 不变 |
| [NEW 完整 runtime](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_holdout_teacher_schema_v2/good_expert_holdout_runtime_v1.py>) | 第 58 行 guard 的新精确 bytes/SHA tuple | 全部 **30 个完整函数**不变，尤其原 runtime147 完整 teacher 相等、固定母身份及 teacherFrozen True |
| [NEW 完整 20 index](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_holdout_teacher_schema_v2/GOOD_EXPERT_HOLDOUT_SOURCE_INDEX_V2.json>) | guard/runtime 两行 path/bytes/SHA；明确 revision2/component seal 路由 | 其余 **18 个完整 row**和所有原 required/inherited/provenance/source_state 值不变 |

完整 teacher dict 不是以 projection 代替 raw 证据：精确九字段相等，并再次以原 `teacher_identity` 严格核对 path/SHA/bytes/frozen；3 个历史计数均 exact int1，2 个 retained flags 均 `is True`。缺/extra/错误类型/False/0.0 均失败，不补值、不制造 approved flags、不使用 subset 接受。

overlay 文件 V2 保留原 `kind=SOURCE_ONLY_GOOD_EXPERT_HOLDOUT_C878_S135_INDEX_V1` **格式 schema**，以 NEW V2 文件、revision2 和独立 seal 区分 SOURCE 身份。D6 preflight/receipt kind 与 source_derivation_version 均为 **V6**。原 aliases 与 flat basenames 仍 20，不改变 native parent 导入链。

[组件说明](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_holdout_teacher_schema_v2/README.md>) 和 [组件 SCHEMA_DIFF](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_holdout_teacher_schema_v2/SCHEMA_DIFF.json>) 给出完整证明；[D6 WHITELIST_DIFF](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_stage_good_expert_holdout_v6/WHITELIST_DIFF.json>) 保留 entry 精确文本差分和未改完整函数 SHA。

## 2. 完整依赖与剩余 metadata SOURCE 审计

- canonical [a1_frozen_eval_runtime_v2.py](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_a1_frozen_eval_integration_v2/a1_frozen_eval_runtime_v2.py>) 仍为 37927 / `7a092364cf63e9621481dc0a5554b56a22e4412cf89870c3db9a124864074b2e`，与 NEW holdout runtime 别名分离，避免循环。全文件核对没有另一个 guard/runtime 硬 pin。
- AppV6 → dc4 Base、原 parent `9679 / fc4458431d375c2b44c063b3f5a8d4ad83ecc6e21d6684625898f7991c51f0ff`、其余 18 overlay 和全部原 resource/wait/close AST 不改。既有 metadata_validate 的 12-module cache 列表已含 guard/runtime/embedded reference，没有新热模块或 cache 绕行。
- 原 core producer 验证、actual0 的 9 counts、完整 checkpoint 保存 metadata、approved RSL source/provenance、select_requested_roles、两角色 make_task、独立 seed / cross-seed / historical-seed negatives 保持原源码。其完整函数本轮没有被执行。
- guard 的重复实际 source rederivation 仍在 select/make_task/group-task/cache/semantic 链。原 TASK、INSTALL_MANIFEST、worker/bridge 全字节 pins、all-state snapshot 与 torch.equal-before-save/FINAL 的证明保留，未使用 fixture 替代未来实际读取。
- 外层 source_cache 保留完整 task teacher，并在后续 semantic 与完整 role teacher 比较；嵌入 mean reference 内部的四身份投影彼此一致，另一处只比较 SHA。未发现第三个 raw/projection identity 冲突。
- 原物理 runtime 全树/staticbanks/deps/vendor7、actual SDK/native binding、App 返回/真实 close、原一 reset 和真实 term/trunc 等仍由父后续流程观察；SOURCE 审计或八项内存测试不代表这些实际 PASS。

母 teacher、own A1 source-container 两类身份继续分离。母 PT 访问 0 是未来保留的 guard/actor 要求，本轮没有开任何真实 PT；fresh WM / optimizer0 不被称为训练。原 N1024/full history 仍保留在 source-container 的 CPU 完整性规则中，不以切片伪装 N80。actual0 capture 仅作 embedded 原 teacher(mean) 保持 baseline。

## 3. 八项 NEW 小测试

[测试源码](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_stage_good_expert_holdout_v6/test_good_holdout_v6_source.py>)、[TEST_REPORT](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_stage_good_expert_holdout_v6/TEST_REPORT.json>)：**8/8 PASS，首轮 0.714s，五项 audit 全 0**。

1. 原 D5 全 8 sealed members 和完整 127 SOURCE mirror pins 只读保持。
2. NEW component 全字节派生与 1/0/3 个函数 AST whitelist；6/30/28 完整函数 source 不变。
3. actual 两角色 raw9 三 dict 正例，以及原4/9 predicate 冲突复现。
4. wrong mother path/SHA/bytes/frozen 仍经原身份 predicate 失败，含三 dict 同时改错的反例。
5. 每字段缺失/extra、bool/float/string 冒充 int1、非 True retained flags 严格失败，无默认补齐。
6. 只执行 entry 精确 deepcopy 表达式，确认 raw9 完整保留且新对象与原 metadata 无共享 dict。
7. complete20 仅两行变化、18 相同、guard→runtime→D6 INDEX_PIN 的精确传递。
8. 剩余 metadata/cache/source mappings/wire/typed publication/resource 原源码保持及 core 无另一个硬 pin。

测试执行的仅为完整 pure `need`/`teacher_identity`、原 runtime 的精确身份语句块、NEW guard 的精确身份语句块和单独 deepcopy 表达式。没有调用完整原 validator/reference function、derive_producer_guard、prepare、metadata_validate、stage 或旧 12/32/36 测试；没有 import consumer/native 模块。

准备历史：第一次仅 SOURCE deriver 的单 token 断言因实际字段是 `producers[role]` 而非预想 `producer` 未命中；只修正 NEW 文本生成器，随后派生成功。该次没有生成 entry 或运行 actual 入口；已生成的四个 NEW component 文件原字节核对一致。八项测试首轮全部 PASS，未将该准备失败或任何旧 actual 失败改记为 PASS。

## 4. 实际 SOURCE 镜像与两个独立封件

[完整镜像](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_stage_good_expert_holdout_v6/SOURCE_MIRROR_INPUTS.json>) 的实际 **145 项**由以下精确去重结果组成：

- 原 **127 项**逐字段、逐字节保持；
- 原 D5 的 8 成员 + seal：9 项；
- NEW teacher-schema 的 5 成员 + seal：6 项；
- actual teacher-schema V1 / V2 诊断和 D5 actual failed-preflight JSON：3 项。

新增合计 **18 项**。这是 workspace-relative 文本 SOURCE mirror，不含实际 runtime/staticbanks/assets/model；并非 flat20 payload 或完整 SDK。R 与 sibling T 的布局保持。D6 自身 **8 个成员 + 独立 seal**须另外携带，145 项不包含其自身以避免循环。flat20 仍须按 ACTIVE NEW V2 overlay index 完整映射，保持其他 18 行；不以逻辑 mirror 取代平铺材料。

[主 SOURCE_INDEX](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_stage_good_expert_holdout_v6/SOURCE_INDEX.json>) 的 ACTIVE `source_index` 与 `flat_source_dir_complete20_mapping` 两条 guard/runtime 实际 row 都指向 NEW component bytes。旧 21075 / `6f2fb9a4c3ad145620e1bb1b9748ae3848ef1287129aa5970dacee22502a128e` index 单独保留为 `historical_original_overlay_source_index`，不把它冒充新 active index。

两个封件：

- [teacher-schema V2 seal](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_holdout_teacher_schema_v2/SOURCE_SEAL.json>)：**5 成员**，root `4b3076d0cb187bd88f22699996f6b8dea9ec8650707ff75fbea204ac95ce9301`。
- [D6 seal](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_stage_good_expert_holdout_v6/SOURCE_SEAL.json>)：**8 成员**；精确 root、成员 bytes/SHA 和镜像 pins 以该 seal 为准。seal 后仅只读核验，源码保持稳定。

[SOURCE packager](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_stage_good_expert_holdout_v6/build_source_v6.py>) 只有 `--derive` / `--seal` / `--verify`，用于两处 NEW 目录的固定文本派生、hash/AST/JSON 和封存，不是新 stager/executor/dispatcher。只读复核命令：

```powershell
& 'C:/Users/lulu/AppData/Local/Programs/Python/Python314/python.exe' -B 'F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_stage_good_expert_holdout_v6/build_source_v6.py' --verify
```

## 5. Typed 路由、历史记录与质量边界

- D6 Source preflight label：`SOURCE_GOOD_EXPERT_HOLDOUT_PREFLIGHT_ONLY_V6`；未来 Source receipt：`SOURCE_MATERIALIZED_GOOD_EXPERT_HOLDOUT_NOT_NATIVE_STAGE_V6`；source_derivation_version=6。
- runtime plan publication 仍只在所有 copy/hash/fsync/retention/provenance 和完整 metadata 验证之后设置原两字段 enabled/staged=True；SOURCE receipt 的 staged/source_native_enabled/dispatched 仍 False。new GROUP_PLAN_bytes/GROUP_PLAN_SHA256 绑定新 runtime bytes。
- 原 actual wire 严格 pin：14112 / `a78cbaf8961264f16bdd1007dbab72a0fb442fae080978f057e52fef1dfd7fd1`；cached published SOURCE：14385 / `54172e4ff8fcd502602d60dfa3c35c9ed5acc02d871691e231637e59123795a0`；附加 canonical：`8c3b55e059c82de8113d4c7a19395c079981b31ffab51266161037b86f1ab51a`。三身份保持分离，不接受任意等价 JSON/CRLF/额外换行；original_plan_SHA 仍绑定原 wire，不是新 plan SHA。
- 原 COMPLETE wire filename 仍 `STAGE_COMPLETE_GOOD_EXPERT_HOLDOUT_V1.json`，这是既有 wire 协议，不是 D6 artifact 标签。private GPU_EX + finite EX、C readonly、emptyGPU23500 MiB、RAM96 GiB、disk25 GiB、1800 wait / 900 ready / 2400 deadline、实际 child p.wait-before-grade/finally-wait-before-unlock 与外层 controller actualwait 的区分均不改。
- 历史四次实际 before-stage failure、D5 原 identity failure、V1 bare `python` RC127 和旧封件保留原记录。后来的 Source 测试 PASS 不回写它们，也不代表实际 D6 preflight PASS。
- 首要目标仍是原好专家通过率保持；H1 冻结不构造，其余六角色 deferred。C878/S135 保留原 N80、每角色 750 controls、原 ascending/descending/standing/物理 D0D7，使用独立 holdout seeds 20260929 / 20260930。统计仍 conditional per-direction / standing，不合并成整个技能90，不发明 E0/S50 predicate，不声称新质量/改进/noninferiority 已测。

父后续自行 review / CPU / preflight / stage / dispatch；本封件不自动 stage、不扩展边界。CFF typed 传播由父在最终双 seal 与实际 pins 交付后处理。
