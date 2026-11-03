# v28：真实原action queue＋tap CPU通过；NEW capture worker SOURCE仍在实现

2026-11-03 19:31 +08:00，接续[v27](<CURRENT_PROGRESS_v27_PHASE30_VERIFIED_PHASE1_CPU_PASS_NATIVE_WORKER_SOURCE_ACTIVE.md>)。持久Goal同ID、最近get revision15/activearmed/round9，五阶段按序，当前仍阶段1；不放行阶段2native，不complete/blocked。原技能80/90与鲁棒性未达，母本/H1/Registry/物理DR/速度/原接受/原预算锁全部保持。

## 新增实际执行，已验证并收取

[source_phase1_actuation_real_cpu_fixture_v1](<source_phase1_actuation_real_cpu_fixture_v1/README.md>)已冻结8成员，15 AST/stdlib测试仅源码合约；父读完fixture359行并明确不以此叫realCPU通过，随后才创建独立NEW用途。

- fixture SHA `2805adf3530def6f1a0e73634a54fdc91ddb1e74e0c157023f008d5a3581277c`；seal SHA `14d7223d09842dddb8e90ab7ee236f3a87aff30e671fab6ef6fe36dad79a9a5a`；root `ee63c60ee9c5411a62e4960c0d4c41f1fa5317aada5f9b48b1153daa2f2b12af`。
- 父实读原PhysicsActionQueue全111行，E3和W35文件SHA均 `a4238c581611ef7cdb710692291ddac48e076364b0587f631eb71fd6a7d15eb8`。普通file-module import并注册sys.modules以保留class source identity；不能exec出无source的class。原actuation tap SHA `b9b9e288124a1ba8c031a030c00a231f4d02d2ba7efee9981141ae90b8e28828`。
- [run_phase1_actuation_real_cpu_v1_once.py](<run_phase1_actuation_real_cpu_v1_once.py>)已消费，marker存在，**不得重放**。NEW remote CPU root由[回执](<reports/PHASE1_ACTUATION_REAL_CPU_V1.json>)记录；job `pwsh-a66b064076334983` RC0/已经实际收取。只上传新源/两个8文件seal及原queue源，不读PT/raw，不造SDK/资源/C账本操作。
- N2、N3均真实运行原queue+旧已封tap；各9lag组合、两个control再partialreset后一control：各432正常group apply ticks，合计864。
- 每个N：全original state/privateRNG bytewise对比604次；ownedTensor防alias432次；methods完整恢复11次；partialreset18次；sameTick/原exception identity8组。全局Python/Torch CPU RNG不变，前后两8成员hash不变。原Queue没有被FakeQueue替换；只有Env/Asset/ActionTerm是fake，lag赋值与neutral0仅synthetic测试设置，非实际DR/default readback。
- **PASS范围是原CPU queue component/tap。** native runtime binding、原SDK、actor35、physicalreadback仍Unknown/未测，`actual_native_binding_pass=false`，native BPTT/模型PT/raw/GPU/canonical均0。

原sensor真实CPU25组bitwise/50identity及SOURCE32+21，actuation父全文review319行并独立28/28测试均保留，详[v27](<CURRENT_PROGRESS_v27_PHASE30_VERIFIED_PHASE1_CPU_PASS_NATIVE_WORKER_SOURCE_ACTIVE.md>)及[父SOURCE报告](<reports/PHASE1_ACTUATION_PARENT_SOURCE_REVIEW_V1.md>)。

## 当前唯一active SOURCE child与具体下一步

`565b1562-3c38-4864-8a0f-ed68a3526f7c` 正在实现NEW [source_phase1_capture_worker_v1](<source_phase1_capture_worker_v1/>)，尚未封/收/父review。默认E3/N80/64、可128，选择单一formal原setup53 reset→55fall/publish→66原有compute，传该原66 obs给NativeTaskBridge(initial_obs,teacher=None)，初始化一次后sensor→actuation安装，反向恢复→bridge→env→完整AppV6/Base。不调用hardtraining main/learner、teacher.state_dict/export，不读任何teacher PT；observer不加reset/compute/noise/SDK getter。原parent 17–44/46–78资源/readiness/wait/release机械保持，NEWkind/memberguard/closeintent/FINAL显式新源，原旧guard不自动放行。

父额外提醒：同feedback_tick下pose publish后的原66 compute也可能合法复用旧sensor/delay cache，**不能宣全fresh clean**。保留原buffer与现存initial FIFO/cur/out/last/sample_tick/episode；clean0缺即Unknown，不主动invalidate/noise draw/tick++/extrareset去“修”。tap后自然mid/end sample才是实际clean16来源。

原finite-validation parent源码21–38/78已父实读：canonical只读generation/remaining>finite_minimum/activeNone及两EX/compute/memory硬门；没有本parent训练expert-sec writer。这不等于SDK wall免费，NEW worker须记录GO→control→Appclose→parentwait非零实际epoch/wall。原协议与source引用不齐是evidence gap，不新造Cwriter/退款/并发账本。child一度提出CONFIRMED_BY_PARENT人工bool硬门，**父明确指出非原机制，child已同意在未封SOURCE中移除**；同样不加人工parent-reviewed stamp，复用原真正hardgate，保留Unknown/来源而非新增审批机制。

cffddedf queue fixture已完成inactive，sensor child亦inactive；没有自己的活跃hostjob/GPU/native/resourceobserver。下一步收并review实际NEW worker/runtime/close/源index全部闭包，先完成可执行NEWpurpose，再最小actualSDK验证，不把SOURCE或SDK RC0独自叫Gate1通过。真实覆盖不足单列INCONCLUSIVE，不强制新增reset或改controls造证据。

## Git状态

Phase30 feature `2d16bf1e1dbf55cd72120c761481b446cbd78622` / annotated `8fd5c6723c784895c44533366eb735c563b89304` /remote branch-tag-peeled verified，详[v27](<CURRENT_PROGRESS_v27_PHASE30_VERIFIED_PHASE1_CPU_PASS_NATIVE_WORKER_SOURCE_ACTIVE.md>)。本v28、v27晚补、父actuationreview、晚到actuation/nativeadapter/queueCPUfixture最终seal与NEW真实CPU脚本/marker/回执、worker候选源**待Phase31追加**；先按Phase30索引精确SHA比对，只补差异，不重跑旧archive/CPU/native，不为Git打开模型/raw。总Goal继续active。
