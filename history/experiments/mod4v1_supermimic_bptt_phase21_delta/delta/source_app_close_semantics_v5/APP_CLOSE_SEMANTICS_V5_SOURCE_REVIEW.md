# V5：原 App fast-close 的严格关闭意图与实际 wait 对账

## 结论与状态

- 本次只新增源候选和 stdlib CPU 证据；代码/API/测试已先独立封存，随后只新增本说明与总清单。未运行 SDK、Torch、GPU、模型/PT、原 worker/owner、训练、原账户、锁、GO 或 Git；未改既有 V1/V2/V3/V4 封件。
- **73/73 CPU PASS，0 failure、0 error，1.2915063 秒**；含 6 个真实 CPU fake 子进程的 return、raise、`os._exit(0/7)` 与先前错误反例。它们不是 SimulationApp/native 验证。
- 真实旧 worker 的实际 App 类型、旧 `fast_shutdown` 值和退出原因仍为 **null**。本次源证据解释“要求 post-close marker 会把原生 fast-shutdown 当失败”的路径，不反推历史进程必走该路径。
- 新 gate 保留全部原 FINAL/error/full-save 校验，只允许**原 reason 精确等于单项 `original_close_completion_missing`**时，由严格 pinned intent + RC0 + 实际 wait 替代缺失 marker。放行结果写 expected nonreturn，`app_close_returned=null`，不伪称 close 返回。

## 1. 实际源证据

1. [SDK App 源:92–123](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/sdk_warp_buffer_appclose_v3/app/exts_0_simulation_app.py#L92-L123>) 默认 `fast_shutdown=True`；[SDK App 源:243–274](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/sdk_warp_buffer_appclose_v3/app/exts_0_simulation_app.py#L243-L274>) 使用普通 `self.config` dict 并接受 launch override；Jupyter 分支可改为 False。因此默认值不等于每次运行的已验证配置。
2. [SDK App 源:848–899](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/sdk_warp_buffer_appclose_v3/app/exts_0_simulation_app.py#L848-L899>) 原 `close(..., exit_code=0)` 有直接 `os._exit(exit_code)` 分支；[SDK App 源:948–964](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/sdk_warp_buffer_appclose_v3/app/exts_0_simulation_app.py#L948-L964>) 注明 fast shutdown 的 framework 路径立即终止进程。
3. [原 contracts:337–373](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_resume_runtime_v2/resume_runtime_contracts_v3.py#L337-L373>) 只在原 App.close 返回后写 App marker；原 [wait gate:95–149](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_resume_runtime_v2/resume_runtime_contracts_v3.py#L95-L149>) 要求生命周期完成。原 fast exit 可能没有执行后续 Python 代码；因此单纯缺后置 marker 不足以判定失败或成功，必须组合本次新 witness。
4. [父获取清单:19–30](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/reports/SDK_WARP_BUFFER_APPCLOSE_SOURCE_V3.json#L19-L30>) 给出的 App 源为 48,933 bytes、SHA256 `6af5372bb0cdda6e665a30cd285ff724b3e5bd012dbdd4df458e0726173fc903`；历史实际 binding/config 仍空。

## 2. 固定 API 与安装依赖

精确文件名见 [API 合同](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_app_close_semantics_v5/API_CONTRACT_V5.json>)：

| 用途 | 新文件 |
|---|---|
| Worker | [worker_supermimic_bptt_app_close_candidate_v5.py](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_app_close_semantics_v5/worker_supermimic_bptt_app_close_candidate_v5.py>) |
| Shared owner | [supermimic_original_owner_shared_app_close_candidate_v5.py](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_app_close_semantics_v5/supermimic_original_owner_shared_app_close_candidate_v5.py>) |
| Exclusive owner | [supermimic_original_owner_app_close_candidate_v5.py](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_app_close_semantics_v5/supermimic_original_owner_app_close_candidate_v5.py>) |
| 兼容 shim | [resume_runtime_app_close_v5.py](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_app_close_semantics_v5/resume_runtime_app_close_v5.py>) |
| stdlib close/gate/recorder | [app_close_semantics_v5.py](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_app_close_semantics_v5/app_close_semantics_v5.py>) |

```python
from resume_runtime_app_close_v5 import close_original_resources, evaluate_waited_worker
closure = close_original_resources(
    bridge, env, ns, lambda name, value: put(out / name, value),
    job_root=J, task=task, primary_error=error,
)
# Owner: 仍在原真实 p.wait() 之后调用，同签名：
semantic = evaluate_waited_worker(J, rc, entry, run_id)
```

新 shim 复用未改动的 [V4 installer](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_resume_runtime_v2/resume_runtime_install_hook_v4.py>)、[V3 contracts](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_resume_runtime_v2/resume_runtime_contracts_v3.py>)、[V2 contracts](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_resume_runtime_v2/resume_runtime_contracts_v2.py>) 及其它原 worker/owner 依赖。未来自有 manifest 应携这些不变依赖和新 helper/shim；不要把 fake fixture/test 当运行依赖。父负责 manifest、原准入、实际验证与 Git。

## 3. 最小变化与不变链

[逐行 diff](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_app_close_semantics_v5/SOURCE_PATCH_V5.diff>)、[构建清单](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_app_close_semantics_v5/BUILD_APP_CLOSE_CANDIDATES_V5.json>) 和 [代码复核](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_app_close_semantics_v5/CODE_VERIFICATION_V5.json>) 记录：把明确白名单变更逆变换后，**整个 worker AST、两份整个 owner AST 均逐节点等于 V4**。

- Worker 仅替换 shim import、pose-event 记录器/最终强刷、close witness kwargs。
- 两份 owner 仅替换 shim import 和 worker 文件名。实际 `p.wait()`、错误后 blocked/pending、其它已开 child 的 wait、原成本结算与最终锁释放链不动。
- 原 C/account 函数、authority/private-GPU/finite 锁类型、reserve、准入、3900/3600/300 窗口与 headroom、save、before_action guard、原 SuperMimicConfig、learner/teacher/DR/physics/reward 不动。
- V3 pose adapter 仍在 build_env 后、原 ONE reset 前；C113 command bind 仍在该 reset 后；bridge/init 顺序不动。没有第二 reset、额外 observation、物理 step、forward、RNG、投影真值覆盖或阈值改动。
- 此改动不是 E2 held-command/sensor 修复，不缩 speed、不拼 stand 到 moving，不增加任务成功代理，也不修改 E0/S50 binary predicate 空缺。

## 4. runtime pin：只看真实普通 Python binding/config/source

[pin 实现:61–149](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_app_close_semantics_v5/app_close_semantics_v5.py#L61-L149>) 要求实际 exact class 为 `isaacsim.simulation_app.simulation_app.SimulationApp`、实际 MRO、bound `__self__`/`__func__` 与 class definition 一致、owner/qualname、模块 class identity、module/class/co_filename 同源、固定 bytes/SHA 和 AST/code 首行 848 一致。plain `app.config` 必须是 exact dict，`fast_shutdown` 必须是 bool；不执行 config descriptor、不读 `_app`/is_running/Carb 状态、不公开 bool verified 或换 pin 参数。

- True：才有资格写 fast intent，仍需其它所有前置条件。
- 已知 False：不改 setting，不造 fast intent；只能走原正常返回 marker 路径。
- 未知/不匹配：先持久化 error，仍尝试原 close；owner fail-closed。

严格 exact class/MRO/source 会在其它 SDK 版本或未知 subclass 上停住；不静默放宽到“同名 method 看起来相近”。Fake 正例只在测试 scope 把 PRIVATE pin 指向自有 fake 源，生产默认 pin 拦 fake 有独立测试。

## 5. intent 发布与原 close

[发布实现:208–226](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_app_close_semantics_v5/app_close_semantics_v5.py#L208-L226>) 使用自有新 production 目录内的未发布临时文件：完整 JSON → flush → file fsync 成功 → 原子 rename 到 `APP_FAST_CLOSE_INTENT_V5.json`。文件已存在即冲突错误，不覆盖旧 witness。Fsync 失败时只有 unpublished 临时文件，owner 不把它当 intent。

[关闭实现:238–324](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_app_close_semantics_v5/app_close_semantics_v5.py#L238-L324>) 先原 bridge.close、env.close 各一次且都返回，无 primary/error sidefile/close/emit 错误，原 FINAL/九计数/完整 checkpoint 元数据自洽、pin 和 plain True 验证通过，才发布 intent；随后立即原零参数 `application.close()`。不传新 exit_code、不改 fast/skip_cleanup、不借 slow shutdown 求 marker。

intent 固定 role/role_key/run/job、实际 binding、原 FINAL **raw bytes/SHA**、counts、checkpoint path/bytes/SHA/counts/fullsave flag、前两 close 的返回证据和无错误声明。该辅助检查不是 actual-wait gate；owner 后续仍执行原 FINAL 全量结构门。helper 不打开 checkpoint，producer full-save receipt 与真实 checkpoint 内容验证的边界保持原样。

普通 close 返回继续原 App marker + lifecycle；Python `SystemExit(0)` 也是 caught/preserved 的 close error，不伪装成 OS hard exit。任何原错误在 App.close 前尽量 fsync 持久化；保持原 raw RC，owner 使用 semantic error 阻断后续 pending。未新增 directory fsync 或断电存储保证；目录/存储崩溃导致证据缺失时 gate 失败，不据此推断成功。

## 6. 实际 wait 后的唯一例外

[gate:364–418](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_app_close_semantics_v5/app_close_semantics_v5.py#L364-L418>) 首先原样执行 V3/V4 wait gate，再查所有自有新/secondary error sidefile。只当原 reasons 精确为 `['original_close_completion_missing']`、RC 是 int 0、无新增理由/错误、strict intent 的 pin/role/run/raw FINAL/checkpoint/counts 完全匹配，而且 App marker 和生命周期文件都确实缺失，才替代这一个理由。

以下仍失败：非零/bool RC，缺/坏 FINAL，错 role/run/view，缺 full-save，counter 不合法，原或新 secondary error，坏/False lifecycle，已出现 App-return marker 但缺 lifecycle，未知 source/mode，改写过的 FINAL bytes、伪造 prior-close bool/count/fullsave、错 pin、缺/坏 intent。含正常返回证据时不借 expected-nonreturn 分支补造生命周期完成。

放行只表达：`actual_wait_returned=True` + `app_close_expected_nonreturn=True` + `app_close_returned=null`。它不是“native close 已经返回”的物理观测，也不是 skill pass、90%、达成 3000 更新或历史退出原因证明。原 finite saved 且 target_reached=False 的执行门语义不被抬高为毕业。

## 7. bounded pose receipt

[recorder:421–491](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_app_close_semantics_v5/app_close_semantics_v5.py#L421-L489>) 保留 first3、last、7 个固定 event counters；最多 4 条 event record，不保留完整历史。原始输入及 emit/snapshot 输出做隔离复制，防止外部修改回执反改内部记录。

首次 3 条、之后每 20 秒或 128 条发布；adapter error 与最终/错误 worker flush 强制发布。单条 metadata 最多 131,072 JSON bytes；未知 event/非有限 clock/非有限 metadata fail-closed。仍写自有原 event 路径，schema kind 明确为 `POSE_CACHE_RUNTIME_ADAPTER_BOUNDED_EVENTS_V5`。10,000-event fixture 验证常量保留数量与低频发布，非每 reset 重写无限历史，零额外 SDK getter/reset/observation/RNG。

## 8. 测试、历史与哈希

- [73 项结果](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_app_close_semantics_v5/CPU_TEST_RESULTS_V5.json>)、[完整最新日志](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_app_close_semantics_v5/CPU_TEST_RUN_V5.log>)、[透明执行历史](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_app_close_semantics_v5/CPU_TEST_EXECUTION_HISTORY_V5.json>)：首次 68 中 1 个新 AST fixture 字符串拼写错误；只改新测试为真实 semantic branch 的 AST 检查，另加严格类型/快照反例至 73 PASS。最初新 transformer 的缩进锚点错误也单列保留。未借此修改旧 owner。
- 六个 CPU 子进程实际等候并观测 hard exit/return/raise；OS hard exit 后无 post marker 的反例在旧 gate 失败，在 strict 新 gate 下通过。其余 metadata 错误仍被拦。日志中的 fsync 失败/持久化失败是故意注入的纯 CPU 反例，不是 native I/O 故障。
- [代码封存清单](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_app_close_semantics_v5/CODE_DELIVERABLES_SHA256_V5.json>)：17 entries + self manifest，self SHA256 `59e5cb530fbf2e2066856d9ba594afec151f4c5b512382a8905671586fe993a7`，bundle `448bc38fdbe7ee0559bd7ea6b355e29d69dd713162712609ab4fdc5368771ec0`。73 项及 9 份源 syntax 编译通过；10 个 bounded 旧输入、V3 9 件封版 bytes/SHA 不变。
- [526 个自有合成 fixture 哈希链](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_app_close_semantics_v5/CPU_SYNTHETIC_CASES_SHA256_V5.json>) 只覆盖本目录新 CPU fixture，不包含真实模型、旧 raw 或 workspace 枚举。测试含“只存 checkpoint receipt、不创建模型文件”的明示 fake，故不是实际存储/完整模型证明。

**冻结约束：代码/API/CPU 封存后不原地重跑测试覆盖结果。复测与任何进一步变更使用全新 scratch/version。后续 docs 总清单只追加本说明、总封存脚本和总清单，不动先封代码。**
