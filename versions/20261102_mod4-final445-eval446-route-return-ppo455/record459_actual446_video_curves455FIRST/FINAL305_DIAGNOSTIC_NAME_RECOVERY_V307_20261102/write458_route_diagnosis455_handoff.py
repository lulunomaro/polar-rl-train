"""Actual work order after detailed human-requested video/curve review; local only."""
from pathlib import Path
import datetime,hashlib,json,subprocess,time,tomllib
P=Path(__file__).resolve().parent;T=P.parent;R=P/'reports'
N=T/'RL_ACTUAL128_RETURN_PPO_PRODUCTION_V455_20261102';Q=T/'RL455_SINGLE_PROCESS_POSTROUND_V456_20261102';E=T/'RL455_FINAL_INDEPENDENT_EVAL_V456_20261102'
D=T/'RL_MOTION_ROUTE_DIAGNOSIS_V457_20261102'
read=lambda p:json.loads(p.read_bytes())
def put(p,v):
    with p.open('x',encoding='utf8')as f:json.dump(v,f,indent=2,ensure_ascii=False,allow_nan=False)
def identity(p):return dict(path=str(p),bytes=p.stat().st_size,SHA=hashlib.sha256(p.read_bytes()).hexdigest())
status=read(N/'reports/ROOT455_STATUS_FIRST_UPDATED.json')
selected={Path(r['path']).name:json.loads(r['UTF8'])for r in status['full_selected_UTF8']}
first=selected['FIRST_ACTUAL_TEACHER_DEPTH_STUDENT455_UPDATE.json'];go=selected['GO_PRODUCTION.json']
binding=read(N/'reports/ROOT455_LIVE_FIRST_VALIDATED_AND_OWNER_BINDING.json')
assert first['passed']and first['controls']==128 and first['student']['actual_onpolicy_samples']==10240
assert first['first_complete']['actor_Adam_step_min']==56635 and first['native24_before_first_WM_step_passed']
launch=read(N/'reports/POSTROUND456_WAITER_LAUNCH.json');assert launch['PID']==56540
cmd="Get-CimInstance Win32_Process -Filter 'ProcessId=56540' | Select-Object ProcessId,ParentProcessId,CreationDate,ExecutablePath,CommandLine | ConvertTo-Json -Compress"
exact=subprocess.run(['pwsh.exe','-NoProfile','-Command',cmd],check=True,capture_output=True,text=True,encoding='utf8')
local=json.loads(exact.stdout);assert local['ProcessId']==56540 and str(Q/'postround456_close_actual455_eval_once.py').replace('\\','/').lower()in local['CommandLine'].replace('\\','/').lower()
put(R/'ACTUAL458_SOLE456_LOCAL_TIMER_EXACT_CIM.json',dict(epoch=time.time(),row=local,read_only=True,no_network=True))
diagnosis=read(D/'reports/ANALYSIS457_ACTUAL446_ROUTE_ACTION_CONTACT_REWARD.json');native=read(D/'reports/NATIVE457_ROUTE_CAUSAL_EVIDENCE_AND_LIMITS.json')
closed=read(R/'ANALYSIS450_FINAL445_ACTUAL446_FACTS_AND_REPLAY_REFUSAL.json')
assert native['all80_top_force_absolute_max_N']==0 and native['native_review']['current_model_native_review']
iso=lambda epoch:datetime.datetime.fromtimestamp(epoch,datetime.timezone(datetime.timedelta(hours=8))).isoformat()
work=dict(epoch=time.time(),local_time=iso(time.time()),human_request='详细看视频，看曲线，看机器人为什么跳不上台阶，机器人为什么选择这个路线而不去跳台阶',
    human_goal='RL actually jumps onto270mm and recovers stably; MPC success is not delivery',
    actual445closed={k:closed[k]for k in('modelSHA','modelbytes','Pi','critic','totalWM','newWM','actorAdam','criticAdam','formal','final','CPU790finite','originalfee','historical_closingbalance','allownwaited_private_shared_released','allSSHclosedFREE')},
    actual446={k:closed[k]for k in('strict','whole_footprint_clear','leading_cross','airborne','full8s','mean_seconds','median_seconds','terminations','longest_top_support_s','mean_tracking_cost')},
    original446_replay_error=closed['replay_failure'],correct451_recovery=identity(T/'RL445_ACTUAL446_REPLAY_RECOVERY_V451_20261102/reports/ROOT451_ACTUAL446_SELECTED_REPLAY_TRANSFERS.json'),
    detailed457=dict(root=str(D),analysis=identity(D/'reports/ANALYSIS457_ACTUAL446_ROUTE_ACTION_CONTACT_REWARD.json'),native=identity(D/'reports/NATIVE457_ROUTE_CAUSAL_EVIDENCE_AND_LIMITS.json'),
        readable=str(D/'README_实际回放与曲线诊断.md'),all400frames4cases=True,current_model_native_reviewed=True,
        measured=native['measured_conclusions'],limits=native['untested'],first128_return_is_test_not_proved_fix=True,
        extra_limit='At.98-1.02s recorded forwardvelocity reverses sharply. Wheelmanifold has no top/edgecontact then; allnonwheel contactmanifolds were not saved. Cannot exclude nonwheel impact or attribute solely to wheels/inair actuation.'),
    actual455=dict(root=str(N),run_id=first['run_id'],source_model_SHA=go['source_SHA'],INDEX=identity(N/'INDEX455_SOURCE_TASK_CALLERS_FROZEN.json'),
        workerSHA=read(N/'TASK455_FROZEN.json')['worker_SHA'],sourceoffsets=dict(actor=56634,critic=13694,WM=36159),
        current_binding=identity(N/'reports/ROOT455_LIVE_FIRST_VALIDATED_AND_OWNER_BINDING.json'),
        original_owner=binding['exact_original_owner'],worker_initial_beforeexec=selected['WORKER_ORIGINAL_IDENTITY_BEFORE_WAIT.json'],
        exact_current_worker=binding['current']['rows']['jump_72']['worker'],
        GO=iso(go['learning_started_epoch']),SAVE=iso(go['save_deadline']),NOMINAL=iso(go['nominal_end_epoch']),normal_earliest=iso(go['nominal_end_epoch']-900),
        FIRST=first,progress_snapshot=selected['LATEST_PROGRESS.json'],FIRST_snapshot_time=iso(selected['LATEST_PROGRESS.json']['epoch']),
        no_remote_refresh_while456active=True,actual128return_controls=128,GAE_lambda=1.,gamma=.99,
        no_reset=True,no_onlineMPC=True,not_depth_only=True,reward_physics_deterministic_action_unchanged=True,
        all_networks_threeAdam_EMA_normRNG_savedorigin_preserved=True,training_realupdated=True,independent_skill_unproven=True),
    sole456=dict(root=str(Q),INDEX=identity(Q/'INDEX456_POSTROUND_FOR455_FROZEN.json'),launch=launch,exactCIM=local,
        BIND_consumed=True,POSTROUND_once_consumed=True,sameprocess_normal_CPU_eval=True,
        result=str(N/'reports/POSTROUND455_RL_REPLAY_EVAL_DECISION.json'),evalroot=str(E),
        image=str(E/'RECORDED456_NATIVE_FRAMES/ACTUAL456_RL_BODY_POSE_SEQUENCE.png'),
        action='Read localwaiter/results/children/once first; alive: no secondSSH/watcher/normal/CPU/eval; onfinal verify actual80/manifold and view_image actualpose then apply detailed457curves to455 before furtherchange'),
    next='Finish alreadyrunning455 and sole456. Compare earlywheeldifferential/yaw/pitch/verticalspeed/wheelclearance/firstgroundreturn/topmanifold. No unchangedhour from survival/loss and no repeatedtraditionalMPC experiments.',
    original_once_never_replay=['445launchFIRSTnormalCPU446eval','451transfer','453staticunused','454CPU','455launchFIRSTbind456'],
    resources='No newfiniteSSH while456alive. Otherwise freshLOCALwideexactknownCIM/serialFREE,parentfreshCNone/private/shared; never steal active/kill/unknownPIDGPUscan; finallySSHclosedSESSIONrestoredFREE',
    budget='Original solecanonical3900save3600exit300strictreserve unchanged; no grant/copy/refund/clearactive/secondwriter. Closingbalances historical only.',
    physical='400Nengineeringk2000/50policy100feedback400physics/.0025TGS32-4/fullD0whitev3D1-D7/.01closureperenv/.01mimic/originalPD_DCclip_queue_solver/historicalH1asset. Camera84x48provisionalnotD435iFPScalibration.',
    success='firstflightwholewheelrearfootprintclear,doublewheelactual400Hztopmanifold,nogroundedge_return,vxyvz<=.03,rollpitch<=10deg,yaw<=.2radcontinuous>=.5s',
    archive=dict(phase='mod4-final445-eval446-route-return-ppo455',record='RECORD459',do_not_retag_previous=True,previous448object='d4a60f4a47b341f46693802d3e7e13021b753612',previous448peel='49319b0e662beaf48afb25094ba780ebfb319be7',previous449main='f30410178844fbd6d122922f218831b1ac095821',lqr='5848b45a99b8c32af02eb61b507c3f95ab39e4ad',alltext_reports_failed_once_required=True,binary_metadata_only_no_modelread=True))
workpath=R/'CURRENT_ACTUAL458_FINAL445_EVAL446_VIDEO_CURVES_LIVE455_SOLE456_WORK_ORDER_V1.json';put(workpath,work)
put(D/'reports/READER457_TOOL_OUTPUT_LIMITS_AND_UNRESOLVED_IMPULSE.json',dict(epoch=time.time(),no_experiment_replayed=True,
    original_tool_read_errors=[
        'Wrong456reportroot looked inQ456/reports; actualPOSTROUND456_WAITER_LAUNCH is inN455/reports; correctedread.',
        'Guessed H1_STEP270_ON_POLICY50_NATIVE_V194 directory absent; actualFUDAN_JUMP_LITERAL_PLANE_400N50_DR_TWO_HOUR_V194 and240package used.',
        'Guessed residual_command389.py absent; no moduleexecution occurred.',
        'Broadrg returned denied rmuc2026_work/unpack_verify_4zomhj13 and truncatedpathlist; no inference fromincompleteoutput; subsequentsearchscopedactualroots.'
    ],
    plot_limit='Earlierplot06autolimitsincludedkinematiccurveoutsidefocusinterval; independentChinesev2plot08setsdisplayedtimeandanglebounds, oldfigurespreserved.',
    unresolved_impulse='ActualrootandnominalmassweightedbodyCOMshowforwardvelocityreversalnear.98-1.02s; wheelcontactmanifolddoesnotcovernonwheelcontacts. No claimthatallrobotcontactsabsent or thatactuationonlyexplainsimpulse.',
    asset_scope='Read historical240asset/contract and243visualmeshes forgeometrydiagnosis only; no newSDK/physics/inference or newassetadmission. USDstageunitmetadata was not used asphysicalcalibration.',
    modelreads=0,NNinference=0,SDK=0,newphysics=0,network=0))
cfg=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text('utf8'))
prompt=f'''每小时继续本聊天RL跳270mm。人类明确“我需要的是rl上台阶”，最新要求“详细看视频，看曲线，看机器人为什么跳不上台阶，为什么选择这个路线”。先读 {workpath.as_posix()}，再读其detailed457 readable/analysis/native。实际source/INDEX/ownreceipt/确切进程与结果优先。保持ACTIVE/currentchat，不新Goal/chat/automation；无变化或不可行动静默，仅实质进展/失败/完成/资源预算网络问题/必需用户行动通知。

445已经fullsave安全关闭/fullformaltransfer/CPU790finite。final34229331B SHA056410f592d07ff63c3acc6adac4d1ebb0357bc154e817568bec56ba155f18ed，Pi=PPO=critic169/WM36159，actorAdam56634critic13694、三Adam/teacherSTD42940/EMA/normRNG/savedorigin完整。normal445CPUonce已消费不得重放。实际44680firstepisodes400controls8s/seed9137samefixededge.8/270newDR完成：0strict0wholeclear0leading80airborne22orientation58full8s/mean6.15125s，全部真实400Hz台顶接触力最大0。不是待评测。原446本地replaydest已复制437的包导致transfermkdir拒绝，原false保留不覆盖；物理446结果有效。451独立只取实际446四个已保存NPZ核两端SHA，0NN/SDK/physics，已关闭释放；原copied446replay不使用。

457已经做4例各400帧实际姿态慢放、侧/俯视密集15帧及6组曲线，当前模型view_image原生已审；图/MP4/GIF/CSV/完整分析在 {D.as_posix()}。测量：前.4s保存前馈左右轮均值2.008/1.896rad_s，被RL残差-7.257/+4.759改为总目标-5.249/+6.655，实测-5.505/+4.004；.4s轮速差积分yaw30.76deg接近实测31.08deg，pitch22.05deg。初始depth识别270mm且四例前20拍valid1，首次missing在.44-.48s后，不能称初始盲视或显式绕路规划。actor无路线planner，6路电机残差形成弯路线。四例轮心最高.240-.286m，较低轮底最高.176-.206m，台顶.270，参考轮心.38-.40。约.76s起跳、1.10-1.12s落回地面，还没到台沿；后续轮胎立面接触2.12/2.30/2.46s且z仅.05-.06m。全80topmanifold0。约.98-1.02s存在前速反转，未保存全非轮manifold，不能排除非轮碰撞，勿把轮胎晚接触推成整机此前绝无碰撞。

逐拍reward各项重建与原均值误差<.001；.4s已yaw31deg/pitch22deg仍reward.964，rotationcost贡献.0383；台前卡住仍~.22/拍。错路线有位置罚，不能说reward奖励绕路；当前reward无显式首次整轮/台顶manifold成功项，短32拍.64s GAE.95与饱和旧策略可能形成存活撑台局部解，尚非唯一因果证明。今后不只报告寿命/loss或盲调参数，必须比较早期差速、姿态、轮净空、首次落地和实际台顶支持。

455在详查前已真实启动，不再launch/FIRST/bind。root={N.as_posix()}，run ACTUAL_RESIDUAL_PPO455_1793628540456858000。owner1486968/create1793628647.19，node1486977/create1793628647.62，worker1486992/create1793628653.76完整exactworker见458绑定；初始Popenbash与后exec身份分开，不unknownPIDscan。GPU-c27eecbd-6838-7290-1cd2-37e34522213d。INDEX455SHAb8a4ce9993381fb15be3fcf2505ad8259686e574648780cefb3495f68c5bfe8f，workerSHA26a291d2ee019707f516a9c0277a8f3610f60056085071f681a94cb22fe420d2。GO{iso(go['learning_started_epoch'])}/SAVE{iso(go['save_deadline'])}/NOMINAL{iso(go['nominal_end_epoch'])}/normal最早{iso(go['nominal_end_epoch']-900)}。原3900save3600exit300唯一canonicalstrictreserve保持，健康不restart/hotpatch/startup或验模重复。

455完整恢复final445所有网络三Adam/STDteacher/EMA/normRNG/savedorigin，offset56634/13694/36159，CUDAresidualRNG真实恢复，physicalDRqueue/replayfresh。实际PPO128controls2.56s/10240samples/GAElambda1/gamma.99/oneepochclip.2，改变实际回报归因窗，reward/physical/deterministicformula保持。饱和感知latentGaussian floor.15/gain.6/cap2与postAdamfullGaussianKL<=.01/maxresidualdelta<=.05保持，每proposal回退完整weightsAdam、一次acceptedcommit。actor103=35proprio9depth59reference/critic106，固定347processed50Hz前馈+1*tanh(actor-origin)，无onlineMPC/接管/torquecloning，非自主depth-only；WMH32独立无actorWMgradient，futuredepthGTmap不入imagination。453metadata32原staticfalseunused保留不执行；454必要final445一次CPUfullrestore和合成fixturepass，不当actualdata，不重PT读。

455真实FIRST128controls10240ownpairs1024physics256feedback，PPO=Pi=critic1/newWM97total36256，actorgrad3.038812critic13.074018/native24通过；KL.002595513/delta.02385843/halfLR5e-5一次commit，doneGAEtrue/terminal0/actorWMgradfalse。首完整32811065B SHAaafc1446bc5d07459e7467efec80f223f161155252e384ac037e99aedc656449，actorAdam56635critic13695WM36256。snapshot576controlsPPO4/WM36704/124orientation仅训练重复episodes，不是独立技能评测。FIRST不是FINAL或成功。

唯一local456已绑定PID56540/create2026-11-02T22:17:53.666981+08，完整CIM见458。root={Q.as_posix()}，INDEX456SHAf09cdab0da5eca1c0e30e96114aedefa3f3616ef6e4fef0a4c3dcdd79c72fbf3。BIND456/POSTROUND456once已消费。先查waiter/children/once/results；alive不第二SSH/watcher/normal/CPU/eval，close/eval仅本地至释放。它localtimer至原normal900/忙localwait，同一processrunpy原normal455fullsave安全退出/fulltransfer/newCPUoffset56634/13694/36159，再独立45680firstepisodes400controls8sseed9137同270newDR/actual400Hzmanifold/记录实际pose。新eval包白名单静态source+两data，不复制旧replay/reports/frames，index排除自身。result={str(N/'reports/POSTROUND455_RL_REPLAY_EVAL_DECISION.json').replace(chr(92),'/')}，evalroot={E.as_posix()}，图RECORDED456_NATIVE_FRAMES/ACTUAL456_RL_BODY_POSE_SEQUENCE.png。结果出后当前模型必须view_image看真实pose/核manifold并沿457详查对比；若仍失败按证据定向修复，不原样再训一小时、不接连传统控制实验。原false/once不覆盖/重放。

任何新finiteSSH前freshLOCAL广exactCIM含MOD4_H1/RMPOLAR/watch/run_once_after_resume/E1collect/prepare_archive/single_gpu/collect_nine/collect_generic/collect_actual/PAIR/stage_new/dispatch/retention及新collector并serialFREE；parentfreshCNone/private/shared准入。活controller只本地，不抢锁/清active/kill/另GPU绕共享锁/unknownPIDGPUscan。凭据只原memory不输出Git，finallySSHclosedSESSIONrestoredFREE；历史余额非实时。成功仍首次飞行整轮rearfootprint越沿/双轮actual400Hz台顶manifold/无groundedge返回/vxyvz<=.03/rollpitch10deg/yaw.2rad连续.5s。400Nengineeringk2000/50policy100feedback400physics.0025TGS32-4/fullD0whitev3D1-D7/.01单envclosure/.01mimic/原PD_DCclip_queue_solver/historicalH1资产保持，不暗换newMOD4v1或冒称适配毕业。84x48暂定camera非D435i实机FPS标定。禁Luna/OpenRouter，只当前模型原生视觉。345unused不启动。

全部source/report/rawfalse/once/445closeCPU790/446实际eval+原replay错/451正确取回/452/453staticfalse/454CPU/455实际launchFIRST/456timer/457详查视频曲线/458handoff/automation按根repoAGENTS及Git政策归档新phase mod4-final445-eval446-route-return-ppo455，查RECORD459实际once/tagobjects。已record不重record/retag，后续ordinarysupplement，push失败续existingobjects。旧448objectd4a60f4a47b341f46693802d3e7e13021b753612/peel49319b0e662beaf48afb25094ba780ebfb319be7、449mainf30410178844fbd6d122922f218831b1ac095821和全部历史tags/peels/lqr5848b45a99b8c32af02eb61b507c3f95ab39e4ad保护。PT/NPZ/USD/media仅真实pathbytes已有SHA，不为Git读模型/跑physics；postGit验证只工具输出不追HEAD报告循环。'''
request=dict(id=cfg['id'],mode='update',kind=cfg['kind'],name=cfg['name'],prompt=prompt,status=cfg['status'],rrule=cfg['rrule'],destination='thread',targetThreadId=cfg['target_thread_id'])
put(R/'AUTOMATION458_VIDEO_CURVES_LIVE455_SOLE456_REQUEST.json',request)
print(json.dumps(dict(passed=True,workorder=str(workpath),request=str(R/'AUTOMATION458_VIDEO_CURVES_LIVE455_SOLE456_REQUEST.json'),sole456PID=local['ProcessId'],phase=work['archive']['phase']),ensure_ascii=False),flush=True)
