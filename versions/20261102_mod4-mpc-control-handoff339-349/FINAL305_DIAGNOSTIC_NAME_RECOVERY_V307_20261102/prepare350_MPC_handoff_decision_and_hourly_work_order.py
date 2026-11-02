"""Persist actual motor-handoff evidence and current continuation; no checkpoint or simulation."""
from pathlib import Path
import hashlib,json,subprocess,time,tomllib
P=Path(__file__).resolve().parent;T=P.parent;R=P/'reports'
A=T/'MPC_PROCESSED_TARGET_PHYSX_COMPARISON_V349_20261102'
read=lambda p:json.loads(p.read_bytes())
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def put(path,value):
    with path.open('x',encoding='utf8')as f:json.dump(value,f,indent=2,ensure_ascii=False,allow_nan=False)
full=read(A/'reports/ROOT349_EVALUATION_FULL_RETURNED.json');result=full['result']
assert full['wrapper_error']is None and result['passed']and result['model_byte_reads']==0
closed=read(A/'reports/ROOT349_ALL_SSH_CLOSED_FREE.json');assert closed['all_owned_SSH_closed']and closed['SESSION_restored']
groups={r['group']:r for r in result['comparisons']}
assert groups['state_target']['cross']==0 and groups['processed_MPC_target']['cross']==13
assert sum(r['strict']for r in groups.values())==0
source=read(T/'MPC_TIMED_CONTROL_EXTRACTION_V347_20261102/reports/ACTUAL347_TIMED_MPC_CONTROL_EXTRACTION_SUMMARY.json')
assert source['source_controller_success']and source['stable_at_end']>3.
q=subprocess.run(['pwsh.exe','-NoProfile','-Command',"Get-CimInstance Win32_Process -Filter \"Name='python.exe' OR Name='ssh.exe'\" | Where-Object { $_.CommandLine -match 'MOD4_H1_SCUT_STEP270|RMPOLAR|watch_|run_once_after_resume|continue_clean_sequential|E1_actual|collect_e1|run_ROOT|prepare_archive' } | Select-Object ProcessId,CreationDate,ExecutablePath,CommandLine | ConvertTo-Json -Depth 4 -Compress"],capture_output=True,text=True,encoding='utf8',check=True)
assert not q.stderr.strip()
rows=json.loads(q.stdout)if q.stdout.strip()else[];rows=rows if isinstance(rows,list)else[rows]
put(R/'LOCAL350_POST349_EXACT_CONTROLLERS.json',dict(epoch=time.time(),rows=rows,scope='fresh local known-controller snapshot; no remote PID scan or authority access'))
image=A/'RECORDED349_NATIVE_FRAMES/ACTUAL349_MPC_TARGET_BODY_POSE_SEQUENCE.png'
render=read(A/'RECORDED349_NATIVE_FRAMES/ACTUAL349_RENDER304_REPORT.json')
assert image.is_file()and render['passed']and render['model_reads']==render['physics_steps']==0
decision=dict(epoch=time.time(),kind='MPC_MOTOR_HANDOFF_ACTUAL349_REVIEW_AND_DECISION350',source_report=dict(path=str(A/'reports/ROOT349_EVALUATION_FULL_RETURNED.json'),SHA=H(A/'reports/ROOT349_EVALUATION_FULL_RETURNED.json')),
 groups=list(groups.values()),native_visual_review=dict(completed=True,image=str(image),bytes=image.stat().st_size,visual_source='recorded actual349 PhysX poses; no NN or simulation re-execution',cases=[0,1,40,41],observations='All four selected cases approach platform and tip/collapse close to edge; source-target cases40/41 still fail near.98/1.00s. No selectedcase proves stablelanding; aggregate13cross from independently measured full80 outcomes.'),
 actual_scope=dict(NN=0,optimizer=0,account_writes=0,new_GO=0,source100Hz_targets_sampled_at50Hz=True,originalPD_queue_limits_physics_retained=True,matching_initial_planned_state_all80=True,DR_same_distribution_not_paired=True,recomputed_closedloop_MPC=False),
 inference='Using processed motor targets produces measured edge-crossing cases absent with state-as-target. It supports prioritizing motor-control handoff; nonpaired DR and changed plant/clock mean not a complete causal isolation or finalfix.',
 remaining=['Preserve original successful closed-loop state-dependent launch/landing feedback, not just fixed-time openloop targets.','Current training target clock50Hz does not execute every source100Hz command; do not call this exact100Hz replay.','Original MuJoCo500us and currentPhysX2500us, asset/contact/DR differences need actual controlled comparison; do not silently change solver/PD/asset.'],
 source347=dict(passed=True,source_controller_success=True,stable_at_end=source['stable_at_end'],versions=source['versions'],original_engine_version_match=False,original_source_success_intact=True),
 action=dict(training345_started=False,reason='User correctly redirected investigation to complete MPC controller; finish transfer before another hour of unverified state-only optimization.',next='Prepare a new bounded no-learning closed-loop/feedforward+feedback motor-interface comparison with explicit100Hz source versus fixed50Hz target scheduling. Preserve all existing safeguards and diagnose first real deviation before choosing training curriculum/objective.',no_identical324_restart=True,no_blind345_launch=True),
 skill_graduation=False,strict_stable_success=0,all349ownedcontrollers_closed=True)
put(R/'ACTUAL350_MPC_TARGET_COMPARISON_REPLAY_DECISION.json',decision)
work=dict(epoch=time.time(),kind='CURRENT_ACTUAL350_MPC_HANDOFF_BEFORE_FURTHER_TRAINING',human_steering='2026-11-02: 我的mpc参数都调出来了，完整轨迹，各个电机啥时候的参数啥都有，咋就是跳不上台阶呢',
 current_truth='324fullclosed+339independentactualeval/nativeviewdone;345preparedunused;346motorsemanticaudit;347sourceactualcommandextractionpassed;349actual50Hztargetcomparison13/40cross0stable;nextcorrectMPCcontrolhandoffbeforelearning',
 latest_decision=str(R/'ACTUAL350_MPC_TARGET_COMPARISON_REPLAY_DECISION.json'),audit346=str(R/'ACTUAL346_MPC_CONTROL_HANDOFF_AUDIT_NO_MODEL.json'),source347=str(T/'MPC_TIMED_CONTROL_EXTRACTION_V347_20261102'),actual349root=str(A),
 final324=dict(SHA='841dd4080ae41558645f98f1105652517716772b8b1f177df8cf8af89a0cc050',bytes=32698221,Pi=4379,WM=16879,actorAdam=52636,criticAdam=9696,CPUfinite=609,no_new_checkpoint_read_for_archive=True),
 actual339=dict(cross=0,strict=0,cases=80,orientation=56,full8s=24,mean_seconds=3.35625,nativeview_completed=True),
 actual342=dict(scope='frozenactualpairedWM64controls;not skill evaluation',one_step_position_RMSE_m=.004578864,H4_position_RMSE_m=.011496116,H8_position_RMSE_m=.018896786,H32_end_position_RMSE_m=.110839635,no_gradient_reliability_claim=True),
 prepared345=dict(run_id='REFERENCE_TRACKING345_1793579610177992700',root=str(T/'REFERENCE_H8_DIRECT_TRACKING_PRODUCTION_V345_20261102'),INDEX_SHA='1e01ecfa4c5ac91bd9b0518a7067d2bd85f8d13c5d92c931b433a87c70ba3c40',GO=False,consumed=False,postround=False,do_not_launch_before_actual_motor_handoff_decision=True,CPU344_fixture_only=True),
 actual347=dict(root=str(T/'MPC_TIMED_CONTROL_EXTRACTION_V347_20261102'),controls500=True,physics10000=True,source_success=True,stable_seconds=source['stable_at_end'],new100Hz_processed_target_trace='reports/SOURCE347_100HZ_PROCESSED_MOTOR_COMMANDS.json',original_source_not_modified=True,NN=0,network=0,GPU=0,account=0),
 actual349=dict(root=str(A),consumed=True,allclosed=True,groups=list(groups.values()),no_training=True,no_model_reads=True,not_full_closedloop_replay=True),
 immutable_failures=['335rootcontractimport0SDK/model/physics','338localCIMregex0network/model','340statickind0network/model','341localcontrollerrefusal0network/model','348unusedcopiedactorassertcaughtstatic0network/model;new349independentrepair'],
 schedule='existingmod4-10hourlyACTIVEcurrentchat;no newautomation or Goal',resource='349 allownedSSHclosed/sessionrestored/FREE; any new remote phase first freshLOCALexactknowncontrollers,serialFREE,originalCNone and private/shared authoritative locks; no secondwatcher, unknownPIDscan or kill',
 invariants='400Nengineeringk2000/policy50feedback100physics400/TGS32-4/2.5ms/fullD0whitev3D1-D7/10mmepisodeclosure/.01mimic; originalsinglecanonical budget3900save3600exit300/strictreserve; no copy/grant/refund/clearactive/secondwriter',
 git='newphase mod4-mpc-control-handoff339-349; use one record_experiment annotatedtrial; all339false/342/344345/346347348349350 source/raw/report/automation indexed; oldphase tag immutable; heavyweightbinary only pathbytesexistingSHA; do not read model for Git',
 next='Implement faithful original MPC motor-control pipeline or a clearly bounded same-interface closed-loop comparator before more training. Preserve source event feedback/launch pose,100Hz commands, mapping/scales/PD/D4/DC envelope. Original50Hz action contract cannot silently become100Hz; diagnostic must explicitly declare scheduling. After any actual run, safeclose->independentfacts->nativeactualposeview->decision. Current 13/40cross is not stable skill.',
 restrictions='No Luna/OpenRouter; current model nativeimage only. MPC plannedmotorcontrols are evidence, not an oracle PhysXactionteacher or unrestrictedforcecloning. HistoricalH1 no silent newMOD4v1 asset switch.')
workpath=R/'CURRENT_ACTUAL350_MPC_MOTOR_HANDOFF_BEFORE_TRAINING_WORK_ORDER_V1.json';put(workpath,work)
configpath=Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml');config=tomllib.loads(configpath.read_text('utf8'))
put(R/'AUTOMATION350_PRIOR_CONFIG.json',dict(epoch=time.time(),config=config))
prompt='''每小时继续本聊天MOD4跳270mm任务。人类授权“新跟踪启动”“继续看收尾然后修复”，2026-11-02最新追问“我的mpc参数都调出来了，完整轨迹，各个电机啥时候的参数啥都有，咋就是跳不上台阶呢”。本轮已据此先核控制交接，不能自动继续只改horizon/reward的一小时训练。每轮完整保存安全退出后立即独立评测和真实姿态回放，再主动修复/合理续训。保持ACTIVE/currentchat，无新Goal/重复automation；无变化或不可行动静默，仅通知实质进展、失败、完成、资源/预算/网络问题和必需用户行动。

首先读 '''+str(workpath).replace('\\','/')+'''。真实冻结source/INDEX/ownreceipt/实际进程优先。旧336工作单与335unused过时。324完整保存已关闭，609finiteCPU已通过；最终32698221B SHA841dd4080ae41558645f98f1105652517716772b8b1f177df8cf8af89a0cc050，Pi4379/WM16879/actorAdam52636/critic9696/teacher17Adam42940STD/EMA/normRNG完整。339已实际独立评测同固定edge.8/270新DR/seed9137：0/80crossstrict，56orientation24full8s，mean3.35625s；真实记录姿态原生视觉已审，绕转/偏离/台前倒。不能再称待评测。342冻结实际配对WM单步.00458m/H4.01150/H8.01890/H32末.11084m，0更新；不是技能评测/物理梯度证明。

344H8directcost候选CPU无step恢复通过；345生产包已冻结但没有STARTconsumed/部署/GO/postround。root REFERENCE_H8_DIRECT_TRACKING_PRODUCTION_V345_20261102，runREFERENCE_TRACKING345_1793579610177992700，INDEXSHA1e01ecfa4c5ac91bd9b0518a7067d2bd85f8d13c5d92c931b433a87c70ba3c40。保留unused，不在MPC控制交接问题未清楚前盲启345。不要修改冻结源/INDEX。actor已有103=35proprio9depth59reference/critic106不是depth-only毕业；CPUfixture不当物理成功。

346明确源码断点：成功MPC100Hz闭环desiredtorque经inversePD转电机target，再D4/PD/DCclip；reference prepare只取qpos/qvel/wheelpose/support并500点取250，tau/appliedtorque丢弃。311是计划关节状态直接作PDtarget，不是忠实MPC控制复现，不能据它失败否定人类MPC。sourceMPC按测得位置/速度触发起跳、实测launchpose、接触触发landing；reference固定episodephase不等价。sourcephysics.0005与当前PhysX.0025，不能宣称唯一因果。

独立347为导出先前缺失的processedtargets/实际application做一次localCPU MuJoCo运行，MPC仍success且stable3.02s，500commands/10000physics，0NN/GPU/SSH/账；本机MuJoCo3.15与原3.12不同，不能称逐点复现原结果，原source不改。目录MPC_TIMED_CONTROL_EXTRACTION_V347_20261102，完整100Hz命令reports/SOURCE347_100HZ_PROCESSED_MOTOR_COMMANDS.json及实际physicsNPZ已有producerSHA。腿target-stateRMSE.13-.16rad/wheeltarget-dq约2.9rad/s，state不等电机command。

独立349已实际执行并安全关闭，0NN/训练/优化/账写。目录MPC_PROCESSED_TARGET_PHYSX_COMPARISON_V349_20261102，ROOT349_EVALUATION_FULL_RETURNED和allSSHclosedFREE可查。全部80同plannedinitial，0..39state-as-target50Hz：0/40cross，40orientation0full5s，mean1.0855s；40..79processedMPCtarget50Hz：13/40cross，33orientation7full5s，mean1.706s；两组strict0。两组DR同分布非逐项paired，source100Hz只取20ms命令并hold20ms，非source完整100Hz闭环controller。支持先修电机控制交接，不证明唯一原因或毕业。原生审图已完成RECORDED349_NATIVE_FRAMES/ACTUAL349_MPC_TARGET_BODY_POSE_SEQUENCE.png；所选四case仍台前倾倒，13cross是全80实际测量，未稳定。

下一步应独立版本做忠实MPC或feedforward+feedback控制链的有限对照，先明确100Hzsource与现50Hzactor/100Hzfeedback/400Hzphysics时序，不能静默改变原queue.control_us、solver/PD/限幅/资产；也不能把openloop目标说成可任意查询PhysX的MPCteacher或做无限制torquecloning。优先核首个偏离时刻、实际target/关节/力矩、eventphase和同初态/DR；根据真实结果再决定参考跟踪/残差策略训练方式。保持原目标和剩余预算，不原样继续绕转学生。

335import/338regex/340kind/341localcontroller拒绝与348unusedcopiedactorassert静态缺陷全部原false保留；349独立修复成功执行。原324normalCPU/328/335/339/342/347/349所有consumed永不重放。any finiteSSH先freshLOCAL广范围exactCIM含RMPOLAR/watch/run_once_after_resume/E1collect/prepare_archive等knowncontrollers，确认serialFREE后连接；parent再原CNone/private/shared准入。活controller只读本地、不双watcher/抢锁/清active/kill/unknownPIDscan。SSHfinallyclose/SESSIONrestore/FREE。

400Nengineeringk2000/policy50feedback100physics400/2.5msTGS32-4/fullD0whitev3D1-D7/10mm单envclosure/.01mimic不改；原singlecanonical3900save3600exit300/strictreserve，不grant/copy/refund/clearactive/第二writer。根/repoAGENTS新MOD4v1registry遵守，historicalH1不暗换资产；84x48暂定camera非D435i实机标定FPS。成功须首次腾空越沿/整轮footprint顶面/.5s稳定与实际contactmanifold，13cross/loss/COM腾空不毕业。禁Luna/OpenRouter，当前模型原生视觉。

所有source/report/rawfalse/once/回放决定/automation入Git，遵polar-rl-train/docs/ALL_TRIALS_AND_REPORTS_GIT_POLICY.md。新phase mod4-mpc-control-handoff339-349，查实际RECORD351/trial对象，已record不重record/retag；后续ordinary补充，push失败续existingobjects。原324phase tagobjectd2e4c479f7ecd7a2974f022a0571c826746fe225/peelb4412bafb86d7f7e4f350feafc7a6bed6c45591e、所有旧tags/peels及lqr5848b45a99b8c32af02eb61b507c3f95ab39e4ad保护。PT/NPZ/USD/media只实际pathbytes已有SHA索引，不为Git读模型/重跑physics。凭据只原memory不输出/入Git。postGit验证工具输出，不追HEAD报告循环。'''
request=dict(id='mod4-10',mode='update',kind=config['kind'],name=config['name'],prompt=prompt,status=config['status'],rrule=config['rrule'],targetThreadId=config['target_thread_id'])
if 'notification_policy'in config:request['notificationPolicy']=config['notification_policy']
put(R/'AUTOMATION350_UPDATE_REQUEST.json',request)
print(json.dumps(dict(passed=True,workorder=str(workpath),groups=list(groups.values()),source347success=True,training345GO=False,resource349allclosed=True,automation_request=str(R/'AUTOMATION350_UPDATE_REQUEST.json'))))
