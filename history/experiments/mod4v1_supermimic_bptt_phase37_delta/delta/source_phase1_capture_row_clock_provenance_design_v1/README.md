# Row / dtype / clock / natural-edge provenance：最小 SOURCE 设计 v1

**DESIGN_ONLY_NOT_INTERFACE_QUALIFICATION；Gate1=UNKNOWN；Stage2=False。**

目录仅含说明、schema/toy、stdlib检查和SOURCE pins/receipt；没有worker、stager、SDK实例或新运行器。Catalog只有Office/ACL技能，与本题不匹配；使用FS与Python3.14 `-B` stdlib。未读whole FINAL/trace/PT/raw，未执行Torch/SSH/SDK/GPU/C/资源/Git，未改旧SOURCE，未访问C2目录或猜其pins。

## 1. 实际证据与SOURCE结论分开

仅打开两份允许的小聚合：[science](<../reports/PHASE1_V4_ADMISSION2_ACTUAL_SCIENTIFIC_CAPTURE_APPLICATION_V1.json#L136-L200>)（33575 B，SHA `942a4fc5b5c77d02c86dbf815ba4b0a71f4bb0116f4738a70a0efba74c69a7d3`）与[queue scalar](<../reports/PHASE1_V4_A2_ACTUAL_QUEUE_SCALAR_DIAGNOSTIC_V1.json#L61-L129>)（7898 B，SHA `b9a83cb124b5d202dfaaf7e10420eb8e447f5111fa34676c630ebb3762c21c07`）。前者发布N80/64 controls/512 physics/128 feedback及实际wait/EX闭包；五个组件CONSISTENT，queue组件CONTRADICTED。后者首定位为control0、seq0、`target_write/legs/tick=int(-1)`，不是将-1归零即可消除的采集语义缺口。C2 clock/scope由A194独立负责，此设计只预留原样关联，不给C2起函数名或pins。

聚合已明确：56条retained feedback、38 normal channel slots、144 decoded witness MID/END pairs；72 unique retained events；6 pre-reset端点、4 reset、**0 linked natural edges、0 retained natural terminal witness rows**。这不是“实际没有natural reset”的证明。原dtype大多已丢、rows仅SOURCE声明、RNG完整states未采集，均保持UNKNOWN。

## 2. 确定的三处信息损失

1. [B2 snapshot:33–54](<../source_phase1_passive_sensor_capture_v2/passive_capture.py#L33-L54>)对**所有**首维等于80的tensor执行`index_select(0,row_ids)`；它不识别字段语义。因此长度恰80的reset IDs也会缩成8，长度79则全保留，形成随K变化的不连续语义。不是reset本身只重置8行。
2. [materialize:120–126](<../source_phase1_capture_worker_v4/phase1_capture_observer.py#L120-L126>)把tensor直接变成`tolist()`，没有写入原shape/dtype/axis/row mapping。dtype损失发生在这里；[runtime.put_json:79–86](<../source_phase1_capture_worker_v4/phase1_capture_runtime.py#L79-L86>)只JSON编码/原子写，不再选row。只有[B2:385](<../source_phase1_passive_sensor_capture_v2/passive_capture.py#L375-L386>)另存了noisy return dtype字符串。
3. [recorder:64–111](<../source_phase1_passive_sensor_capture_v2/passive_capture.py#L64-L111>)是混合事件first32/last32，不是每channel/每control配额；[special:22–44](<../source_phase1_capture_worker_v4/phase1_capture_observer.py#L12-L44>)对三类事件独立last4，且terminal hook每control都调用，不只done时。中段reset可留下而其相邻terminal、MID/END或actor已被滚走。`max_events=100000`只是capture上限，不等于保存全部payload。C窗口仍仅[first2/last2](<../source_phase1_capture_worker_v4/phase1_capture_observer.py#L73-L87>)。

## 3. 逐字段provenance表

`KNOWN_SOURCE`是源内可定位；`KNOWN_AGGREGATE`只是上面发布的聚合；两者都不自动变成逐tensor实测。下表的shape是source约束，实际shape/dtype必须从已有tensor元数据记下，不能由列表/默认float32补造。完整文件SHA与35个完整definition的行号、签名、source/AST SHA见[SOURCE pins](<SOURCE_PINS.json>)。

| source字段 → 已有存储 | 行/shape/dtype语义 | clock/phase与现retention | 最低设计 / 当前状态 |
|---|---|---|---|
| `feedback(env,key,raw)` → `feedback.clean`：[B2:339–363](<../source_phase1_passive_sensor_capture_v2/passive_capture.py#L339-L363>) | 原N×w，w=3/3/4/4/2；现只0..7；原dtype随输入 | [原sampling:74–86](<../discovery/reward_command_audit_v1/E3/runtime/isaac/mod4/feedback_delay_runtime.py#L74-L86>)每4物理ticks只执行五个已有term；混合first/last | clean16输入来源KNOWN_SOURCE，保留域内值一致性KNOWN_AGGREGATE；改为每control两normal slot各五channel的typed witness pack，实际dtype/row mapping待新采集 |
| `sensor.cache[key]=(last,noise)`、`bias`、`episode`、`draw_counts` → `sensor_stage`：[B2:364–387](<../source_phase1_passive_sensor_capture_v2/passive_capture.py#L364-L387>) | last/episode是N整数；noise N×w、bias N×4；均witness8；draw_counts是完整小scalar dict | before/after同原call；`fresh_due_local`未存 | 各tensor保留自己的source_shape/dtype/mapping；local due仍UNKNOWN，勿新算GPU due mask |
| delay实际输入 → `delay_actual_input`；原输出→`actual_return/feedback.return`：[B2:388–402](<../source_phase1_passive_sensor_capture_v2/passive_capture.py#L388-L402>) | N×w，不做cast或反推noisy-clean | 同feedback clock，first/last | 8行typed envelope，actual return与used noise保持各自原dtype |
| `delay.cache[key].last/cur/out/sample_tick/ready`、delay/episode → before/after：[B2:320–325](<../source_phase1_passive_sensor_capture_v2/passive_capture.py#L320-L325>) | last/sample_tick/episode整数N，ready bool N；cur/out N×w；8行 | `sample_tick`可能前一100Hz tick；reset后-1是原合法sentinel，不混同非法writer clock | 原缓存字段已存在KNOWN_SOURCE；每字段记语义而非按shape推role。warmup/同tick复用不能叫fresh |
| `_clock` → physics_tick/feedback_tick/common_control/phase/reset_depth：[B2:309–318](<../source_phase1_passive_sensor_capture_v2/passive_capture.py#L309-L318>) | 小Python scalar，不是row tensor | normal=`scene_update && reset_depth==0 && tick%4==0`；MID tick%8=4，END正tick%8=0；初始化tick0单列 | 原样留raw counters、原phase与控制loop index；不拿common_step_counter或C1 tick修造physical tick，不把reset内部重复call算normal sample |
| `bridge.pre.term/trunc` → terminal payload：[bridge:93–96](<../source_runtime/native_supermimic_bridge.py#L93-L96>)、[B2:411–422](<../source_phase1_passive_sensor_capture_v2/passive_capture.py#L411-L422>) | 原桥已分别clone全N80 masks；B2现误按通用selector缩8。s1是N×physical-width，仍只8行 | 原termination compute之后、真正reset之前；special last4 | **仅term/trunc保留完整80 bool**，dtype/shape实记；s1仍8。无需新增pack/term计算、SDK getter或nonzero |
| `state.terminated/truncated`、transition的term/trunc/xi1_valid/ep_step → [bridge:141–144](<../source_runtime/native_supermimic_bridge.py#L141-L144>) | 已存在的分离bool flags；transition不是新重建。除term/trunc两mask外其他tensor只8行 | env.step返回后，boundary严格检查之后；当前只有sum counters，没有每control masks序列 | 每control记post-return完整term/trunc及来源，可复用已有owned clone；不要为observer再OR/nonzero或调用context/pack；xi1 terminal已mask，勿当terminal clean35 |
| `_reset_idx(ids)`原入参 → reset.ids：[B2:423–447](<../source_phase1_passive_sensor_capture_v2/passive_capture.py#L423-L447>) | **ID列表轴不是env行轴**；K∈[0,80]整条保留；原SDK[248–253](<../discovery/sdk_reward_command_call_order_v1/envs/manager_based_rl_env.py#L248-L253>)已nonzero→squeeze→`.int()`，不可猜long | 同一次原调用的entry/before/after；special last4 | 完整既有IDs，K=80也不切；不重新nonzero。没有callback时写NOT_OBSERVED，不伪造空IDs或触发reset |
| reset前后`sensor_episode/delay_episode/delay.cache` → before/after | episode/cache仍仅witness8；全IDs不等于全部80行episode状态 | 同一个原reset调用前后，reset depth/phase标识保留 | atomic boundary pack关联相同control/event；外部rows的episode正确性仍UNKNOWN，不为全量证明复制N80其他tensor |
| `state.obs['policy']` → actor35_original_buffer：[worker:142,161](<../source_phase1_capture_worker_v4/worker_passive_interface_v1.py#L135-L164>) | N×35，原返回对象identity；8行；actor不是clean | 初始0及每50Hz返回后，special last4 | typed8行原actor，不重建、不调用compute_obs/clean_policy。untapped bitwise仍UNKNOWN |
| 初始sensor memory → [initial_sensor_memory:98–117](<../source_phase1_capture_worker_v4/phase1_capture_observer.py#L98-L117>) | existing dict/cache/FIFO、8行、dtype未存 | 原reset53→place55→compute66之后、同tick可能旧cache | clean0保持UNKNOWN；保存已有last/sample_tick/episode等，绝不invalidate/tick++/重新抽样 |
| C1 queue12字段、write args、static → [C1:40–75](<../source_phase1_actuation_capture_v1/actuation_tap.py#L40-L75>)、[143–181](<../source_phase1_actuation_capture_v1/actuation_tap.py#L143-L181>) | C1目前full tensor clone，随后tolist丢dtype/axis；目标可能有显式env_ids子集，不能仅看首维认全env轴 | queue tick来自原参数；term/setter `counter-1`、method固定group；首/末2control | C2负责clock/parented writer；这里仅要求其最终原始字段能进入同样typed envelope，target子集row mapping引用**已有**env_ids参数，未知则UNKNOWN。不访问/实现C2 |
| stored_rng_counts → [observer:90–95](<../source_phase1_capture_worker_v4/phase1_capture_observer.py#L90-L95>) | 仅sensor.draw_counts scalar dict | before/after与sensor_stage.before/after；无完整states | 支持限定SOURCE/call-count论证，既非bias/delay全部抽样计数，也非全局RNG状态相等 |

## 4. MID clean35 / actor35：本目标不需要新增

五channel的16维是原100Hz sampling函数实际已经计算的raw参数；每control MID/END各一次，保持pre-manager scale，量纲见[SOURCE channel表](<../source_phase1_passive_sensor_capture_v2/source_api.py#L20-L23>)。其余19维（command3/height1/wheel-pos2/last-action6/mode7）在MID没有同一次完整clean actor采样；此设计不补造，即使某项是常数或看似可沿用END值。actor只50Hz；要证明“原actor消费噪声/延迟后的16通道”用**END原返回raw35 + 同tick既有缓存 + 原scale**的离线关系即可，MID仍只校验原clean16/used-noise/delay链。MID full clean35、MID actor35、terminal clean35均UNKNOWN_NOT_COMPUTED；不调用[clean_policy / sensor_sdk_audit](<../discovery/reward_command_audit_v1/E3/runtime/isaac/mod4/feedback_delay_runtime.py#L88-L147>)，这些方法会新增observation/getter甚至涉及RNG-state查询。

## 5. 最小候选变化：只设计，不改已封函数

| 候选接点（未来新lineage） | 最小变化 | 仍需保持完整不变的原调用/函数 |
|---|---|---|
| B2 `tensor_snapshot_adapter` + `PassiveCapture.attach` 的snapshot callsites | typed snapshot明确三种role：ENV_ROWS_WITNESS、ENV_IDS_FULL、TERMINAL_BOOL_FULL。在**选择前**记source_shape/dtype/source_env_axis，在选择后记retained_shape/显式row mapping；默认未知role不按首维猜测。原数据不cast，不动输入；metadata来自已有tensor属性，不是SDK getter | 每个原sensor/delay/update/terminal/reset函数一次、原参数/返回对象/异常原样；原MRO/class descriptor/source-byte检查仍完整。新B lineage需由父与B owner接线并重封，非本目录实现 |
| V4 observer `materialize` | 对typed envelope只转换已owned tensor数据；metadata原样通过，旧opaque/UNKNOWN不补float32。纯runtime `put_json`不需变化 | 无callback内CPU拷贝/JSON/I/O；不改App binding/close/64MiB现有上限 |
| V4 observer recorder retention | 现有已snapshot的normal feedback payload按control关联，每control MID/END各5channel；额外保留完整小mask/IDs的atomic boundary pack。避免复用last4拼接天然边 | 完整physics/feedback/step/reset/actor调用不变，无新采样；现first/last诊断可原样留，不改global-slot计数成per-row fresh计数 |
| V4 worker已在`bridge.step`前后的control上下文 | 用现有Python loop index关联tap metadata，保存现有pre flags、post flags，绝不新求reset IDs或操作env clock | [worker:104–126](<../source_phase1_capture_worker_v4/worker_passive_interface_v1.py#L102-L126>)原53→55→66、bridge.device boundary、[157–164](<../source_phase1_capture_worker_v4/worker_passive_interface_v1.py#L153-L164>)for_action→one bridge.step→after_original_step；原[SDK step:192–273](<../discovery/sdk_reward_command_call_order_v1/envs/manager_based_rl_env.py#L192-L273>)、完整bridge与E3 reset/step一字不改 |
| C2接口 | 等父/A194最终SOURCE/API，消费原parent/scope/clock字段；本设计不预测实现或pins | C/资源/canonical/actor/raw35/物理/DR/接受条件不动 |

**保留界限**：仅原64或128controls；normal sample packs上限`128*2*5=1280`条、每tensor最多8 witness行；clean16最大`128*2*8*16=32768` scalar（其他used-cache字段单独计预算）。boundary packs最多128条，每条分别全80 bool term/trunc及真正callback的完整K≤80 IDs；s1、episodes、所有其他tensor仍8行。所有mask/IDs完整保存到每control的小ledger，未借`any()/nonzero()`选“有趣事件”。无callback→NOT_OBSERVED；不为了coverage多reset。超cap/缺channel/缺edge写不完整/UNKNOWN及范围，不补值、不延长deadline、不增自我approval flag。

天然link的键是`capture_run_id + worker_control_index + termination_event_id + reset_event_id`，另保留同一次call的原physics/feedback/common counters、phase、reset_depth。事件ID只是observer元数据，**不是物理时钟**。entry原flags→同control原reset IDs→witness episode/cache before/after→原post-return flags/actor必须成同一pack；不可只按相等tick跨reset配对。对未保留或非witness行的episode/cache验证仍UNKNOWN。初始显式reset发生tap安装前，单独声明，不伪装natural edge。

## 6. 初始binding / 原adapter target-check：已有数字，不新增readback

准确singular函数是[verify_actuation_binding:129–170](<../source_phase1_capture_worker_v4/phase1_capture_observer.py#L129-L170>)，由[worker:133](<../source_phase1_capture_worker_v4/worker_passive_interface_v1.py#L129-L140>)调用；**定义在observer，不在runtime**。它认证queue/adapter类与原process/apply wrapper的source/code；现`target_writers`仅保存group、setter method、same-asset identity、bound-self关系、module/qualname，**未保存`term._joint_ids`，也未认证SDK setter完整source**。same asset context不是same DOF集合。

原D4 [完整apply:38–55](<../discovery/reward_command_audit_v1/E3/runtime/isaac/mod4/action_delay_sdk_adapter.py#L38-L55>)已经调用原apply一次、恢复原_processed_actions，随后自己读取`asset.data.{joint_pos_target|joint_vel_target}[:,this._joint_ids]`，计算error、更新`formula_max_error`、assert≤1e-6，最后`calls[key] += 1`。这是**原adapter已有target-buffer检查**，不是observer独立readback；也不等于物理关节/执行器效果。此设计绝不再次读取asset.data、计算GPU差值或调用[audit:72–73](<../discovery/reward_command_audit_v1/E3/runtime/isaac/mod4/action_delay_sdk_adapter.py#L72-L73>)。

| 可从已验证实例的已存`__dict__`取得 | 未来仅metadata快照 | 当前证据层级 / 未知 |
|---|---|---|
| adapter.calls、formula_max_error、collect、terms | 初始/结束各一次，只复制小Python int/float/bool/dict；记录同adapter实例/source pin与control范围。缺键/非plain scalar→UNKNOWN，不调用property/audit | SOURCE_AVAILABLE；A2未发布这些原数字快照，不补造512/0。calls在assert后增加，结合delta只覆盖对应成功的原apply检查，不自动覆盖运行前/异常路径 |
| 每group原term与已存_asset身份 | 原样记录group、term identity、asset identity及setter方法名；原已保存的module/qualname继续保留 | 当前binding已观察，但SDK setter source资格仍UNKNOWN |
| `object.__getattribute__(term,'__dict__').get('_joint_ids')` | 存储为Python list/tuple/slice时原样保留顺序/类型/切片三元组；如果是tensor，只留已有shape/dtype/identity，**数值UNKNOWN**；缺键也UNKNOWN | 不能因source使用_joint_ids就宣称实际实例已有可读Python DOF列表；不通过getattr触发descriptor，不展开未知slice、不新取GPU values |
| 原setter args/kwargs中的`joint_ids/env_ids` | 使用C owner已经捕获的原参数；env-axis与DOF-axis分开，显式env_ids子集mapping，不按shape猜role | 需要未来C2实际parent/scope与binding term/asset一致；本设计不猜C2API、也不访问其目录 |

未来consumer的严格join必须同时具备：同run/同asset、binding中的term及可知DOF IDs、正确setter method、原writer args/kwargs IDs、实际parent/scope关系。没有任一项即UNKNOWN/UNJOINED；setter kwargs缺失不凭legs/wheels名补默认DOF。stored `formula_max_error/calls`可标为`ORIGINAL_ADAPTER_STORED_CHECK`，`observer_independent_readback=UNKNOWN_NOT_CAPTURED`与`external_physical_effect=UNKNOWN`分别保留；不把原adapter已有assert包装成observer新实测或自我approval。

## 7. no-extra-draw的可支持范围

- [SensorCorruption.apply:28–38](<../discovery/reward_command_audit_v1/E3/runtime/isaac/mod4/sensor_mild_math.py#L28-L38>)的原noise draws只在原due分支，draw_counts记录noise抽样行数；[reset:20–26](<../discovery/reward_command_audit_v1/E3/runtime/isaac/mod4/sensor_mild_math.py#L20-L26>)的bias rand没有同一counter。[FeedbackDelay.reset:9–15](<../discovery/reward_command_audit_v1/E3/runtime/isaac/mod4/feedback_delay_mild.py#L9-L15>)有原randint，而apply无RNG。这些完整原函数应逐bytes/AST保持不变。
- SOURCE侧可核验新snapshot/recorder/materialize只有detach/index-select/clone/已存字典元数据，没有rand/RNG-state/getter/obs/reset调用；每wrapper原call数量、原返回identity/异常、实际已有draw_counts前后与callback计数可支持**限定的无额外draw源路径声明**。相同tick也不应为了对比再调用sensor/apply或policy。
- A2聚合只证明已有counter顺序CONSISTENT、no-extra-draw为SOURCE声明；bias_rng/noise_rng/delay_rng/全局Python与Torch完整state equality、无tap反事实及原始actor bitwise均UNKNOWN。不要求新增get_state/get_rng_state/state_dict/export_resume，后两者还可能触发额外SDK读取；不发明自我许可字段。

## 8. 交付与检查

[schema与明确synthetic toy](<schema_example.json>)定义逐tensor envelope、完整ID/mask例外、normal sample pair与同control边界；toy使用不同dtype并含witness外row79的terminal，不是A2数据。[8项stdlib检查](<test_provenance_design.py>)只hash/AST现有完整SOURCE及验证toy元数据；不import任何目标模块。最终范围/测试结果见[receipt](<SOURCE_RECEIPT.json>)。设计完成不等于采集合格，整A2/Future新候选的未知项与Stage2=False保持不变。
