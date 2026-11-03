# Phase1 E3/N80 被动接口验证：具体 SOURCE worker

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

## 10个最小调用点差异

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

Python3.14 `-B`、stdlib fake/AST；不导入torch/SDK/psutil/原native worker，不装SDK、不创建临时resource。Fake close使用in-memory FS，假env/App恰好各一次与全部错误路径。机械parent全部resource/finally blocks做逐行相等测试。完整测试、操作零值与来源封印见后续同目录SOURCE receipt/seal。
