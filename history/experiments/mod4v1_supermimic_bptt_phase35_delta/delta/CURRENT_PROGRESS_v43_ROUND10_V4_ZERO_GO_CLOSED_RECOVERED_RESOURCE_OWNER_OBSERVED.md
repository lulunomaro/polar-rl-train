# v43：Round10确认V4零准入已闭合；终末只读恢复，原资源owner仍在

2026-11-04 00:49 +08:00。实际getGoal **rev17/active/armed/round10/48**，ID `goal-1c14ef7d-c888-4287-83bf-c008d54545fb`；仍阶段1，无新合格SDK采样/新训练/Stage2或技能率。H1/母本/Registryv12/物理DR/接受/预算与原资源规则保持。前源版本与真实CPU见[v42](<CURRENT_PROGRESS_v42_V4_FULLY_STAGED_ORIGINAL_RESOURCE_WAIT_COLLECTOR_ACTIVE.md>)。

## V4原purpose已消费、1800秒自然失败，未测试设备修复

root尾 `DEVICE_BINDING_V4_20261103_232922_1793719762179514600`；parent1549989/controller1549982。Round10 [own发布终末快照](<reports/PHASE1_V4_ROUND10_PUBLISHED_CLOSURE_RECOVERY_SNAPSHOT_V1.json>)实际RC0：

- 原resourcewait **121条**，first1793720016.9528055，last1793721817.1980746；每条locks_held0/SDK或selectedmodel未开/Cwrites0，最后remaining0。
- 原parent自己抛`Originalresourcewait1800sexpiredwithoutSDK/model/foreignactions`，PARENT_EXIT_SCOPE **1793721817.2216127（00:03:37）/wall1800.297255039215s**，child_waits[]、allownwait/privateGPU_EX/globalfinite_EX release均True、Cwrites0/SDK_PT_opens0。
- 原outer实际Popen.wait返回1793721817.2370126/RC1/controllererrors[]，wall1800.6472935676575。固定parent/controller /proc实例均已不在。**不是以PID消失替代wait**，wait原件同时存在且bytes/SHA已取。
- ACTUAL_GROUP_ADMISSION/CHILDREN/GO/workerREADY/workerFINAL均无；producercounts仍null、技能率null；是0准入不是0%技能，V4代码尚未native检验。

[真实zeroGO摘要](<reports/PHASE1_V4_ZERO_ADMISSION_CLOSED_TRUTH_V1.json>)已固定以上事实；未重开PT/raw/SDK。

## 本地collector状态丢失与终末恢复（不是重启）

本轮job_list为空、旧job `pwsh-04ffe22045de4981`返回unknown；原marker23:38保持，原output目录/pointer未产。Windows仅匹配自己旧collector脚本的Python进程检查count0、没有导出其他命令行、未停止任何进程。故具体本地丢失原因UNKNOWN，不假设remoteparent停过。

NEW [terminal-only恢复源](<recover_phase1_v4_round10_closed_metadata_once.py>)在已确认原outerwait/EX闭合且自己旧进程不在后，先核相同原outer文档SHA/身份，再完整import原27/runtime→core→AppV6→Base和原schema/close validator。**无watch调用/循环/parent或资源操作**，只一次small/big own metadata packet；原producer grade/错误不重跑不改。

[恢复回执](<reports/PHASE1_V4_ROUND10_CLOSED_METADATA_RECOVERY_V1.json>)RC0（指reader运输，不是原parent成功），packet2,665,905B，旧once/root未动。新[canonical pointer](<PHASE1_E3_CAPTURE_DEVICE_BINDING_V4_LATEST_CLOSED_RESULT_PATH.json>)→[recovered CLOSED](<reports/PHASE1_E3_CAPTURE_DEVICE_BINDING_V4_RECOVERED_CLOSED_R10_20261104_004237/CLOSED_RESULT.json>)，原collector逻辑仍 **FAIL_CLOSED_CAPTURE_EXECUTION、controls:null、actualparentRC1**。Recovery job pwsh-531af5ba2d134dd0与snapshot3b06…均已RC0收，未造成功。

科学whole-FINAL应用runner仍未执行：无合格原FINAL，所以不造whole/零数据或把Source/CPU冒Stage1。

## 当前资源真实快照与唯一后台observer

[00:46新readonly资源快照](<reports/PHASE1_V4_POST_TIMEOUT_RESOURCES_ROUND10_SNAPSHOT_V1.json>)RC0，epoch1793724369.616133：

- canonical actual active owner `MOD4V1_SCUT_REPAIRED_E0_20000ENV_1H_1793723033230108600`，parent1551922，kindMOD4V1_SCUT_PPO_FINITE；开始1793723083.5611253，max_parent_seconds3900。**这是另一个原登记owner，非本agent启动或本轮E0评测结果，绝不干预**。
- 两authority WRITE PID1551922、finite_environment_validation READ PID1551922；GPU0私EX当时records空。原global finite EX与activeNone条件未满足，GPU空闲不越过它。
- remaining274232.7009584904/reserve86412.86069250107（只读快照，非writeback）；未copy C bytes/加预算/清锁/发外国signal。

NEW **只读release observer** `pwsh-cbcdaf9c3b9348d1` 已启动，当前唯一相关后台job（需以后job_output收）。[源](<observe_phase1_v4_post_timeout_release_round10_once.py>)复用原完整read-only代码，cap1800/interval20，不启动任何parent/锁/Cwrite/SDK；不是延长旧wait。current=`reports/PHASE1_V4_R10_POST_TIMEOUT_RESOURCE_OBSERVER_CURRENT_V1.json`，final=`reports/PHASE1_V4_R10_RESOURCES_RELEASED_AFTER_ZERO_GO_TIMEOUT_V1.json`。正释放见证也非lease，任何新独立用途仍要原parentfresh准入。不盲重排新1800父窗口。

## Source和下一步

D664上轮operational-gap任务失败且目录无落盘，本轮已send_message继续同只读小任务，禁止实现activation/stager/controller/新调度器；现有消息确认good stagerV2 plan enabled/staged false→stage原字保存，而parent入口要求true，待其小MD/JSON说明是否已有typed发布模块。不把消息冒已存report或本轮native证据。

可在无GPU操作下准备新的独立Admission2静态素材，但**无正资源见证不得dispatch**；旧V4 root/once/观测超时原件均不动。真实0GO已sourceclosed，有实际工作不blocked，Goal不complete。

## Git

feature HEAD9f2891dd380b2e76fd93103766a4f337cb23dbe9且clean；Phase34远端exact已验证。NEW Phase35 archive源21223/aa01d975…尚未record；它需要真实V4双wait/EX，此时已满足，能忠实归档0GO而非pass。应收v38–v43、全部V4 final Source/父回归/实际CPU/350payload/3851stage/原timeout/本地jobgap/终末恢复/新资源快照和observer点时状态，再唯一trial/feature push与remoteexact核验。归档后新observer结局/Admission2/Source gap文档等再append。

模型/raw或任何旧physical/CPU/record不为Git重跑；main仅读不写。当前没有自己活跃SDK scene或BPTT，唯一后台是readonlyobserver。
