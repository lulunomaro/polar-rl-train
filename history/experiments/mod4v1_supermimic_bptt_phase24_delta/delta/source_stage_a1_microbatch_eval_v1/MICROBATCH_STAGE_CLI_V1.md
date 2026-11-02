# E3 + W35 frozen 微批：仅新 root 的 source-stage CLI

## 稳定入口

[stage_a1_microbatch_eval_v1.py](<stage_a1_microbatch_eval_v1.py>)：29335 bytes，SHA256 `dff8143d2464f82f720497ddfe4c241cfd4846e938a9f975962defdaac8c893b`。标准库，无安装项。只接受 `--preflight-only` 或 `--stage`，不启动 parent/worker，不获取 C/锁/SDK/GPU，不操作训练 owner。

[20 项 fixture 结果](<TEST_RESULTS_STDLIB_STAGER_V1.json>)：20/20 PASS，完整 sealed microbatch metadata CLI 被执行；仅 synthetic fixture，不是 actual Linux/native stage、模型加载或技能通过证据。旧封件及 active 源未变。

## 输入与关闭边界

- `--source-dir`：父上传的 **13 个 flat basename**；Windows `path` 仅 provenance，Linux 用 `replace('\\','/').rsplit('/',1)[-1]`。别名取原 index 的 `relative`，各 basename、别名均唯一。
- `--source-index`：原 index 的新位置，原字节 **4529 bytes / SHA256 `42e4714c8adf4361351e052d4006f863452fbad557343cc22f9dbad21951beaf`**，无需重封路径。
- `--original-group-root`：原 NINE N80 runtime group，完整静态树保留。默认读其中原 plan；可用 `--original-group-plan`、`--original-plan` 或 `--plan` 显式提供 portable 原 metadata，先核对原 group/assets/contract/worker-file pins。
- `--native-root`：Admission2 实际已关闭的原 native root。先读其原 `OWNER_PLAN/OWNER_EXIT_ACTUAL/COHORT_FINAL`，要求实际 all-wait/cost-settled/leases-released、无 parent errors，全部 actual GO 有正常 terminal semantic。再核对 E3/W35 原 `PARENT_WAITED_ACTUAL`、实际 successful A1 `production/FINAL.json` 和 full-save receipt。
- 每个 selected `FINAL.json` 物理 byte read 一次，并对同一 bytes 算 SHA。整个 stage **不 stat/open/hash/copy/decode checkpoint**；模型 path 仅 lexical metadata。旧 mother 字段移入 `historical_mother_source`，新 `source_*` 只来自 own actual A1 FINAL checkpoint。
- `--new-root` 必须不存在，且与各输入树互不包含。preflight 不建 root；stage 一次 mkdir + exclusive writes，出错保留 `STAGE_ERROR_MICROBATCH_V1.json`，该 root 已消费，换新 ID/root，不覆盖重试。

原 outer V5 semantic 通过时，其 nested V4 的单一 `original_close_completion_missing` 是已有 strict fast-close substitution 的历史结果，不将它误判为新 worker error。原 actual errors 则原样阻断。

## CLI（父执行；本交付未执行实际 staging）

源码包解开后：根目录有本 CLI、原 index、说明/测试 receipt；`flat_sources/` 是原 13 小源。

```bash
PAYLOAD_DIR='[UPLOADED_SOURCE_BUNDLE_DIR]'
BASE='/home/lc01/Zonglin Li/zonglin2/tasks'
ORIGINAL="$BASE/MOD4V1_NINE_N80_SINGLE_GPU_PARALLEL_V8_20261102_101426_1793585666425343700"
NATIVE="$BASE/MOD4V1_A1_RAW35_V6_ADMISSION2_20261102_231937_1793632777470828000"
GPU_UUID='[ORIGINAL_AVAILABLE_GPU_UUID]'
GROUP_ID="MOD4V1_A1_FROZEN_E3_W35_MB1_$(date +%Y%m%d_%H%M%S)_$(date +%s%N)"
NEW_ROOT="$BASE/$GROUP_ID"

/home/lc01/Zonglin\ Li/zonglin2/run-python.sh -B \
  "$PAYLOAD_DIR/stage_a1_microbatch_eval_v1.py" \
  --original-group-root "$ORIGINAL" \
  --source-dir "$PAYLOAD_DIR/flat_sources" \
  --source-index "$PAYLOAD_DIR/MICROBATCH_STAGE_INDEX_V1.json" \
  --native-root "$NATIVE" --new-root "$NEW_ROOT" \
  --group-id "$GROUP_ID" --gpu-uuid "$GPU_UUID" --preflight-only

# 同一新 ID/root，preflight 通过后，独立显式 stage；它仍不 dispatch。
/home/lc01/Zonglin\ Li/zonglin2/run-python.sh -B \
  "$PAYLOAD_DIR/stage_a1_microbatch_eval_v1.py" \
  --original-group-root "$ORIGINAL" \
  --source-dir "$PAYLOAD_DIR/flat_sources" \
  --source-index "$PAYLOAD_DIR/MICROBATCH_STAGE_INDEX_V1.json" \
  --native-root "$NATIVE" --new-root "$NEW_ROOT" \
  --group-id "$GROUP_ID" --gpu-uuid "$GPU_UUID" --stage
```

## 保留项、metadata 验证与下一道门

- 原完整 non-model static runtime/lib、`.npz/.npy` 静态数组、assets、factories、`ROLE_CONTRACTS`、wrappers 与其它 `worker_files` 保留，重算 bytes/SHA；不裁剪 AST、不执行旧 parent。拒绝 model/state/log/raw/kit/private/cache 等名字先于 DirEntry 类型判断，不跟随 symlink。`.py` 静态 helper 不因 `raw_` 等前缀误删；绝对 `/home`、`/tmp` 祖先不当作相对排除项。
- native E3 的完整 **7 文件 vendor** digest 必须是 `ddf9d6e1744c050fd5298805d125a611673ff22ade52c5177fb02c488ff8f0c0`；`__init__.py` 必须只有 docstring，原字节复制，不补富入口，不裁剪。13 aliases 中的三 vendor 文件必须与 native tree 字节相同。
- preflight 在 flat 小源上执行 **完整原 sealed** `frozen_eval_microbatch_runtime_v1.py --validate-plan`，plan 只在内存提供，不建目标 root；stage 后在实际 installed aliases 上再执行完整 CLI。没有 AST 分段、mock 子集 validator、旧 parent import。
- sealed core 的 `_producer_descriptor` 原有 `Path(checkpoint).resolve()` 会隐式 lstat；此工具**仅在 metadata CLI 的短调用期**把 model suffix 的 resolve 变成 lexical，并阻断 model stat/open 与 budget 文件 I/O，随后恢复。封件原文不变。这不是物理 checkpoint containment 观测；未来 original admission 后，原 cache 的 own-byte/hash/decode 校验照旧。
- 新 plan 保留 8-role 原字典，只请求 **E3 + W35**，6 个明确 deferred；N80/seed/controls/物理 DR/验收分母不缩。没有 3000 步门槛。E3 原 74 rescue + 6 normal 分开；W35 combined events 不冒称 moving rate。
- `comparison/relative_improvement/paired_actual_reference/UID/reference_cache/overall_eight_pass_rate` 仍 null。这是 candidate-only 质量检验准备，不是母本配对效果结论。
- `STAGE_COMPLETE_MICROBATCH_V1.json` 仅源码 stage 完成。未来 dispatch 由父在原 finite EX/private EX、canonical 单 parent、原 GPU/RAM/disk/admission/barrier/deadline/实际 close-wait 门下另行执行。当前工具的 `resource_admission`、`actual_frozen_evaluation` 仍 null，训练原成本与 error 账不改。
