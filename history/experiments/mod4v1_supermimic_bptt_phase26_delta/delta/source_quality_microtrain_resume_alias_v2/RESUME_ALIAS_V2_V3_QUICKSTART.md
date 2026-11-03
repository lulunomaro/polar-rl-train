# CPU resume alias：修正 fixture V2 / 最小 core V3

仅 NEW SOURCE；本目录没有执行 Torch、训练、SDK、GPU、SSH、原 PT、C、锁、stage 或 dispatch。父级逐个在已有 CPU 环境执行。旧 13 件、旧 811 core、CPU V1 四件及 teacher guard 7c 全保持原封。

## 1. 两次独立证据目的

- **A / CPU V2**：[修正 fixture](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_quality_microtrain_resume_alias_v2/test_quality_microtrain_torch_cpu_v2.py>) 仍严格使用原 811 core。stale JSON 的 attempts / optimizer / verified 同时 3→4，actual=4，checkpoint counts 同步；先通过合法 ordering，再要求真实 payload3 在原 q gate 以精确 counter mismatch 信息被挡。其余 positive、14 负例及 whole decoded-root value/version 检查保留。预期 3→5 与 14 negatives 完成后，旧 alias 仍使整体 RC1；此预期不会被当成 PASS 或改写最终 guard。
- **B / core V3**：[最小新 core](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_quality_microtrain_resume_alias_v2/ctx_reward_full_resume_candidate_v3.py>) 只加 `import copy` 和 `load_full_checkpoint` 的首语句 `payload = copy.deepcopy(payload)`，位于 `ext` 校验及所有模型/optimizer/replay/pending/RNG 操作之前。全 root（含未知字段）一起复制，不筛字段、不切 replay、不额外 decode；后续完整原 body 和其余模块 AST 不变。
- **C / CPU V3**：[同 fixture 对照](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_quality_microtrain_resume_alias_v2/test_quality_microtrain_torch_cpu_v3.py>) 对 A 只改 payload-core PIN、报告 kind/purpose、receipt 文件名。四项逆向还原后源码 bytes 与 A 完全相同。预期 whole source guard 成立；实际结果保持 null，待父级 CPU receipt。

两脚本仍让 full-loader API 收到 retained root 本身，不在测试外部传 working copy。V3 的隔离仅发生在新 core 入口内部。diagnostic deepcopy 仍只用于比对。

## 2. 原 CLI 完整沿用，分开全新 OUT

```bash
# COMMON_SOURCE_DIR 是既有只读小源码所在目录；vendor/deps 沿用原 CPU 环境。
common=(
  --vendor-parent "$VENDOR_PARENT"
  --legacy-support "$COMMON_SOURCE_DIR/test_resume_legacy_torch_cpu_v2.py"
  --fixture "$COMMON_SOURCE_DIR/synthetic_cpu_contract_check.py"
  --bridge-source "$COMMON_SOURCE_DIR/native_supermimic_bridge.py"
  --resume-contracts "$COMMON_SOURCE_DIR/resume_runtime_contracts_v3.py"
  --raw35-source "$COMMON_SOURCE_DIR/command_tracking_torch_candidate_v1.py"
  --microtrain-contracts "$COMMON_SOURCE_DIR/quality_microtrain_contracts_v1.py"
)
# 如原环境使用额外依赖目录，给两条命令相同的 --dependency-path 参数。
python -B test_quality_microtrain_torch_cpu_v2.py "${common[@]}" \
  --payload-core "$COMMON_SOURCE_DIR/ctx_reward_full_resume_candidate_v2.py" \
  --output-dir "$ABSENT_OUT_A"
# A 的整体 RC1 / 完整 receipt 必须原样保留；不是 silent retry 或替换旧 V1。
python -B test_quality_microtrain_torch_cpu_v3.py "${common[@]}" \
  --payload-core ./ctx_reward_full_resume_candidate_v3.py \
  --output-dir "$ABSENT_OUT_C"
```

输出分别为 `QUALITY_MICROTRAIN_TORCH_CPU_RECEIPT_V2.json` / `QUALITY_MICROTRAIN_TORCH_CPU_RECEIPT_V3.json`。两个 OUT 必须互异、事先不存在。无 `--repair`、fallback、working-copy 或降级 guard 开关；CPU 3→5 不计 native expert updates，不宣称质量收益。

## 3. 历史与验证边界

真实 CPU V1 的 source PIN 是最终 753，不是临时 83；83 runner 仅在父级本地 prelaunch guard 被挡，marker/connector/remote 均未启动。真实 V1 positive 的实际 start3/delta2/total5、WM/aux20→22、critic3→5有效，但整体失败：原 decoded source 的 opt_wm/opt_pi step/exp_avg/exp_avg_sq 多处值/版本实测改变，raw bytes 未变；旧 fixture 在 ordering gate 提前异常，14 negatives 未完成。pending alias=True 只证明引用关系，不推定 pending 的值也已改变。

本地 8 个 NEW stdlib/source fixture 使用真实未改 q/base，已验证 ordering 修正后 metadata4 合法、derived target6、payload3 只在预期 mismatch gate 失败；另证 whole-module/load-rest AST、未知 root / memo 语义、copy 异常早于旧 body、旧 13 + CPU V1 四件不变。未导入 Torch，未执行 core load body、旧 20 测试或任何 CPU tensor suite；这些不是实际 V2/V3 的结果。

## 4. Future bindings 仅说明，不安装

原 stage V6 的 166–169 行证实两个 logical aliases：

```text
worker_sources/ctx_reward_full_resume_candidate_v2.py
worker_sources/ctx_reward_learner.py
```

未来单独审阅、单独用途的 source manifest 必须让两处都指向同一完整新 V3 bytes/PIN。旧 bindings/proof 的 811 是 HISTORICAL，不覆盖新 core；本目录的 future bindings 没有更改旧 manifest。旧 embedded-teacher guard 的 hard7c 也未改。legacy executor 当前未因质量收益被选择 native enabled；bound/H32 为独立工作，均未接入。即便 CPU V3 PASS，也只证明该软件 alias 修复，不是 native/skill 通过。
