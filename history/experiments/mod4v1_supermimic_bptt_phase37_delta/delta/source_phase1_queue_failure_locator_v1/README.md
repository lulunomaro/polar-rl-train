# Queue failure scalar locator V1 — SOURCE ONLY

## 唯一用途与现有证据

父允许的[小聚合 science report](<../reports/PHASE1_V4_ADMISSION2_ACTUAL_SCIENTIFIC_CAPTURE_APPLICATION_V1.json#L133-L199>)：原64 controls/512 physics/128 feedback、published execution consistent；五个其他有限组件 consistent，queue 组件 `CONTRADICTED: typed integer/range`。这些是聚合收据，不是本件读取的原 whole/trace，也不是物理故障根因。原 contradiction 保留。

本件只定位原 validator 哪一行/字段/原 scalar predicate 抛异常。没有 whole FINAL/trace、SSH/PT/raw/SDK/Torch/GPU/C/锁/Git/训练操作，没有原 source/封件编辑、monkeypatch、getter、改数据、转换类型、放宽 predicate、retry 或新运行门。

## 纯 API 与调用者义务

[locator](<queue_failure_locator_v1.py>)：

```python
result = locate_queue_failure(worker_final, pure_module)
assert result['input_unchanged']
```

- `worker_final` 只能是调用者提供的 acyclic decoded JSON 原 dict；本件不自行打开任何目标。`pure_module` 是调用者已经按下表真实 bytes/SHA 合格的原 pure 对象；本件不 import/open 它。
- API 检查 module/function 原 globals、code name/first-line/同一 filename、Missing/QUEUE/GROUPS 形状，限定原函数及其 nested code frames。这个 in-memory 形状检查不是 source 身份认证，不替代调用者 byte pin。
- 直接调用原 `actuation_component` **一次**，不换函数、不转换/重跑 predicate；捕获原 Missing/ValueError/其他 Exception，不吞成通过。即使原函数正常返回也只记 `RETURNED_NOT_ADMISSION`，不导出整个 return。
- 输入前后各作同定义 canonical JSON SHA256；同一原 dict 传入。若不同则 `INPUT_CHANGED_NO_REPAIR`，不恢复/掩盖改动。测试逐项验证 input canonical、pure module keys/function identities 未变。
- 不覆盖旧 application/report；`gate1=UNKNOWN, exact=false, stage2_GO=false` 恒定。父的未来独立科学 purpose/限定原 worker dict 调用另行负责；本件未进行 actual locator 调用。

## 有界输出

最多12个**原 pure** traceback 帧，仅 function/line 与以下白名单：integer.x 的精确 Python type/value/low；field.key（Unknown dict 只取 status/reason）；vector.v/首个 object-identity index（标注 basis）、matrix row index；queue_state 当前 loop `k`/width；validator-local event 的 seq/kind/group/tick、window.control_index。集合不输出元素，字符串128字符上限、原异常 message256上限，其他 locals、q/e/input、target/full trace 均不序列化。

`integer_callsite_fields` 只是冻结源该行的候选字段：原[validator:367–381](<../source_phase1_capture_evidence_verifier_v1/capture_evidence_verifier_v1.py#L367-L381>) 的 status 两项、retention 两项、control_index、event.seq、event.tick；共享一行时不伪造单字段结论。queue `k` 是原 loop 局部值，不自动断言它就是之后表达式的根因。event 是原 validator 的局部上下文/明确标注的 identity witness，不是物理 fault 结论。

Python3.14 inline seq-listcomp unwind 会清除 `e` 或恢复**上一个 window**的旧 `e`：仅在原:378 利用后续原 field.obj / integer.x identity，从当前 events 找首个 scalar witness，并输出 basis；不再跑任何 predicate。原[整数规则:54–56](<../source_phase1_capture_evidence_verifier_v1/capture_evidence_verifier_v1.py#L54-L56>) 保持 `type(x) is int and (low is None or x >= low)`；`True/0.0` 不冒 int，`-1` 对 low=0 失败，但对 low=-1 有效。

## 11项 NEW stdlib 回归

[NEW tests](<test_queue_failure_locator_v1.py>) 自建一控制、80行、4+2组、各8 apply 的纯 decoded fixture（不代表真实64/128-control合同）。覆盖正常原 component、负tick/float/bool、原 low=-1、首/后 window seq identity、status/retention/window callsite、queue vector v/index/k、Unknown dict/string与缺字段、payload/getter隔离、module API/无 monkeypatch、AST 无I/O/目标导入/formatter。

[收据](<TEST_RESULTS_V1.json>)：Python3.14.3 `-I -S -B`，最终11/11 PASS，2.060s，Torch未导入、旧 tests 未执行。初次10/11中1个 FAIL 是本 locator 缺 seq 上下文，不是原 predicate 失效；之后11/11及加后 window 反例后的最终11/11均记录，原失败 stack/pins/history 保留。没有 actual case/cause 结论。

## 精确只读输入 pins

| 输入 | bytes | SHA256 / source锚 |
|---|---:|---|
| [原 pure](<../source_phase1_capture_evidence_verifier_v1/capture_evidence_verifier_v1.py#L357-L445>) | 41739 | `2b4ae157a54ea59711556cb8dc02c18151db54afc5b5d0dcff95bc0c5a86e979`；41–81 helpers、357–445 queue |
| [原 application](<../source_phase1_actual_capture_application_v1/actual_capture_application_v1.py#L85>) | 9896 | `2fdac2ffe491fee7f20ef96b128c0b00f6a8dd9d94f8fe604c021e9bf36dd5ba`；未改 |
| [旧 synthetic 源只读](<../source_phase1_capture_evidence_verifier_v1/test_capture_evidence_verifier_v1.py#L37-L78>) | 24712 | `ad80940ca8b08c14a9b8aefd0b43a4c08062e85921919826f92c63624bb50612`；未导入/执行旧 tests |
| [原 actuation tap](<../source_phase1_actuation_capture_v1/actuation_tap.py#L143-L178>) | 18278 | `b9b9e288124a1ba8c031a030c00a231f4d02d2ba7efee9981141ae90b8e28828`；event字段源，不推断物理原因 |
| [唯一小聚合 report](<../reports/PHASE1_V4_ADMISSION2_ACTUAL_SCIENTIFIC_CAPTURE_APPLICATION_V1.json#L185-L188>) | 33575 | `942a4fc5b5c77d02c86dbf815ba4b0a71f4bb0116f4738a70a0efba74c69a7d3`；不是 whole/trace、不是测试输入 |

本目录仅5件：[seal](<SOURCE_SEAL.json>) 固定 locator/tests/README/test receipt 四成员，含以上输入 pin；自身递归 hash 排除，最终交付另报自身 bytes/SHA。旧 pure/application 源 SHA 在测试前后及封存时复验一致。
