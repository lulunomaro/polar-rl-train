# Good-expert holdout materializer V2 — SOURCE_READY_FOR_PREFLIGHT_NOT_NATIVE

仅准备 C878/S135 原技能保持、独立 seed 评测的 SOURCE。原 8/14 封件、原 20 overlay 和原 parent 均保持固定。此版本修复 V1 的 **26 vs 真实 27** 原依赖闭包缺口，并独立保全同 alias 被 NEW overlay 替换的原字节。没有实际 prepare、preflight、stage、dispatch、SSH、SDK、GPU、模型/raw、C ledger、锁或 Git 操作。

- SOURCE 状态：`SOURCE_READY_FOR_PREFLIGHT_NOT_NATIVE`。
- `enabled/source_native_enabled/staged/dispatched = False`；`actual_native_binding = UNKNOWN`。
- 本包不产生新质量结果，不声称改善、非劣或全技能 90%；不补发既有训练证据。
- 原 V1 的只读结论仍是 `NOT_LAUNCH_READY`，记录在 [原 readiness 报告](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_holdout_parent_readiness_review_v1/SOURCE_REPORT.md>)；它没有被本版改写。

## 1. 最窄来源变更

主入口：[stage_good_expert_holdout_v2.py](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_stage_good_expert_holdout_v2/stage_good_expert_holdout_v2.py>)。该入口由 [derive_stage_good_holdout_v2.py](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_stage_good_expert_holdout_v2/derive_stage_good_holdout_v2.py>) 对固定 V1 全文作计数严格的最窄派生；不是另造 executor/stager 框架。

| 项目 | V2 行为 |
|---|---|
| 修改的原函数 | 仅 `prepare`、`preflight_summary`、`stage` |
| 原函数保留 | 其余 22 个完整 AST 相同，包括 `main`、`native_boundary`、`producer_final`、`metadata_validate`、完整 AppV6→Base import 检查和原静态遍历 helpers |
| 新增纯源码 helpers | `preservation_digest`、`original_dependency_map`、`retain_originals`、`validate_preservation`、`preservation_summary` |
| 固定 original GROUP_PLAN | 14385 bytes / `54172e4ff8fcd502602d60dfa3c35c9ed5acc02d871691e231637e59123795a0` |
| 固定额外原依赖 | `single_gpu_group_supervisor.py`，9247 bytes / `7c826b983887cb9ec890c92737095c5e7e7d93538fafaa211021fea2e0d9fc27` |
| 原依赖集合 | 24 个既有文本依赖 + 2 个原资产 metadata + 固定额外 supervisor = 精确 27；不接受任意 extra、少项、重复或改 PIN |
| 新 active parent | 仍为 `single_gpu_good_expert_holdout_parent_v1.py`；与原 supervisor alias 不同 |
| wire receipt | `STAGE_COMPLETE_GOOD_EXPERT_HOLDOUT_V1.json` 保持；仅 SOURCE receipt `kind` 为 V2 |
| 原 plan 上限 | 262144 bytes 不变；完整保全证明置 sidecar，而非膨胀 plan |

原 parent 私有 GPU EX＋全局 finite EX、C readonly、空 GPU 23500 MiB、RAM 96 GiB、disk 25 GiB、1800 wait、900 ready、2400 deadline、真实 `p.wait()` 后 semantic grade、finally wait 后 unlock 完全保持。没有新 manual-review/approval boolean、C writer 或 Popen。

## 2. 独立原字节保全，而非两份相等数组自证

未来 `prepare` 沿原真实 entry 读取完整允许的原 worker_sources、pinned_assets、两角色完整 runtime/source/static-bank/deps，以及原完整 vendor7。原 denied 名称仍先于 DirEntry 分类过滤；本次 SOURCE 没有读取真实 bank/资产/vendor7 全树。

在 overlay 前，独立保留全部输入的 `input_path`、`bytes_read`、SHA、logical alias 和完整 logical-tree digest。仅出现 **同 alias 且不同 bytes/SHA** 时，原字节迁移至：

```text
worker_sources/good_holdout_retained_original/<original alias>
```

原三处真实冲突是 E1 worker、bridge、factory；active alias 使用既定 NEW overlay，原 alias 对应的旧字节由明确 mapping 保全。原 supervisor 目前没有 active alias 冲突，保持原 alias；测试另覆盖同名不同内容的合成 supervisor 冲突。相同 alias/相同字节不额外复制。

未来 `stage` 按原 stream-copy 实际读入字节计数与 hash 形成 `written` observations，逐项与独立原输入对应；缺 retained、改 hash、伪造路径、丢原依赖、两份同样伪造的 baseline/installed 都失败。结果另写：

```text
RETAINED_ORIGINAL_STATIC_FILES_GOOD_EXPERT_HOLDOUT_V2.json
```

sidecar 最大 8 MiB，receipt 固定其 bytes/SHA。它不替代模型物理包含性、真实原资源准入、父等待或 native 证据。

## 3. 真实 SOURCE 接口接受性与测试边界

[NEW 测试源码](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_stage_good_expert_holdout_v2/test_good_holdout_v2_source.py>) 运行 18 个新的窄回归，**不是重跑旧 18 个测试**。结果见 [TEST_REPORT.json](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_stage_good_expert_holdout_v2/TEST_REPORT.json>)。

- 真实固定 27 GROUP_PLAN 全 bytes/PIN、25 个原文本源码 PIN、extra 缺失/篡改/重复/未知 extra。
- 三处真实 E1 overlay 冲突；原 supervisor 未冲突与合成同名冲突分别保全。
- 独立原 input path/read bytes/logical digest 与实际 stream observations；缺项、改 hash、伪造两相等数组、冲突 retained alias 的负例。
- **实际未修改的完整 `metadata_validate`、实际 overlay `_stage_file_metadata/select_requested_roles/make_task`**，分别对 seed 20260929 和 20260930，接受原 extra＋retained worker_files；历史 seed、跨 seed、缺 alias、重复、路径穿越、错 bytes 等负例。
- 原 parent 全源 PIN/hash-loop AST、完整 22 函数保留、3 函数白名单与 sidecar 不进入 plan。
- 完整 AppV6→dc4Base、canonical7a092、whole metadata 模块真实导入；没有 stub/裁剪模块，没有 worker/parent main。

fixture 仅使用明确 FAKE 的 static/vendor marker、synthetic producer TASK/manifest/FINAL 和只在内存中的 own-container path。母 teacher 身份与完整 producer worker/bridge source guard 不变，FAKE PT 路径从未创建/stat/open。临时目录用标准 `tempfile.tempdir` 指向 NEW，所有写入被限定在本目录。原 source 与封件前后 SHA 相同，audit 的 model/stat/open、真实 raw、native imports、process/network/lock、escaped writes 全 0。

这不是目标环境原 bank/资产/vendor7 完整性测试、真实 SDK/MRO/robot-writer/pose binding、physical readback、模型 freeze/read-count、真实 App close 或真实 parent wait 的证据。

## 4. 完整 SOURCE 包与 flat20 路由

需携带本完整封件的 9 个成员及 seal；外部实际文本依赖清单由 [build_source_manifest_v2.py](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_stage_good_expert_holdout_v2/build_source_manifest_v2.py>) 生成。新 `SOURCE_MIRROR_INPUTS.json` 用 `workspace_relative` 保留两个 sibling project trees；`F:/RMPOLAR-RL` 只是原始 provenance，可在另一 workspace 下按同样两个顶层目录布局。数量以实际清单计算，不硬编码旧数量。

外部清单包含固定原 25 文本、原 GROUP_PLAN、完整 20 overlay 的真实来源、旧封件成员/provenance、实际 producer guard worker source 和固定只读 readiness 报告。它是 **SOURCE 文本闭包**，不包含模型、真实 raw bank、原资产或完整 vendor7/runtime；这些仍是未来 original-root/native-root 的独立实际输入。

新 `SOURCE_INDEX.json` 给出每个 overlay 的 `relative`、`flat_name`、`source_workspace_relative`、bytes/SHA。未来 `--source-dir` 必须是这 20 个完整原文件按 `flat_name` 放置的平面目录，`--source-index` 必须传旧 sealed [GOOD_EXPERT_HOLDOUT_SOURCE_INDEX_V1.json](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_expert_holdout_subset_v1/GOOD_EXPERT_HOLDOUT_SOURCE_INDEX_V1.json>)，**不是**本版 materializer 的 `SOURCE_INDEX.json`。旧 index 的 Windows path 仅用于取 basename/provenance；真正安装 alias 使用 `relative`。没有自动下载、远程 executor 或大 stager。

封件/只读复核入口（本次仅本地 SOURCE 执行）：

```powershell
& 'C:/Users/lulu/AppData/Local/Programs/Python/Python314/python.exe' -B 'mod4v1_supermimic_bptt_20261102/source_stage_good_expert_holdout_v2/derive_stage_good_holdout_v2.py'
& 'C:/Users/lulu/AppData/Local/Programs/Python/Python314/python.exe' -B 'mod4v1_supermimic_bptt_20261102/source_stage_good_expert_holdout_v2/test_good_holdout_v2_source.py'
& 'C:/Users/lulu/AppData/Local/Programs/Python/Python314/python.exe' -B 'mod4v1_supermimic_bptt_20261102/source_stage_good_expert_holdout_v2/build_source_manifest_v2.py' --verify
```

`--verify` 只读；builder/derive 的默认路径仅可独占创建或验证相等，从不覆盖已固定结果。测试写本 NEW 的 source report，不应在封件后为了进度再改动结果。

## 5. 未来 CLI 协议示例——本次没有执行

参数保持 V1。每个 seed 需不同的 absent absolute new-root、对应 group-id 和独立 purpose；seed 20260928 的旧结果不重标为新 evidence。示意：

```bash
python -B "$PACKAGE/stage_good_expert_holdout_v2.py" \
  --original-group-root "$ORIGINAL_V8_CLOSED_ROOT" \
  --source-dir "$COMPLETE_FLAT20_SOURCE_DIR" \
  --source-index "$SEALED_GOOD_EXPERT_HOLDOUT_SOURCE_INDEX_V1" \
  --native-root "$CLOSED_ADMISSION2_ROOT" \
  --new-root "$TASKS/MOD4V1_GOOD_EXPERT_HOLDOUT_V2_SEED20260929_UNIQUE" \
  --group-id MOD4V1_GOOD_EXPERT_HOLDOUT_V2_SEED20260929_UNIQUE \
  --gpu-uuid "$GPU_UUID" --seed 20260929 --preflight-only
```

另一 seed 使用 `20260930` 和完全独立 root/id。未来若单独执行 `--stage`，只物化、只输出 SOURCE receipt、parent_launches=0，所有 native flags 仍 False；不是 native enable/dispatch。失败 root consumed，不重试同 root。本包不包含独立外部 controller、collector 或 own-purpose external wait receipt；下一步由父 agent 独立 review/CPU/preflight/部署/调度。

## 6. 技能与质量协议完全不变

完整 8-role catalog，仅构造 CURB_PROTECTED878/SLOPE135，其他 6 deferred，H1 不构造；每角色 N80/750 control，ascending27/descending27/stand26，原 D0D7、DR、commands、接触/endpoint/standing 条件、physics/feedback/actor 6000/1500/750 保持。seed 20260929 与 20260930 分属独立 purpose。

actor 始终来自 actual0-update own A1 fullcapture 的 embedded **原 teacher public mean**；own container 与 mother 身份分开，不把 fresh WM/optimizer0 当训练。原 wholepi/STD/Norm/freeze、physical checkpoint containment、one-bytes/hash/decode、mother reopen0 guard 保持；source-only 本次没有打开任何 checkpoint。

已发布旧 seed 20260928：C878 ascending26/27、descending27/27、standing26/26；S135 27/27、27/27、26/26。新独立 seed 没有实测。未来统计仍按 direction/standing 条件分别报告；不混成整个技能 90%、不引入 E0/S50 predicate、不声称新质量已测。good holdout 不依赖 Stage2 residual actor 或训练改善。
