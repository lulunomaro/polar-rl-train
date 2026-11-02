# A1 native V5：stage-only 与 once-only dispatch 分离

本目录仅源码工具；默认只读。此代理没有运行真实 stage/dispatch，没有读取 C/锁/GPU/SDK/原 PT。父代理审读/执行。V5 code seal 固定为 `59e5cb530fbf2e2066856d9ba594afec151f4c5b512382a8905671586fe993a7`。

## 1. 显式 source-index（输入 root 中仅放小源码，不放模型）

```json
{
  "kind": "SEALED_A1_NATIVE_V5_SOURCE_INDEX_V1",
  "sealed": true,
  "v5_code_seal_SHA": "59e5cb530fbf2e2066856d9ba594afec151f4c5b512382a8905671586fe993a7",
  "files": [
    {"source_relative": "source_app_close_semantics_v5/worker_supermimic_bptt_app_close_candidate_v5.py", "install_relative": "worker_sources/worker_supermimic_bptt_app_close_candidate_v5.py", "SHA": "7c42986077de62278e33a49f560f22602c9ba4d4e69b058f5f5f8f0893c099c7", "bytes": 17704}
  ]
}
```

`files` 必须列齐以下 14 个 install_relative（上例仅示一行）。`source_relative` 相对显式 `--source-dir`，允许重排输入包路径；所有 SHA/bytes 从**这批小源码**核对，不触碰 teacher。禁止 symlink/absolute/../模型/预算状态路径。

| install_relative | 对应封版源码 |
|---|---|
| `three_slot_common_v1.py` | 原 helper eaf6aa1a…，字节原样；放输入包 `authority_helpers/` 等不含 budget 的路径 |
| `single_writer72_authority_V85M_source.py` | 原 helper ceba8067…，字节原样 |
| `shared_gpu_admission_v1.py` | 原 helper 0ed3ca0e…，字节原样 |
| `supermimic_original_owner_shared_app_close_candidate_v5.py` | V5 shared owner 0f161804… / 12478 B |
| `worker_sources/worker_supermimic_bptt_app_close_candidate_v5.py` | V5 worker 7c429860… / 17704 B |
| `worker_sources/app_close_semantics_v5.py` | d64732c9… / 24782 B |
| `worker_sources/resume_runtime_app_close_v5.py` | 208c4774… / 870 B |
| `worker_sources/native_supermimic_bridge.py` | 原 bridge 8211964c… |
| `worker_sources/ctx_reward_full_resume_candidate_v2.py` | 8116ea35… |
| `worker_sources/resume_runtime_contracts_v3.py` | dc4bc671… |
| `worker_sources/resume_runtime_install_hook_v4.py` | 85f2fd4e… |
| `worker_sources/command_tracking_torch_candidate_v1.py` | bb7555ff… |
| `worker_sources/original_role_command_binding_candidate_v2.py` | 348d0a09… |
| `worker_sources/pose_cache_runtime_adapter_v3.py` | 73145a1c… / 16757 B |

每个完整 SHA 已在 stager `FIXED_PINS` 中强校验。自动生成根部四个 gate/helper 镜像；payload core 自动同时安装为 `ctx_reward_full_resume_candidate_v2.py` 与 `ctx_reward_learner.py`，二者字节相同。非 shared owner可选，不作运行入口。

## 2. 只读 preflight，再 stage（两个命令仅最后参数不同）

```bash
PYTHON=/absolute/existing/python
RUN=MOD4V1_A1_RAW35_V5_NEW_UNIQUE_ID
ROOT=/absolute/original/tasks/$RUN
INPUT=/absolute/new_small_source_bundle

$PYTHON -B stage_a1_native_v5.py \
  --source-plan /absolute/read_only/original/SOURCE_PLAN.json \
  --source-dir "$INPUT" --source-index "$INPUT/SEALED_A1_SOURCE_INDEX_V5.json" \
  --vendor-dir /absolute/existing/supermimic_vendor_v2 \
  --deps-dir /absolute/existing/sm_deps \
  --assets-dir /absolute/existing/pinned_assets \
  --new-root "$ROOT" --run-id "$RUN" --target-bptt-steps 3000

# 父审读输出后，以同一输入执行；仅新增 --stage
$PYTHON -B stage_a1_native_v5.py \
  --source-plan /absolute/read_only/original/SOURCE_PLAN.json \
  --source-dir "$INPUT" --source-index "$INPUT/SEALED_A1_SOURCE_INDEX_V5.json" \
  --vendor-dir /absolute/existing/supermimic_vendor_v2 \
  --deps-dir /absolute/existing/sm_deps --assets-dir /absolute/existing/pinned_assets \
  --new-root "$ROOT" --run-id "$RUN" --target-bptt-steps 3000 --stage
```

`--source-plan` 只读原八角色元数据，保留 teacher path/SHA/bytes、seed、base_root、原 `family=formal/w35/e1`。另设 `algorithm_family=a1_raw35_legacy_v1`。顺序固定 E3/W35/C113/C878/S135/S50/E0/E2，H1 排除，全部 `A1_RAW35_FRESH` / N1024 / H16 / hist10 / 9 counts 期望0。无 A0 4912 偏移。命令/传感仍 legacy held+aux，非 B/C/D 改善声明。

stage 先创建 SCHEDULE_PUBLIC 配置后才做 owner `verify_sources` 的 AST 选取校验（C 用 sentinel，不导入 authority/owner）。新根目录独占；失败保留 STAGE_ERROR，不覆盖/修补重跑。成功最后写 `STAGE_COMPLETE_V5.json`；内含 root/角色安装 manifest SHA、计划/schedule SHA。资产必须含原 USD/contract，SHA 2c421a8e…/bae3203a…；静态 npz/npy 保留。模型/production/kit/private/cache/log/jsonl/预算状态在 DirEntry 分类之前跳过。

## 3. 独立 dispatch：父先写新 purpose marker

```json
{
  "kind": "PARENT_APPROVED_NEW_A1_NATIVE_V5_DISPATCH_ONCE",
  "run_id": "MOD4V1_A1_RAW35_V5_NEW_UNIQUE_ID",
  "root": "/absolute/original/tasks/MOD4V1_A1_RAW35_V5_NEW_UNIQUE_ID",
  "stage_complete_SHA": "[SHA256_OF_STAGE_COMPLETE_BYTES]",
  "owner_relative": "supermimic_original_owner_shared_app_close_candidate_v5.py",
  "dispatch_token": "[NEW_UNIQUE_PARENT_PURPOSE_TOKEN_AT_LEAST_16_CHARS]",
  "actual_native_launch_requested": true,
  "original_authority_gates_required": true,
  "no_foreign_owner_signal_or_C_steal": true
}
```

```bash
# 缺 --dispatch 时只读；父审读后追加 --dispatch 才一次 Popen
$PYTHON -B dispatch_a1_native_v5_once.py \
  --stage-root "$ROOT" --run-id "$RUN" \
  --stage-complete-sha '[EXACT_STAGE_COMPLETE_SHA]' \
  --parent-marker /absolute/new/PARENT_DISPATCH_MARKER.json \
  --python-runner /absolute/existing/original/python
```

独立 dispatch 再核全部 manifests/SHA、无 stage error、无 owner purpose、无各角色 TASK/GO/production，父 marker 绑定 exact root/run/stage/owner。`--dispatch` 仅独占 purpose marker 一次 + 原 shared V5 owner一次 Popen；不运行新 ledger/资源锁，不读 C/GPU，不 signal foreign owner；原 owner 自行执行原 C/locks/reserve/3900/3600/300/1800 gates。Popen 成功只是 dispatched，不代表 admitted/GO/训练/技能通过。
