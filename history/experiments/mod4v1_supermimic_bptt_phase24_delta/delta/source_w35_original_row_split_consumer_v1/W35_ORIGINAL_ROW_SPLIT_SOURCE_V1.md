# W35 原生行事实 moving / standing 单遍分组消费 V1

## 状态与边界

**源码与自己合成字节测试完成；本子代理实际 raw grading = 0。** 只在本新目录新增 consumer、测试和说明；旧 microbatch / accepted / 控制循环 / observer / row writer 源保持原样。父代理在本次 NEW 实际冻结评测完成原 close/wait 后，可为这个明确的新 grading 目的，对刚产生的自己 raw 消费一次；这里没有翻读任何旧 raw、PT、NPZ，也没有 SSH、SDK、Torch、GPU、账户、锁或 Git 操作。Catalog 仅 Office/ACL，与本任务不匹配，实际使用 read/grep/写文件/stdlib CPU CLI。

运行件：[consumer:197–204](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_w35_original_row_split_consumer_v1/w35_original_row_split_consumer_v1.py#L197-L204>)。**26594B / SHA256 `8b593a95c62981434dc99fc2475f1b7808b30f809109897e54c9db1f7d9ce879`**。精确参数与 JSON 字段见 [API 合同](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_w35_original_row_split_consumer_v1/API_CONTRACT_W35_ROW_SPLIT_V1.json>)。

## 原源字段与含义：不新造 accepted 谓词

| 原证据 | 用途 |
|---|---|
| [RM70 open:76–88](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/NINE_N80_PARALLEL_SOURCE_V8/rm70_intervals227.py#L76-L88>) | `standing=self.stand` 来自原 `cmd.is_standing_env`；不是从 BODYvx、nominal_speed 或误差均值推断。 |
| [close:138–150](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/NINE_N80_PARALLEL_SOURCE_V8/rm70_intervals227.py#L138-L150>) | 原 kin 为 along/cross/yaw 条件；原 `complete=lookup[ids]&self.known[ids]&~self.term[ids]&~self.timeout[ids]`。consumer 只消费其已存 Boolean，不重新量化数值阈值或重建自然 timer mask。 |
| [原 row:151–170](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/NINE_N80_PARALLEL_SOURCE_V8/rm70_intervals227.py#L151-L170>) | UID、source counters、起止 controls/ticks、start、standing、原 kin/complete/fact、ter/tru、end reason 和原终止原因。原 `complete_interval_bounds_fact=complete&kin`；字段缺项/错型/矛盾为 unknown。 |
| [emit_columns:135–137](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/NINE_N80_PARALLEL_SOURCE_V8/rm70_intervals227.py#L135-L137>) | 原 tensor→CPU→Python→append 完全未改；本消费器不接入运行期，也不增加 getter/observer。 |
| [原 finish:184–190](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/NINE_N80_PARALLEL_SOURCE_V8/rm70_intervals227.py#L184-L190>) | window-end partial；pooled events、producer receipt 与 full-expert UNKNOWN 分开。conditional command interval grade 不等于 full W35 skill graduation。 |
| [header:79–87、append:99–118](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/NINE_N80_PARALLEL_SOURCE_V8/positional_rows227.py#L79-L118>) | 实际 JSONL 是 `[schema_id,[values...]]`；必须读取 companion schema 的 constants+positional_fields。header `source_model_SHA` 与 row `source_SHA` 指 model SHA。 |
| [配额/finish:119–151](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/NINE_N80_PARALLEL_SOURCE_V8/positional_rows227.py#L119-L151>) | 原 data+schema 192MiB 上限、attempted/dropped/retained、schema/data bytes/SHA 与 rows_by_schema；不增加配额，不推断丢失样本属于哪组。 |
| [原 W35 worker:49–51、117–118](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_a1_frozen_eval_integration_v2/worker_formal_a1_frozen_candidate_v2.py#L49-L118>) | observer model 参数是 `task['source_SHA']`；FINAL 存 `skill.original_RM70_interval_route_facts` 和 source_cache、role/group。 |

两原源精确指纹：`rm70_intervals227.py` 14185B / `d84182d3675f41d53d35da54c4d80519b9b2280ccb6d3f47f33cfff64029d609`；`positional_rows227.py` 6557B / `72627c449b8ce071bcf278027ef1f9fe6a32ab7f2d20910e895fb13bf8f3fd29`。它们是 Python 源指纹，**与 CLI expected-source-sha 的模型指纹不同**。

## 父调用：只针对本次 NEW 自己的闭合 case

```bash
python -S -B w35_original_row_split_consumer_v1.py \
  --input "$NEW_W35_CASE/RM70_SAME_UID_COMMAND_AND_ROUTE_FACTS227.positional.jsonl" \
  --case-root "$NEW_W35_CASE" \
  --expected-role W35 \
  --expected-source-sha "$ACTUAL_A1_CHECKPOINT_SHA" \
  --expected-group "$ACTUAL_NEW_GROUP_ID" \
  --output "$NEW_UNUSED_OUTPUT/W35_ORIGINAL_SPLIT_GRADE_V1.json"
```

- `--case-final` 默认 case-root 下的 FINAL；`--schema` 默认其 producer.schema_path。schema/data/FINAL 解析后的真实路径均须在显式 case-root 内，且 data/schema 精确等于原 producer 路径。输出必须为全新文件。
- `facts = FINAL['skill']['original_RM70_interval_route_facts']`；`producer = facts['producer']`；原 pooled counters 在 `facts['events']`。
- 原 header.producer_metadata 可能为 `None`，row 没有独立 role/group 字段。必须由真正该 case 的 FINAL 绑定 W35/group、exact N80/1600、passed_execution 和 source_cache.source_SHA；命令行 role 字样不是来源证明。父原 actual wait/closure/资源门仍是父的职责，本工具不冒充其通过回执。
- FINAL 与 schema 各只读取一次；schema 原字节直接传 API，不重序列化当作字节证明；raw 一次 open、forward stream、同时 SHA/行数统计，不 seek、不 reopen。
- 核对原 producer 的 data/schema bytes/SHA、rows/schema counts、attempted/dropped、配额与原 pooled events。消费期间 size/mtime 变化会清空率并标记完整性失败。

## 可复用 API 与输出语义

```python
result = stream_consume(
    binary_stream, schema=header_dict, schema_raw=header_original_bytes,
    expected_role='W35', expected_source_sha=actual_candidate_sha,
    producer=original_producer_receipt, case_metadata=actual_case_FINAL,
    expected_group_id=actual_group_id, data_basename=original_basename,
)
```

API 不打开任何路径、不 close caller stream。只给 `record_type='same_UID_original_RM70_command'` 分组；catalog-route 事实另计为 ignored，不变成技能成功样本。

- `groups.moving/standing`：`N`=证据完整的保留行中原 natural-complete 非终止区间数；`n`=其中原 fact=true；`false`=其中原 fact=false；原 complete=false 单列 `partial`、不纳入条件分母；相关缺项、非真 Boolean、矛盾、UID 问题单列 `unknown`。`unknown_standing` 独立，不从 vx 回填。
- 原身份 `(env_id, episode_uid, command_uid, same_UID_segment)` 不跨 reset 拼接；原 source_E1_episode / original_command_counter 保留。重复身份会撤销先前贡献并将所有拷贝置 unknown，避免挑第一条成功。原源 counter 是有符号整数，不新造负数哨兵规则。
- 原 controls/ticks/ter/tru/start/fact 的一致性校验仅作数据完整性检查，不改变原 kin accepted 数值阈值。输出保留 end-reason、ter/tru、原 reason flags 计数、原 UID/source/flags 顺序摘要 SHA 和带行号的 bounded unknown 身份例子；完整 raw 原样保留并绑定整文件 SHA。
- `rate=n/N`、Wilson95 只描述已验证的保留有效区间。**N=0 时 rate/Wilson 为 null**。schema/data 字节证明缺项或错误时，即使 n/N 结构可见，率也为 null。return 0 表示保留行 artifact grade 完成，不代表无 unknown/drop，更不代表任务达到 90%。
- 任意 unknown、drop、格式/字节错误或必要 metadata gap：各组 `all_original_complete_population_rate=null`。drops 只保留全局原计数，组别分配为 null。完整条件总体只限这个 case 的原 observer command intervals，不延伸为整个专家所有域。
- `relative`、`mother_actual_reference`、`full_expert_skill_rate` 永远 null；未实测母本，不输出改进效果，也不把 boundary/nofall/均值当标签。

## 合成测试与封件

[测试](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_w35_original_row_split_consumer_v1/test_w35_original_row_split_stdlib_v1.py>)：37/37 PASS、0 fail、0 error、0.058638s；见 [测试结果](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_w35_original_row_split_consumer_v1/CPU_TEST_RESULTS_V1.json>)。覆盖 moving/standing、partial、N0、真 Boolean/缺 UID、zero-vx 非站立反例、与数值 MAE 相反的原 Boolean、重复撤销、source/group/root、schema/data SHA、drops、pooled events、恶形 JSON/长行、single-pass/no-seek、CLI 新文件不覆盖。只有 BytesIO 和本目录新建的明确 synthetic case；不含实际评测数字。首次 35/35 已通过，后增加两项缺证明/根路径测试成 37/37，未盲重跑实际文件。

[完整封件清单](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_w35_original_row_split_consumer_v1/DELIVERABLES_SHA256_V1.json>) 包括运行件、API、源输入/旧封件不变核验、测试历史与自己 synthetic 文件指纹。它是源码级封件，不是本次实际冻结评测结果。
