# Phase1 E3/N80 被动接口验证：SOURCE worker V2 / 三项最小修复

## V2 source derivation，wire V1 保持

本目录是新SOURCE lineage `source_version=2`。V1的13封件文件、原17来源、B/C、旧materializer全部原封保留；task/plan/sourceIndex typed kinds、purpose、安装alias及9336B/d557 parent不变。新真实group由父创建为`MOD4V1_PHASE1_E3_PASSIVE_CAPTURE_V1_BOOTSTRAP_FIX_V2_<unique>`，不复用已消费V1 root。本地测试不是新native admission。

| 必要修复 | 原始证据 / V2差异 | 分类 |
|---|---|---|
| preSDK bootstrap | V1实际worker35报`ModuleNotFoundError: No module named 'launch_storage_contract'`；实际3675行inventory唯一完整alias为`worker_sources/parent/launch_storage_contract.py`(117B/e40b51…)与`worker_sources/parent/n80_gpu_capacity.py`(653B/ab26d1…)。首次导入前加group该真实目录并核完整来源/实际module/function/cached污染，不写stub、不截半函数。 | ACTUAL_V1_TRIGGERED_PRE_SDK_MODULE_RESOLUTION_FAILURE |
| 非fast returned元数据签名 | canonical core491实际签名为`_validate_returned_app_binding(binding, helper)`；V2恢复第二参数为已加载的完整AppV6 helper。 | SOURCE_UNTRIGGERED_BY_ACTUAL_V1 |
| binding严格对应 | 默认`put_json`仍加epoch；仅原binding写入显式`add_capture_epoch=False`，所以独立文件的原binding与intent/returned严格相等，未删collector字段、未跳校验、未改fast mode。 | SOURCE_UNTRIGGERED_BY_ACTUAL_V1 |

V1现场是**preSDK bootstrap中断**：无common GO、producer counters/FINAL缺失仍为null，不是技能0%。原parent实际wait与两EX释放及wall成本保留在父取证report；后两项只是在该现场未触发的独立源码缺口。具体证据路径/完整SHA、V1冻结seal与最窄diff写在[CAPTURE_SOURCE_INDEX.json](<CAPTURE_SOURCE_INDEX.json>)的`source_derivation`，不是改写V1历史。

### D664 metadata-only bootstrap API

```python
# Only after ordinary stdlib-safe worker-module import; do not call worker.main.
value = worker_passive_interface_v1.bootstrap_original_helpers(group)
modules = value['modules']  # launch_storage_contract + n80_gpu_capacity, FULL originals
receipt = value['origin_evidence']
# Do NOT call parent_five_storage / capacity_ctor / an SDK factory for this test.
```

入口仅读取`group/worker_sources/parent`两个完整已知源码、正常import并核actual `__file__`/spec.origin/bytes/SHA/函数compiled-code/缓存污染；返回真实module与来源证据。既不使用本地Windows provenance路径作为部署路径，也不以group根/runtime/lib猜alias。metadata入口不创建storage、不调用capacity constructor、不构造SDK、不授予resource admission。父后续仍需独立Linux metadata import/Root alias验证。

## 交付边界

- **SOURCE candidate，非技能评测、非训练、非实际SDK验证。** PURPOSE=`NEW_PASSIVE_INTERFACE_PROBE_NO_TRAIN`，E3-only/N80，默认64 controls、可选128；完整原8-role catalog仍保留，其余7成员deferred。`synthetic_zero6`仅显式合成动作tape；模型PT读取0，teacher=None，learner/optimizer/replay创建0。
- 实际stage/dispatch/SSH/PT/SDK/native/GPU/resource gate/canonical/锁操作均0。SOURCE的fake PASS既不是现场接口合格，也不是技能0%或旧160/1600分母。
- 输出始终`capture_interface_passed=False / gate1=UNKNOWN / exact=False / stage2_GO=False`；独立记录bounded execution与coverage inconclusive。

## 具体入口与原始顺序

[worker_passive_interface_v1.py](<worker_passive_interface_v1.py>)保留唯一formal E3 setup：原[worker_formal_bound_only_v1.py:53–66](<../source_bound_only_native_integration_v1/worker_formal_bound_only_v1.py#L53-L66>)的reset53→E3 fall/publish55→已存在compute66。原DR memory getter63属于原setup，不额外添加observer SDK getter。物理dt=.0025、decimation8、control=.02、100Hz反馈、TGS32/4、.01闭环/.01mimic、原DR/命令/phase/speed/acceptance保持原状。

1. 原poseCacheV4在唯一原显式reset前安装；原66返回的obs原样传入原NativeTaskBridge(initial_obs=obs,teacher=None)。init_state恰好一次，没有fallback compute。原bridge完整pack/context的原SDK读取是其本来行为，不冒充纯tap。
2. 同一env/bridge实例上，先安装已封件B sensor，再安装已封件C actuation。实际env MRO/function/module/code SHA检查由B原preflight完成；actuation queue/adapter/process/apply再做实际绑定与原code/source校验；SDK target writer仅绑定观察，不冒充physical readback。
3. `OriginalEpisodeBoundary.for_action → bridge.step(zero6) → after_original_step(terminated,truncated)`；原bridge内恰好一次原env.step，原terminal pre-reset保留；actor35直接取原返回policy buffer。同对象/shape只证明来源，untapped bitwise仍UNKNOWN。
4. 原66同tick可能合法复用旧sensor/delay cache，**initial不是fresh clean0**。`trace.initial_sensor_memory`保存现存cache/FIFO/cur/out/last/sample_tick/episode及既存时钟；缺值UNKNOWN。不invalidate、不tick++、不重抽、不多reset。自然mid1/end2反馈才进入B的实际clean16输入捕获；full clean35始终UNKNOWN。
5. 结束时依次actuation→sensor→bridge restore，再一次bounded trace/FINAL export，最后原env.close→完整AppV6/Base绑定→原App.close。所有close均尝试；冲突保留为错误。App fast intent不代替实际p.wait。

## 继承的V1 10个最小调用点差异（V2额外仅上列三项）

| 调用点 | NEW差异 | 原逻辑保留 |
|---|---|---|
| [runtime.select_requested_roles](<phase1_capture_runtime.py>) | NEW purpose、E3-only、64/128 capture_controls | 原完整8角色catalog与全source/static inventory |
| [runtime.make_task / validate_group_task](<phase1_capture_runtime.py>) | NEW kind/role/合成动作/PT0；同一installed group/runtime root、预SDK GPU==CUDA_VISIBLE_DEVICES及deadline>now、两唯一非负fd/fstat、实际admission | 原FD仅fstat，未发明kernel/path锁检验；无新增acquire/release/owner/budget writer |
| [parent.main](<single_gpu_passive_capture_parent_v1.py#L11-L78>) | import/metadata NEW；45行明确1个E3成员 | 原17–44、46–78逐行一致：1800等待、私GPU_EX+finiteEX、只读canonical、ready、Popen.wait、finally全部wait后EX释放 |
| [worker.main setup](<worker_passive_interface_v1.py>) | 从原formal setup投影E3；移除A1 PT/actor，仅teacher=None | 原53→55→66；pose/DR/资产/阈值/原guard |
| [worker.main capture](<worker_passive_interface_v1.py>) | 原bridge+sealed B/C；zero6、64/128；original-buffer witnesses | 不增加plant step/reset/compute/RNG/observer getter |
| [observer.make_recorder / initial_sensor_memory](<phase1_capture_observer.py>) | bounded first/last+global100Hz call-slot统计、initial现存cache | global slot != per-row episode fresh；clean0 UNKNOWN |
| [runtime.close_original_eval_resources](<phase1_capture_runtime.py#L276-L334>) | 机械复制原evalclose365–421；仅NEW capture labels、preclose、App调用epoch | 原env.close/App.close次数、full AppV6→Base、fsync intent与错误链 |
| [contract.validate_preclose](<phase1_capture_contract.py#L115-L131>) | NEW capture FINAL/count/restore语义，不读取teacher质量 | 不调用/放松原training `_validate_final_for_intent`；不借旧qualityTrue |
| [runtime.evaluate_waited_eval_case](<phase1_capture_runtime.py#L212-L240>) | NEW FINAL、实际counts、envclose、原App binding/intent或returned | 只在原parent actual p.wait后调用，RC0单独无效 |
| [runtime.batch_result / grade_closed_capture_group](<phase1_capture_runtime.py#L243-L272>) | NEW execution与coverage语义、GO→终点wall metadata | 原PARENT_EXIT_SCOPE全部child waits+完整EX释放仍必需；outer parent wait单独pending |

## 有界证据，不伪称全Gate1

- Sensor使用sealed B原API，first32/last32/max100000；额外特殊ring各4个terminal/reset/actor，witness rows0..7同device clone。Global100Hz counters仅`channel+global physics/feedback tick` call slots；**per-row episode fresh due/pairs仍UNKNOWN**，不得混同B原episode+tick+key缓存证据。
- Actuation原sealed C capacity8192、每control drain，只保留前2/后2 control windows；cap仅限制storage，原C cap后仍clone每个event。无每tick JSON/CPU export。该成本明确保留，不以PT0宣称SDK wall免费。
- 自然terminal/partial-reset未出现时，coverage报告inconclusive；不为覆盖主动制造reset。B terminal pre-reset/partial-reset payload原样保留供后续verifier。raw35不倒造clean35。
- Sensor draw counters只读既存内存；不是全局RNG流相等证明。actual untapped/tapped bitwise、per-row sample alignment、SDK物理参数readback仍需真实receipt。

## Source pins / 资源成本 / 剩余接口

[CAPTURE_SOURCE_INDEX.json](<CAPTURE_SOURCE_INDEX.json>)验证原17完整源码与独立canonical alias，完整AppV6/Base、frozen helper、poseCacheV4、bridge、正式worker来源均保留；B13、C8、旧adapter10、partition9封件成员全部逐bytes/SHA验证，C原182来源全部只读核验。未来materializer必须保留全8 runtimes/static banks/pinned assets/worker files/vendor7完整树，不能只挑AST模块。**本包不生成该materializer/dispatcher，也不把供给的baseline自证成独立来源。**

原qualified finite validation parent协议原样保留：privateGPU_EX+finiteEX，canonical generation/remaining/minimum/activeowner只读，1800等待及原2400 worker deadline；two-authority、trainSH/evalEX、3900–3600–300、reserve86412.86069250107均不重解释、不新设writer、不以NEWpurpose跳过原guard。成本metadata记录SDK wall非零、GO/close/actual-wait-return/finally-release epochs；外部实际settlement来源仍是SOURCE evidence gap，**没有新建父审批布尔gate**。

仍待父review及后续独立执行入口：NEWpurpose的原sourcehardpin/newkind接入；全static baseline独立pin；outer controller对parent的真实Popen.wait；真实原resource gate/SDK/native capture与live verifier。已有old guard并未自动放行新worker。

## 本地 SOURCE 验证

Python3.14 `-B`、96项stdlib fake/AST/真实metadata import与临时FS测试；不导入torch/SDK/psutil/原native bridge，不装SDK，不acquire临时resource。除继承fakeFS外，还实际导入完整原Base/AppV6/core与两完整staged helper（不裁函数），执行真实`put_json/fsync/atomic replace → close_original_eval_resources → evaluate_waited_eval_case`的fast/非fast临时FS roundtrip，并把V1 epoch污染注回独立binding文件，严格验证两分支均失败。绑定对象层明确是synthetic metadata fixture/假env/App，原helper/core的完整校验函数保持真实；不是SDK binding资格证明。所有临时文件只在本NEW目录的专属scratch中，清理前逐个核绝对归属；SOURCE audit单独记录这些实际元数据FS写/rename/删除，不伪记为全文件操作0。机械parent资源/finally blocks和V1 parent/contract/observer逐bytes不变。完整测试、操作零值与来源封印见同目录SOURCE receipt/seal。
