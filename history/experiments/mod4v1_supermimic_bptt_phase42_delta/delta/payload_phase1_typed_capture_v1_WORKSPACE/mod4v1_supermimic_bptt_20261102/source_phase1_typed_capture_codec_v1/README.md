# Typed capture codec + bounded control ledger v1

**SOURCE_ONLY；Gate1=UNKNOWN；Stage2=False。** Catalog只有Office/ACL技能，与本题不匹配；使用FS/Python3.14 `-B` stdlib。新目录独立实现小codec与ledger，不是worker/stager/controller，不import Torch/SDK、不创建env，不修改旧设计7件/B2/V4/C1/C2。C2目录/报告未访问；真实Torch CPU由父另行执行。

## 1. 文件与职责

- [codec与ledger](<typed_capture_codec.py>)：唯一实现模块，只import `math`；无旧runtime依赖。
- [NEW schema](<SCHEMA_V1.json>)：字段、四种显式role、clock、retention与UNKNOWN。
- [12项own fake/metadata/AST检查](<test_typed_capture_codec.py>)：FakeTensor测试接口，不是SDK或真实Torch验证。
- [SOURCE pins](<SOURCE_PINS.json>)：固定上游设计7件与B2/V4/C1只读SOURCE引用；不是运行许可。
- [SOURCE receipt](<SOURCE_RECEIPT.json>)、[seal](<SOURCE_SEAL.json>)：最终测试/审计与固定bytes/SHA。

## 2. 拟冻结API（已实现）

```python
from typed_capture_codec import CaptureCodec, ControlLedger, CaptureError

codec = CaptureCodec(tensor_type, *, witness_index, witness_env_ids, n=80)
envelope = codec.capture(tensor, *, role, source_ref, source_field,
                         clock, env_axis, group=None)
codec.validate_owned(envelope, *, allowed_roles=None)
json_tree = codec.materialize(value)  # ONLY outside original callback/control loop

ledger = ControlLedger(codec, *, controls, run_id)
ledger.begin(control_index, *, clock)
ledger.normal_sample(channel, slot, clean, *, clock, payload=None)
ledger.pre_reset(term, trunc, *, clock, event_id, payload=None)
ledger.reset(ids, *, clock, event_id, before=None, after=None, outcome='RETURNED')
pack = ledger.end(*, post_term, post_trunc, clock, actor=None)
owned_tree = ledger.finish()
json_tree = codec.materialize(owned_tree)  # explicit separate outside-loop phase
```

上面是**签名说明**，不是可直接执行的Python调用语法；实际调用中的`*`由Python关键字参数完成。`tensor_type`由父传入已有Tensor类，`witness_index`由调用方传已有一维int64、同device的索引tensor，`witness_env_ids`为明确Python列表/tuple（1..8个唯一0..79整数）。codec不创建arange，不读取索引tensor数值以对比列表；输出明确`CALLER_DECLARED_INDEX_BINDING_NOT_READBACK`，不冒充实测row mapping。source_ref也是caller给出的来源引用，codec不承担SDK source资格检查。

### 显式role，不按shape猜类型

| role | 验证与选择 | metadata/ownership |
|---|---|---|
| `ENV_ROWS_WITNESS` | caller显式env_axis且该axis长度80；已有同device witness index；`detach().index_select(axis,index)` | 选择前保存真实shape/dtype/device/axis；index_select自身产生owned storage，不再clone一次；保留≤8行及显式env IDs |
| `ENV_IDS_FULL` | 一维K≤80、原integer dtype、env_axis=None；`detach().clone()` | 整条保留，包括K0/K79/**K80**；不cast int32→long，不把IDs当env轴 |
| `TERMINAL_BOOL_FULL` | 原bool[80]、env_axis=0；`detach().clone()` | pre/post term/trunc各自完整80，不OR、不nonzero、不any |
| `QUEUE_GROUP_FULL` | 明确legs/wheels group及env_axis长度80；`detach().clone()` | 原queue group**全部80行**，其余slot/width维原样；这是NEW角色，明确修正旧设计中“其他tensor泛化witness8”的queue例外 |

四种role全部先存metadata再选择/复制。旧设计的`source_pin_ref`保留，并增加等值`source_ref`对应API参数；原dtype字符串、original_shape/retained_shape、source_env_axis、显式row_mapping、original_device和原clock全部保留。`evidence_level=OWNED_TENSOR_SNAPSHOT_NOT_SDK_PROVENANCE_QUALIFICATION`不宣称实地验证。裸tensor、未知role、伪造/缺失metadata均触发`CaptureError`。

`materialize`只对已owned tensor执行outside-loop `detach().cpu().tolist()`；不再clone、cast、`float()`或假设float32。Python int（包括>2^53）、bool保留其native类型，浮点值连同真实dtype metadata保存；这是JSON typed envelope，不是无损bitwise tensor格式，也不隐式重建为float32。非JSON/非finite内容报metadata错误而非静默改数。callback内没有CPU拷贝、JSON或文件I/O。

## 3. Ledger接点与严格所有权

1. 原control循环调用`begin(index, clock=原存储clock)`，顺序0..controls-1、一次一个open control；controls仅64或128。
2. B3原feedback hook只在原normal采样点调用`normal_sample`：slot为小写mid/end，channel为原五通道，clean envelope的原shape分别80×3/3/4/4/2。传入**已经owned**的原payload树；ledger只验证metadata和保存引用，既不clone也不重新采样。两个slot每个五channel，最多1280 normal records；clean16 witness最多32768 scalar。
3. 原termination hook已经完成一次原compute/bridge pre capture后，调用`pre_reset`，传已有完整term/trunc与已有s1/cache payload。s1、sensor cache等仍witness≤8；若payload含queue group则必须明确full80 role。重复引用同一已有mask合法，不再复制。
4. 原reset wrapper保持其原调用/返回/异常，在finally或完成时调用`reset`，传**原callback IDs的owned副本**、已有before/after与原outcome。每原step最多一个此callback；重复metadata callback报错。outcome RAISED也保留IDs与已得before/after并标INCOMPLETE。没有原callback就不调用，pack保持`NOT_OBSERVED, ids=None`，绝不伪造空IDs。K0的实际callback与没有callback明确不同。
5. 原`bridge.step`及严格boundary检查之后，worker未来薄接点调用`end`传原post term/trunc和可选原END actor35 witness。缺actor/pre/normal记录只标INCOMPLETE及字段名，不补值、不补obs/reset。actor仍50Hz；MID19/MID fullclean35/MID actor35/terminalclean35为UNKNOWN。`end`不替代原strict boundary。
6. outside-loop `finish`返回already-owned树，再显式materialize。若有open control，先报告metadata错误，不擅自合成post flags。只有记录控制数量满足时`all_controls_observed=True`，这只是数量，不表示每pack完整、更不是Gate1。

reset记录保存**调用时已存在的prior_termination_event_id**；稍后补来的pre不反向修复配对。run/control/event IDs加原physics/feedback/common counter/phase/reset_depth保留因果上下文；事件ID是metadata不是时钟。原clock字段名与值保持B2形式，不修整tick-1、不改变counter。normal只接受原`is_original_100hz_slot=True`、phase=scene_update/depth0，MID tick%8=4、END正tick%8=0；reset内部或obs重复call不计为normal。

**Ownership handoff**：`capture`产生的owned buffer及metadata交出后由调用方只读；ledger保存相同对象引用，不用第二次clone强行隔离恶意后续修改。`validate_owned`检查metadata形状/dtype/device和显式role，但不读tensor数值或重新证明ID范围/索引内容/噪声公式/真实物理效果。普通payload内每个tensor都必须先通过显式role envelope；没有“shape80就自动ENV行”的fallback。

## 4. 保持与边界

- 原reset→fall/publish→obs、actor raw35、物理DT/decimation/DR/acceptance、SDK return identity/异常、资源/EX/关闭链均由原owner保持；本模块不接触这些原函数。
- 无新SDKgetter/audit/getstate/nonzero/any/obs/reset/RNG；无Torch import、index allocation、训练、stage/dispatch、全FINAL/trace访问。
- CaptureError是instrumentation metadata失败，不是重放原call、补采样、fallback getter或放宽acceptance的理由。B3仍须按原try/except guard保留原回调次数/identity/异常，并记录INCOMPLETE；此目录不接入B3，也不修改C2/controller。
- fullqueue80与完整IDs/flags的资源开销需要父CPU/后续原资源gate独立确认；SOURCE fake PASS不承诺native耗时/预算，既有deadline/retention上限与Stage2=False不变。

## 5. 本地验证范围

```powershell
& 'C:\Users\lulu\AppData\Local\Programs\Python\Python314\python.exe' -B -m unittest -v test_typed_capture_codec
```

12 tests覆盖四角色、K0/1/79/80、bad shapes/dtypes/role、显式非0 axis与同device索引、large-int/bool/half metadata roundtrip、owned别名隔离、ledger零二次clone、正常双slot、NOT_OBSERVED区别空IDs、异常/晚pre不修复、128cap、fullqueue80、AST无额外路径、旧设计7件/旧SOURCE pins未改。FakeTensor是真正Torch API的受控替身，不是实际Torch/SDK；真实CPU由父另行run，接口Gate1仍UNKNOWN。
