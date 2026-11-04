# Phase1 typed-native passive producer — SOURCE only

## 结论与边界

NEW `PHASE1_TYPED_NATIVE_PRODUCER_ABI_V1` 的最小原 worker 集成；不是 native 执行结果、技能评测或训练入口。
本封件只执行 Python 3.14 `-B` stdlib / own-fake / AST / SOURCE 哈希检查。实际 Torch CPU、SDK、GPU、PT、资源 gate、EX、canonical、SSH、stage、dispatch 均为 0；旧封件、旧测试和实际报告保持原状。
`NEW_PASSIVE_INTERFACE_PROBE_NO_TRAIN`：仅 E3 / N80，默认 64、可选 128 controls；显式 synthetic zero6、PT0、teacher=None，无 learner / optimizer / replay / export。
`passed_execution`、`metadata_retention_complete`、科学一致性是三个不同字段；本 producer 始终保留 `science_consistency_status=UNKNOWN_PENDING_TYPED_CONSUMER`、`capture_interface_passed=False`、`gate1=UNKNOWN`、`exact=False`、`stage2_GO=False`。RC0、0% 或收齐元数据都不变成技能成功。

## 原完整闭包与当前文件

- `single_gpu_passive_capture_parent_v1.py` 完整 9336 bytes / `d5575ff2e670fd18ea0a09d9f3d5c05c46bf606a027fcb84d97c6e34a88a2b41`，与冻结 V4 字节一致。原资源 owner/private_GPU_EX/finiteEX、实际子进程 `Popen.wait`、finally 中全 child waited 后双 EX release 原样保留。
- 独立 alias 的 canonical 37927 / `7a092364cf63e9621481dc0a5554b56a22e4412cf89870c3db9a124864074b2e`，完整 AppV6 27769 / `3d2d75196fb98fdb45c80a79b5b8bb69873e7c0c2c0b0f6f6610eb11a8c63c39` -> 完整 Base、poseCacheV4、完整 native bridge 13125 / `8211964c2ce3dd78fdb9fee6603ee4a4dcfbca6fa9d7df44f20d3ddb7aaead29` 与 original17 都保留。
- 完整 `close_original_eval_resources`、GPU/deadline/fstat/root 等原函数 AST 相同；完整 helper bootstrap 函数不变，正常导入原 117-byte storage / 653-byte capacity 源文件，不使用 stub。
- 原物理 400Hz / dt=.0025、控制 50Hz / decimation=8、feedback 100Hz、DR/命令/phase/speed/acceptance、原 owner/canonical、3900/3600/300/1800 与 reserve86412.86069250107 无改动。原有限验证成本协议保留；真实成本结算 UNKNOWN，没有新增 approval bool 或成本写入器。
- 完整八角色 runtime/static banks/vendor7 均是必要原始树。`FINITE_SOURCE_BUNDLE.json` 只是 34 个完整文件映射（17 original + 5 candidate + 9 dependency + 2 bootstrap + 1 ABI），**不是完整 static tree，也未复制任何文件**。
- 全字节/SHA/AST 校验 V4 13、B4 21、codec 7、C2 5 个上游成员，旧 manifest 155 完整源 / 435 pin refs、C 原始 182 完整源，以及继承封件。B2 原 seal 没有 root 字段：保留其固定 null / 完整 seal SHA / 全 13 成员，不发明 root；其余 root 使用各自原算法。

## 十处接口改动组；不是重写调度器

| 边界 | 实际变化 / 保持项 |
|---|---|
| 1. `validate_task` / `validate_plan` | 新 typed TASK/PLAN/integration 与显式 `typed_producer_schema`；旧 kind 不被当成新 schema。完整八角色目录保留，仅 E3 被选择。 |
| 2. `make_task` | 只增加 typed ABI 元数据；同一个既有 GPU/EX/有限 deadline/paired-pose/cost 协议。 |
| 3. `wait_start` / `batch_start` | 新 common-start 字面 kind；原 readiness/barrier/deadline 流程不变。 |
| 4. `worker.main` tap 安装边界 | 完整原 setup 前缀相同：原 reset53 -> E3 place/publish55 -> 原 compute66 -> 原 bridge init 一次；随后加载完整已 pin B4/codec/C2。一个预建 witness index。B4 原 default22+3 -> 原实际 MRO/source/code/closure preflight -> 六 hooks，不走 CPU direct-attach。 |
| 5. `worker.main` 唯一控制循环 | `begin_control` -> 原 boundary.for_action -> 一次原 bridge.step -> canonical 严格返回 flags -> `end_control` 使用原 END actor35 buffer -> C2 drain。无新增 reset/step/compute/clean_policy/SDK getter/RNG 调用。 |
| 6. `initial_sensor_memory` / `stored_clock` / `stored_actuation_evidence` | 原实例已有 memory / clock / D4 calls、formula_max_error、collect 和 term/asset identity；clean0 同 tick cache UNKNOWN；不新增 target readback 或 RNG-state 查询。 |
| 7. `adopt_queue_owned` / `typed_c2_memory` / `typed_c2_event` | C2 已 detach+clone 的明确 queue/command/selected-target 全 80 行按 `QUEUE_GROUP_FULL` 原 owned buffer 接纳，不再 clone/cast。静态 per-env 值 witness8；小 JOINT IDs/opaque tensor 只有 UNKNOWN 元数据，不冒充 `ENV_IDS_FULL`。 |
| 8. `WindowRetention` / `incomplete_capture` | sensor ledger 保留全部 64/128 controls；C2 只 first2/last2，每窗口原 8192 event cap，中间 UNKNOWN。RAISED/缺回调保留原 B4 pending pack / provenance，不补造 end 或 finish。 |
| 9. `candidate_final` / `validate_preclose` | 新 FINAL 与 typed ledger/C2 identity；执行计数和科学字段分离。仍要求原 reverse-restore 与 close/wait，不把 metadata 或 RC0 当 Gate1。 |
| 10. `evaluate_waited_eval_case` / `batch_result` / `grade_closed_capture_group` | 新 typed waited/group/grade kind；原实际 child wait 与完整 env/App close 验证闭包保持。完整原 parent 执行 finally 后才调用 grade；独立 outer parent `Popen.wait` 仍单独必要。 |

实际 AST 差异是 contract 四函数、runtime 六个元数据函数、worker 的 `main`、observer 两个既有节点 + 八个新增 helper；旧 generic recorder/materialize 被移除。三个原 observer 源绑定/RNG-counter/restore 函数、bootstrap、完整 parent 与十五个资源/加载/close runtime 函数受等价检查；不是声称只改了十个函数。

## 真实 wire ABI

以 `PRODUCER_ABI.json` 和实际 contract 常量为准：

- TASK `PHASE1_TYPED_NATIVE_CAPTURE_E3_N80_TASK_V1`；PLAN `PHASE1_TYPED_NATIVE_CAPTURE_E3_ONLY_PLAN_V1`。
- integration / WORKER_SCENE_READY / WORKER_EVAL_STARTED / PRE_CLOSE kind：`PHASE1_TYPED_NATIVE_CAPTURE_SOURCE_V1`。
- case FINAL：`PHASE1_TYPED_NATIVE_CAPTURE_E3_N80_FINAL_V1`；common-start：`PHASE1_TYPED_NATIVE_CAPTURE_COMMON_START_V1`；group FINAL：`PHASE1_TYPED_NATIVE_CAPTURE_GROUP_FINAL_V1`。
- waited / closed-grade：`PHASE1_TYPED_NATIVE_WAITED_EXECUTION_SEMANTICS_V1` / `PHASE1_TYPED_NATIVE_CLOSED_SOURCE_GRADE_V1`。
- 原 PARENT_STARTED `ONEGPU_PHASE1_PASSIVE_CAPTURE_E3_ONLY_PARENT_V1`、完整 AppV6/Base 内部 close kinds、`PHASE1_CAPTURE_GROUP_CLOSED_SOURCE_GRADE_V1.json` 文件名保持旧值。
- 异常 artifact `cases/E3/TYPED_CAPTURE_INCOMPLETE_V1.json`，kind `PHASE1_TYPED_NATIVE_CAPTURE_INCOMPLETE_V1`；不是成功 FINAL。

`FINAL.sensor` 是原 B4 `PASSIVE_SENSOR_CAPTURE_V3` 完整 report；`control_ledger` 原 kind `BOUNDED_TYPED_CONTROL_LEDGER_V1`，原键 `normal_channel_records`（不是 `normal_records`），原全部 control packs / MID+END 五通道 / pre-reset / reset / post-return / END actor35 / B3 callback provenance 均保留。full80 flags 与原 int32/int64 K0..80 reset IDs 不被裁成8行；缺回调不是观察到 empty IDs。

`FINAL.actuation.capture_schema=PHASE1_TYPED_C2_EVENT_WINDOWS_V1`；每条原事件仍是 `ACTUATION_CLOCK_SCOPE_V2_SOURCE_DISABLED`。原所有 event 键、args/kwargs、12 queue fields、raw tick、scope、selected target、status/outcome/exception 保留。`event.tick` / raw_stored_counter / parent context 是原未验证 event clock；另列 `adoption_clock` / envelope.source_clock，后者不替代前者。same-asset term context 不是 DOF/target pipeline 或物理读回证明。

唯一 serializer 是已发布 codec 的 `materialize`，在 C2.close -> B4.close -> bridge.close **之后**、原 env/App close **之前**。无 float cast；int64 `2**60+7` 与 bool 的 own-fake JSON 数值测试保真。header 保留原 dtype/shape/device/axis/source/clock；JSON 本身不构成 SDK 或索引/来源独立读回证明。

## 十项新增 SOURCE 测试

`test_typed_native_source.py` 只加载完整 stdlib 元数据模块、显式 own `FakeTensor` 与 AST；不调用 worker.main、真实 B4/C2 hook 安装、真实 tensor/SDK/DR。没有重跑旧套件，也没有将父 CPU 报告当本封件结果。

1. 完整冻结依赖/155+182 源闭包和 34 全文件 overlay、完整 static-tree pending。
2. 实际 ABI/wire、新旧 kind 负例，执行计数与 science/SDK/Gate1 分离。
3. 完整原 setup AST 前缀、原 reset/compute/init/step 单次、begin/end 顺序。
4. 完整已发布 B4 default 固定 22 函数 + 3 codec class / FieldSnapshot proof，空 pins 负例。
5. C2 full80 原 owned buffer 无二次复制/选择/cast，outside materialize 保留 int64/bool。
6. 原事件全键、原 tick != adoption clock、小 JOINT IDs UNKNOWN、context 不签 DOF/pipeline。
7. C2 first2/last2 和中间 UNKNOWN，原有限 cap 负例。
8. 原 pending 对象/RAISED/provenance 不补造 finish/end，逆序 restore 即使有冲突仍尝试全部。
9. 完整原 parent bytes、资源/close 等价与 App binding 原 false-epoch/完整 helper 验证。
10. 默认 native install 顺序、export 晚于 restore、无新增 MDP/RNG/SDK getter。

复核只运行以下 NEW SOURCE 测试，明确不是 SDK 命令：

```powershell
& 'C:\Users\lulu\AppData\Local\Programs\Python\Python314\python.exe' -B '.\mod4v1_supermimic_bptt_20261102\source_phase1_typed_native_capture_v1\test_typed_native_source.py'
```

`seal_source.py` 是本地 one-shot SOURCE seal；产物已存在即停止，原封件不覆盖。`SOURCE_RECEIPT.json` 记录本次 10 项结果、完整 pins、audit 与实际禁用操作；`SOURCE_SEAL.json` 对全部 15 个成员封存。

## 明确剩余 blockers（本次不执行）

1. 父 review 新 purpose/newkind/sourcehardpin 和独立完整八 runtime/static banks/vendor7 baseline 的真实来源与完整 future materializer；34 文件 overlay 不替代这些原树，不使旧 gate 自动接纳新 worker。
2. 新原资源 gate / CPU 或 SDK/native 验证由父另行放行；本次 SDK/MRO/active binding/同实例现场证据均 UNKNOWN。原 C 账本/owner/EX/canonical 规则与原成本协议不变，真实 settlement 仍待原协议证据。
3. outer controller 实际 parent `Popen.wait`、完整 child wait/AppV6->Base 关闭/双 EX release 的现场 receipts；SOURCE 和 close-intent 都不代替实际 wait。
4. A194 NEW pure consumer 检查实际 typed payload；actual clean/noise/delay/partial-reset/100Hz 时钟与返回 identity、untapped actor35 对照、逐行 episode freshness、真实原 callbacks/RNG 无扰动、C2 窗口可用性/JSON footprint 仍需现场证据。全 MID35/clean35、private RNG-state equality、非 witness sensor rows、中间 C2 windows、SDK 物理 readback、DOF/target pipeline join 保持 UNKNOWN。

Stage2 native training 未放行。本 SOURCE 封件不产生技能结论或 Gate1 PASS。
