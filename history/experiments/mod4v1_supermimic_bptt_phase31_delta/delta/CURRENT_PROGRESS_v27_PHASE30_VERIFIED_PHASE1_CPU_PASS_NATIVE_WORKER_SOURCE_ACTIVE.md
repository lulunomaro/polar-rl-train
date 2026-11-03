# v27：Phase30远端核验；阶段1 CPU通过，真正NEW native worker开始实现

2026-11-03 19:12 +08:00，Goal round9结束前交接。Goal `goal-1c14ef7d-c888-4287-83bf-c008d54545fb` 最近实际get **revision15 / active / armed / 9/48**。用户15:38要求重排顺序已实际EDIT14，自动round9成为15。五阶段与原冻结边界见[v26](<CURRENT_PROGRESS_v26_GOAL_REORDERED_PHASE1_SOURCE_CPU_VERIFIED_NATIVE_GATE_PENDING.md>)及[执行计划](<PAPER_ALIGNED_REBUILD_20261103/EXECUTION_PLAN_V1.md>)；最终80/90原技能+鲁棒性/保持未达，不complete/blocked。现在仍阶段1，不放行阶段2native训练。

## 本轮证据没有升级成技能或SDK通过

父独立分区32/32、sensor21/21 stdlib测试通过；分区9成员/source202 hash一致。两个NEW真实Torch CPU用途已经RC0/收取：原Sensor/Delay reference10项；真实原两类+sealed tap25组bitwise输出相同/50次原return identity，全source queue/private RNG/globalTorchPythonRNG守恒。[综合进展](<PAPER_ALIGNED_REBUILD_20261103/PHASE1_VERIFIED_PROGRESS_V1.md>)与[CPU tap回执](<reports/PHASE1_PASSIVE_TAP_CPU_V1.json>)记录清楚：fakeenv、非native preflight、没有actor35/PhysX证明，native BPTT/SDK/选定模型/raw/GPU/canonical均0。

原噪声/延迟两类源SHA aa853a74… /90b339a6…；各CPU once marker已消费，不重放。分区与sensor原两封件保持，当前static DR/dynamic queue/clean16/fullclean35 Unknown/command units/episode-clock缺口见[v26](<CURRENT_PROGRESS_v26_GOAL_REORDERED_PHASE1_SOURCE_CPU_VERIFIED_NATIVE_GATE_PENDING.md>)。

## 另两个SOURCE交付已到，尚需父全文review

### actuation observer

[source_phase1_actuation_capture_v1](<source_phase1_actuation_capture_v1/README.md>)：8成员、28/28 stdlib fake PASS，182原source SHA匹配。seal `ed77f3a3b0ce7aea6f904a09be8d038097bfb00729d57bec94feae5ab67bd081`，content root `e5d17421d46dae13b792b19bf83d90d85f2ffb3d7d814ba49940d79e25337286`。稳定API `install_actuation_tap(env,capacity=8192)` / `drain` / `snapshot_static` / `status` / `close`，offline三validator。

只wrap已有queue.submit/apply、actionterm process/apply、asset target writer原arg；不wrap env reset/queue reset/termination/sensor，因此与sensor六hook可组合。static仅已有内存字段；setter arg/config不是真实physicalreadback，后者Unknown；runtime_binding/actualSDK/exact仍Unknown/false。真实Tensor冻结路径还没测，需要下述NEW CPU fixture。

### native interface adapter（不是worker）

[source_phase1_native_probe_integration_v1](<source_phase1_native_probe_integration_v1/README.md>)：33 stdlib fake/AST PASS，完整原17 source映射/AppV6→Base/canonical7a092来源与B sensor13文件固定。content root `9c8e85e30fb1499d818c8933ac46a871cc6a8970a023051d636320d67aa93c96`；adapter4977B SHA `32a582f1ec84d2adc8fd6731f1aed6956ddf7d927e8d830502ce18093c123ca0`。

父已实读完整README80行。旧frozen正式worker没有NativeTaskBridge，旧训练main硬training/4FD/N512+3000/learner，两个main都不直接调用冒接口probe。当前只有接已建同env/bridge的adapter、SOURCE capture schema/只读sourcepreflight，**真正NEW worker、capture close-intent/FINAL、sourcehardpin/purpose准入还没有实现**。其sealed README写actuation deferred是该SOURCE capture时的历史状态，actuation刚到的seal由后续NEW worker包绑定，不改旧seal。

原bridge84–161父已实际读：teacher只state_dict/export用；接口zero-action/PT0可以teacher=None但严禁这两保存接口；bridge.init_state必须传原已有obs，避免额外compute；step原一次env.step+pre-reset term/trunc，无learner。若采用formal构造路线，必须保留原53 reset→55 E3 fall/publish→66既有compute顺序，以原66 obs传initial_obs；别用pose前旧resetobs或另加observer compute。选择一条完整原setup路径，不混搭两个worker。

## 已开始的下一项具体SOURCE（两child正在工作）

- `565b1562-3c38-4864-8a0f-ed68a3526f7c` NEW [source_phase1_capture_worker_v1](<source_phase1_capture_worker_v1/>)：**实现真正worker**与eval专用close/新FINAL/purpose任务合同，默认E3/N80/64controls、syntheticzero6/PT0。原parent资源/actualPopen.wait/EX释放整段与完整AppV6→dc4 Base保留；NEWpurpose guard独立显式，不借旧qualityTrue。不得调training `_validate_final_for_intent`伪装capture。no stage/dispatcher/SSH/SDK/GPU/C/Git/旧sourceedit，先交源+fake/AST tests+seal。实际执行资格与terminal/partialreset等覆盖不全分开，未自然发生报inconclusive，不额外reset造覆盖。
- `cffddedf-0c4e-4a0f-bffd-8b2d48a6785b` NEW [source_phase1_actuation_real_cpu_fixture_v1](<source_phase1_actuation_real_cpu_fixture_v1/>)：精确原PhysicsActionQueue真实Torch CPU fixture源，父显式供torch/原class；小N/九lag组合/两control8ticks/partialreset、bitwise queue/RNG/returnidentity/Tensor owned clone与bounded/restore。child本机无Torch，只AST/stdlib，不执行真实CPU；父之后用NEW独立remoteCPU用途。不能将FakeQueue当真实class或复用已消费sensorCPU用途。

这两新SOURCE尚未收/审/测/封，不把派发当已实现。父下一round先收review并测真实action queue+组合，再检查NEWworker完整原resource/close/wait/source闭包，另建最小actualSDK接口purpose。当前没有自己的活跃hostjob、GPU、资源observer或native进程。两SOURCEchild在工作不等于远端训练。资源实际可用性需新parent重验，不沿旧free GPU快照。

## Phase30实际Git完成

```text
feature mod4v1-experts-fulldr-rm70
HEAD 2d16bf1e1dbf55cd72120c761481b446cbd78622
annotated trial trial-20261103-mod4v1-supermimic-ordered-rebuild-phase1-source-cpu-interface-phase30
annotated object 8fd5c6723c784895c44533366eb735c563b89304
remote branch / tag object / peeled commit exact verified, worktree clean
6720 entries /6199 priorSHArefs /66 new texts
latest remote main READ-ONLY e9953da0aa1ec089f814a682c7c245b8c4828bd3
archive job pwsh-81bf7684e10b4983 RC0/收取
push job pwsh-261a829da14a4acf RC0/收取
```

[archive30](<archive_phase30_ordered_phase1_source_cpu_delta.py>)已消费一次，不能重跑record/源扫描补档。旧Phase29 builder模板CRLF导致首个NEW prepare在`known={}\n`字符串断言失败，发生在新archive源/record/Git之前；原失败builder保留，NEW V2仅normalize CRLF→LF再prepare成功，[错误与V2回执](<reports/PHASE30_BUILDER_CRLF_PREEXEC_FAILURE_AND_V2_SOURCE.json>)入本次归档。没有重跑CPU/native/旧archive。

Phase30捕获Goal执行计划/v25-v26/分区与sensor封件、真实reference/tapCPU及源码/全部失败/Unknown/late好专家materializer/actuation-nativeSOURCE的point-in-time文本。models在stat/read前跳过，raw/PDF/gzip/banks只metadata。**晚到actuation/nativeadapter最终seal需按Phase30索引逐项比对补齐；此v27与新的worker/queueCPUfixture及后续实际用途待Phase31追加**。不冒称后生成报告已在旧commit，main仅读不push/reset。总Goal保持active。

## 19:18 父补充review（待Phase31）

父已实际read actuation_tap.py全319行/README88行，独立复跑28/28 stdlib fake通过，详[父SOURCE复验](<reports/PHASE1_ACTUATION_PARENT_SOURCE_REVIEW_V1.md>)。未发现已确认静态源码阻断；真实Tensor/queue CPU、live binding、physical readback均不升级。capacity只限保留量，满后仍有clone成本；恢复冲突必须检查restoredfalse而非仅closed。两新增SOURCE child仍在工作，NEW worker还未收件/审阅/运行；无新native或host背景job。
