# CPU 验证 V2：只修实际构造器初始化次数的测试预期

## 当前入口

父代理应执行 [test_resume_legacy_torch_cpu_v2.py](<test_resume_legacy_torch_cpu_v2.py>)，**32048 bytes**，SHA256 `4a4141259410702d2103952a828be31a7ddaf28057272b69bbf8a8bde3109e55`。

CLI 与 [V1 source guide](<CPU_VALIDATION_SOURCE_GUIDE_V1.md>) 完全相同，仅替换脚本文件名并使用新的、从未存在的 `--output-dir`。输出 receipt 名为 `SYNTHETIC_TORCH_RESUME_RECEIPT_V2.json`。V2 不依赖/导入 V1 主脚本；V1 输入、原 core/contracts/raw35 五个 source pin 均不变。

[构造器差异](<CONSTRUCTOR_INITIALIZATION_DIFF_V2.patch>) / [构建记录](<BUILD_CONSTRUCTOR_EXPECTATION_V2.json>) 保留全部更改。

## 1. V1 真实 CPU 失败及原因

父代理已经实际 CPU 执行冻结 [V1 script](<test_resume_legacy_torch_cpu_v1.py>)，其 SHA 仍为 `08c89b3603eb7b32b4eb430a9cde112035ca187695272ee992742ceb147079d7`；[原 V1 CPU receipt](<../reports/LEGACY_A0_A1_FULL_RESUME_CPU_V1.json>) 保留，returncode=1、passed=false。

失败精确在 V1:364：

```python
assert fresh_env.calls == fresh_env.fresh_initializations == 0
```

已读真实 vendor [learner:225–242](<../source_core_review/evidence/learner.py#L225-L242>)：构造时 `_critic_input_dim()` 调用 `_state_info()`；当 `env.state is None`，后者即执行原 `env.init_state()`。因此构造 fresh learner 已有 **1 次**初始化，尚无 collect action；不是 decoded loader 额外 reset。

[实际 decoded loader:520–561](<../source_resume_runtime_v2/ctx_reward_full_resume_candidate_v2.py#L520-L561>) 没有 `init_state()`/`reset()` 调用；本地 AST 检查同样验证这一点。原 core/worker/vendor/contracts 不改。

V1 达到该失败行前，A0 的四模型/四 optimizer/normalizer/replay/counters 与 RNG **状态**比较、实际 teacher value 检查已执行；但 next-draw RNG probe、继续3→4、后续 teacher/cross-view 负例及 A1 分支尚未形成整体通过证据。不能把该局部到达位置改写成整套 PASS。

## 2. V2 唯一功能性修正

V2 在 restored learner 构造后、单次 Pinned read/load 前采集实际初始化快照：

```python
initializations_before_load = fresh_env.fresh_initializations
assert initializations_before_load == 1 and fresh_env.calls == 0
```

完整 loader 后要求 `calls==0`、初始化计数与快照相同且仍为1；continued collect1 后要求 `calls==1`、初始化计数仍为1。运行 receipt 记录 `before_full_load`、`after_full_load`、`after_continued_collect` 三个实际值，而不是只写布尔。

没有放宽 loader/teacher/replay/RNG/counter/dimension/view gate，也没有手动恢复 RNG 或增加 reset。两个版本的24个其他函数 AST 逐一相同，包括 `make_learner`、`pinned_read_and_load`、`assert_all_restored`、`rng_sequence_probe`、`assert_teacher`、`write_own_synthetic`。主 run/main 仅因嵌套函数/版本 receipt 名产生差异。

## 3. 已完成的本地检查

- [原 source-contract 22项](<test_source_contracts_stdlib_v1.py>) 已通过，receipt [LOCAL_STDLIB_SOURCE_CHECK_V1.json](<LOCAL_STDLIB_SOURCE_CHECK_V1.json>)；0 Torch/SDK/PT/native。
- [V2 delta 7项](<test_constructor_correction_stdlib_v2.py>) 全部通过，0.030s，receipt [LOCAL_STDLIB_CONSTRUCTOR_CHECK_V2.json](<LOCAL_STDLIB_CONSTRUCTOR_CHECK_V2.json>)。检查冻结 SHA、import 无 Torch、真实 vendor 调用链、loader 无 reset、三时点快照顺序、其他函数 AST 相同、旧 CPU 失败证据保留。
- V2 已 AST/compile；没有本地执行 Torch。父代理的新 CPU V2 实测独立于这些 source 检查，本文件生成时仍待结果。

## 4. 仍严格保持的软件边界

实际 CPU 脚本仍按 A0/A1 各 collect8/WMaux20/pi3，生成自己的新 synthetic full PT，真实 metadata gate、单次字节读取/SHA/BytesIO decode、decoded full loader，比较4模型/4opts/norm/replay/history/RNG/counts，继续3→4；无 oracle、无新 projection、无 bound/anchor/reward 变化。A0↔A1 shape/view 负例与坏 teacher weights/buffer 负例保留。

所有身份都明确 SYNTHETIC；原 bootstrap/selected PT 不读取。父另 v5 App.close fast-nonreturn 门/pose adapter 分支不参与本脚本，不导入 worker/App/SDK，不等待或修改那些封件。软件通过也不等于 native E0/E2 full restore、真实噪声/DR/physics/getter/cache绑定或技能成功率证明。
