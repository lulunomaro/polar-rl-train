# E3/W35 frozen microbatch staging V2 — 最小完整 close 依赖补齐

## 稳定交付

- CLI：[stage_a1_microbatch_eval_v2.py](<stage_a1_microbatch_eval_v2.py>)：32953 B，SHA256 `9c788fc5435dcbe2af25d13390c2fb008be77c23fbe83104b170d8091cb72952`。
- 新 index：[MICROBATCH_STAGE_INDEX_V2.json](<MICROBATCH_STAGE_INDEX_V2.json>)：4886 B，SHA256 `69688e86528e400f188de3f147614cde5c66f86985adaceed805af800819dc50`。
- 原 13 index entries 完全保留；第 14 项仅为完整 [resume_runtime_contracts_v3.py](<../source_resume_runtime_v2/resume_runtime_contracts_v3.py>)：22337 B，SHA256 `dc4bc67193457a4fb72b125d23fa482cd3d686363bd1a93eb07268f4e4e26cb7`，安装到新 root 同名文件。完整 373 行，未裁模块。
- 原 microbatch runtime 的 13-required-aliases 继续作为 subset；其 schema、kind、purpose、parent、worker、cache/caller、actor、teacher、reward、accepted predicate、N80、seed、DR/physics、原 resource/actual-wait cleanup 全部保持。新 index/stager 的 source receipt kind 独立为 V2；评测 plan 仍为原 microbatch V1 schema。

## 已核实的旧失败

[实际 V1 metadata](<../reports/ACTUAL_FROZEN_E3_W35_BATCH_V1_20261103_010143/CURRENT_METADATA.json>) 的 close traceback 为：runtime `close_original_eval_resources` 468 → `_pinned_module` 95 → 完整 AppV6 helper 23 `import resume_runtime_contracts_v3 as _base` → `ModuleNotFoundError: No module named 'resume_runtime_contracts_v3'`。E3 已写 FINAL 和 160 controls 也不消除 close failure。旧 root/error/FINAL 原样保留；不记成完整执行或效果成功。

## 本次最小变化

1. 14-map index 加入上述完整依赖；原 13 每项 path/relative/bytes/SHA256 均相同。旧封件全部只读。
2. 新 CLI 仅调整旧 `source_mappings`、`metadata_validate`、`preflight_summary`、`stage` 四个函数及常量；其它旧函数 AST 一致。新增 `verify_close_dependency_imports`。
3. preflight 和 stage 后均在原 metadata I/O guards 内执行 **真实完整** AppV6 helper + Base contracts import，不是 stub，不是 AST 截取。核实文件 bytes/SHA、实际 import origin、`helper._base is actual_imported_contracts`、实际常量/函数和 import roots。Base 的全部 imports 为 stdlib；App 的唯一项目依赖是该 Base。
4. flat input 依然按原 Windows provenance path 的 basename 查源；App 的 flat 物理文件名是 `app_close_semantics_v6.py`，装入逻辑名/installed alias 仍为 `app_close_semantics_v5.py`。阶段根使用真实同名完整 Base。所有模块/路径/I/O guards 结束后还原。
5. 原 full microbatch `--validate-plan` 仍执行；无旧 parent 执行，无模型 stat/read/hash/decode，无 C/锁/SDK/GPU 操作。真实 App 实例绑定、实际 close、parent wait 仍为 null/未执行。

## 父代理 native CLI 模板

解包新 bundle 后，`flat` 内应为完整原 13 源加第 14 完整 Base。Index 中 F: 路径仅为 provenance；native 不追踪这些路径。

```bash
PYTHON=/path/to/existing/python
CLI=/path/to/source_stage_a1_microbatch_eval_v2/stage_a1_microbatch_eval_v2.py
FLAT=/path/to/source_stage_a1_microbatch_eval_v2/flat
INDEX=/path/to/source_stage_a1_microbatch_eval_v2/MICROBATCH_STAGE_INDEX_V2.json
OLD_N80='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_NINE_N80_SINGLE_GPU_PARALLEL_V8_20261102_101426_1793585666425343700'
NATIVE_A2='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_A1_RAW35_V6_ADMISSION2_20261102_231937_1793632777470828000'
GROUP=MOD4V1_A1_FROZEN_E3_W35_BATCH_V2_YYYYMMDD_HHMMSS_UNIQUE
NEW_ROOT="/home/lc01/Zonglin Li/zonglin2/tasks/$GROUP"
GPU_UUID=GPU-EXACT_UUID

"$PYTHON" -B "$CLI" \
  --original-group-root "$OLD_N80" \
  --source-dir "$FLAT" --source-index "$INDEX" \
  --native-root "$NATIVE_A2" --new-root "$NEW_ROOT" \
  --group-id "$GROUP" --gpu-uuid "$GPU_UUID" --preflight-only

# 同一不存在的新 root，独立实际 stage 一次；stage 不 dispatch。
"$PYTHON" -B "$CLI" \
  --original-group-root "$OLD_N80" \
  --source-dir "$FLAT" --source-index "$INDEX" \
  --native-root "$NATIVE_A2" --new-root "$NEW_ROOT" \
  --group-id "$GROUP" --gpu-uuid "$GPU_UUID" --stage
```

`--original-group-plan` / `--original-plan` / `--plan` 保留旧可选语义。失败 new root 已消耗，下一次使用另一个全新目的/root。原 V1 两角色的 actual wait、原资源释放/cost-close/error 保留由父主线核对；stager 验证的是训练 A2 的原 closure 元数据，不代替旧 frozen V1 的真实退出或新目的原 admission。新 dispatch 仍独立经过完整原 resource/finite/private gates。

## 测试与界限

[八项增量测试结果](<TEST_RESULTS_CLOSE_DEPENDENCY_V2.json>)：8/8 PASS，2.454 s。包含完整真实 App/Base import、旧 13 缺件的原样 `ModuleNotFoundError` 复现、14-map fake stage 后再次真实 import、新 worker_files 的实际 bytes/SHA、缺件/改字节阻断、其它函数 AST 一致、guard/module restoration。旧 20 测试仅作历史基线，本次未重跑、不合计为 28。

测试 fixture 仅写本 NEW V2 目录，借用旧 fixture 构造函数时仅内存更改其 HERE；原 V1/源模块不改。8 项为 stdlib source/import/fake-filesystem 软件验证；实际 native stage、SDK/RSL 推断、close/wait、C/PT/GPU 操作均 0。它不证明 native close 已通过，更不证明 reward/跟踪有效。paired mother、UID、raw-cache 对齐、相对效果及 overall-eight 仍为 null；W35 combined event 不冒充 moving pass rate。
