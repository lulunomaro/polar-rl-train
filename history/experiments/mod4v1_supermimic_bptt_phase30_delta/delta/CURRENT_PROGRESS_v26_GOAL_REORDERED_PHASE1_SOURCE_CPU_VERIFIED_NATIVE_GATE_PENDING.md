# v26：Goal已重排，阶段1 SOURCE/真实CPU通过，现场SDK门仍待验证

2026-11-03，Goal round9。直接接续用户15:38“重新搞goal开始按照你说的顺序推进”。实际持久Goal同ID `goal-1c14ef7d-c888-4287-83bf-c008d54545fb` 由revision13 EDIT到14，自动round9 get为**15 / active / armed / 9/48**。顺序已真实写入Goal，不只是todo：[执行计划](<PAPER_ALIGNED_REBUILD_20261103/EXECUTION_PLAN_V1.md>)。

## 顺序及冻结边界

1. 当前阶段1：static DR / dynamic actuation+feedback queues / clean100Hz+外部原noise-delay分区、被动capture与现场proof。
2. 阶段2等Gate1：同k8 predicted-state/context上的state+learned heads闭环，不未来真dynamic xi teacher-force。
3. 地形/任务Markov、E2原指令参考/phase/resample、timeout/bootstrap。
4. critic/残差support/饱和/合法start/H16-32分别单因素。
5. 质量支持才1–2角色有限真实BPTT增量→fullsave/实际SDKclose/父wait/结算释放→原技能独立多seed复测。

八nonH1/H1冻结、Registryv12/母本/旧候选/失败全部保留；约3000只过程，80/90原技能+鲁棒性/保持未达，E0/S50原binary authority仍null。不盲续坏legacy，不把source/CPU/RC0当技能；不complete/blocked。原2c/bae400-k2000-d3/50-100/.0025TGS32,4/.01闭链/.01mimic/全D0D7/速度/原接受/canonical唯一writer/两authorityEX/私GPU_EX/有限trainSH-evalEX/reserve86412.86069250107/3900-3600-300/1800不改，不外国signal/锁清理/退款/新账本/扩预算。此轮native训练、SDK、GPU、选定模型PT/raw、canonical操作均0。

## 阶段1已真实完成

- [分区SOURCE](<source_phase1_state_context_partition_v1/README.md>)9成员冻结；seal SHA `e7f3d29bc0319fbd9f0d4e1d5a4981edd551b6c47f16431c8545bb86b7756630`、root `0feb70e552a915ca698b87cdc7a4e3b22ee614e86ce55c2b9677a6f0e9c30bdf`。八实际STARTUP/layout、159命名字段/76 extended缺件offsetnull，source202项hash相同。父[独立复验](<reports/PHASE1_PARTITION_PARENT_SOURCE_VERIFY_V1.json>)32/32 stdlib测试通过、前后9成员hash未变。
- [sensor passive tap](<source_phase1_passive_sensor_capture_v1/README.md>)13成员冻结，seal SHA `3d5fd4febf9232a8113b4d93dbf8d3d6a19658690e973d6485c1aedc39e18881`；passive_capture.py `7df0694d6eb53d822395d7f5ccb066783a8b8fdefc80834096e5f32a5b677df8`，source_api.py `324ac762b755f5e957d8c69e8f177a674ad3b5f3f23c491f720e1711348bd26c`。父review后修正两问题再seal：部署路径用actual module/code filename而非Windows出处，mutable root asset default也核验。父通过unittest discover又实际只读复验21/21。
- 实际NEW remoteCPU [原两类reference](<reports/PHASE1_SENSOR_REFERENCE_CPU_V1.json>)，job `pwsh-67f7d47c8f6e4af9` RC0/已收取：原SensorCorruption60行与FeedbackDelay41行精确SHA，新synthetic输入，10项通过。16control/32regular feedback ticks+sameTick partialreset；每channel258draw；age0/10000us都观察；队列/RNG守恒。source SHA分别 `aa853a74a2c2d8840d003caab13a853bade0d761cf7966e4d13c200b929817b8`、`90b339a6d3690294798befefb33e7f27cb7c3bfa0d8e38c98312e207685b5665`。
- 实际NEW remoteCPU [真实两类+封sensor tap](<reports/PHASE1_PASSIVE_TAP_CPU_V1.json>)，job `pwsh-97f472945d1b4d69` RC0/已收取：25组output bitwise相同/50次原return identity，baseline和observed的sensor、delay各25call，完整source privateRNG/state+globalTorchPythonRNG不变，capture_errors0。**fakeenv，不走native preflight，不是actor35/SDK/PhysX证明**。13成员前后SHA未变。
- [综合阶段1进展](<PAPER_ALIGNED_REBUILD_20261103/PHASE1_VERIFIED_PROGRESS_V1.md>)已写；普通SOURCE测试复跑不产生新native用途/旧receipt改写。两个NEW CPU once已消费，marker存在，不能重放；源脚本/报告均保留。

## 确认缺口与当前进行项

raw35已noisy/delayed；旧feedback_delay只有配置lag，没有FIFO/clock；motor episode_scale4+2/mu等未进旧xi；action pending/applied缺issue/due/valid。command_time_left native秒stored*.01，recovery_age/stable stored已经秒，仅记录编码映射不热改旧norm。clean16可沿自然调用采；mid/end完整clean35原来没算，Unknown。episode+tick+key区分sameTick cache-hit/partialresetfresh；warmup lag1 age0/readyfalse。这些发现不是原失败因果或修复收益证明。

Source子任务当前：
- `0ad8300a-6e15-43f7-ad90-657780f697bf` sensor SOURCE已完成inactive。
- `cffddedf-0c4e-4a0f-bffd-8b2d48a6785b` 第一分区SOURCE已完成，现NEW [actuation capture](<source_phase1_actuation_capture_v1/>)：wrap原queue.submit/apply/原target setter arg、static已有属性，明确actual physical readback缺件；不patchreset，避免与sensor双wrap。
- `565b1562-3c38-4864-8a0f-ed68a3526f7c` NEW [native integration SOURCE](<source_phase1_native_probe_integration_v1/>)：发现旧frozen worker不构造NativeTaskBridge且parent/语义固定2member160/1600；不会直接改purpose贴tap假装准入。准备接原env+bridge首次reset后已有obs的最小adapter、显式capture kind和semantics。**真正NEW worker/App-close-FINAL语义/完整sourceindex/原parent新purpose准入尚待实现和审阅**，无stage/Popen。

阶段1当前 `SOURCE_CONTRACT_FROZEN + REAL_CPU_CLASS_TAP_PASS; ACTUAL_NATIVE_GATE_UNKNOWN`，admittedfalse。后续先收/审这两源、补真实入口与完整原关闭资源链，再最小有界SDK接口窗；不放行阶段2native。没有自己的活跃hostjob/GPU/resourceobserver；不能从source任务inactive或host时间间隔猜远端资源空闲。

## Git

Phase29已远端核验：feature `8700b912c08f8e1b5d45bbfc152a2524cc7ff755` / annotated obj `780bff9ea6ca2f073253a301e84e37c88ed011d4`，详[v25](<CURRENT_PROGRESS_v25_PHASE29_VERIFIED_PAPER_METHOD_GAPS_NEXT_FIX_DESIGN.md>)。父复查本地branch同feature、clean、HEAD同29；最新remote main仅读 `386555939f2fc4baa1ee585975f46bf7061db568`，独立推进，不push/reset。

此v26、新Goal执行计划、两SOURCE封件/测试、两个实际CPU用途/回执、late好专家materializer封件与当前actuation/native-adapter point-in-time源码**待Phase30追加**。后续capture之后的新源/封件/交接再如实pending下一append；不为Git重跑CPU/native/旧once、不读模型/raw内容、不把SOURCE说成现场通过。Root无AGENTS，真实仓库repo-lqr/AGENTS和两记录政策已实读。
