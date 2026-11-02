# SuperMimic+BPTT新Goal：源已封版分发，原卡/原authority等锁，尚未实际GPU训练

用户2026-11-02 17:41直接要求：找两空闲卡、以SuperMimic BPTT替代20次PPO、每专家至少几千更新、80%中间保底/最终至少90%，设置Goal开始训练。已create/edit **goal-1c14ef7d-c888-4287-83bf-c008d54545fb revision2 active/armed max48rounds**。范围沿用八条非H1：E0/E2/E3/W35/C878/C113/S135/S50；H1冻结。原20PPOGoal get_goal已null，原8x20+8scope全闭合的成果/Registry12/phase17均保。

## 训练实现与真实口径

source_runtime/{native_supermimic_bridge.py,worker_supermimic_bptt.py,supermimic_original_owner.py}为新源。真实原IsaacLab MOD4v1环境采样、原vendor状态WM＋ctx_reward_learner真实环境r/done/delta-xi监督头，actor/critic H16 imagination BPTT，**不是可微PhysX、不是PPO/单步BC**。teacher原35→6冻结、残差学生，原raw35 observation不二次噪声；新pi/WM/critic/aux optimizer，不假恢复原PPO17Adam。N1024 fresh原训练constructor全D0–D7，非N80 capacity或20k历史slice；teacher从Registry12当前scopedbest完整checkpoint一次byte/SHA/decode，母本与上轮候选都保。

Core封版 source_core_review/ctx_reward_learner.py **35812B SHA2603308f1adfe65f576eaf2aa3e0275d8465f110e6edd6e3db38304bf3e72039**，28AST/stdlib源测试非runtime。真实计数读counts.pi_bptt_optimizer_steps，必须actualoptimizer posthook+finite nonzero paramgrad/paramdelta/lr+future→a0及future→s1→a0 WM VJP，WM-only100warmup、WM/aux/critic步不算pi。每条目标3000 verified steps，lr1e-4/H16/.4UTD/buffer128/hist10/batch512/WM512*3/4batch，完整新learner/replay/RNG/obs_hist/counter/collect_fraction/pending_iteration保存。env export exactFalse，原新freshepisode reset-resume须明示，不假完整PhysX warmstart续轨迹。

Bridge捕获原termination_manager.compute之后/原reset之前物理s1，真实term/trunc；done的actor nextobs不可取则xi1=0/xi1_validFalse，context loss/normalizer严格mask(~done & valid)，不把reset后观测当terminaltarget。新ctx源保存原obs35+DR/queue/feedback/contact/torque/phase特征；外源命令/height/mode/DR短16H固定，精确last_action22:28与wheelzero14:16投影；**E2 body/world command演化是短H模型近似，未宣语义已修复**，最终world原谓词另评。原reward、任务、终止/2c-bae/400-k2000-d3/50-100Hz/.0025TGS32,4/.01m-.01rad未改。

## 实际分发/父控与初始源错误

root **/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_SUPERMIMIC_BPTT8_V1_20261102_181251_1793614371303119100**，8角色各966–1043非PT文件与全部manifest已stage，0模型复制/SDK/GO/C写。SUPERMIMIC_EIGHT_V1_DISPATCH_ONCE.json记录第一次parent1475369（18:13:04），但其模块导入原three_slot_common需SCHEDULE_PUBLIC.json，stage遗漏配置，**它在OWNER_STARTED/锁/GO/PT/SDK/C写之前退出**；FIRST_OWNER_ACTUAL_LIFECYCLE_DIAGNOSIS_ONCE.json有完整ownclosed stderr。stager已消费别重跑！

已新unused-owner修复launcher repair_missing_schedule_preGO_and_dispatch_owner_once.py：fresh确认旧parent不live、ownerstarted与八roleGO全absent，仅增加原SCHEDULE_PUBLIC config（非账本），源helper/original owner代码未变；记录PREGO_MISSING_SCHEDULE_SOURCE_ERRATUM.json。新实际parent **1475630 creation1793614676.22（18:17:56）**，SCHEDULE_CONFIG_REPAIRED_OWNER_DISPATCH_ONCE.json；schedule SHA bce1f5b8d29ae1d3dfb7e35efe0cc812cbbd84ba47e249af6124582f0b9153a8。当前原1800s preGO resourcewait（partial_locks0/PTSDKGOCwritesFalse）。原两authorityEX/每卡privateEX/finiteSH与原预算/reserve保留，b.charge_values原helpersSHA eaf6../ceba..，原C唯一writer，无新账/extension/refund。原3900max/3600save/300headroom。

## 资源实证：初始两空闲，现被其他既有原owner占用，别清锁/干扰

初始17:45:33两4090 UUID16828.../c27...各24203MiBfree/util0/compute空，原CownerNone/remaining355407.87773919106/reserve86412.86069250107。但源准备时另一已有项目任务已17:46:54开原owner。

最后只读diagnosis ACTUAL_PREGO_PROJECT_LOCK_WAIT_DIAGNOSIS_ONCE.json（18:20:17epoch1793614817）：canonical active **Linux_LQR_MPC_DEPTH_STUDENT389_1793612814735279864** parent **1474033**，卡1compute **1474057**占4542MiB/util37/free19653，卡0仍free24203/util0；原C两authority **WRITE EX1474033**，卡1private **WRITE EX1474042**，真实kernel modes，不是fuser猜。remaining353407.65216732025。**GPU0虽闲，但原唯一authority正在别的task持有，不能双writer/抢锁/kill。** 当前自己的原parent1475630在1800preGO等待（约最晚18:47:56），不把等待称开始BPTT。其后若原timeout0GO，保错误并在资源实际释放后新unused parent-window接续，别重放已消费stager；不能改原gate/清锁/共享卡。

## 唯一仍相关在跑job

**pwsh-6f9acdad28e04fa4**：collect_actual_supermimic_run_metadata_once.py，10h/20s自身publishedmetadata观察器；current指针 SUPERMIMIC_EIGHT_V1_LATEST_METADATA_WATCH.json→reports/ACTUAL_SUPERMIMIC_EIGHT_V1_20261102_181444/CURRENT_METADATA.json。当前parent_currentNone、original_resource_wait Errno11、八条未GO，**native actualBPTT0/无skillrate**。先job_output，不重复collector/PPO/SDK；closed后一次收ownmetadata与stdout，不读模型/raw/C。旧stagerjob pwsh-6b7ac085807b48a8、缺cfg诊断pwsh-f07c824be8434618、cfg修复pwsh-c94c8477d9f84b15、等锁诊断pwsh-fc97ae6b66eb4b76均已完成已收。

可用但**还没执行**：source_runtime/synthetic_cpu_contract_check.py + run_cpu_software_contract_check_once.py。这是无SDK/无模型/无GPU/无C的remoteCPU纯合成autograd软件测试（core+MDP+teacherwrapper），即使通过也绝不计expertBPTT/原native训练。原资源等锁期间可独立做，实际目标计数仍0。

## 验收源码审计已完成，不假90

source_acceptance_review/EXPERT_90_PERCENT_ACCEPTANCE_CONTRACT_SOURCE_V1.json 54174B SHAa245c70354a815f475daccc4ec4945faa0ee6192e25bc923bd6026e3a2072083，33source/publishedmetadata refs、8角色excludeH1；54纯CPU合成test全过。**E0与S50原binary毕业谓词依当前已查源仍缺，rate保持null。** E2原sameUID/episode/direction/sign/moving±4 signed2pi along.5±.05/cross±.05/yaw±.2，complete事件分母partial另列；getterphase/rootpoint验证待做，不x8/改tol。W35原axis=_command_heading+(vx<0)pi，tol=max(.03,.1|vx|),yaw.2,natural非term/timeout且startobserved，moving/standing分开，matchedUID/referencegap未补。E3原firstepisode credited、74rescue/normal6排除、stable50=public100Hz .5s，请用原maskedterm真实done。C878/C113/S135自身sameepisode两轮orderedendpoint/Fz>1N原时钟，stand不cross。

## 用户最新追问 fullDR 腿连杆质心/质量（18:23后）

已额外从**当前stage实际E0 runtime**只读fetch mild_dr.py/chassis_com_component.py/autonomy_policy.py到discovery/current_DR_scope/，未GPU/SDK/model/C写；job pwsh-3f5e727509ef4233已收。当前mild_dr 9083B SHAa8c4fb06f16dbad215b3a380420909a80680f9819d9bdcfbf5f816061222fb7e，lines73–79每episode perenv一个factor∈[.9,1.1]同时作用**所有rigidbody质量和惯量**，所以腿/连杆质量涵盖，但**不是各杆独立比例**。chassis_com_component.py 2588B SHA7954ccf5fb391b820b970ee0d1f47c1db04b7f3f2036f475f9fa3333634a6502，profile明写chassis-only，独立xyz±.005m。因此**当前只底盘COM随机，腿/连杆COM并未独立随机；mod4v1新名义COM不是COM随机域覆盖。** 用户这条只是询问确认，未擅自改物理DR或Goal、未热patch已分发任务。回答应纠正笼统fullDR，不说全覆盖。

## Git待办与下一步

已读repo-lqr docs/ALL_TRIALS_AND_REPORTS_GIT_POLICY.md+NEXT_AI_GIT_WORKFLOW.md。所有本root源、两个agentSOURCE-only证据/错误、资源/cfg失败/修复/卡wait、本handoff与旧v23 lateGoalclosepending都**尚待phase18新SuperMimic首阶段归档**；不要声称已推。repo现feature mod4v1-experts-fulldr-rm70、旧最终phase17commit de21f20380296541e5fd508e87edb27ff0a2483b/annotated6a3f58bd..，main独立推进，按原record_experiment与exact-short-dir staging追加唯一trial，只feature/tagpush不main，旧记录/权重大raw只索引，不为Git再开模型/raw或跑GPU。两个agentd154/269均inactive，源已封版。

下一步：优先处理新用户DR扩域指令（若明确提出）；否则等原权威释放/自parent实际GO，runtime真实native/梯度错误需保留然后修**新版本**，不能把source28test或syntheticCPU当nativeBPTT。启动后以actual current producer计数与跨时WM梯度receipt为准。每条先3000真实BPTT再独立多seed原scope验证，缺项明列；目标90未达前Goal不complete，不为原资源暂等伪blocked（当前round0）。
