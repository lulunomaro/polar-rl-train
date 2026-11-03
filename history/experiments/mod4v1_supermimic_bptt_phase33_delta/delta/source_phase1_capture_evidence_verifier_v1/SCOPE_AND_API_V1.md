# Phase1 decoded capture verifier — SOURCE/fake only

**状态：schema-level pure verifier；未读取真实 capture，缺 ORIGINAL FINAL → `NOT_EVALUABLE` / execution `null`。** Catalog 为 Office/ACL，无 RL 匹配；使用 read/glob/grep。只新增本目录文件；未运行 worker/旧 tests/once，未读取 PT/raw/actual report/B2，未用 SSH/SDK/GPU/账本/锁/Git，未启动训练或改 producer。

## API / caller 的原件责任

[`capture_evidence_verifier_v1.py`](<capture_evidence_verifier_v1.py>) 唯一入口：`verify_capture(final, task, lifecycle, provenance)`。参数均为已 decode 的 builtin 值；`final` 为 ORIGINAL **whole** worker FINAL 或 `None`，不是 collector projection。返回新 dict；无 I/O、目标模块导入、入口执行、输入改写或 RNG 调用。

- `task`：原发布的 E3/N80/seed20260928、64/128-control passive synthetic-zero6 task，保留原 physics/fullDR/asset/contract、0 PT/0 update、null skill。不是旧 quality task。
- `lifecycle`：以下 alias 的值为各自完整原发布文档，不是为 verifier 重造的投影：`group_final`=group FINAL；`parent_exit_scope`=PARENT_EXIT_SCOPE；`source_grade`=PHASE1_CAPTURE_GROUP_CLOSED_SOURCE_GRADE_V1；`common_go`=GROUP_EVAL_START；`worker_ready`=WORKER_SCENE_READY；`worker_started`=WORKER_EVAL_STARTED；`env_close`=ENV_CLOSE_RETURNED_PHASE1_CAPTURE_V1；`app_close_binding`=APP_CLOSE_BINDING_PHASE1_CAPTURE_V1；fast 路径另给 `app_fast_intent`=APP_FAST_CLOSE_INTENT_PHASE1_CAPTURE_V1，nonfast 给 `app_close_returned`；`parent_started`=PARENT_STARTED；`parent_dispatch`/`controller_started`/`outer_parent_wait` 为 frozen controller 发布的原 dispatch、started、PHASE1_CAPTURE_PARENT_WAITED_ACTUAL_V1。原 worker/parent error 若存在分别保留在 `worker_error`/`parent_error`。
- `provenance.schema_reference_id` 为 frozen V2 reference root `83cb35d61298fdac4d2c720d1322ada0fbfa43b866709b4e5958b99ac82b62d2`；`schema_source_pins` 按模块 `SOURCE_PINS` 的17个 alias 给 `{bytes,SHA256}`。它们只是**已审 schema/方法出处**，不是 actual producer 的 whole-runtime index/seal 验证；不要求未来用 B1 old runtime 才可验。
- `provenance.whole_documents` 对 `worker_final`、`task` 与各 lifecycle alias 给 `{original_bytes, original_SHA256, decoded_canonical_SHA256}`。前两项由 caller 对原字节取得；后一项是本模块 `digest(decoded_whole_document)`，只用于绑定本次输入，不冒充原字节 SHA。fast intent 必须绑定 worker FINAL **original** bytes/SHA。processor 不认证这些 caller 元数据，也不读取文件或补造缺件。
- 当前只实读 frozen V2+B1+C+controller。未来 V3/B2 实际 provenance 仍由 parent 另绑定确切新 index/seal；本版始终报告该项 `UNKNOWN`，不假称 V3 fully source-verified。若格式确有差异，只能另做 NEW 版本的最窄 schema/pins 传播，不改冻结源；未读取 B2 或浮动源。

## 检查与 Unknown 分层

1. 严格 bool/int、有限数、shape、原 whole-schema；50/400/100Hz 与64/128 controls aggregate counts、reverse restore、typed timestamps、child actual wait、两 EX release、source-grade/outer real-wait linkage。RC0/fast intent/metadata 不是实际 wait；outer RC1 可证明发布 wait fact，但 closed execution=false。dispatch PID/start-ticks/SHA 只交叉绑定已发布身份，不新增 PID-gone、costwriter 或 resource admission。
2. retained feedback：3+3+4+4+2 clean16、used-noise/leg bias、noisy→delay actual input、cache cur/out/last/sample_tick/ready、warmup、sameTick reuse、episode lineage、MID/END 与 reset-internal SceneUpdate。采用源期望 float32 两次相加的 decoded value consistency；不是全部 tensor dtype/bitwise 证明，不建立统一 FP64 baseline 门。缺 dtype → 对应检查 Unknown。
3. original actor35 仅同返回 buffer 的8行 sanity/35列；不是 untapped counterfactual bitwise。physical pre-reset s1/term/trunc 与保留的 reset ids/episode/cache 可作局部边校验；缺自然终端或未保留边为 Unknown，不把 SOURCE 补成 actual proof。
4. retained actuation：4-leg/2-wheel processed target→queue submit→8个2.5ms apply→original writer，逐字段连续链、due/first issue、0/2500/5000µs first latency 与更长 held age、邻接 control 的 partial-reset validity/issue清除及 unselected 保留。无 reset hook，actual reset tick/neutral physical value Unknown。
5. **WindowRetention 仅 first2+last2；sensor first32/last32 与 special cap4。** 这些不是完整64/128 control trace。decoded list shape/typed值可验；row mapping 只有 SOURCE 声明，materialize 丢失大部分 actual dtype/row metadata。stored DR/scale/counters ≠ SDK physical readback/独立 RNG stream equality；无新增 getter/obs/reset/RNG 的声明仍为 SOURCE，不是 paired untapped measured proof。

每检查为 `CONSISTENT / CONTRADICTED / UNKNOWN`；顶层即使全部局部一致仍为 `INCONCLUSIVE`，`gate1=UNKNOWN, exact=false, capture_interface_passed=false, stage2_GO=false`。`execution.value` 只表示 supplied decoded bounded counters+published wait closure 的一致性，非 component/完整运行来源/技能通过。缺 FINAL 保留 failure metadata，所有 actual counts/execution 为 null，不用零填充。

## 收据与可选后续

[`TEST_RESULTS_V1.json`](<TEST_RESULTS_V1.json>) 是 Local314 `-I -S -B`、27项自建 stdlib/AST/synthetic 测试的收据；fake 正例/负例不是 SDK/live PASS。首轮26项的1个 `StopIteration` fixture错误已保留：只改一份重复 actor payload，retention 先阻断而 helper 请求被跳过组件；修正自己的 fixture，producer 不变。

唯一可选 metadata 提案：将导出前**已持有** tensor 的 actual dtype / captured shape / actual witness row IDs 随原 data 旁存；无额外 SDK 调用/RNG，不实现 emitter、不修改 B/B2/worker。当前下一步仅供 parent final review；后续实际 capture 若成功，再用原 whole FINAL/task/原 lifecycle 及精确新 producer provenance 调用本纯处理器，不据本 SOURCE/fake 进入 stage2。
