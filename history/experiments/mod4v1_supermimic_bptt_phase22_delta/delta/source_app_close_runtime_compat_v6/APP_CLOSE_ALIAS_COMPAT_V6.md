# V6：仅公开 SimulationApp export-alias 兼容

**Source/stdlib 交付；本子代理新增 native/SDK/Torch/GPU/PT/C/锁/GO/Git 操作均为 0。** Catalog 的 Office/ACL 不匹配本任务；实际采用 FS/read/grep/CLI/stdlib。旧 V5、已封 A1 eval 件和 405 的 timestamp adapter 保持原样。

## 单文件接入

[新 helper](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_app_close_runtime_compat_v6/app_close_semantics_v6.py>) **27769 B**，SHA256 `3d2d75196fb98fdb45c80a79b5b8bb69873e7c0c2c0b0f6f6610eb11a8c63c39`。

未来 stager 只将上述**同一 bytes**安装为逻辑 ABI `app_close_semantics_v5.py`，owner 与 worker 都采用此新 pin；保留原 V5 shim、worker、owner、close 调用/参数/模式。source index 显式记录 V6 origin、bytes、SHA；不是修改旧 V5 封件。[API](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_app_close_runtime_compat_v6/API_CONTRACT_V6.json>)与[精确 diff](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_app_close_runtime_compat_v6/SOURCE_PATCH_V5_TO_V6.diff>)可直接审查。

唯一生产 class-module 白名单为 `isaacsim.simulation_app.simulation_app`、`simulation_app.simulation_app`。保留 exact `SimulationApp`/`object` MRO、bound self/func、close owner/qualname、module/class/code 文件一致、48933 B/SHA `6af5372bb0cdda6e665a30cd285ff724b3e5bd012dbdd4df458e0726173fc903`/close848 无 decorators，以及 plain `app.config` exact dict/fast bool。没有 wildcard、任意 subclass、headless 类猜测或 source pin 放宽。

producer 与 owner receipt validator 都按**实际允许 module**构造 actual_class/MRO/close_owner/close_module，不只放宽首个 class 检查而留下 canonical module 硬编码。[新 producer/validator:109–198](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_app_close_runtime_compat_v6/app_close_semantics_v6.py#L109-L198>)增加 actual_module、actual_type_name、source_code_version=`V6_PUBLISHED_SIMULATIONAPP_EXPORT_ALIASES`、helper 来源路径/bytes/SHA；owner 同时验证版本与新 helper SHA。失败 trace 含 [plain Python actual names:81–106](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_app_close_runtime_compat_v6/app_close_semantics_v6.py#L81-L106>)；不为诊断读取 SDK getter。wire 的 V5 intent/binding 名称作为 ABI 留存，不把旧 receipt 冒充新实际 binding。

## 来源与真实 unknown

[SDK expose_api:167–199](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/sdk_reset_cache_backend_v2/isaacsim/package_init.py#L167-L199>)明确 direct `isaacsim.simulation_app` 与 fallback `simulation_app` 两导出，并注册 alias；[原 AppLauncher import:27–29](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/sdk_app_launcher_actual_v6/app_launcher.py#L27-L29>)和[创建:1174–1208](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/sdk_app_launcher_actual_v6/app_launcher.py#L1174-L1208>)沿公开 `SimulationApp` 构建。

[已闭 V5 诊断:26–91](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/reports/A1_V5_CLOSED_TIMESTAMP_APPCLOSE_DIAGNOSIS_V1.json#L26-L91>)显示 E3/W35 primary timestamp 错误与 secondary `actual application exact class differs`，**没有打印当时 actual module**。本件仅实现 published-source 支持的两个候选；过去实际 module、V6 实际 native binding、真实关闭结果仍 null，不回填为 alias 已证实。

## 旧 gate 与测试

15 个既有函数/类 AST 逐体相同，含 close、intent/fsync、FINAL/full-save、所有新/secondary errors、实际 wait 后的窄例外、bounded recorder；original app.close 零参调用、模式、first two closes、RC/FINAL/error gates均未改，计账/锁/lease/deadline/learner/physics/DR/奖励源码未写。

- [新增 alias/source 测试](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_app_close_runtime_compat_v6/test_alias_compat_v6.py>) **16/16 PASS**：两 alias producer+validator 一致、unknown module、伪 canonical class/module、subclass、源码/方法owner/receipt SHA、fast False、原 pin 对全部 fake 保持 fail-closed。
- [新 scratch 复用的旧行为 gates](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_app_close_runtime_compat_v6/GATE_SCRATCH_V6/test_reused_v5_gates_v6.py>) **64/64 PASS**，含 6 个实际 CPU fake child wait/return/raise/exit0/exit7/primary-error 测试。没有执行 SDK。旧 9 个 worker-source AST tests 不重复，替以本件对所有未改 gate 的直接 AST 相等检查；原 worker/owner 根本未复制修改。
- 首次复用 64 项仅一个旧 fixture 附加的报错文字断言未包含新先行 `unpublished actual module`，runtime 早已 fail closed；只修改**新 scratch** assertion 后通过，helper SHA 从未变化。[透明历史](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_app_close_runtime_compat_v6/CPU_TEST_EXECUTION_HISTORY_V6.json>)保留该失败。fsync negative fixture 的 persistence-failure 输出是预期注入，不是实际 I/O 故障。

所有正向 fake 都用 PRIVATE own-file source pin，不是实际 SimulationApp 验证。旧封件 SHA、bounded input 与 scratch 索引列入最终 seal；父代理/405负责新 source index、真实准入与实际 binding receipt，本件不启动任何 native。
