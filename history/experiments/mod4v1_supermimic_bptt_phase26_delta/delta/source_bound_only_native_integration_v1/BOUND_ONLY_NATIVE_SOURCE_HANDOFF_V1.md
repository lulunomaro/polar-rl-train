# E3/W35 ZERO_UPDATE bound-only：独立 native-capable 源封件

## 1. 状态与用途

本封件实现 **SOURCE 候选**，`source_native_capable=true`；本子代理的 `actual_staged=false`、`actual_native_enabled=false`、native/Torch/PT/raw/SSH/GPU/C/锁/Git 操作数为 0。只执行了 stdlib 构建、真实完整模块导入、AST 与自有假源测试。原 V1 已封件文件保持原字节。新用途是 **先测零更新 postprocess，再另立 bounded 短训练用途**；这里的 probe BPTT、训练、pi/wm/aux/critic optimizer 更新均为 0。

新标签在 [helper:15–26](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_bound_only_native_integration_v1/bound_only_native_helper_v1.py#L15-L26>)：

```text
policy_variant = A1_RAW35_ZERO_UPDATE_BOUND_ONLY_TANH_NATIVE_PROBE_V1
purpose = FROZEN_ZERO_UPDATE_BOUND_ONLY_E3_W35_NATIVE_N80_V1
receipt_kind = FROZEN_ZERO_UPDATE_BOUND_ONLY_NATIVE_MEAN_RECEIPT_V1
plan_kind = FROZEN_ZERO_UPDATE_BOUND_ONLY_NATIVE_PLAN_V1
task_kind = FROZEN_ZERO_UPDATE_BOUND_ONLY_N80_TASK_V1
integration = FROZEN_ZERO_UPDATE_BOUND_ONLY_NATIVE_INTEGRATION_V1
effective_actor = OWN_A1_TEACHER_PLUS_POINT05_TANH_RESIDUAL_ZERO_UPDATE
```

**新 helper/route 的 `native_enabled=True` 是被显式选中的 route capability，不是已经运行的事实。** 原 V1 的 False 字段保持原义；本版字段并未借旧 False 伪称已启用。metadata CLI、preflight、stage receipt 另列 `actual_native_enabled=false`；`staged=true` 仅表示静态文件独占复制成功。原资格、外部执行父进程实际 p.wait、GPU/private-EX/global-finite-EX、C readonly、原关闭证明必须由父方未来实取。完整字段见 [字段合同](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_bound_only_native_integration_v1/BOUND_ONLY_NATIVE_FIELDS_CONTRACT_V1.json>)。

## 2. effective actor 与 storage 身份严格分开

保存容器仍是已合格原 A1 whole checkpoint，E3 SHA `a4c56390b4c549ba8bfb808a63206c0816ad50e8c9659dc053f98cc66b3c8127`、W35 SHA `b2f2878ff9aa04ddcd283fe71f5b5924b1bff78b3f04118cfa689244b0665cff`，来源是已读小 metadata；本子代理未 stat/read/hash/decode 这些 PT。原 family/view/variant、历史 producer BPTT 2182/1973 与原 bootstrap teacher 身份仍作为 storage provenance。effective actor 则明确为：

```python
base = teacher(original_noisy_delayed_raw35, stochastic_output=False)
delta = residual(original_history10, known_command3)
action = clamp(base + 0.05 * tanh(delta), -6, 6)
```

唯一动作数学在 [forward:95–112](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_bound_only_native_integration_v1/bound_only_native_helper_v1.py#L95-L112>)。相对原 V1，`make_bound_only_wrapper`、`build_bound_only_mean_policy`、`BoundOnlyFrozenMean`、`BoundOnlyPolicyCaller`、`ReadOnlyActionStatistics` 五个函数/类的 AST 逐字结构相同；只新增版号/capability/validator 标签语义，动作数学不再调整。

- 总 clip 前残差每个分量实数界为 0.05；经过相同 clip 后，相对 **clipped teacher** 的每分量界也为 0.05。
- 这不是相对旧 unbounded candidate 的 0.05 界，也不是 L2 向量界。`delta=1000, teacher=0` 时，旧 action=6，新 action≈0.05，差约 5.95。
- 原 V1 父方软件 CPU 已见 4×N80 独立公式误差 0；float32 teacher-component max `0.050000011920928955` 按 `1e-6` 容差通过；相对旧 unbounded 的 `0.954431414604187` 是同输入动作差，不是技能收益。该证据保留于 [V1 CPU 元数据](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/reports/BOUND_ONLY_FROZEN_CPU_V1.json>)，不冒充本新 native 版本已运行。

## 3. actor API 风险与最小接法

原 wrapper 构造器会清零 residual 最后一层；因此新 subclass **继承原 ctor 并在完整 strict load 之前构造一次**。fresh cache 在构造开始即 claim `_built=True`，失败也不清回 False；不重包已加载 actor、不重建已用 cache、不 fallback 到旧 mean。

- [完整构造/strict load:163–215](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_bound_only_native_integration_v1/bound_only_native_helper_v1.py#L163-L215>) 保留原 1ea4 cache、全部 pi key/shape/dtype/finite/value、norm/teacher、whole CPU root、eval/no-grad/device 守卫；没有 learner/optimizer/WM/replay 恢复。
- [mean 与边界:115–160](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_bound_only_native_integration_v1/bound_only_native_helper_v1.py#L115-L160>) 继承原 act 函数对象；[caller:218–240](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_bound_only_native_integration_v1/bound_only_native_helper_v1.py#L218-L240>) 要求同字节 Base37927/7a092 `OriginalEpisodeBoundary`，原 true T/Tr、真实 step→下一次 act、原 noisy/delayed35/history10/current-frame padding/knowncmd 行为保留。
- [新 route:28–56](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_bound_only_native_integration_v1/bound_only_native_route_v1.py#L28-L56>) 用 `caller_type` 虚工厂。新 runtime adapter [446–467](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_bound_only_native_integration_v1/bound_only_native_runtime_v1.py#L446-L467>) 继承该 actor，不调用原 actor 再 build/包第二次。check/check_actor/whole-root guards 保持原方法对象。
- 新 runtime→新 route→**canonical original** core；canonical core 从未被新 runtime 覆盖。真实完整导入已经验证没有同名循环，未用 stub 放行。
- [producer 源守卫:125–141](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_bound_only_native_integration_v1/producer_bound_probe_guard_v1.py#L125-L141>) 从原 TASK/INSTALL_MANIFEST/完整 worker+bridge byte PIN 重导出 teacher 完整 state_dict snapshot/equal 机制；不接受自行声明的 True。该机制与已合格 teacher-native 原版 AST 相同，来源证明不是本子代理新建 GPU trace。

## 4. 完整 17 项映射及关闭链

[完整 index](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_bound_only_native_integration_v1/BOUND_ONLY_NATIVE_STAGE_INDEX_V1.json>) 17 项；相对原 14 项仅替换 parent/runtime/formal 三条 route、加 native helper/native route/producer guard；其余 **11 项原字节不动**。原其他 worker_files、所有原 static/runtime/vendor 依赖继续完整复制。关键保留：

|逻辑别名|bytes|SHA256|
|---|---:|---|
|canonical core|37927|7a092364cf63e9621481dc0a5554b56a22e4412cf89870c3db9a124864074b2e|
|whole A1 cache|19226|1ea4bcfa1081d63d0da2136fedf8c9fafa508d7bb2155095352da496327e4a21|
|AppV6 logical v5 alias|27769|3d2d75196fb98fdb45c80a79b5b8bb69873e7c0c2c0b0f6f6610eb11a8c63c39|
|完整 Base v3|22337|dc4bc67193457a4fb72b125d23fa482cd3d686363bd1a93eb07268f4e4e26cb7|

真实完整 AppV6→Base 导入见 [stager:358–400](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_bound_only_native_integration_v1/stage_bound_only_native_v1.py#L358-L400>)。新 [parent 结束包装:80–84](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_bound_only_native_integration_v1/single_gpu_e3_w35_bound_only_parent_v1.py#L80-L84>) 在完整原 main/finally 之后才做 source grade；原 private EX/global finite EX/C readonly/1800 等待与 deadline/actual p.wait/释放顺序保留。parent main、formal main AST 仅标签白名单变化；原 error/close 函数及 source-cache/close 语义块相同。App.close 原调用及 fast-close intent 并未改动。

新外层 source-cache key 为 `bound_only_probe`，历史 BPTT 别名明确仅属 source producer；[语义门:470–547](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_bound_only_native_integration_v1/bound_only_native_runtime_v1.py#L470-L547>) 排除旧 unbounded/teacher/V1 False 标签、synthetic receipt、更新计数或边界缺口、原 error、非零 RC、关闭证据缺失。最终 [closed-source grade:549–605](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_bound_only_native_integration_v1/bound_only_native_runtime_v1.py#L549-L605>) 仍将 `qualified_bound_probe_execution=null`，外部执行父进程 p.wait 证明在此不生成。

## 5. 父方未来独立 preflight / stage CLI（本子代理未对实际树运行）

把 index 的 17 个 `entry.path` 对应 **Python 源文件完整字节** 上传到一个 exclusive 新 `SOURCE_FLAT`，使用原 provenance path 的 **basename**，不是 `relative` 的重命名 basename。例如 App 源文件 basename 是 v6，而安装逻辑 alias 是 v5；formal 源 basename 与安装 alias 也不同。index 中 Windows 路径只留作 provenance，远端 source_mappings 不解引用它们。另上传本版 stager 与 index。上传代码源不接触模型。

```bash
# 以下均为父方未来选择的独立 NEW root；SOURCE_FLAT 应含 17 个完整源 basename。
PYTHONDONTWRITEBYTECODE=1 "$PYTHON" -S -B "$SOURCE_FLAT/stage_bound_only_native_v1.py" \
  --original-group-root "$ORIGINAL_GROUP" --original-group-plan "$ORIGINAL_GROUP/GROUP_PLAN.json" \
  --source-dir "$SOURCE_FLAT" --source-index "$SOURCE_FLAT/BOUND_ONLY_NATIVE_STAGE_INDEX_V1.json" \
  --native-root "$CLOSED_A1_NATIVE_ROOT" --new-root "$NEW_BOUND_GROUP" \
  --group-id "$NEW_BOUND_GROUP_ID" --gpu-uuid "$GPU_UUID" --preflight-only

# 仅在父方选择后独立执行；复制静态源/资产，仍不 dispatch。
PYTHONDONTWRITEBYTECODE=1 "$PYTHON" -S -B "$SOURCE_FLAT/stage_bound_only_native_v1.py" \
  --original-group-root "$ORIGINAL_GROUP" --original-group-plan "$ORIGINAL_GROUP/GROUP_PLAN.json" \
  --source-dir "$SOURCE_FLAT" --source-index "$SOURCE_FLAT/BOUND_ONLY_NATIVE_STAGE_INDEX_V1.json" \
  --native-root "$CLOSED_A1_NATIVE_ROOT" --new-root "$NEW_BOUND_GROUP" \
  --group-id "$NEW_BOUND_GROUP_ID" --gpu-uuid "$GPU_UUID" --stage
```

默认统计 off。若父方明确选择，两个 CLI 都加 `--collect-action-statistics`。统计只在同一 forward 的已算 teacher/delta/action 上读 scalar；额外 teacher/residual/obs/RNG/physics 调用为 0；host sync 增加 walltime 的可能性不标作 simtime。实现见 [statistics:41–92](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_bound_only_native_integration_v1/bound_only_native_helper_v1.py#L41-L92>)。

[metadata 校验:403–454](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_bound_only_native_integration_v1/stage_bound_only_native_v1.py#L403-L454>) 执行完整 metadata CLI；guard 在 finally 还原 Path/open/stat/modules，模型 resolve 仅 lexical，不 stat/read/hash/decode PT，不触 budget/C/锁。preflight 不建 new root。stage 独占 new root，唯一成功 receipt 为 `STAGE_COMPLETE_BOUND_ONLY_NATIVE_V1.json`；失败写 `STAGE_ERROR_BOUND_ONLY_NATIVE_V1.json` 并消费 root，无同 root retry。实现见 [stage:476–506](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_bound_only_native_integration_v1/stage_bound_only_native_v1.py#L476-L506>)。封件不自动 dispatch，也不提供冒充实际准入的 receipt。

父方未来独立软件 CPU 可运行 [新 native-capable 自有 synthetic 脚本](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_bound_only_native_integration_v1/remote_cpu_bound_only_native_synthetic_v1.py>)：

```bash
# 使用原 Torch/RSL/TensorDict/vendor/wrapper 软件依赖；不启动 SDK。
# PYTHONPATH 至少包括 SOURCE_FLAT；沿原 V1 父方 CPU 环境提供其余依赖。
"$CPU_PYTHON" -B "$SOURCE_FLAT/remote_cpu_bound_only_native_synthetic_v1.py" \
  --new-output "$NEW_UNUSED_OWN_SYNTHETIC_CPU_OUTPUT"
```

此脚本另行上传，不在 17 个 runtime mapping 内。只保存/读取自身新建 synthetic 全容器；每个独立 case 一个 cache 一次 decode，STD 与 norm 负例分隔、不 rearm、不读取原模型；本子代理未执行 Torch 脚本。

## 6. 测试、范围与仍为空的事实

[新自测](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_bound_only_native_integration_v1/test_bound_only_native_stdlib_v1.py>) 最终 **22/22 PASS、0 failures、0 errors，10.6895259s**；[最终 receipt](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_bound_only_native_integration_v1/TEST_RESULTS_BOUND_ONLY_NATIVE_FINAL_V1.json>) 明示 Torch/native/原 PT 等为 0。覆盖完整 import/alias 无循环、11 原依赖原字节、17 项 exclusive fake-stage 与完整 receipt filename、main/close AST、V1 动作/构造/守卫 AST、fresh-cache 单虚工厂 build、source/container/teacher 身份分离、zero-update typed inner counters、stats default/显式 bool、原 true T/Tr、metadata model-stat 拦截/还原、原错误/RC/关闭/实际 child-wait/lease 缺口保持失败、源篡改挡在 import 前、失败 root 不重试。

首次 22 项 21 PASS、1 ERROR：新测试误写原 guard 函数名 `source_audit` 导致 `StopIteration`；查得真实名 `source_guard_mechanism` 后只修新 fixture。首次 [错误 receipt](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_bound_only_native_integration_v1/TEST_RESULTS_BOUND_ONLY_NATIVE_STDLIB_V1.json>) 与最终 receipt 均保留；未改算法或旧源来迁就测试。

scope 固定 E3/W35 N80、seed20260928、160/1600 controls、原 DR/physics/acceptance：E3 原 rescue74 与 normal6 分列，normal 保持性不是 rescue 分母；W35 moving/standing 原 complete-conditional denominator 分列，partial/unknown/drop 独立，不把 pooled FINAL events 当 moving。未来自己的闭环 raw 如需一次 grade，由父方沿原独立 consumer 执行，本子代理不读 raw。

已合格 teacher 与旧 candidate 两组仍是单 seed、独立 cohort；相同计划 pose/seed 不是匹配实际 UID/DR trace。当前 **bound-only native 通过率、相对提升、因果/训练效果、matched UID、qualified execution 全为 null，保留母本、不 promote**。下一窗口应先取得此 ZERO_UPDATE probe 的独立合格闭环，再另立 bounded 短训练版本与 matched/多 seed 对比，将 postprocess 效果和训练效果分开。
