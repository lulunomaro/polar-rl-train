# Good-expert independent holdout：只读 launch-contract review V1

## 结论

**状态：`NOT_LAUNCH_READY`。唯一已经由固定原 metadata 集合比较确认的阻断点，是旧物化 CLI 的原 dependency 集合 26 对真实 27。**

- 原始技能保持是首要目标；本检查不训练、不打开模型、不派发评测。CURB_PROTECTED878 / SLOPE135 的新独立 seeds 20260929、20260930 尚无本次实际准入或质量结果。
- 本报告仅审阅已封 SOURCE、已发布原 metadata 和本地来源代码；实际 E1 native instance 的 pose/SDK binding、资源准入、模型包含性、实际 App close 均保持 `UNKNOWN`。
- Phase1 B1 的 reset-identity 现场失败不直接传染到此 E1 路径；两处 Phase1 close 源码问题在这里也已排除。此结论不等于实际 native PASS。
- 此处记录旧 V1 的真实状态；后续若有 NEW 修复 lineage，本报告不回写旧 seal，也不把旧 V1 重标为可执行通过。

## 1. 本次范围与只读记录

技能 catalog 只有 Office 与 Windows ACL 类，无 RL 匹配；使用 FS read/glob/grep 和 Python stdlib 的 JSON、SHA256、集合比较，不加载 Office 技能。未执行任何 stager / prepare / preflight / stage / parent / worker / Popen；没有重跑旧 18-test 脚本，没有 SSH、SDK/Torch、真实 PT/raw、GPU、C-budget、锁或 Git 操作。

独立只读核验：

| 项目 | 结果 |
|---|---|
| 旧物化封件 | [SOURCE_STAGE_GOOD_EXPERT_SEAL_V1.json](<mod4v1_supermimic_bptt_20261102/source_stage_good_expert_holdout_v1/SOURCE_STAGE_GOOD_EXPERT_SEAL_V1.json>)：8 members，root `94330bb54b9dda0a7081d139f1cd0bd156f5e62c387273871f5b7cfebdea2e79` |
| 原 holdout SOURCE 封件 | [GOOD_EXPERT_HOLDOUT_SOURCE_SEAL_V1.json](<mod4v1_supermimic_bptt_20261102/source_good_expert_holdout_subset_v1/GOOD_EXPERT_HOLDOUT_SOURCE_SEAL_V1.json>)：14 members，root `032c431b844aedc02bffad76549b9516f92e5cfd06cce6194e47d5f4451c7534` |
| 当前逐文件核验 | 两封件共 22 members 的 bytes/SHA 及 root 均一致；上游 index 的 44 text rows / 40 unique source paths 均匹配；原始额外 supervisor 另行读取/hash |
| 运行边界 | stager executions 0；旧 tests replay 0；model/native/resource opens 0；仅本 NEW 报告写入 |

封件一致与旧 18/21 fake tests 只说明 SOURCE 回归与历史封存状态，不说明实际输入闭包、native construction 或技能保持已通过。

## 2. 确认阻断：固定原集合 27，旧 CLI 只接受 26

固定输入证据为 [GROUP_PLAN.json](<mod4v1_experts_fulldr_rm70_20261101/reports/NINE_SINGLE_GPU_V8_CLOSED_20261102_101543/GROUP_PLAN.json>)，14385 bytes，SHA256 `54172e4ff8fcd502602d60dfa3c35c9ed5acc02d871691e231637e59123795a0`；这正是 [上游 index:321–323](<mod4v1_supermimic_bptt_20261102/source_good_expert_holdout_subset_v1/GOOD_EXPERT_HOLDOUT_SOURCE_INDEX_V1.json#L321-L323>) 指向的已发布原计划。

[旧 CLI:293–297](<mod4v1_supermimic_bptt_20261102/source_stage_good_expert_holdout_v1/stage_good_expert_holdout_v1.py#L293-L297>) 的条件是：

```python
expected = {row['relative']: ... for row in index['inherited_original_worker_source_entries']}
# 加 required_original_pinned_assets 两项后，expected = 24 + 2 = 26
need(type(old_files) is list and len(old_files) == len(expected)
     and {r['relative'] for r in old_files} == set(expected),
     'complete original worker_files dependency set differs')
```

逐项集合差异（直接解析上述固定 JSON，未调用 CLI）：

```text
expected_count = 26
actual_original_worker_files_count = 27
missing_from_actual = []
extra_in_actual = {
  "single_gpu_group_supervisor.py": {
    "bytes": 9247,
    "SHA256": "7c826b983887cb9ec890c92737095c5e7e7d93538fafaa211021fea2e0d9fc27"
  }
}
```

额外项的完整本地来源 [single_gpu_group_supervisor.py](<mod4v1_experts_fulldr_rm70_20261101/NINE_N80_PARALLEL_SOURCE_V8/single_gpu_group_supervisor.py>) 已 FS-read，实际 bytes/SHA 与该 row 完全相符。它是原九角色 supervisor，不是新的两角色 active parent。本轮没有导入或运行它。

因此，按旧 CLI 规定的固定原组输入，该集合断言会在 native 构造前失败。旧 18 个 fake tests 没有暴露真实原集合的第 27 项。后续 NEW lineage 应精确保留 27 项及其 provenance；原 supervisor 与新 active supervisor 区别标识，若同 alias 异 bytes 则独立 retained namespace 保留原 bytes、映射及独立 origin 对 installed-stream 的核验。删除原项或仅放宽集合断言不构成修复。本报告不改旧 CLI。

## 3. 已封 CLI、输入布局与未来调用合同

旧入口 [stage_good_expert_holdout_v1.py](<mod4v1_supermimic_bptt_20261102/source_stage_good_expert_holdout_v1/stage_good_expert_holdout_v1.py>)：38828 bytes，SHA256 `fc9dd74437258d408e0223359b45814909b5a9a2f80df450dfdea1f546290a2f`。旧物化 index [SOURCE_STAGE_GOOD_EXPERT_INDEX_V1.json](<mod4v1_supermimic_bptt_20261102/source_stage_good_expert_holdout_v1/SOURCE_STAGE_GOOD_EXPERT_INDEX_V1.json>)：4039 / `ddc7d82e9855102258402c95edfac6c2691c59cd9a5a9adf336869a99e2d060d`。上游 [GOOD_EXPERT_HOLDOUT_SOURCE_INDEX_V1.json](<mod4v1_supermimic_bptt_20261102/source_good_expert_holdout_subset_v1/GOOD_EXPERT_HOLDOUT_SOURCE_INDEX_V1.json>)：21075 / `6f2fb9a4c3ad145620e1bb1b9748ae3848ef1287129aa5970dacee22502a128e`。

以下仅记录已封参数合同，**本轮未执行，旧 V1 当前有第 2 节阻断**：

```sh
python -B stage_good_expert_holdout_v1.py \
  --original-group-root "$ORIGINAL_GROUP_ROOT" \
  --source-dir "$FLAT_20_SOURCE_DIR" \
  --source-index "$PINNED_HOLDOUT_SOURCE_INDEX" \
  --native-root "$ADMISSION2_CLOSED_ROOT" \
  --new-root "$ABSENT_NEW_ROOT_FOR_ONE_SEED" \
  --group-id "$GROUP_ID_FOR_ONE_SEED" \
  --gpu-uuid "$GPU_UUID" \
  --seed 20260929 --preflight-only
# 另一个独立 root / group / purpose：--seed 20260930。
# --preflight-only 与 --stage 必须二选一；本轮二者均未执行。
```

- `original-group-root` basename 固定为 `MOD4V1_NINE_N80_SINGLE_GPU_PARALLEL_V8_20261102_101426_1793585666425343700`。
- `native-root` basename 固定为 `MOD4V1_A1_RAW35_V6_ADMISSION2_20261102_231937_1793632777470828000`，应为真实闭合的 admission2 metadata/source。
- `new-root` 必须绝对、尚不存在、与输入树不相交、basename 等于 group-id；group-id 只允许原有字符规则并含对应 seed。旧 stager 没有额外固定新 prefix；真正原 parent 要求 root 位于 `/home/lc01/Zonglin Li/zonglin2/tasks` 下。每个独立 seed 各一个新 root，不复用已消耗 root。
- `source-dir` 是 **20 个 source 原 basename 的 flat 目录**，不是任意 R-relative mirror 根。index 中 Windows 路径只是 provenance：取 `Path(entry['path']).name` 读 flat source，再安装为 `entry['relative']`。它没有 Phase1 的 `--source-root` 适配接口。mirror 打包若保持 R-relative 树，需要明确 flat 映射。
- 原 static 前置条件：完整 `worker_sources`、`pinned_assets`、两个 selected-role 原 runtime 树（全部允许的 static banks / deps）、以及 admission2 E3 的完整 7-file vendor。完整 vendor 固定 tree SHA `ddf9d6e1744c050fd5298805d125a611673ff22ade52c5177fb02c488ff8f0c0`。下节 20 overlays 从来不是完整 SDK/runtime/static 闭包。
- USD / contract 的 metadata pins 分别为 `2c421a8ec66e425ee6e47341ed0803f2c7e84f1f50afcc726572027ef6566ef3` / `bae3203a7c30f75e29c20c0b0d0e215af5edfc7dbeacb9ebc5310f7867c98755`；本轮未开真实资产/raw。
- 对 source mirror 的计数要分清：index 的 20 overlay + 24 inherited rows 是 44 rows / 40 unique source paths；加缺失 supervisor 后是 41 unique text-source origins，另需 CLI/index/原固定 plan 等 provenance。完整真实 static 输入量尚未本轮 inventory，不用 text 数量替代。

## 4. 完整 20 overlay：flat source → installed alias → PIN

| Installed alias | Flat source basename / 本地来源 | Bytes | SHA256 |
|---|---|---:|---|
| `worker_sources/e1/e1_parallel_worker_safe.py` | [e1_good_expert_holdout_worker_v1.py](<mod4v1_supermimic_bptt_20261102/source_good_expert_holdout_subset_v1/e1_good_expert_holdout_worker_v1.py>) | 14129 | `20068d302d713e9826ba4ea4ae9f44708d8cfd2f4965e8b29d16181d4bda9f3e` |
| `worker_sources/e1/e1_fresh_runtime_bridge.py` | [e1_good_expert_holdout_bridge_v1.py](<mod4v1_supermimic_bptt_20261102/source_good_expert_holdout_subset_v1/e1_good_expert_holdout_bridge_v1.py>) | 3552 | `603ee68ffa3dd46d2b5d14d26497aa4ad6ebbf4371548f8eede14fa5e5555f26` |
| `a1_frozen_eval_runtime_v2.py` | [a1_frozen_eval_runtime_v2.py](<mod4v1_supermimic_bptt_20261102/source_a1_frozen_eval_integration_v2/a1_frozen_eval_runtime_v2.py>) | 37927 | `7a092364cf63e9621481dc0a5554b56a22e4412cf89870c3db9a124864074b2e` |
| `frozen_a1_raw35_v1.py` | [frozen_a1_raw35_v1.py](<mod4v1_supermimic_bptt_20261102/source_eval_a1_raw35_v1/frozen_a1_raw35_v1.py>) | 19226 | `1ea4bcfa1081d63d0da2136fedf8c9fafa508d7bb2155095352da496327e4a21` |
| `pose_cache_runtime_adapter_v3.py` | [pose_cache_runtime_adapter_v4.py](<mod4v1_supermimic_bptt_20261102/source_native_v6_runtime_compat/pose_cache_runtime_adapter_v4.py>) | 18161 | `7357827a72a03f6300ce3f7c6da3ad2a05a551480a1aad04a91dbaac4a497e2f` |
| `app_close_semantics_v5.py` | [app_close_semantics_v6.py](<mod4v1_supermimic_bptt_20261102/source_app_close_runtime_compat_v6/app_close_semantics_v6.py>) | 27769 | `3d2d75196fb98fdb45c80a79b5b8bb69873e7c0c2c0b0f6f6610eb11a8c63c39` |
| `native_supermimic_bridge.py` | [native_supermimic_bridge.py](<mod4v1_supermimic_bptt_20261102/source_native_v6_runtime_compat/_SOURCE_INPUT/sealed_source/native_supermimic_bridge.py>) | 13125 | `8211964c2ce3dd78fdb9fee6603ee4a4dcfbca6fa9d7df44f20d3ddb7aaead29` |
| `supermimic_vendor_v2/networks.py` | [networks.py](<mod4v1_supermimic_bptt_20261102/source_core_review/evidence/networks.py>) | 8609 | `c7829e6a1bb9166d724a931858b76424439f371669dfb4bb534b9e76c5c74706` |
| `supermimic_vendor_v2/geometry.py` | [geometry.py](<mod4v1_supermimic_bptt_20261102/source_core_review/evidence/geometry.py>) | 6960 | `89ac3b9470fd6f041fd418365283355a07ad96c4bf38740cf3c5d2d98acb7787` |
| `supermimic_vendor_v2/contract.py` | [contract.py](<mod4v1_supermimic_bptt_20261102/source_core_review/evidence/contract.py>) | 2517 | `d756f2a102a81b2f16295dad66f46e9783b42a3f67e7416360fcf136c2ff06ce` |
| `single_gpu_good_expert_holdout_parent_v1.py` | [single_gpu_good_expert_holdout_parent_v1.py](<mod4v1_supermimic_bptt_20261102/source_good_expert_holdout_subset_v1/single_gpu_good_expert_holdout_parent_v1.py>) | 9679 | `fc4458431d375c2b44c063b3f5a8d4ad83ecc6e21d6684625898f7991c51f0ff` |
| `good_expert_holdout_runtime_v1.py` | [good_expert_holdout_runtime_v1.py](<mod4v1_supermimic_bptt_20261102/source_good_expert_holdout_subset_v1/good_expert_holdout_runtime_v1.py>) | 56370 | `4ea1470d0255bf172a8bc2e16ce70ceae45a91e32ad622e8df6119f4f8ba0c9f` |
| `resume_runtime_contracts_v3.py` | [resume_runtime_contracts_v3.py](<mod4v1_supermimic_bptt_20261102/source_resume_runtime_v2/resume_runtime_contracts_v3.py>) | 22337 | `dc4bc67193457a4fb72b125d23fa482cd3d686363bd1a93eb07268f4e4e26cb7` |
| `embedded_teacher_reference_v1.py` | [embedded_teacher_reference_v1.py](<mod4v1_supermimic_bptt_20261102/source_frozen_embedded_teacher_reference_v1/embedded_teacher_reference_v1.py>) | 16333 | `400e06ea2c04edaab8330022a53455e13629b7f35d3ac7066f51df1acfcd0407` |
| `producer_teacher_guard_v1.py` | [producer_teacher_guard_v1.py](<mod4v1_supermimic_bptt_20261102/source_frozen_embedded_teacher_native_v1/producer_teacher_guard_v1.py>) | 8902 | `855e13c931eb8b8711a15b829a4ca95b10692f11b6a68df73a1dece18f98ecf0` |
| `worker_sources/e1/e1_route80_factories.py` | [e1_good_expert_holdout_factories_v1.py](<mod4v1_supermimic_bptt_20261102/source_good_expert_holdout_subset_v1/e1_good_expert_holdout_factories_v1.py>) | 23877 | `e4f7b5464e8bb26a0222bae2c367e02aee86db48bbbd2ff6c31a4fcfeeaa23e5` |
| `worker_sources/e1/worker_curb878_n80.py` | [worker_curb878_n80.py](<mod4v1_experts_fulldr_rm70_20261101/E1_N80_FRESH_FULLDR_PARALLEL_SKILL_SCREEN_SOURCE_V5_FEEDBACK_DESCRIPTOR/worker_curb878_n80.py>) | 103 | `d40ab8c4c76234fd1869acfe3d4a23646ca18195bd349d0b14a240b24da4a793` |
| `worker_sources/e1/worker_slope135_n80.py` | [worker_slope135_n80.py](<mod4v1_experts_fulldr_rm70_20261101/E1_N80_FRESH_FULLDR_PARALLEL_SKILL_SCREEN_SOURCE_V5_FEEDBACK_DESCRIPTOR/worker_slope135_n80.py>) | 94 | `2568ae5ab0f8db24e6cdd8b9f368ec881b099bf3750215c5e9aa83ec4dc03e42` |
| `worker_sources/e1/e1_endpoint_predicate.py` | [e1_endpoint_predicate.py](<mod4v1_experts_fulldr_rm70_20261101/E1_N80_FRESH_FULLDR_PARALLEL_SKILL_SCREEN_SOURCE_V5_FEEDBACK_DESCRIPTOR/e1_endpoint_predicate.py>) | 2504 | `c6bfc7832226963daee96ed9c7f7d6fb989a87a6f8bc5f21d77a85bc69fd0361` |
| `worker_sources/e1/ROLE_CONTRACTS.json` | [ROLE_CONTRACTS.json](<mod4v1_experts_fulldr_rm70_20261101/E1_N80_FRESH_FULLDR_PARALLEL_SKILL_SCREEN_SOURCE_V5_FEEDBACK_DESCRIPTOR/ROLE_CONTRACTS.json>) | 40841 | `07b902c0ae3a496e6431ee7413c2256a84f701791fb90af3f57be17af8263218` |

## 5. 实际 E1 factory / reset / doneflag 链

入口是 [C878 wrapper](<mod4v1_experts_fulldr_rm70_20261101/E1_N80_FRESH_FULLDR_PARALLEL_SKILL_SCREEN_SOURCE_V5_FEEDBACK_DESCRIPTOR/worker_curb878_n80.py>) 或 [S135 wrapper](<mod4v1_experts_fulldr_rm70_20261101/E1_N80_FRESH_FULLDR_PARALLEL_SKILL_SCREEN_SOURCE_V5_FEEDBACK_DESCRIPTOR/worker_slope135_n80.py>) → installed `e1_parallel_worker_safe.main_role`，对应完整 NEW [E1 worker](<mod4v1_supermimic_bptt_20261102/source_good_expert_holdout_subset_v1/e1_good_expert_holdout_worker_v1.py#L92-L135>)，不是只接受 E0/E2/E3/W35 的 formal worker。

真实顺序：group root 及对应 E1 runtime sys.path → 原 E1IsolatedAppLauncher → 原 SDK imports → unchanged cache / 原 teacher mean → [两角色 factory](<mod4v1_supermimic_bptt_20261102/source_good_expert_holdout_subset_v1/e1_good_expert_holdout_factories_v1.py>) → pose / fresh guard 安装 → **恰好一次显式 env.reset** → ready → 本组两成员 barrier → 原 control loop → env close / FINAL → finally 原 App close。E1 入口不导入 Phase1 曾缺失的 storage/capacity 两模块。

- 只构造 C878/S135；完整八角色 catalog 保留，其他六 deferred，H1 不构造。
- 两个角色各 N80 / 原 750 controls。每角色一次执行应为 6000 physics、1500 feedback、750 actor calls；物理 dt .0025、decimation 8、反馈 100Hz、策略 50Hz、TGS[32,4]、closure/mimic .01、原 D0–D7 与接受条件保留。
- factory 仅以 protocol 给两角色路由新 seed。ascending/descending/standing 为 env_id%3 的 27/27/26；±.3 与 standing 原条件、curb .275 / slope 1.2、原 EndpointPredicate 均不改。
- vector 不偷偷 reset；first_start 与真实 terminated/truncated 供原 episode boundary，原 plant loop 与命令注入结构保留。standing 的 no_failure 是原 group/first_ordinary_failure_control 语义，不新造 crossing predicate。

## 6. 原 teacher 身份与独立 seed 统计边界

[Runtime:93–108](<mod4v1_supermimic_bptt_20261102/source_good_expert_holdout_subset_v1/good_expert_holdout_runtime_v1.py#L93-L108>) 保存 actual0-update own A1 fullcapture 的路径字符串、220144758 bytes 身份与母 teacher 身份：

| 角色 | actual0 owncontainer SHA256 | original mother SHA256 |
|---|---|---|
| CURB_PROTECTED878 | `ae4ac8d31b82c9b7488e7e40419bf2d590be6566822b78a7604e49f848e6bcfe` | `db3d5a6a2a81fb71f6f4e3ca0ee18c09785ddff80b990787960ffc3d8d376d68` |
| SLOPE135 | `22d7ea42c208256cc5c89980472f72df71d8f279a9bc98f09c1eaa8426f2abe1` | `ec5b495691e10bf4ef6587e7fad99df02a18ff48e44f6b70d5170aaa7b641b05` |

保持 baseline actor 为原 embedded public teacher(mean)，不是 fresh residual / fresh WM / optimizer0 的“SM训练后模型”。whole-pi / STD / Norm / freeze / N1024 保留 CPU 全状态 / 物理 N80 包含性 / one-byte-read + hash + decode guard 保留；预计实际 admitted cache 只打开自己的完整容器一次、mother reopen 0；本轮对此没有模型 I/O。

[Producer guard](<mod4v1_supermimic_bptt_20261102/source_frozen_embedded_teacher_native_v1/producer_teacher_guard_v1.py>) 要求真实 producer TASK、INSTALL_MANIFEST、FINAL 及完整 source：worker 17704 / `7c42986077de62278e33a49f560f22602c9ba4d4e69b058f5f5f8f0893c099c7`，native bridge 13125 / `8211964c2ce3dd78fdb9fee6603ee4a4dcfbca6fa9d7df44f20d3ddb7aaead29`。allstate snapshot / torch.equal 覆盖 save 与 FINAL；已有报告布尔值不是替代品。

唯一已发布历史质量基线是 [原八专家报告](<mod4v1_experts_fulldr_rm70_20261101/MOD4V1_EIGHT_EXPERTS_POSTTRAIN_FINAL_V1.md>)：seed20260928/N80/原750，C878 ascending26/27、descending27/27、standing26/26；S135 27/27、27/27、26/26。新 seeds 各有独立 purpose，不把旧 seed 重评伪装新增。

[独立 seed 汇总:170–219](<mod4v1_supermimic_bptt_20261102/source_good_expert_holdout_subset_v1/good_expert_holdout_runtime_v1.py#L170-L219>) 仅在两个 seed 的真实 closed/waited 结果存在时汇总 conditional per-direction complete/contact（每方向分母54）与 standing no_failure（分母52），Wilson95% 只作描述，不声称跨 seed IID、noninferiority、整体技能90或改善。此报告无新增质量统计。

## 7. 已排除的源码问题与仍未知的 pose/close gate

### 7.1 Phase1 两个 close 问题在这里没有同形缺陷

[Holdout runtime:554](<mod4v1_supermimic_bptt_20261102/source_good_expert_holdout_subset_v1/good_expert_holdout_runtime_v1.py#L554>) 的 put_json 是 canonical 原函数，[canonical:77–84](<mod4v1_supermimic_bptt_20261102/source_a1_frozen_eval_integration_v2/a1_frozen_eval_runtime_v2.py#L77-L84>) 原样序列化字典，不向 binding 再塞 epoch；[holdout runtime:767](<mod4v1_supermimic_bptt_20261102/source_good_expert_holdout_subset_v1/good_expert_holdout_runtime_v1.py#L767>) 调用 `_validate_returned_app_binding(binding, helper)`，两个参数正确。

完整 AppV6→dc4Base pins 已在第 4 节列出，canonical7a092 与新 runtime 是独立 alias，无循环。源码排除两个问题，不等于实际 returned / fast close 已验证；旧 semantic fixtures 和 AST 证明不替代实际 App binding/close。

### 7.2 B1 reset tap 与 holdout pose 是不同校验对象

[Holdout bridge:9–17](<mod4v1_supermimic_bptt_20261102/source_good_expert_holdout_subset_v1/e1_good_expert_holdout_bridge_v1.py#L9-L17>) 调用 pose installer 后安装 FreshDRNominalGuard，并仅将 env.reset 包装为一次计数；没有 Phase1 B1 tap 针对 env._reset_idx 的 expected-identity 校验。

[Pose adapter:132–180](<mod4v1_supermimic_bptt_20261102/source_native_v6_runtime_compat/pose_cache_runtime_adapter_v4.py#L132-L180>) 检查的是 robot root writer/delegates：MethodType、self、真实 MRO 原定义、Articulation / ArticulationData 完整原 SDK source 与 buffer 关系。错误名含 `NOT_ORIGINAL_BOUND_METHOD` / `METHOD_NOT_DEFINED_IN_ACTUAL_MRO`；SDK 两 source pins 为 220628 / `47d96553282b389493e69f691b8dcbfeb98997a5a80b88c2571c60ba8b58cb6d` 与 91275 / `43a31992353ad3a500024d0ec908d5b253ada7a0aac9a1cd2261466e10bda4ff`。仅原 writer 返回后执行原缓存 timestamp 失效；没有增加 reset、physics 或随机 draw。

本地来源链 [E1ResetEvidenceLearningEnv](<mod4v1_experts_fulldr_rm70_20261101/E1_three_variants_GPU_actual_v1/CURB_PROTECTED878_ACTUAL_TYPED_SOURCE_V1/runtime/isaac/mod4/e1_reset_evidence_training_env.py>) → [E1TerrainLearningEnv](<mod4v1_experts_fulldr_rm70_20261101/E1_three_variants_GPU_actual_v1/CURB_PROTECTED878_ACTUAL_TYPED_SOURCE_V1/runtime/isaac/mod4/e1_terrain_training_env.py>) → [E1ChassisTerrainEnv](<mod4v1_experts_fulldr_rm70_20261101/E1_three_variants_GPU_actual_v1/CURB_PROTECTED878_ACTUAL_TYPED_SOURCE_V1/runtime/isaac/mod4/e1_terrain_runtime.py>) → [ChassisPDMod4Env](<mod4v1_experts_fulldr_rm70_20261101/E1_three_variants_GPU_actual_v1/CURB_PROTECTED878_ACTUAL_TYPED_SOURCE_V1/runtime/isaac/mod4/chassis_pd_training_env.py>) 已读取；D7 [ChassisCOMSDK:39–41](<mod4v1_experts_fulldr_rm70_20261101/E1_three_variants_GPU_actual_v1/CURB_PROTECTED878_ACTUAL_TYPED_SOURCE_V1/runtime/isaac/mod4/chassis_com_pose_roundtrip_sdk_adapter.py#L39-L41>) 包装 env._reset_idx，[同文件:99–111](<mod4v1_experts_fulldr_rm70_20261101/E1_three_variants_GPU_actual_v1/CURB_PROTECTED878_ACTUAL_TYPED_SOURCE_V1/runtime/isaac/mod4/chassis_com_pose_roundtrip_sdk_adapter.py#L99-L111>) 包装 mild.audit，而非 robot root writer。局部来源 grep 见原 root-write 调用，没有相应 writer 赋值替换。

**这只排除“B1 同一 source guard 直接出现在 holdout”的说法，不证明 native robot writer 可通过。** 文件存在不是 active 证据；未来实际 installed E1 runtime 全树 / canonical metadata / 实例 MRO / SDK source binding 尚需原准入 gate，记 `UNKNOWN`。旧 fake pose installer 与两 seed fixtures 没有证明这一点；本轮不借用 B2 浮动封件或改 pose。

## 8. Parent / controller / collector：已有什么，实际还缺什么

| 项目 | 当前状态 / 缺件 |
|---|---|
| 两角色 native parent | 第 4 节完整 parent 已存在并 pinned；不是缺 parent 源码。它的 entry 要求 plan enabled/staged=true，当前 source plan 均为 false |
| 资源与关闭语义 | 原 private GPU EX + finite EX、C readonly、empty GPU23500MiB/util0、RAM96GiB、disk25GiB、wait1800、ready900、deadline2400 完整保留；实际 p.wait 在 semantic gate 前，finally 等全部 child wait 后再解 EX。本轮没有实际资源证据 |
| 能通过真实 fixed-plan 的 materializer | **确认缺件：旧 26 集合应为完整真实 27；必须 NEW lineage 保全原 source，不改 seal** |
| 实际输入 source/static 闭包 | 两 selected runtime 的完整原 static bank/deps、full vendor7、原 worker27、原资产、真实 actual0 producer metadata/guard；本轮只核对 source/发布 metadata，不宣称这些已全部物化 |
| 原 teacher admitted cache / actual E1 pose | 真正资源准入后才做原 cache 读取 / 物理包含性 / 实例 binding；当前 UNKNOWN |
| 每独立 seed 的外部一次性 controller | 尚无此 holdout 专用已封完整接口证据：需要绑定新 root、GPU、seed/purpose、精确物化 receipt、原两角色 parent 的一次启动及真实外部 p.wait；不从 Phase1 controller 名称类推适配，也不造 manualreview 布尔门 |
| metadata-only collector | 需要捕获该 root 的实际资源准入、WORKER_ERROR/FINAL/PRE_CLOSE、实际 child waits、parent exit/双 EX 释放、外部 parent wait 与 closed semantic/source grade，并显式区分 execution 与 quality；现有源中没有此新独立 holdout 的一次性 collector 封件 |
| 双 seed 统计入口 | 汇总函数已有；仍需两个独立 purpose 的真实结果和外部等待证据后使用，无结果时不创建得分 |

旧 stage 的固定 receipt 名是 `STAGE_COMPLETE_GOOD_EXPERT_HOLDOUT_V1.json`；source-only materialized=true 仍伴随 source_native_enabled/staged/dispatched=false、parent_launches0，resource_admission/actual_frozen_evaluation/comparison/overall-eight 为 null。单凭该 receipt 不具备真实启动资格。失败时 root 被消耗，维持原一次目的和证据链。

## 9. 本次完成边界

- 完成：真实 entry/import/factory/reset/doneflag 及 teacher 角色核对、两独立 seed 合同、完整 CLI / flat 映射与 pins、原 fixed-plan 集合差异、两 close 源码点排除、reset-tap 与 robot-pose 区分、native unknown 与实际缺件列表。
- 未执行：旧或新物化 CLI、真实 preflight/stage、parent/controller/collector、任何模型与 native 评测。本报告没有新质量结果。
- 最终状态保持 **`NOT_LAUNCH_READY`**。原好专家保持目标继续，和父 B2/V3 实际执行优先级独立；本轮仅报告，不以 SOURCE 测试替代真实准入。
