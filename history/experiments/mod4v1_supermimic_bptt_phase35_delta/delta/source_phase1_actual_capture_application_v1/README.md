# Phase1 actual-capture application — SOURCE / decoded-only

**状态：纯 API 已有20项自建 stdlib synthetic 测试；本任务实际 capture/document 读取数0，actual counts/execution 均 `null`。** Catalog 为 Office/ACL，无此任务匹配 Skill；使用 read/glob/grep。只在本 NEW 目录写文件；旧 producer/verifier/seal 保持原 bytes。无 SSH/remote fetcher/stager/scheduler、实际 report/trace/PT/model/raw 读取、SDK/GPU/账本/锁/Git 或训练。

父最后转述的 V3 仍是 READY/GO 后原 boundary 报错、worker fast-close RC0 带 ERROR、parent/outer RC1 已闭合，未取得合格 whole FINAL；本任务未读取这些 actual 报告，未验证 flags 类型/shape，也不诊断该根因。该失败不被零计数或 synthetic 正例覆盖。未来版本身份仍待父另证。

## 1. 固定纯 API

[`actual_capture_application_v1.py`](<actual_capture_application_v1.py>)：

```python
apply_capture(final, task, lifecycle, original_byte_provenance,
              reported_producer_pins=None)
```

- `final`：ORIGINAL **whole** worker FINAL 或 `None`；`task`：原 passive E3 task 或 `None`；`lifecycle`：alias → 原完整发布文档。`None` alias 仅表示未取得，不代表空发布件。
- `original_byte_provenance[alias]`：`{original_bytes, original_SHA256, decoded_canonical_SHA256}`。前两项来自原字节；后一项为 frozen `pure.digest(decoded_whole_document)`，只绑定 decoded 输入，和 original byte SHA 是不同概念。调用方已有的 whole read/hash/decode cache 可复用，别把 JSON 重序列化 SHA 冒充原 SHA。API 不认证 caller attestations，也不执行 read/hash/decode cache 获取。
- `reported_producer_pins` 是可选原 source 字节 metadata，三个 key 为 `capture_source_index`、`worker_source_seal`、`B2_sensor_source_seal`，各值 `{bytes,SHA256}`。只与 `V3_REVIEWED_REFERENCE` 对照；匹配也不认证实际 staged runtime，不匹配也不新增运行门。**V3 reference tuple / 17 schema pins 都不构成 V4 身份。**
- API 调用已封 [`verify_capture`](<../source_phase1_capture_evidence_verifier_v1/capture_evidence_verifier_v1.py#L470-L517>)，构造17项 **schema/method** reference，不将 B1 reference 偷换为 V3 producer pin。导入时调用方需把本目录和 frozen verifier 目录加入 Python module path，并先按本目录 [source pins](<SOURCE_PINS_V1.json>) 核对字节；API 自身不作 FS 查询。

```python
# 以下对象均已由调用方从真实原件获得并保存在内存；这里没有任何 I/O。
from actual_capture_application_v1 import apply_capture
review = apply_capture(original_whole_worker_final, original_task,
                       original_lifecycle_aliases, original_byte_metadata,
                       reported_producer_pins=original_source_byte_metadata)
```

完整 lifecycle alias 定义沿用 frozen [Scope/API](<../source_phase1_capture_evidence_verifier_v1/SCOPE_AND_API_V1.md#L9-L13>)；本模块 `ARTIFACTS` 给出逐 alias 原发布相对名。fast intent / nonfast returned 按原 binding 选择；错误文档若存在原样保留。

## 2. collector projection 的实际 gap / 最小未来原件

已实读 frozen [remote reader:51–57,92–111](<../source_phase1_capture_result_collector_v3/remote_metadata_reader.py#L51-L111>)：worker projection 丢弃 `sensor/actuation/rng_counts/bounded_trace/original_setup`；group FINAL 的 `terminal[].data` 和 TERMINAL_ROWS 同样被投影。[reader:126–158,297–299](<../source_phase1_capture_result_collector_v3/remote_metadata_reader.py#L126-L158>) 的 whole-read/hash/parse 是内部 cache 事实，export 仍是 projection。[summarize:154–168](<../source_phase1_capture_result_collector_v3/collect_capture_result.py#L154-L168>) 的 `worker_observed/published_metadata` 也没有还原 payload。

因此 API 遇到已知缺 whole 字段的 worker/group 投影，直接返回 `NEEDS_ORIGINAL_WHOLE_ARTIFACTS`、`pure_review=None`、counts/execution `null`，不把它喂给 pure 当 whole。仅 metadata 表明读过大文件，补不出原 payload。

只有未来 NEW scientific-purpose 确实成功且父持有原件时，最小输入为：

1. 原 **whole worker FINAL**；
2. 原 **whole group FINAL**：pure 要求其 `terminal[].data` 与 worker whole 完整相等；仅另给 worker 而保留 group projection 仍有 gap；无需额外重复 TERMINAL_ROWS；
3. 已持有的原完整 task / lifecycle SMALL 文档及各自 original bytes/SHA。若曾丢失元数据，优先用原 cache，而非重构/重序列化；不存在的发布件保留 unavailable。

父可在新的独立科学目的下自行作每必要原件一次 bounded whole read/hash/decode/cache；本包既不实现也不触发该动作。当前失败 root 无合格 FINAL，保持 gap，无 actual fetch 准备、重试或补造。

## 3. 整理结果及算法对齐

- `counts` / `execution` 原样透传 pure：后者仅表示 **decoded published bounded counters + wait closure**，不是组件、完整运行、技能或 Stage1/Stage2 通过。component 矛盾可与该窄 execution=true 同时存在；单项不会被抹去。
- `evidence` 分组：retention；retained 100Hz MID/END + noise-used/cache；physical pre-reset/partial reset；actor same-buffer；queue issue/apply/write/reset；stored RNG/DR source claims。保留 pure 的 `CONSISTENT/CONTRADICTED/UNKNOWN` 及 detail，未执行/未保留项是 Unknown，不填0/PASS。
- B2 的 [feedback/sensor/delay capture:339–401](<../source_phase1_passive_sensor_capture_v2/passive_capture.py#L339-L401>) 捕获 actual raw、实际 cached used-noise/bias、noisy return、delay before/after 和实际 return；`fresh_due_local/local_delayed_mask` 原本 Unknown。数学检查仍由 [pure:254–325](<../source_phase1_capture_evidence_verifier_v1/capture_evidence_verifier_v1.py#L254-L325>) 按 `float32(float32(clean+noise)+bias)`、warmup / sameTick cache / per-row episode 执行。`1 + 2^-24 + 2^-24` 的两次 F32 加法结果1，和一轮最终舍入不同；这里只作 decoded 条件数值一致性，不称全部 tensor actual dtype / bitwise 证明。
- [B2 pre-reset/reset:411–447](<../source_phase1_passive_sensor_capture_v2/passive_capture.py#L411-L447>) 与 [pure queue:365–445](<../source_phase1_capture_evidence_verifier_v1/capture_evidence_verifier_v1.py#L365-L445>) 原算法不复制、不放宽：4-leg / 2-wheel processed target → submit → 8次2.5ms apply → original writer，due/first latency 与 held age 区分，邻接 partial-reset flags/issue 清除与未选行保留。
- [observer:73–126](<../source_phase1_capture_worker_v3/phase1_capture_observer.py#L73-L126>) 只保留 first2+last2 actuation windows、sensor first32/last32/special cap4。normal100Hz 必须 scene_update、reset_depth0、tick%4==0；reset-internal 不是 normal。initial cache 同 tick 可复用，clean0/freshness 不作伪推断。materialize 丢失大部分 tensor dtype/row metadata；row mapping 仅 SOURCE，未保留边/localDue/自然终端/full clean35/private RNG equality/physical readback 继续 Unknown。

顶层固定 `gate1=UNKNOWN, exact=false, capture_interface_passed=false, paper_ready=false, stage2_GO=false`，不修改旧 always-UNKNOWN 语义，不用0/74技能表推接口，不新增 wall/资源/审批门。父已更正早先45s为笔误；原1800 preGO / 900 ready / 2400 worker 不动，本 API 无计时器。

## 4. 收据与封存

[`TEST_RESULTS_V1.json`](<TEST_RESULTS_V1.json>)：Local314 Python3.14.3 `-I -S -B`，20/20 **本目录新测试** 首次通过，未导入 Torch、未执行旧 tests/producer。测试覆盖 missing FINAL/failure/null、双 projection gap、窄 execution 与组件分离、original byte/canonical SHA、F32/warmup/sameTick/reset-internal/dtype Unknown、future tuple 不成新门、输入不变和 AST 无 fetcher/entrypoint。queue/reset full 算法继承旧 pure source，未在本任务再跑 SDK 或完整 queue fixture。

[Source pins](<SOURCE_PINS_V1.json>) 固定20项 pure/code/schema refs、V3/B2/collector 原 source 与精确行号；17项旧方法 pin 逐 bytes/SHA 复核，pure/V3/B2/collector 四组旧 seal 的40个成员全部复核一致。另仅作 AST 对照：B1/B2 的 `PassiveCapture.attach/_clock/_delay_state/report` 和 `BoundedRecorder` 五处完全相同，支撑 payload/clock/retention 方法沿用，不是 actual runtime/callable 身份证明。[Source seal](<SOURCE_SEAL.json>) 固定本目录五个成员，seal 自身字节 SHA 在最终交付外报。下一步只供父 final source review；未来成功新 purpose 再对真实原件独立执行，不据 synthetic 收据推进 Stage1/Stage2。
