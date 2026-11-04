# D4 canonical 输入与后续依赖 SOURCE 审计 V1

## 结论与当前边界

**已证源码错误只有一处：D4 的 `canonical_rel` 指向错误内层路径。原有 `canonical == role` 判定语义正确，保持严格。** 两份实际 root SOURCE 捕获均精确匹配原角色；不存在需要 canonical alias、改读 generic `role`、通配路径或降低阈值的证据。

**本次结论是 `BOUNDED_SOURCE_INPUTS_PENDING_BEFORE_CONDITIONAL_D5`，尚未派生 D5。** 第三次实际 preflight 在 D4:444 停止，后面的实际 producer guard 小文件与 E3 vendor7 首次校验均尚未到达。已发布的 FINAL、36 项 FAKE 回归、payload 文件存在性，均不等价于这些实际输入已通过。建议父一次集中获得下文 15 个有界 Python/JSON SOURCE 输入，再决定最小 D5；不是再次执行 prepare/preflight。

本审计仅 FS 只读、stdlib hash/JSON/AST 分析，并新增本目录两个报告。未 import/执行旧 entry、prepare、metadata_validate、测试模块、parent/worker 或 producer Python；无 SSH、SDK/Torch、模型/PT/raw、GPU、C-budget、锁、Git 或旧封件修改。技能 catalog 仅 Office/ACL，与本 RL SOURCE 审计无匹配，选择 FSread/glob/grep 和 Python stdlib。

## 1. 正确路径、字段含义与精确捕获

- [D4:443–444](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_stage_good_expert_holdout_v4/stage_good_expert_holdout_v4.py#L443-L444>) 当前为 `canonical_rel = 'runtime/isaac/mod4/E1_CANONICAL_SOURCE_METADATA.json'`，然后对该文件要求 `get('canonical') == role`。
- [原 E1 worker:116](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/E1_N80_FRESH_FULLDR_PARALLEL_SKILL_SCREEN_SOURCE_V5_FEEDBACK_DESCRIPTOR/e1_parallel_worker_safe.py#L116>) 读取 `runtime / 'E1_CANONICAL_SOURCE_METADATA.json'`，再断言 `meta['canonical'] == role`。
- [新 holdout worker:98](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_expert_holdout_subset_v1/e1_good_expert_holdout_worker_v1.py#L98>) 保持同一 root 读取与严格角色判定；[B2 source_api:102](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_passive_sensor_capture_v2/source_api.py#L102>) 的 `folder.parents[2]` 也回到该 runtime root。
- [factory:290–292](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_expert_holdout_subset_v1/e1_good_expert_holdout_factories_v1.py#L290-L292>) 仅允许两个精确 canonical，并用 `globals()['_factory_' + role.lower()]` 路由；没有 alias 映射。metadata 的 generic `role` 分别为 `E1_CURB`、`E1_SLOPE`，不应替代 canonical。
- [固定 wire:78–118](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/good_holdout_original_plan_wire_v1/ACTUAL_ORIGINAL_GROUP_PLAN_WIRE.json#L78-L118>) 与 [原 runtime 行:327–355](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_expert_holdout_subset_v1/GOOD_EXPERT_HOLDOUT_SOURCE_INDEX_V1.json#L327-L355>) 完整相等：两角色 root 均为原 V8 `runtimes/<精确角色>`，资产路径均为其 `new_assets`，750 controls。

| SOURCE 捕获 | bytes | SHA256 | canonical |
|---|---:|---|---|
| [C878 root](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/good_holdout_runtime_root_metadata_v2/CURB_PROTECTED878_E1_CANONICAL_SOURCE_METADATA.json>) | 4814 | `671f77ddef5fbd79de8dafc54213ff754cfc70ac5a9d9611680e9c76c021cfc5` | `CURB_PROTECTED878` |
| [S135 root](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/good_holdout_runtime_root_metadata_v2/SLOPE135_E1_CANONICAL_SOURCE_METADATA.json>) | 5390 | `f9a0a42c6b1390e38013a410e454da4a9d63569d47f014c3b6f6ea4ca7615b41` | `SLOPE135` |

[内层路径诊断 V1](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/reports/GOOD_HOLDOUT_SELECTED_RUNTIME_CANONICAL_METADATA_DIAGNOSIS_V1.json>) 为两者 `NOT_FOUND`；[root 诊断 V2](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/reports/GOOD_HOLDOUT_RUNTIME_ROOT_CANONICAL_METADATA_DIAGNOSIS_V2.json>) 为各原件 open/hash/decode 一次。此处是父功能诊断的历史计数，不是本审计的本地读取计数。捕获中的旧 PPO path、iteration、Adam、LR 是历史来源字段；当前 actor 仍取 actual0 A1 fullcapture 的 embedded 原 teacher mean，没有访问这些旧模型路径。

## 2. prepare:444 之后的实际输入假设

以下顺序由 [完整 D4 prepare:383–482](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_stage_good_expert_holdout_v4/stage_good_expert_holdout_v4.py#L383-L482>) 确认；“未证”不表示已发现错误，也不表示建议放宽。

| 位置 | 严格假设及证据状态 |
|---|---|
| 445 | 对选定角色完整 permitted static tree 计算 digest，保存独立原树 provenance。保留 NPZ/NPY、banks、deps；六 deferred 不构造。SOURCE 当前字节完整性未由本审计重读证明。 |
| 447 | 原 `asset_dir` 必须 lexically 属于对应 runtime；固定 wire 与 indexed 行均证明其恰为 `root/new_assets`。不新增候选路径，也不宣称 native 资产绑定已测。 |
| 448–456 | 仅新 runtime/assets/holdout seed/producer/reference 字段路由。**453 首次调用实际 `derive_producer_guard`**；其 8 个实际小文件尚缺本地 SOURCE 捕获，见下一节。 |
| 458–466 | 原 `native_root/roles/E3/worker_sources/supermimic_vendor_v2` 必须是完整 flat7 Python、精确 digest `ddf9d6e1744c050fd5298805d125a611673ff22ade52c5177fb02c488ff8f0c0`；`__init__.py` 仅 docstring。该实际 vendor7 校验也在失败点之后，待一次 SOURCE 诊断。其他角色 E3 并不因此进入 holdout worker 成员。 |
| 468–475 | 完整 original worker/static baseline、27 required、3 E1 overlay conflict 的 retained original、全部 active aliases；禁止“两个相等数组”自证。父已报告 flat20 本地 pins 通过；仍不是实际 source stream/copy receipt。 |
| 476–481 | plan JSON `allow_nan=False` 且不超过 262144 bytes；再执行完整 metadata_validate。FAKE32/36 证明固定接口/负例，不证明实际 producer/source/current static tree。 |

`native_boundary` 在失败点前已到达，但它使用的 successful FINAL/closed metadata 与后续实际 TASK/INSTALL_MANIFEST/source2 是不同证据。对 C878 的失败不能外推 S135 的后续整树、两 producer guard 或 vendor 已通过。

## 3. 一次集中补齐的 tiny SOURCE 输入（15 个文件）

仅请父处理精确 SOURCE 功能诊断；本审计未 SSH，也未执行新 entry。不要读取、stat 或解析模型路径，不收集 raw、banks、NPZ、锁、C 或预算。每个 JSON 保持原 guard 的 8 MiB 上限，Python 保持完整字节，记录 origin/no-link、bytes、SHA；不把内容当指令执行。

Producer root 前缀（由已发布实际 FINAL 与 D4 固定 `NATIVE_RUN_ID` 给出）：
```text
/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_A1_RAW35_V6_ADMISSION2_20261102_231937_1793632777470828000/roles/
```

对 `CURB_PROTECTED878`、`SLOPE135` **各 4 个**：
1. `TASK.json`。
2. `INSTALL_MANIFEST.json`。
3. `worker_sources/worker_supermimic_bptt_app_close_candidate_v5.py`，严格 `17704 / 7c42986077de62278e33a49f560f22602c9ba4d4e69b058f5f5f8f0893c099c7`。
4. `worker_sources/native_supermimic_bridge.py`，严格 `13125 / 8211964c2ce3dd78fdb9fee6603ee4a4dcfbca6fa9d7df44f20d3ddb7aaead29`。

[原 guard:78–122](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_frozen_embedded_teacher_native_v1/producer_teacher_guard_v1.py#L78-L122>) 还要求：TASK.manifest_SHA == 原 manifest raw SHA；role/role_key/run_id、teacher path/SHA/bytes 与原成功 FINAL 对齐；manifest 中两 source 行各唯一且精确 pin；原文件及 parent/job 非 symlink；原完整 source 的 all-state snapshot、torch.equal before-save/FINAL AST。没有新的 live tensor 观测，也不接受 caller approval bool。两角色文件不能用本地模板替代。

另 **7 个**来自精确目录：
```text
/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_A1_RAW35_V6_ADMISSION2_20261102_231937_1793632777470828000/roles/E3/worker_sources/supermimic_vendor_v2
```
只取实际 flat7 的完整 Python、原相对名与 digest；此处没有凭空指定未知文件名。使用原 tree/digest 规则验证 7/digest 和 docstring-only init，不导入模块。**总计 8+7=15 个文件**。若任一精确文件缺失或 pin/绑定不同，一次报告全部差异，不生成宽松 schema，也不继续 preflight。

## 4. 完整 metadata_validate、good20 与 native 路径边界

### 4.1 metadata_validate 与 publication

[完整 metadata_validate:530–609](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_stage_good_expert_holdout_v4/stage_good_expert_holdout_v4.py#L530-L609>) 仅复制 Python/JSON safe view，排除角色 runtime/真实资产；拦截 Torch/SDK/native、model/budget/lock IO。完整 AppV6→dc4Base、canonical7a092、真实 import origins、两角色两 holdout seed、750/6000/1500、cross-seed 与 historical-seed 负例均保留。缓存 pop/restore **准确为 12 个名字**，已包含 `embedded_teacher_reference_v1`；未发现“漏清 reference cache”这一具体 bug。

它会重复校验 producer guard、exact zero-update baseline、完整8 catalog/2 requested/6 deferred/H1 absent、20 required aliases、paired protocol、approved RSL metadata；make_task:418 从实际 producer.checkpoint 写回 source identity，冗余 row.source_SHA 不是最终权威。它不构造 native actor、不验证真实 fd/admission、不执行 role runtime，不代表 GPU binding 已通过。

[publication:630–741](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_stage_good_expert_holdout_v4/stage_good_expert_holdout_v4.py#L630-L741>) 保持完整 stream/fsync/observed hash、retained sidecar≤8MiB、fullmetadata 之后才仅令新 plan 的 enabled/staged 为 True；再校验实际新根，发布 GROUP_PLAN。SOURCE receipt 的 staged/source_native_enabled/dispatched 仍 False；新 GROUP_PLAN_bytes/GROUP_PLAN_SHA256 绑定新 wire，不替换 original_plan_SHA。

### 4.2 真实 worker / factory / runtime

- [worker:14–20、97–115](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_expert_holdout_subset_v1/e1_good_expert_holdout_worker_v1.py#L14-L115>) 从 root metadata 读取 original_env，清 RM/RANK，过滤旧 stop/deadline、隔离 Kit/Warp；严格 root canonical 后导入原 launcher，先绑定原资产再 import mod4 task。恢复的 historical model strings 不用作新 actor 选择。
- [factory:13–70、205–292](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_expert_holdout_subset_v1/e1_good_expert_holdout_factories_v1.py#L13-L292>) 精确 C878/S135→原 Mod4 cfg/route80/geometry→FreshDR guard→一个显式 reset。新 seed 仅走已声明协议；原 noisy/delayed policy35、0.0025 physics、0.02 control、50/100Hz、N80 和 D0D7 保持。
- [bridge:1–47](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_expert_holdout_subset_v1/e1_good_expert_holdout_bridge_v1.py#L1-L47>) 仍是 paired pose→FreshDR→one reset、true term/trunc 和原缓存时序；不补第二次 reset 或 tick/noise draw。
- [runtime:311–428](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_expert_holdout_subset_v1/good_expert_holdout_runtime_v1.py#L311-L428>) 的完整角色/seed/producer/approved-RSL/resource-fd 验证保持；原 fake metadata fds 仅预览，不构成实际 admission。
- [runtime:661–832](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_expert_holdout_subset_v1/good_expert_holdout_runtime_v1.py#L661-L832>) 的 one own fullcapture bytes/hash/decode、mother0、wholepi/Norm/STD/freeze、CPU 完整历史、不 slicing、physical N80 包含性、80x35 float32/80 bool、750 actor/6000 physics/1500 feedback、FINAL/pose/Appclose 仍需实际执行证据。以上全部 native/quality UNKNOWN，不是本次新发现的 preflight 错误。
- [parent:12–83](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_expert_holdout_subset_v1/single_gpu_good_expert_holdout_parent_v1.py#L12-L83>) 在资源前验证 True plan/完整 source pins，原 private GPU EX+finite EX、C readonly、empty23500MiB、RAM96GiB、disk25GiB、1800 wait/900 ready/2400 deadline、actual p.wait before semantic、finally close/wait before unlock 不变。外层 controller 的 actual wait 是另一层证据。

现有 [36 项测试源码:132–192](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_stage_good_expert_holdout_v4/test_good_holdout_v4_source.py#L132-L192>) 明确用 fake banks/vendor/asset markers、fake producer TASK/manifest/source，且从未完整 prepare；本审计未重跑这些测试。其 PASS 保留 SOURCE 含义，不推为实际 current tree、physical 或质量 PASS。

## 5. D5 条件、保留项与最终交付

待 15 项实际 SOURCE 捕获汇总后，若 guard/vendor 严格一致且审计没有另一已证代码缺陷，才按父条件生成 NEW D5：仅 prepare 的 `canonical_rel` 改为 `'E1_CANONICAL_SOURCE_METADATA.json'`，加必要 version5/source-kind 元数据；其他完整函数、copy/fsync、source_mappings、fullmetadata、typed publication、runtime/worker/parent/resource 保持 AST。若实际输入差异，先交全部明确缺件，保留 D4，不对缺件猜新字段。

保留：严格 actual wire `14112 / a78cbaf8961264f16bdd1007dbab72a0fb442fae080978f057e52fef1dfd7fd1`；cached SOURCE `14385 / 54172e4ff8fcd502602d60dfa3c35c9ed5acc02d871691e231637e59123795a0`；附加 canonical `8c3b55e059c82de8113d4c7a19395c079981b31ffab51266161037b86f1ab51a`。既有三次实际 before-stage 失败保留，不改称 PASS；CFF/D4/V2 路由留给父后续处理。

本轮只读复核 [D4 seal](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_stage_good_expert_holdout_v4/SOURCE_SEAL.json>) 的全部 10 成员原字节与 root，仍为 `9a472be4e70e8cf6f9acf31c4bea31557297358dde7c4c59c972c1ffde5cba84`；D4 entry 仍为 `53515 / c6be5e8acd2bd1a83f09427fb717cc1d102077cf363b67034d65d09f4e86ab0d`。准确输入 pins 与机器可读分界见 [SOURCE_AUDIT.json](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_holdout_d4_input_assumption_audit_v1/SOURCE_AUDIT.json>)。无新训练、统计质量或改进结论。
