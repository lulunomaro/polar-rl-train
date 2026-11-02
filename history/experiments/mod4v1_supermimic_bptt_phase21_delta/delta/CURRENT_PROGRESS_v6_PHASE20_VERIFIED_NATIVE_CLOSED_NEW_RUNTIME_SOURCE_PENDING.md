# v6 — Phase20远端核验完成；首轮native已闭合，新runtime源待接续

## 权威状态与用户新要求

- Workspace `F:\RMPOLAR-RL`；R为本目录。现有工程SSH入口位于T的project_connector.connect72，凭据仅在已有helper内存使用，不输出/归档。远端B=`/home/lc01/Zonglin Li/zonglin2`；run-python.sh不仅重置cwd，也使CPU V2的PYTHONPATH尝试未生效，实际依赖应在Python启动后显式sys.path设置。
- Goal `goal-1c14ef7d-c888-4287-83bf-c008d54545fb`，最近get为revision10、round6/max48、active/armed。每条计划3000 verified policyBPTT和原技能80%中间/90%最终都未完成；不要complete/blocked，自动续接时先get_goal。
- H1冻结；八非H1。19:15直接请求奖励/指令跟踪鲁棒性，已完成两专项源审计、独立软件验证与新候选。未修改原速度、物理、DR、接受阈值或正式best注册表。
- 18:48允许低占用但有其他进程的GPU共享，仍遵原canonical/privateEX/finiteSH、原budget/reserve；future共享owner源已存在但首轮未采用。原两个UUID16828f91/c27eecbd卡。不要抢外国锁/别的canonical owner，不增加或复制账本。
- Skill catalog只有Office/ACL，无RL匹配；使用现有工程SSH/CLI/文件工具。只读源用read/glob/grep，模型/旧raw不为状态/Git再次打开。

## 首轮真实native全部已结束，不再是两卡训练中

远端root：
```
/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_SUPERMIMIC_BPTT8_V1_20261102_181251_1793614371303119100
```
原parent1475630于epoch1793620256.081064实际exit；原wait/costsettled/leasesreleased全true。唯一observer hostjob `pwsh-0628d778d2fa4b85`已自然结束且输出已收集，不要重启旧observer/worker/stager。当前无本任务native GPU worker。

[真实闭合摘要](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/reports/FIRST_NATIVE_WINDOW_CLOSED_TRUTH_V1.json>)及[完整闭合元数据](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/reports/ACTUAL_SUPERMIMIC_EIGHT_V1_20261102_184527/CLOSED_RESULT.json>)为状态源：

- E0 2520真实verified policyBPTT，iter2620，finite3600保存边界，完整新learner保存。producer247769313B、SHA `5d51d72194d32d196865a4bf83075e6c21a216ceb15798dde935510108b6c335`；remote role/E0/production/checkpoints/model_BPTT002520_I002620_S0006_complete.pt。
- E2 2392，完整checkpoint实际iter2492（不要用旧PROGRESS2490），247769249B、SHA `6b666ecb24f2e48557775cc9ec14140fe8bba353c006220bc57253020b3a30dc`；remote role/E2/production/checkpoints/model_BPTT002392_I002492_S0005_complete.pt。
- 六条E3/W35/C878/C113/S135/S50在bridge.init_state的quaternion/gravity guard失败，teacher各一次原全checkpoint读取已发生，learner未构造/first policy action未发生；producer counts/startup/FINAL均null。BPTT=0由trace位置推断，勿写成已发布counter0或技能通过率0。
- 总verified native4912，原GO到actualwait expert-seconds7603.138181686401；两条均未到3000，更不是90%技能达标。两母本/新候选完整保留，所有原teacher/currentbest与H1未覆盖。
- 八进程RC0但六有WORKER_ERROR/FINALnull，原owner只按rc阻断所以继续排完整队列。worker源码79–80实际raise，app.close是否覆盖exit为unknown；不要再声称worker源码直接吞异常。新owner应检查rc OR WORKER_ERROR OR缺失/坏successFINAL。原cost/退出记录保留，不回写成失败退款。
- E3gravity err1.000219，W35 .1558399，其余tilt约.05；不要降低1e-3/盲改quat。SDK物理/reset确实执行过，不能写六条SDK0。

## 奖励/指令结果和测试

主交付：[父层结论与统一消融方案](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/REWARD_COMMAND_ROBUSTNESS_FINDINGS_V1.md>)。

- 当前residual泄露true state/DR/contact/delay queues，teacher raw35不等于student可部署35；新raw35视图需fresh网络/Adam/count0，不slice旧full-context权重或拼次数。
- E2原nonholonomic vx=2Vcos(heading-axis),vy0，H16/.32s yaw4扫73.3386度，最大解析held误差1.1943908827m/s；非实测。W35 allrough为BODYvx[-.3,.3]，负vx参考轴+pi，运动/站立分母独立，未知resample保留unknown。
- 实际reward gateoff，alive/termination/base_contact/height_square0，SCUT exp分母std非std平方。站立/height/action权衡、E3gravity轴姿态代价倒置局部0为源反例，不是runtime hacking/通过率证据。
- C113新worker缺原axis绑定，父新source helper在ONE reset之后/first action之前只同步无noise command[:3]，CPU13通过；未部署。本轮C113更早guard失败，所以没在错误轴上训练。
- original100Hz noisy/delayed35保留；strict projection缺真实sample/clock标unknown，不从50Hz端点造exact物理sensor。

封版代码/报告：
- [reward审计](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_reward_review_v1/REWARD_COMMAND_AUDIT_SOURCE_V1.md>)62/62 stdlib PASS；[reward清单](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_reward_review_v1/DELIVERABLES_SHA256_V1.json>)89小输入SHA复核。
- [command审计](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_command_review_v1/SOURCE_COMMAND_REWARD_AUDIT_V1.md>)37/37 stdlib PASS。
- [Torch22组件收据](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/reports/COMMAND_CANDIDATE_TORCH_CPU_V1.json>)22/22真实CPU、H16 VJP非零、optimizer0/native0。
- [C113 CPU13收据](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/reports/ORIGINAL_C113_AXIS_BINDING_CPU_V2.json>)native0/no SDK。
- [actual-core CPU V3](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/reports/COMMAND_CANDIDATE_CORE_INTEGRATION_CPU_V3.json>)PASS：H16/hist10、WM/aux20、policy/critic3；三次future→s1→a0与paramdelta非零，actor35、teacher冻结、CUDAfalse。**这些3仅合成软件步，native0**。V1/V2缺rich历史全部保留；V3 after-launcher sys.path加入已封E0worker_sources/sm_deps，无SDK/旧PT/物理/账。
- 三冻结源保持：Torchcandidate `bb7555ff2de598677ea6cfe5dadefe0a9cfe37d37661635d186bcb14c1df2223`；22test `3ac2d347ba10333cc3e10870ac94225c04963570c8d5e6c9263cefadf0595703`；candidatecore `c0cc5d201e98598d32f62572a61be633cb7d8bcdf53e5f33883792df12539454`。原core `2603308f...72039`未改。strict候选新sensor oracle只是synthetic，实际噪声幅值/时钟/binding未验证。
- 测量审计final46/46 stdlib，E0/S50原binary accepted仍null；不凭MAE/nofall/S135阈值造90%。

## 当前两个source-only子任务（正在工作，非GPU执行）

1. Agent `82c79d2f-d50f-4737-894e-53caab47cbc4`：封版[reset-cache/failclosed v2](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_bridge_reset_cache_review_v2/BRIDGE_RESET_CACHE_FAILCLOSED_SOURCE_REVIEW_V2.md>)49/49 stdlib PASS，30输入SHA复核，12文件seal。Physx源pose setter漏8派生缓存失效、timestamp严格<、update(0)无效、reset forward到obs无scene.update是已证明源链；旧workerlive binding/stamps/rootcause仍null。另NEW source_pose_cache_runtime_adapter_v3在写，不改sealed v2。
   - 稳定API `from pose_cache_runtime_adapter_v3 import install_pose_cache_runtime_adapter_v3; handle=install_pose_cache_runtime_adapter_v3(env.scene['robot'], receipt_callback=callback)`。
   - build_env之后/唯一fresh reset之前安装；实际writer __self__/__func__/MRO/sourceSHA47d965...、data类/MRO/source43a319...双pin；仅原fullstatewriter成功返回后8cache.timestamp=-1，不extra step/reset/obs/RNG/g getter。记录小before/afterclock/stamps/calls；未知binding failclosed；旧bridge转换和1e-3保留。
2. Agent `4051d3a1-84e3-47db-8d60-b72e8d8535d5`：NEW source_resume_runtime_v2，v2 source/stdlib50已完成，现另加v3 variants，不修改v2字节。
   - 原core只有load(path)无load_full_checkpoint，拆新copy payload-loader以一次bytes/hash/decode恢复完整4model/4opt/replay/RNG/counters，allow_environment_reset=True+streamcut/freshhist，原VJP/collect等保持。
   - owner新增语义error gate而account/admit/锁/有限窗/C完全不变；新worker实际teacherGPU params+buffers load后及progress/save/final逐值比较，非只CPU原root版本。
   - C113 binder接入afterONEreset/beforeBridge.init；缓存adapter要beforeONEreset。未来支持A0 fullctx resume（不当部署）与A1 raw35fresh0/同variant完整续训，禁止A0→A1切shape/Adam/计数。
   - 已核对A1可以用旧core+Raw35ActorMDP(base,projector=None)：旧core只调用delegate的project_predicted_context，不调用strict新project_transition_context；因此A1保持legacyheld/aux近似，不需要synthetic oracle，绝不标E2已修/sensor exact。TeacherResidualPolicy actor_offset0，goal3、actor35，WM/critic privileged。
- Sibling send_message被host挡（belongs to another parent session）；**两child之间由父relay**，别让其反复重试。父已向405转发cache稳定API，还缺最终SHA/bytes descriptor。
- 这些新source尚未native准入或部署。不要原root复跑原6错误用途；新source/新unused jobroot/明确新协议，先CPU restore/interface验证，再实际资源gate与倾斜reset的真实cache/quat receipt。尽快推进有效训练而非为了额外数值规则空转；原physics保护不降。

## Git Phase20真实完成；本v6和晚源等待Phase21

- Feature `mod4v1-experts-fulldr-rm70` HEAD `4afdba074f3d295cd78ed4bf46a5cc779ff97b70`。
- Annotated trial `trial-20261102-mod4v1-supermimic-reward-command-closed-truth-phase20` object `47b91b18d093e7543ebe446b9285bd9e4ba0f3cb`，peeled HEAD相同，atomic push+remoteexact已成功，workingtree clean。
- Remote main只读当时 `013ee164aa11762e075152befcb7e1ecb2314f63`，独立推进，不hardbind旧main/不push-reset main。
- [Phase20源索引](<F:/RMPOLAR-RL/repo-lqr/history/experiments/mod4v1_supermimic_bptt_phase20_delta/SOURCE_INDEX.json>)2555 entries/118旧SHA引用/2439新变文本；包括双审计、全部CPU失败/成功、native两fullsave与六错误/closewait/原成本、晚measurement seal、父主报告、capture时已有cache/resume源。
- point-in-time后新/变的v3 cache adapter、resume variants、最终seal/测试和本v6 **PENDING Phase21 append**，不要声称已进phase20。Phase20记录脚本已消耗，不重跑，为后续新delta用record_experiment unique annotated trial+exactshortdir adapter。模型只producerpath/bytes/SHA索引，无模型stat/hash/decode forGit。
- 所有本轮host jobs（observer、CPU22、C11313、integrationV1/V2失败/V3成功、SDK source fetch、archive20、push20）已结束/相关output均收集；原source/native once不重放。
