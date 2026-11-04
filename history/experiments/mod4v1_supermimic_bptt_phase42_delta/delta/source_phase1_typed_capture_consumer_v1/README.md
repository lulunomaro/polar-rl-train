# Typed capture consumer V1 — SOURCE only / disabled

本目录只含纯 decoded-JSON consumer、14 个 stdlib synthetic case、结构说明与封件；未绑定 worker，未读取真实 FINAL/trace/reports，未运行 Torch/SDK/native/训练。旧 pure/application/locator/C1/C2 及资源、关闭体、DR/H1 母本保持原样。

## 最小 API

```python
verify_typed_capture(worker_final, task=None, lifecycle=None, provenance=None)
```

[实现](<typed_capture_consumer.py>) 无 I/O、hook、target import 或输入修改。通过普通完整模块 import 复用[原 pure](<../source_phase1_capture_evidence_verifier_v1/capture_evidence_verifier_v1.py#L54-L81>) 的 exact-int、typed_equal、digest，以及完整 `f32`、`execution`、`outer_wait_contract`；没有 AST 裁剪或改旧 globals/输入冒充旧 kind。调用端负责正常导入路径及独立 source 资格核对。

输入是完整原 worker/TASK，以及 lifecycle 中完整 `group_final,parent_exit_scope,source_grade,common_go,worker_ready,worker_started,env_close,app_close_binding,app_fast_intent OR app_close_returned,parent_started,controller_started,parent_dispatch,outer_parent_wait`。`group_final.terminal[0].data` 必须与完整 worker 逐类型相等；collector 投影不是替代品。[结构 schema](<SCHEMA_V1.json>) 是文档，不是另一套验证器：程序额外区分 decoded `1` / `1.0` / `False`。

`provenance.whole_documents` 按 `worker_final,task` 及各非 None lifecycle alias 分列 `original_bytes/original_SHA256/decoded_canonical_SHA256`。程序只重算完整 decoded canonical digest，绝不把它当原字节 SHA；reported source pins、source_ref==source_pin_ref 都只是 caller/source claim，不自动认证真实代码、Tensor bits、row index 或运行时绑定。所有四项输入有整体 canonical before/after，差异保留为矛盾。

## 真实 SOURCE ABI 与检查边界

依据[实际 producer ABI](<../source_phase1_typed_native_capture_v1/PRODUCER_ABI.json#L47-L109>)：

- `sensor.control_ledger` 保原 `BOUNDED_TYPED_CONTROL_LEDGER_V1`；64/128 个原 pack，确切计数 key `normal_channel_records`，cap 128/1280，run_id=`TASK.group_id+':E3'`。`sensor.incomplete_current_control`/`typed_pending_control` 保原 pending，不补 END/空 IDs。
- 每控制 MID/END 各五通道宽度 3+3+4+4+2=16；原 normal slot / physics / feedback / command clock 绑定，绝不补 MID 剩余19、fullclean35。仅 post_return END 保原 actor35；原 prephysical s1 与 full80 term/trunc 不被 reset 后状态替代。
- 四类 envelope 的 original dtype/shape/env_axis/retained mapping/role/source_ref/clock 均检查。当前 producer witness 元数据明确 IDs0..7；通用 codec helper 另测试显式非连续 [2,79]，不把 row index 当 env ID。IDs 原整数 K0..80、bool flags 全80、QUEUE_GROUP_FULL 全80 4+2 完整保留，绝不裁到8。
- 正常 float32 只验证原左结合 `f32(f32(clean+noise_used)+bias)`，并区分 sameTick、warmup、delay0/1、episode/cache。其他浮点 dtype 原 metadata 保留，算术标 UNKNOWN，不转换成 float32 冒充。
- `actuation.capture_schema=PHASE1_TYPED_C2_EVENT_WINDOWS_V1`；每 event 原 C2 标签不变。first2/last2 才有原事件，middle 明示 UNKNOWN。所有原事件包括 auxiliary/unparented 均保留；自然 issue/submit/apply/term 的 tick/原参数仍 exact int>=0，负数、float、bool 仍矛盾。
- C2 outside adoption clock 是[producer stored_clock](<../source_phase1_typed_native_capture_v1/phase1_capture_observer.py#L18-L24>) 的独立最小 metadata 域：无 sim_time_us、control_slot='UNKNOWN'；不补字段、不回填 event.tick。B4 正常钟仍用完整原 clock predicate。UNPARENTED writer 的 tick N/A、原 stored_counter0 独立保留，不制造 apply(-1)。
- same-asset TERM context 只证明父 seq/group/clock；setter name、joint-ID provenance、参数数值相等都不是 DOF/target/physical-readback join。该 join 固定 UNKNOWN。队列自身原 submit/apply full80 算术仍严格检查，context writer 的不同参数只记录歧义，不硬当执行器公式失败或成功。
- callback provenance 将 no callback / OBSERVED_METADATA_FAILED / RAISED / late-unjoined / END missing 分开；只有原 full80 preflags + 原 full IDs + 时钟/事件关联完整才核对 reset episode/cache。未观察自然 reset/sameTick 标 NOT_OBSERVED，不提升为反事实资格。

## 结果、测试与下一步

每项为 CONSISTENT / CONTRADICTED / UNKNOWN；任何真实矛盾保 CONTRADICTED。全有限项相容，整体仍 INCONCLUSIVE；缺成功 FINAL/仅 INCOMPLETE 的 capture_evaluability 为 NOT_EVALUABLE；若另有原字节声明矛盾，整体仍保 CONTRADICTED。published worker counts、实际外层 wait/child wait/EX/close decoded 闭合与有限科学相容、完整 Gate1、质量分别列示：固定 Gate1 UNKNOWN / Stage2 false / exact false / interface false / quality 无结论。

[14 个测试](<test_typed_capture_consumer.py>) 仅 stdlib synthetic，未重跑旧 27/20/11/CPU。覆盖 dtype/full IDs/full bool80、float32 左结合、warmup/sameTick、时钟、非连续 partial/full80 reset、callback 失败类、END/pending、N/A 与坏 physics、row79 queue 反例、context 非 DOF、whole/byte/canonical 分层。首轮及中间草稿失败与修正保存在[测试记录](<TEST_RESULTS_V1.json>)：包括 synthetic alias、错误 held-age 预期、字面 UNKNOWN 标签及双钟域遗漏调用点；不是实际 capture 失败。合成 lag2 跨控制边界时 held age 可达 22500us，而 first-transition latency 仍 0/2500/5000us，两者分列。

下一步仅由父代理在 NEW one-whole-cache purpose 下独立读取/认证真实原字节、完整 source/runtime/生命周期，再调用此 API。该步骤不由本目录执行；未产生 native/技能/因果收益证据，更无百分比资格。

精确 bytes/SHA、producer 最终封件及 source 行引用见 [SOURCE_SEAL](<SOURCE_SEAL.json>)。额外依据：[published codec](<../source_phase1_typed_capture_codec_v1/typed_capture_codec.py#L78-L229>)、[原 B4 callbacks](<../source_phase1_passive_sensor_capture_v4/passive_capture.py#L496-L555>)、[完整 C2](<../source_phase1_actuation_clock_scope_v2/actuation_tap_v2.py>)；它们均只读保留。
