# V6 新窗口：已封源码映射、双 CLI 与父代理小 payload

## 当前交付状态

- [V4 pose adapter](<pose_cache_runtime_adapter_v4.py>)：18161 bytes，SHA256 `7357827a72a03f6300ce3f7c6da3ad2a05a551480a1aad04a91dbaac4a497e2f`。
- [App V6 helper](<../source_app_close_runtime_compat_v6/app_close_semantics_v6.py>)：27769 bytes，SHA256 `3d2d75196fb98fdb45c80a79b5b8bb69873e7c0c2c0b0f6f6610eb11a8c63c39`；父代理已确认稳定 pin。其逻辑安装名保持 `app_close_semantics_v5.py`，源码版本为 `V6_PUBLISHED_SIMULATIONAPP_EXPORT_ALIASES`。
- [V6 stage CLI](<stage_a1_native_v6.py>)：26059 bytes，SHA256 `9c68f5f7c59a5fc0d2ea9cc8d7dcc5eacd3577f795c9f0bdad28bed5ce8aeef0`。
- [V6 dispatch-once CLI](<dispatch_a1_native_v6_once.py>)：9465 bytes，SHA256 `7ecab0e372064c0c5ceaccc8f02a79350e9c7a538e3fb158a5426a04dfce38ae`。
- [66 项 pose shadow 收据](<CPU_TEST_RESULTS_V4.json>) 与 [37 项 stage/fake/mock 收据](<TEST_RESULTS_STDLIB_STAGE_DISPATCH_V6.json>) 全部 PASS；共 103 个测试方法，不再叠加其历史 54/29 子集。两 CLI 的 `--help` 已实际验证。
- [37 项测试源](<test_stage_dispatch_stdlib_v6.py>)：20830 bytes，SHA256 `9e0c84ffdeb1ea789b4ed0eeccdffd93de79204f5e1c68987c1b0c5199eceb7e`。真实 14 个小源 bytes/SHA 已逐个比对，非 mock golden pin。
- [静态源码/历史未知项证据](<RUNTIME_SOURCE_EVIDENCE_V6.json>)：SHA256 `094e89086a28d3d17ffdf48e0b2ba06375391b8d6bd15a74c1524dd36989544c`；[详细证据与最小计划](<V6_RUNTIME_SOURCE_EVIDENCE_AND_MINIMAL_PLAN.md>) 中“App helper 待 relay”是早先时间点状态，本文件的稳定 pin 与下方完整映射将其取代。历史 raw timestamp type/value、实际 App module 与新 native 回执仍为 UNKNOWN。

本专项只构建源码/小源包、stdlib shadow/AST/fake fixtures。未实际 native stage/dispatch/retry，未 SSH、SDK/Torch、GPU、原 PT、C/锁、Git。fixture 中调用的 `stage()` 只复制人工假静态文件；`Popen` 总被 mock。

## 14 项 source map

下表均是逻辑安装路径配置；仅两项 SHA 变化，其余十二项保持已封原 bytes。

| 逻辑安装路径 | 小源包中的实际源文件 | SHA256 |
|---|---|---|
| `three_slot_common_v1.py` | `sealed_source/three_slot_common_v1.py` | `eaf6aa1a06d2a49570eff54af5447395210c6de9f3a9c43d566d1adad4e53044` |
| `single_writer72_authority_V85M_source.py` | `sealed_source/single_writer72_authority_V85M_source.py` | `ceba8067ceaffa8f2a978a0165b1ef06fc28b980d5f9da29ba03c760d9c1d98c` |
| `shared_gpu_admission_v1.py` | `sealed_source/shared_gpu_admission_v1.py` | `0ed3ca0e1f449a4c63deb1d6ba4f9037672438e1def74ffbb654efa3a7c3c42d` |
| `supermimic_original_owner_shared_app_close_candidate_v5.py` | `sealed_source/supermimic_original_owner_shared_app_close_candidate_v5.py` | `0f1618046d5751879f0ce40ff4b7424c83303ed1f61066521215c1d40eb76619` |
| `worker_sources/worker_supermimic_bptt_app_close_candidate_v5.py` | `sealed_source/worker_supermimic_bptt_app_close_candidate_v5.py` | `7c42986077de62278e33a49f560f22602c9ba4d4e69b058f5f5f8f0893c099c7` |
| `worker_sources/resume_runtime_app_close_v5.py` | `sealed_source/resume_runtime_app_close_v5.py` | `208c4774f1033627c01253afe45ade9c426fdd9be70e76328125a59a80a20c5a` |
| `worker_sources/app_close_semantics_v5.py` | **`sealed_source/app_close_semantics_v6.py`** | **`3d2d75196fb98fdb45c80a79b5b8bb69873e7c0c2c0b0f6f6610eb11a8c63c39`** |
| `worker_sources/native_supermimic_bridge.py` | `sealed_source/native_supermimic_bridge.py` | `8211964c2ce3dd78fdb9fee6603ee4a4dcfbca6fa9d7df44f20d3ddb7aaead29` |
| `worker_sources/ctx_reward_full_resume_candidate_v2.py` | `sealed_source/ctx_reward_full_resume_candidate_v2.py` | `8116ea358dfe32e0efd568d00661ab1e13b602d267ea4b580ced04ec39e898ac` |
| `worker_sources/resume_runtime_contracts_v3.py` | `sealed_source/resume_runtime_contracts_v3.py` | `dc4bc67193457a4fb72b125d23fa482cd3d686363bd1a93eb07268f4e4e26cb7` |
| `worker_sources/resume_runtime_install_hook_v4.py` | `sealed_source/resume_runtime_install_hook_v4.py` | `85f2fd4e45802eb94eb2311cf69410e5b20b1264255a2b0b562aa3c67f87405e` |
| `worker_sources/command_tracking_torch_candidate_v1.py` | `sealed_source/command_tracking_torch_candidate_v1.py` | `bb7555ff2de598677ea6cfe5dadefe0a9cfe37d37661635d186bcb14c1df2223` |
| `worker_sources/original_role_command_binding_candidate_v2.py` | `sealed_source/original_role_command_binding_candidate_v2.py` | `348d0a09911a36ca9007ab5bb15f0b3e82bac3ab554cb8d73c62f8f0b5a763ea` |
| `worker_sources/pose_cache_runtime_adapter_v3.py` | **`sealed_source/pose_cache_runtime_adapter_v4.py`** | **`7357827a72a03f6300ce3f7c6da3ad2a05a551480a1aad04a91dbaac4a497e2f`** |

原 payload core 同 bytes 安装到 `worker_sources/ctx_reward_learner.py` alias；V3 contracts、V4 hook、V5 shim 与逻辑 App helper 同 bytes 镜像到新 root，以满足 unchanged owner 的 import 路径。

新的 source index kind 是 `SEALED_A1_NATIVE_V6_SOURCE_INDEX_V1`。`v5_abi_code_seal_SHA=59e5cb530fbf2e2066856d9ba594afec151f4c5b512382a8905671586fe993a7` 仅是历史 V5 bundle/ABI 参考；不声称新 helper 或新 pose adapter 属于该旧 bundle。完整 V6 mapping 具有自己的 index SHA、实际源文件名和 replacement 列表。

## 父代理：小源包构建命令

以下命令只构建本地小源包。当前专项已经执行一次 seal/payload 后，不应再次运行覆盖；输出存在会直接停止。实际字节数/SHA 见生成的 receipt。

```powershell
& 'C:\Users\lulu\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe' -B .\seal_stage_sources_v6.py
& 'C:\Users\lulu\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe' -B .\build_parent_payload_v6.py
```

产物结构：

```text
V6_PARENT_SMALL_SOURCE_PAYLOAD.zip
  stage_a1_native_v6.py
  dispatch_a1_native_v6_once.py
  V6_STAGE_CLI_AND_STATUS.md
  V6_SOURCE_PROVENANCE_AND_SEAL.json
  PARENT_SOURCE_PAYLOAD_MANIFEST_V6.json
  _SOURCE_INPUT/
    SEALED_A1_SOURCE_INDEX_V6.json
    sealed_source/   # 恰好14个小.py文件
```

将该包放在新 native root 之外。它不包含 role runtime 静态树、SDK、sm_deps、vendor、模型或预算状态。

## 父代理：未来新 root 的 stage-only CLI

所有路径均由父代理使用已存在的原静态输入显式提供。`ORIGINAL_PLAN_JSON` 是原八角色 metadata-only source plan；不读取 teacher PT。`INPUT` 是解包后的独立小源目录，不能是新 root。`NEW_ROOT` 尚不存在且 basename 必须等于新的 run-id。

```bash
RUN_ID=MOD4V1_A1_RAW35_V6_[UNUSED_UNIQUE_SUFFIX]
NEW_ROOT="[TASKS_DIR]/$RUN_ID"
INPUT="[INDEPENDENT_V6_SOURCE_INPUT]"
PYTHON="[EXISTING_ORIGINAL_PYTHON]"

# 默认只读prepare，不创建native root、GO或owner
"$PYTHON" -B "$INPUT/stage_a1_native_v6.py" \
  --template-plan "[ORIGINAL_PLAN_JSON]" \
  --source-dir "$INPUT/_SOURCE_INPUT" \
  --source-index "$INPUT/_SOURCE_INPUT/SEALED_A1_SOURCE_INDEX_V6.json" \
  --vendor-dir "[EXISTING_SUPERMIMIC_VENDOR_V2]" \
  --sm-deps-dir "[EXISTING_SM_DEPS]" \
  --assets-dir "[EXISTING_ORIGINAL_PINNED_ASSETS]" \
  --new-root "$NEW_ROOT" --run-id "$RUN_ID"

# 父代理决定实际stage时，原参数完全不变，仅添加 --stage
```

显式 `--stage` 也不启动 owner。静态树白名单仍是 runtime/lib/original_field/new_assets/assets/producer、top-level py 和原指定 JSON；在分类/stat 之前跳过 model/production/kit/private/cache/log/jsonl/PT/budget 等名字。bank 的 npz/npy 保留。原资产 SHA 为 `2c421a8ec66e425ee6e47341ed0803f2c7e84f1f50afcc726572027ef6566ef3` 与 `bae3203a7c30f75e29c20c0b0d0e215af5edfc7dbeacb9ebc5310f7867c98755`。

Stage 最后才生成 `STAGE_COMPLETE_V6.json`；失败保留 `STAGE_ERROR_V6.json`，不在原 root 重放。`SCHEDULE_PUBLIC.json` 在原 owner 导入之前生成，它只是原 helper 配置，不是 ledger。source-only owner preflight 只运行原 `require/verify_sources` AST，C 使用 identity sentinel，不访问真实 C。

## 父代理：单独 dispatch-once

父 marker 绑定实际新 root/run、`STAGE_COMPLETE_V6.json` 的真实 SHA 及 unchanged shared owner：

```json
{
  "kind": "PARENT_APPROVED_NEW_A1_NATIVE_V6_DISPATCH_ONCE",
  "root": "[EXACT_CANONICAL_NEW_ROOT]",
  "run_id": "MOD4V1_A1_RAW35_V6_[UNUSED_UNIQUE_SUFFIX]",
  "stage_complete_SHA": "[ACTUAL_NEW_STAGE_COMPLETE_SHA256]",
  "owner_relative": "supermimic_original_owner_shared_app_close_candidate_v5.py",
  "dispatch_token": "[NEW_SINGLE_PURPOSE_TOKEN_AT_LEAST_16_CHARS]",
  "actual_native_launch_requested": true,
  "original_authority_gates_required": true,
  "no_foreign_owner_signal_or_C_steal": true
}
```

```bash
# 默认仅复核metadata/完整source manifests及父marker，不Popen
"$PYTHON" -B "$INPUT/dispatch_a1_native_v6_once.py" \
  --stage-root "$NEW_ROOT" --run-id "$RUN_ID" \
  --stage-complete-sha "[ACTUAL_NEW_STAGE_COMPLETE_SHA256]" \
  --parent-marker "[NEW_PARENT_MARKER_JSON]" \
  --python-runner "$PYTHON"

# 父代理决定实际启动时，原参数完全不变，仅添加 --dispatch
```

Dispatch 先排除 owner 已启动、任一 GO/TASK/production、stage 失败或 purpose 已消耗；然后独占创建 `PARENT_DISPATCH_CONSUMED_V6.json`，只 `Popen` 一次原 shared owner。这个文件是目的标记，不是新的 resource lock/ledger。真实 admission、C/account、原锁/reserve、GPU/asset gate、3900/3600/300/1800 时限完全由原 owner 执行。

## 不变项与仍待 native 证据

角色顺序仍为 E3/W35/C113/C878/S135/S50/E0/E2，H1 排除。A1_RAW35_FRESH、九计数从零、N1024/H16/history10/至少3000，原 seed/teacher metadata/base_root/native family 均保留。只换两项 runtime compatibility source；不混入原 A0=4912，不加 E2 tracking/sensor exactness/bound/anchor/reward 修复、不缩 DR 或验收。

后续新 native 才能产生实际 timestamp type/value tag、robot/data/MRO binding、App 实际 module/MRO/源码 pin、close witness、生产计数与目标完成证据。103 项软件测试或 source ZIP 均不是 native 成功、原技能通过率、90% 声明。
