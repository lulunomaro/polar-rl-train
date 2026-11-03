# v42：V4完整物化/单父控已启动，原资源锁等待；唯一collector继续

2026-11-03 23:46 +08:00。Goal最新实际rev15/active/armed9/48保持；Stage1真实接口仍未通过、Stage2训练不放行。H1/母本/Registryv12/原physics/fullDR/接受/资源C/期限保持。详细已封来源见[v40](<CURRENT_PROGRESS_v40_V4_WORKER_SEALED_PARENT44_CPU_PASS_PROPAGATION_FINAL_PENDING.md>)；本次不是E0技能评测/新训练。

## 当前唯一相关后台工作（不要重复）

**`pwsh-04ffe22045de4981`**：由[一次V4 collector caller](<collect_phase1_capture_device_binding_v4_closed_metadata_once.py>)启动，唯一own metadata collector，20s/cap6000仅其观察时限，原parent1800preGO/900ready/2400worker未改。它仍running，最近一次job_output无新stdout。没有第二观察器/新parent、没有自己的SDK scene获准入证据。

NEW独立root：
```text
/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_PHASE1_E3_PASSIVE_CAPTURE_V1_DEVICE_BINDING_V4_20261103_232922_1793719762179514600
```

- [实际preflight](<reports/PHASE1_E3_CAPTURE_DEVICE_BINDING_V4_ACTUAL_PREFLIGHT.json>) RC0；[实际stage](<reports/PHASE1_E3_CAPTURE_DEVICE_BINDING_V4_ACTUAL_STAGE.json>) RC0，**3851件/独立原static3592/3冲突retained**。比V3多12个readonly boundary proof（8member+seal+3source refs），不是多runtime。stage SHA **`9288a45e4301854f051567015027e1b4788c36de1630037b3dff05ed1bf391f8`**。
- [实际单parent dispatch](<reports/PHASE1_E3_CAPTURE_DEVICE_BINDING_V4_ORIGINAL_PARENT_DISPATCH_ONCE.json>)：epoch1793720016.3392937，controller**1549982/startticks146140012**、parent**1549989/startticks146140035**，GPU0 UUID `GPU-16828f91-2b45-b646-8dc0-9481138e2842`。parentd557/controller9595及全部实际资源门原样。**Popen不是GO**。
- [一次只读own发布metadata快照](<reports/PHASE1_E3_CAPTURE_DEVICE_BINDING_V4_ACTUAL_ADMISSION_SNAPSHOT.json>) RC0，job `pwsh-51cdc40e8eda42f8`已收：admission/children/barrier/parenterror/exit均null；原wait39条，latest epoch**1793720587.009296**，`[Errno 11] Resource temporarily unavailable`，locks_held0/SDK_or_selected_model_openedfalse/Cwrites0/remaining_wait1229.9434364628978。本快照没有验证具体外部owner，不猜owner、不清锁、不延时。尚无SDK/selectedPT open、无技能分数，非0%技能。

原uploader/stage/dispatcher都已once消费，不可重放。原parent将自己fresh检查/自然超时/实际wait/finally EX释放；父不发外国signal、不复制/清canonical/退款/加窗口。若collector通知完成，先job_output收原RC和actualclosure，再读新pointer，不relaunch。

## 最终来源已父核，非native证明

- worker4 final13/ba340…，index134423/75e36…；单行env.device→已有bridge.device；其余4candidate和原大闭包不改，父44通过。
- mat4 final11/68c5e…，332R-relative镜像/350payload4,666,872B；父44/41.549s、audit0，完整原static/B2/Source8/同bootstrap/AppV6-fullBase/独立origin-retained-stream保留。
- collector4 final9 **seal4866/23a5267920106b40b1efcf5db7921a16c6418621365d18933f0c9d69bfefc594**、rootff037967e391148328fc7a3400eb30b41b1123cab5313954d87e2d779067ba2c；[父51](<reports/PHASE1_COLLECTOR_V4_PARENT_SOURCE_VERIFY_V1.json>) **51/51/3.210s**，原50/B2extra174/boundary9三库分开、production AST仅report尾、wholeFINAL1read/cache/projectiontruth/producergrade/双waitEX全保。无Source升级现场flags或根因。
- 原小[实际CPU报告](<reports/PHASE1_BOUNDARY_DEVICE_ACTUAL_CPU_V1.json>)仅synthetic字符串/规范设备对照2步11负例/RNG输入不变，actualV3flags未记录/null。V4仍需真实SDK验证。

## 后续准备（未执行）

[科学whole-cache processor源](<phase1_scientific_capture_cache_apply_v1.py>)与[NEW runner源](<run_phase1_v4_scientific_capture_application_once.py>)已写、**未消费/无actual whole trace读取**。仅若V4真正qualified闭合，才新科学用途读原whole worker+group FINAL各一次bytes/hash/decode，其他完整metadata复用collector，原projection不可冒whole；委托已封pure+application，保留unknown/contradiction，不自动放行Stage2。若缺/失败FINAL则不调用，不造数据。原pipelinecollector读取仍是自己生命周期用途，科学用途另ID，不为标签/Git重读旧raw/模型。

BAC good-holdoutV2 SOURCE review最终PASS(scope)/非launch，父read44行；D664现NEW `source_good_holdout_operational_gap_review_v1` **只读**追踪enabled/staged真实source路径和未来每seedcontroller/collector/outerwait缺口，不实施activation/fix/调度或实际stager/模型/SDK/C。好专家质量评测尚未运行，接口V4优先。

## Git

Phase34 actualremoteexact HEAD9f2891dd380b2e76fd93103766a4f337cb23dbe9、tagobj35fb29b7bf40dc9a02a1896359449b66e8ce238d；main只读359505…无写。NEW [Phase35 archive源](<archive_phase35_v4_device_contract_delta.py>)**21223/aa01d975ac9c764183a9e0255d8941188d49d0c0716965d8cdcb931689261041**仅生成未record，guard要求本次V4真实双wait/双EX后才能消费；失败/0GO也保留实际状态，不强要pass。

**v38–v42/CPU fixture与actual结果/V4最终源+父回归/350payload/实际preflight-stage-dispatch-本次wait快照/未来闭合/pureapp与good-review/新SOURCE后续均待Phase35。** 必须实际closed后记录、唯一annotated trial/feature only push和remoteexact；任何新科学analysis/后续fix/报告在该capture后再append。原once/物理/模型/raw不为Git重跑。Goal继续active，不complete/blocked。
