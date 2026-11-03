# 接续 R63：仅timed-push名义气弹簧FF反补偿，尚未物理准入

## 目标、环境与冻结边界

用户19:39再次要求继续。父实读Goal `goal-4d4bef80-e614-432d-a8cd-8f385ef2dd7d` revision14/roundsStarted8/max12，active/armed；不要重建或提前complete/blocked。cwd F:/RMPOLAR-RL；Python C:/Users/lulu/AppData/Local/Programs/Python/Python314/python.exe，-B/BLAS-OMP-MKL1，最多4物理CPU；无GPU/SSH/PPO/canonical/专家工作树或index/新agent/Mnemon写。Office/ACL技能与本轮控制代码不匹配，用文件/CLI；dangerfullaccess、approvaldisabled，不escalate。只复用C `abf2088f-af10-479a-9108-202785031447` 与model `e4e6c8f2-f08d-4df1-9150-945c804e8c2a`。

[开源任务接续](<CONTINUATION_OPEN_SOURCE_V1.md>)、[R62实际关闭](<CONTINUATION_R62.md>)保存旧事实。SPR/Qi审读已完成并交付；MATLAB有帮助非必需，未安装/运行。H1/H2/H4/H5/Stage1与所有旧模型/gain/gates保持；H5仍40/64，R62新AIR002所选四TRAIN1/4相对旧同四2/4，不作成功替换。PH7真commit223577994e0f750e0ae062ce9ffee204273c90a2已推送，不重record。

## 已完成：名义弹簧符号/端点

[分解报告](<SPRING_PUSH_DECOMPOSITION_V1/REPORT.md>)41行与[receipt](<SPRING_PUSH_DECOMPOSITION_V1/RECEIPT.json>)82行父已read。静态式rhs=L-tauMotor-G-other，因此固定其余项撤抵消为FF_new=FF_old+G，而非删gravity/整trim或物理spring/damping。G是absolute motor joint-output Nm，LEG0/1/3/4；delta协向量不是执行器行。

一次1NominalModel/3terms/27FK，168checks0、17typed错误；FD最大1.016857709e-9Nm、虚功2.034e-10W，门未放宽；0MuJoCo/旧QA/DR/PHY。端点数据[ENDPOINTS](<SPRING_PUSH_DECOMPOSITION_V1/ENDPOINTS.json>)SHA1b47bb7d75205c907f9116cb658adbb2922e82decee2c9b19c2fab8d86db762e，[helper](<SPRING_PUSH_DECOMPOSITION_V1/spring_push.py>)SHA5732a0b3ba3338ec8d573a66fb9884871bc2abda7f960db2cd9deb6e7708bde9。Crouch G4约[-12.76046,+12.76046,-12.76046,+12.76046]，pushend约[-17.88960,+17.88960,-17.88960,+17.88960]。轮增量0且旧微小trim bit保留。仅名义端点、两端混合非任意q(t)精确去弹簧，实际DR/中间动态误差未知。

## 新controller与已完成单测

[controller](<SPRING_PUSH_RELEASE_V1/controller.py>)SHA8d59143b961e1ff93e284cd81be8070508d580509985aa41e3d26db7ab4e8765。继承Position→LandingV3→ObserverV2→V1，绝不叠AIR002。默认False；先旧gain构造Base，才为push创建新dict+新tau数组；LEG加G而wheel不加0；super一次/finally还原g/end identity。GroundController.tau_eq原本alias原gain，已避免污染。firstpush不要求launched；旧guard/position下一tick/observer/PD/32限/roll/yaw/wheel/final40不变。仅静态FF改变，后续相同公式不保证不同闭环轨迹相同。

C已一次执行[新UNIT_RESULT](<SPRING_PUSH_RELEASE_V1/UNIT_RESULT.json>)PASS_NEW_500X3_SYNTHETIC_NOT_PHY，父已read26行：9129checks0，3实例各500帧，101approach/14push/25flight/360capture，Geometry84(内部pose420)<128，0新NominalModelFK/0MuJoCo。defaultoff旧math/log/ref/ctrl/observer bit同；enabled push原式oracle误差0、wheel bit同，非push固定输入bit同；firstpush1.01此前launchedFalse但appliedTrue，9typed/guard/finally错误通过。不是1500机器人trial，不重跑500。

[新entry](<SPRING_PUSH_RELEASE_V1/run_manual_spring_push_v1.py>)108行、[binding](<SPRING_PUSH_RELEASE_V1/binding.py>)34行父已read。缓存/旧gain q与τ/表与helperSHA在真实plant构造前验证；默认off不读表。loop及原good/main/local/FullDR/driver表达式AST保持。metadata新kind NEW_NOMINAL_SPRING_RELEASE_PUSH_ONLY_TRAIN、result enabled来自实际hop、manifest requested、dataSHA与CORE/ENTRY/DATA actualfile records齐全；标明push改、air/capture公式未改。C实际ENTRY_RESULT已PASS26/0，父已read关键字段：help1、actualCtor2/fakePlant2/fakeDR2，packet/loop/actuator/Geometry/MuJoCo/NominalFK全0；5 binding错误都在预期路径，默认off补偿读0。第一次admission harness在任何执行前因`__code__and`连写SyntaxError；父read原source/log后仅批准1空格修正，原版/失败记录保留，新run_entry_once_v2.py先AST及逐byte反查再一次执行；未重复500/数学。实际entrySHA b7a8c4b76192a57d0e4e63ce9b4c0ad9a1cfde78451a21dea855b16d6aaf82c3，bindingSHA7f0135b063a8c4d6f459972d8ce40172d038322efbf744c62e8df949c93df4a4，harness9e5fcb6ce0a80e95a74bdefce1825c4be8ebb5e37308cd597522a95e667f2044。这仍不是真实模型准入。 [查路径事件](<SPRING_PUSH_RELEASE_V1/READ_ERRORS.json>)只两次猜错旧目录，0unit/PHY事件，已实际import链解决。

## 父工作流已完成与仍待验证

[generic binder](<candidate_case_evidence_v1.py>)SHAf81c5655465a9ef6b59ff47456fd40c66bacf551f3b1db4db75f222ba6817174：实际config/result.config canonical全量匹配、kind/严格feature、CORE/ENTRY/DATA runtimeSHA=source lock且data字段相同；只关联不是动态资格。

[V5 nominal launcher](<launch_manual_profile_train_v5.py>)SHA389f70fd5c4d197998c0894cb5585477d53531286c067946a37ebb21fc521808：V2 artifact软件stop不动；flat后先实际关联再按原gate/匹配profile选RM；RM后再关联，source/review/parentapproval均绑定。由[deriver](<derive_candidate_nominal_launcher_v5.py>)仅AST生成。

[新工作流preflight](<PARENT_R63_BINDING_PREFLIGHT_V1/RESULT.json>)一次12fixtures/25checks0，8metadata+4实际V5顶层mock，共6fakecallbacks、0真实进程/controller/model/PHY。mock controls1/steps20绝非机器人消耗；不重跑旧16fixtures。[model缓存](<R63_PHASE_SOURCE_REVIEW_V1/WORKFLOW_MATH_DELTA_002.json>)仅新5文件已read/hash，未发现delta blocker；仍等待最终entry/unit/protocol，不是物理审批。

[草案计划](<R63_SPRING_PUSH_PLAN_V1.json>)只新nominal flat→matching RM，全部原gate；通过RMlocal+mainfirstflight后另审批固定旧TRAIN4602/4605/4606/4610，属于旧outcome选择的机制队列非独立holdout。最多6case/4800ctrl/96000steps只是预算，本轮至此实际新R63 PHY仍0。新[paired launcher](<launch_r63_spring_paired_train_v1.py>)已写但未执行/终审：两波各2，wave后关联失败则停未来波；实际保存行/未启动/无batch未知要区分，不推预算为消耗。尚待新元数据workflow测试和review；不可直接launch。

父已一次执行[metadata preparer](<prepare_r63_spring_nominal_v1.py>)，PASS_R63_METADATA_FREEZE_FROM_SAVED_ZERO_STEP_EVIDENCE_NOT_DYNAMIC_ADMISSION；[nominal plan](<R63_SPRING_PUSH_ADMISSION_V1/PROTOCOL.json>)/[source index](<R63_SPRING_PUSH_ADMISSION_V1/SOURCE_PREEXEC.json>)/[metadata result](<R63_SPRING_PUSH_ADMISSION_V1/RESULT.json>)冻结74small源，0新controller/model/PHY/旧QA，原loop+grade AST一致。model已受托最终delta终审(另审paired代码条件)，尚无父launchapproval；下一步read最终review，父hash-bound approval后V5新nominal。若flat失败RM延期；若软件错误停波留prefix；无内批改gain/阈值/时序/种子。物理之后按原门和实际数记录，不宣传270已成。

## PH8源码快照正在独立推进，不是Git审批

[明确cutoff](<PH8_ARCHIVE_CUTOFF_R62_INSIGHT.json>)父已写，model agent正在ownrepo PH8_SOURCE_PREPARATION：仅关闭R62六物理(4800/96000、nom2/2、所选四1/4)、诊断/两开源材料/私有geometry/centroidal/新sealed弹簧数学；active SPRING_PUSH_RELEASE、R63 plan/binder/V5/mock等全部排除。cutoff中的简写case名只是提示，实际从三个闭合PROTOCOL核对r62_airref002_paired_RM_DR_*。

只snapshot到review handoff/manifest/资格边界/consistency/gaps；未授权commit/tag/push。大raw/PDF/ZIP/USD/mesh只producer metadata，不为归档重读或重hash；SPR CRC不冒新cryptographic SHA、Qi LF/CRLF双SHA保留。历史missing/conflicting保留unknown。其他专家树/index不碰。R63所有新代码/测试仍后续PH9或下一稳定cutoff待定，不塞已锁PH8。
