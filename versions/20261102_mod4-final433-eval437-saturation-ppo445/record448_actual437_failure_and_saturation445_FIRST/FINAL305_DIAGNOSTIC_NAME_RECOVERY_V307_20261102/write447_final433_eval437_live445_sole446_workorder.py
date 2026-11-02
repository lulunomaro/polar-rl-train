"""Actual437 failure/native review to live saturation-aware445 and sole446 close/eval handoff."""
from pathlib import Path
import datetime
import hashlib
import json
import subprocess
import time
import tomllib

P=Path(__file__).resolve().parent;T=P.parent;R=P/'reports'
N=T/'RL_SATURATION_ACTUAL_PPO_PRODUCTION_V445_20261102'
Q=T/'RL445_SINGLE_PROCESS_POSTROUND_V446_20261102'
E=T/'RL445_FINAL_INDEPENDENT_EVAL_V446_20261102'
read=lambda path:json.loads(path.read_bytes())
H=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
def put(path,value):
    with path.open('x',encoding='utf8')as stream:json.dump(value,stream,indent=2,ensure_ascii=False,allow_nan=False)

facts=read(R/'ANALYSIS440_ACTUAL_FINAL433_EVAL437_FACTS_AND_MANIFOLD.json')
diag=read(R/'DIAG441_ACTUAL437_SATURATED_RESIDUAL_NATIVE_AND_EXPLORATION.json')
cpu=read(T/'RL_SATURATION_EXPLORATION_REPAIR_V442_20261102/reports/CPU442_SATURATION_EXPLORATION_FULL_RESTORE_ADMISSION.json')
snap=read(N/'reports/ROOT445_STATUS_FIRST_UPDATED.json')
files={Path(row['path']).name:json.loads(row['UTF8'])for row in snap['full_selected_UTF8']}
task=read(N/'TASK445_FROZEN.json');go=files['GO_PRODUCTION.json'];first=files['FIRST_ACTUAL_TEACHER_DEPTH_STUDENT445_UPDATE.json']
assert first['passed']and first['actual_new_PPO_updates']==1 and first['student']['exploration_gain']==.6
assert facts['strict']==facts['whole_footprint_clear']==0 and diag['native_review']['current_model_native_viewed']
query="Get-CimInstance Win32_Process -Filter \"Name='python.exe' OR Name='ssh.exe'\" | Where-Object { $_.CommandLine -match 'MOD4_H1|RMPOLAR|watch_|run_once_after_resume|E1collect|prepare_archive|single_gpu|collect_nine|collect_generic|collect_actual|PAIR|postround' } | Select-Object ProcessId,ParentProcessId,CreationDate,ExecutablePath,CommandLine | ConvertTo-Json -Depth 5 -Compress"
result=subprocess.run(['pwsh.exe','-NoProfile','-Command',query],capture_output=True,text=True,encoding='utf8',check=True)
rows=json.loads(result.stdout)if result.stdout.strip()else[];rows=rows if isinstance(rows,list)else[rows]
launch=read(N/'reports/POSTROUND446_WAITER_LAUNCH.json')
exact=[row for row in rows if row['ProcessId']==launch['PID']]
assert len(exact)==1 and 'postround446_close_actual445_eval_once.py'in exact[0]['CommandLine']
put(R/'ACTUAL447_SOLE446_TIMER_FRESH_EXACT_CIM.json',dict(epoch=time.time(),rows=rows,sole446=exact[0],newSSH=False))
zone=datetime.timezone(datetime.timedelta(hours=8))
times={key:datetime.datetime.fromtimestamp(go[key],zone).isoformat()for key in('learning_started_epoch','save_deadline','nominal_end_epoch')}
times['normal_earliest']=datetime.datetime.fromtimestamp(go['nominal_end_epoch']-900,zone).isoformat()
other=Path('F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/reports/ACTUAL_SUPERMIMIC_EIGHT_V1_20261102_184527/CLOSED_RESULT.json')
otherclosed=read(other)
put(R/'ACTUAL447_PRIOR_OTHER_OWNER_RELEASE_BEFORE437.json',dict(epoch=time.time(),path=str(other),bytes=other.stat().st_size,SHA=H(other),
    original_root=otherclosed['root'],parent_exit=otherclosed['parent_exit'],metadata_epoch=otherclosed['epoch'],
    no_current_resource_balance_claim=True,localmetadataread_only=True))
work_path=R/'CURRENT_ACTUAL447_FINAL433_EVAL437_FAIL_LIVE_SATURATION445_SOLE446_WORK_ORDER_V1.json'
work=dict(epoch=time.time(),kind='FINAL433_ACTUAL437_EVAL_FAIL_LIVE_SATURATION_AWARE_RL445_SOLE446',
    latest_human='我需要的是rl上台阶',objective='RL actuallyup270mm withstablerecovery; traditionalMPC not delivery',
    supersedes='438 unused437/resourcewait is historical;437actualcompleted/nativeviewed;445nowlive withsole446timer',
    final433=dict(closed=True,CPU795finite=True,SHA='db6944ceca539106bb392a881185f1e85917efa5a9325bbeec72863f8240e04f',bytes=34402073,
        Pi=161,critic=161,totalWM=30731,actorAdam=56465,criticAdam=13525,allthreeAdam_STD_teacherEMA_normRNG_origin_complete=True,
        normal_CPU437_consumed_no_replay=True),
    actual437=facts,native437=diag['native_review'],diagnostic441=diag,
    repair_decision='No unchanged433 continuation: actual437zerowholeclear/no topmanifold, longcasewheelresidualstanhbound. Change trainingexplorationdistribution, retain deterministicpolicy/reward/physicalandfullAdam.',
    CPU442=cpu,unused443=dict(preserved=True,START=False,modelreads=0,SDK=0,physics=0,network=0,
        reason='prepare443 relative postround production root remained BOUNDED instead of SATURATION; rejected beforeINDEXfreeze; independent445 fixedbare rootnames'),
    actual445=dict(root=str(N),run=task['run_id'],task=str(N/'TASK445_FROZEN.json'),indexSHA=H(N/'INDEX445_SOURCE_TASK_CALLERS_FROZEN.json'),
        workerSHA=task['worker_SHA'],learnerSHA=cpu['learnerSHA'],CPU442learnerbyteexact=True,
        sourceSHA=task['source_SHA'],source_offsets=[56465,13525,30731],GPU=task['GPU_UUID'],
        owner=read(N/'reports/ROOT445_ORIGINAL_OWNER_LAUNCH_ACTUAL.json')['owner'],
        node=read(N/'reports/ROOT445_ORIGINAL_NODE_LAUNCH_ACTUAL.json')['node'],
        original_worker_before_wait=files['WORKER_ORIGINAL_IDENTITY_BEFORE_WAIT.json'],
        worker_exe_note='OwnimmediatePopenreceiptcapturedrun-python.sh bashbeforeexec; do not invent later exe or query unknown PIDs',
        GO=go,times_Asia_Shanghai=times,FIRST=first,subsequent_snapshot=files.get('LATEST_PROGRESS.json'),
        fullsource433_noAdamnetworkreset=True,actor103='35proprio+9currentdepth+59plannedreference',critic106=True,
        residual='fixed347processed50Hztable+1*tanh(actor-origin);saved389originfrozen',onlineMPC=False,autonomous_depthonly=False,
        actualPPO='32controls2560samples/oneepochclip.2gamma.99GAE.95actualrewarddone/WMH32independentnoactorWMgrad',
        exploration='perchannelGaussianlatentstd=min(2,sqrt(.15^2+(.6*mean)^2));fullGaussianlogprob/KL;deterministicactionunchanged',
        frozen_learnedSTD_teacher17Adam42940_preserved=True,
        postAdam='meanKL<=.01/maxnormalizedresidualdelta<=.05;allrejectedweightsAdamrestored;oneacceptedcommit',
        new_physicalDRqueue_replay=True,savedCUDAresidualRNG_restored=True,reward_physics_acceptance_unchanged=True,
        launch_FIRST_consumed=True,no_restart_hotpatch_repeatstartupchecks=True,FIRST_not_skill_or_final=True,
        allSSHclosed=read(N/'reports/ROOT445_STATUS_FIRST_UPDATED_SSH_FREE.json')),
    postround446=dict(root=str(Q),indexSHA=H(Q/'INDEX446_POSTROUND_FOR445_FROZEN.json'),
        bind_and_timer_consumed=True,launch=launch,exactlocal=exact[0],
        script=str(Q/'postround446_close_actual445_eval_once.py'),evalroot=str(E),
        result=str(N/'reports/POSTROUND445_RL_REPLAY_EVAL_DECISION.json'),image=str(E/'RECORDED446_NATIVE_FRAMES/ACTUAL446_RL_BODY_POSE_SEQUENCE.png'),
        normal_earliest=times['normal_earliest'],
        scope='Localtimer tooriginalnormal900 then sameprocessnormal445fullsave/close/fulltransfer/newCPUoffsets56465/13525/30731;newfinal44680firstepisodes400controlsseed9137/newDR/fixed270/manifold/render;waitlocalagainbeforeeval',
        alive_means_no_secondSSH_or_normal_CPU_eval_watcher=True,
        onresult='Currentmodelnativeview_image actualposes/manifold then proactiveRLrepairorjustifiedcontinuation'),
    physics='400Nengineeringk2000/50policy100feedback400physics/.0025TGS32-4/fullD0whitev3D1-D7/10mmperenvclosure/.01mimic/PD_DCclip_queue_solver/historicalH1exactproducer',
    budget='Originalsinglecanonical3900save3600exit300strictreserve;nograntcopyrefundclearactiveorsecondwriter',
    acceptance='Firstflightwholewheelrearfootprintclear/doublewheelactual400Hztopmanifold/nogroundedge_return/vxyvz<=.03m_s/rollpitch<=10deg/yaw<=.2rad/continuous>=.5s',
    sensors='84x48provisionalmountnotD435ihardwarecalibrationFPS;nofutureactualdepthGTmapinimagination',
    resource='EveryfiniteSSHfreshLOCALbroadexactknownCIM/serialFREE,parentfreshCNoneprivate/shared;alivetimerlocalonly;finallySSHclosedSESSIONrestoredFREE;no unknownPIDGPUscan kill',
    historical='416actual4230of80mean.812nativeviewed;389actual4044070strictnativeviewed;345unusedno_start;434localbusy0physicspreserved',
    reader_errors='Readonlymissingoldlaunch433filename/diag425filenamecorrected; no model/SDK/network/physicalsideeffects;443actualstaticfailurepreserved',
    next='Read446timer/once/resultsfirst;liveonlylocal. No rerun445launchFIRSTbind or oldonce. Onfinalpose/manifoldreviewactonRLresult.',
    git=dict(phase='mod4-final433-eval437-saturation-ppo445',record448='Checkactualonce/tagobjects;recordonce newphase thenordinarysupplements',
        prior439='013ee164aa11762e075152befcb7e1ecb2314f63',prior436object='1b309d3b6fa4a8fa41496956df61f116bae2b6ab',prior436peel='1044a69fef42ace2dee82f2dcb229538dc029a9b',
        protect_alltags=True,lqr='5848b45a99b8c32af02eb61b507c3f95ab39e4ad',noarchive_modelreads_orphysics=True))
put(work_path,work)
cfg=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text('utf8'))
prompt=f'''每小时继续本聊天MOD4跳270mm。人类明确“我需要的是rl上台阶”，交付为RL实际跳台并稳定，传统MPC不是交付。已授权新跟踪启动/继续看收尾然后修复。每轮完整保存安全退出后立即独立RL评测与真实姿态回放，当前模型必须view_image原生审图/核manifold，再按真实结果主动定向修复或合理续训，不等催促、不原样续退化任务。ACTIVE/currentchat，不新Goal/chat/重复automation；无变化不可行动静默，只通知实质进展、失败、完成、资源预算网络问题和必需用户行动。

首先读 {work_path.as_posix()}。实际冻结source/INDEX/ownreceipt/确切进程/结果优先。旧438unused437/resourcewait过时。433完整关闭/CPU795finite，437已实际独立评测并原生审，当前445真实训练和唯一446timer，绝不再launch445/FIRST/bind，健康不restart/hotpatch/重跑startup或模型验证。

final43334402073B SHAdb6944ceca539106bb392a881185f1e85917efa5a9325bbeec72863f8240e04f/Pi161critic161WM30731、actorAdam56465critic13525。437同final/80firstepisodes400controls8s/seed9137新DR同fixededge.8/270实际完成：0/80strict、0wholefootprintclear、0leadingcross、80everairborne、44orientation、36full8s、mean4.30925s/median1.57s、longesttopmanifold0。安全allownwaited/private共享释放/SSHclosedSESSIONrestoredFREE。不是待评测。当前模型已view_image原生审真实图：env0/40/41约1.14-1.54s台前/台边倾倒；env1跑满8s但斜卡在台前下方，不是台顶成功。440全80/manifold和441实际motor/target/root/残差已保存。env1两轮残差各354/400拍abs>.95，末rootx.563/z.295、参考x1.38/z.536。只是selected证据，不当all80视觉或唯一因果。

定向修复是饱和感知探索：原latentGaussianstd.15经tanh在mean3时实际residualstd约.00158，饱和后动作探索几乎消失；不调reward/horizon/PD/solver。442新CPU一次必要final433fullrestore，actorcritic三Adam/EMA/origin/teacherSTD完整56465/13525/30731，CUDA16B RNG保留opaque、CPUfixture显式generator。22保存坐标行重复为32controls并新合成latent只作CPU算法fixture，非实际onpolicy数据。新std=min(2,sqrt(.15^2+(.6*mean)^2)) perchannel，概率用实际state-dependentGaussian/fullGaussianKL。TorchNormallogprob误差1.9e-6/KL误差9.3e-9，actorgrad2.7074critic3.4837，acceptedhalfLR/KL.00220768/maxdelta.0368878；候选weightsAdam全部恢复，0生产优化/SDK/physics。deterministic evalactor输出/动作差0，terminalGAE无bootstrap通过。CPU不是物理成功，不重复读PT验模。

443/444准备在INDEXfreeze前发现postround相对root仍BOUNDED而实际SATURATION，0START/model/SDK/physics/network。原source/原staticfalse保留unused，不执行不改。独立445/446修bare rootnames后四actualcontract导入与Task匹配通过、CPU442learner逐字节复用，冻结INDEX445SHA={H(N/'INDEX445_SOURCE_TASK_CALLERS_FROZEN.json')}、workerSHA={task['worker_SHA']}、learnerSHA={cpu['learnerSHA']}。

实际445root={N.as_posix()}，run={task['run_id']}。原ownerPID1482264/create1793622408.75、node1482274/create1793622409.15、ownworker1482287/create1793622415.32；完整exe/argv/root/controlcwd见447/实际launch/status。worker即时Popenidentity是run-python.sh bash，勿捏造后exec身份或unknownPIDscan。GPU={task['GPU_UUID']}。GO{times['learning_started_epoch']}，SAVE{times['save_deadline']}，NOMINAL{times['nominal_end_epoch']}，normal最早{times['normal_earliest']}。原3900save3600exit300唯一canonicalstrictreserve保持。

445完整恢复final433所有网络/三Adam/STD/teacher17Adam42940/EMA/normRNG/saved389origin，不resetAdam/回退权重。固定347processed50Hz电机前馈+1*tanh(actor-origin)，actor103=35proprio9currentdepth59plannedreference/critic106，非自主depth-only，无onlineMPC/接管/力矩cloning。actualPPO32controls2560samplesoneepochclip.2/gamma.99GAE.95、实际同exp(-weightedtrackingcost/5)与done直接入actor；WMH32独立无actorWMgradient，futureactualdepthGTmap不入imagination。唯一变化训练latent探索std perchannel=floor.15/gain.6/cap2，原learnedSTD42940仍冻结。postAdam完整GaussianmeanKL<=.01/maxnormalized残差delta<=.05，拒绝proposalweightsAdam全部还原、只commit一次acceptedstep。deterministic评测动作公式没变，physicalDRqueue/replayfresh、CUDAresidualsamplingRNG真实恢复。

实际445FIRST64controls5120ownpairs512physics128feedback，Pi=PPO=critic1/newWM33total30764，actorgrad3.5483568critic9.6709728有限非零，native24通过。实际latentstdmean.60657/max2、acceptedLR5e-5/half/2proposals、postAdamKL.00597859/maxdelta.03330595、一次commit，actualdoneGAEtrue/terminal0/actorWMgradfalse。首完整32808633B SHA71c7f022301be49a8a2198bd9adf0bd8660af418b3016b24977897558971f006/actorAdam56466critic13526WM30764。后snapshot92controls/PPO1/WM30792/40orientation是训练重复episode事件，不是80独立评测或技能通过。

唯一localpostround446已bind并启动PID46516/create2026-11-02T20:28:20.059169+08，完整exactCIM见447。root={Q.as_posix()}，scriptpostround446_close_actual445_eval_once.py，INDEX446SHA={H(Q/'INDEX446_POSTROUND_FOR445_FROZEN.json')}。BIND446/POSTROUND446_ONCE已消费。它localtimer到原normal900，忙仅localwait，同一processrunpy normal445fullsave/安全退出/fullformaltransfer/newCPUoffsets56465/13525/30731，再独立446同final一次actor+origin读取、80firstepisodes400controls8s/seed9137同fixed270新DR/actual400Hzmanifold/有限记录bodypose原生渲染。evalindex排除自身，normalclose后eval前再freshLOCALwait避免434竞态。原窗口不改。

先读446waiter/children/once/results；活着不第二SSH/watcher/normal/CPU/eval，close/eval期间只本地直至controller释放。结果={str(N/'reports/POSTROUND445_RL_REPLAY_EVAL_DECISION.json').replace(chr(92),'/')}，evalroot={E.as_posix()}，图RECORDED446_NATIVE_FRAMES/ACTUAL446_RL_BODY_POSE_SEQUENCE.png。结果出来当前模型必须view_image原生审图/实际manifold，再按实际RL越台/稳定/寿命/误差主动修复或合理续训，不只报结束；失败原once/false保留、独立版本修不重放。

其它SUPERMIMIC8已发布原OWNER_EXIT/allownwaited/costsettled/leasesreleased且collectorclosed，本地freshCIMFREE后才run437/445。任何新finiteSSH仍须freshLOCAL广exactknownCIM含MOD4_H1/RMPOLAR/watch/run_once_after_resume/E1collect/prepare_archive/single_gpu/collect_nine/collect_generic/collect_actual/PAIR及新collector并serialFREE，parentfreshCNone/private共享准入。活controller仅本地，不抢锁/clearactive/kill/另GPU绕共享锁/unknownPID或GPUscan。每次finallySSHclosed/SESSIONrestored/FREE，凭据仅原memory不输出入Git。历史余额不当实时。

成功仍首次飞行整轮rearfootprint越沿、双轮实际400Hz台顶manifold、无回地面退沿，vxy/vz<=.03m_s、rollpitch<=10deg/yaw<=.2rad连续>=.5s。loss/COM/腾空/leadingedge/full8s不毕业。物理400Nengineeringk2000/50policy100feedback400physics2.5msTGS32-4/fullD0whitev3D1-D7/10mm单envclosure/.01mimic/原PD_DCclip_queue_solver/historicalH1exactproducer资产保持，不暗换newMOD4v1/冒称专家适配毕业；84x48camera暂定非D435i实机标定FPS。唯一原canonical3900save3600exit300strictreserve不grant/copy/refund/clearactive/第二writer。禁Luna/OpenRouter，仅当前模型原生视觉。历史416/423与389/404407已评已审非待评；345仍unused不启动，MPC不是RL交付。

所有source/report/rawfalse/once/437actualeval+native/440441/442CPU/443staticfalse/445launchFIRST/446timer/447handoff/automation按根repoAGENTS和polar-rl-train/docs/ALL_TRIALS_AND_REPORTS_GIT_POLICY.md进入Git。新phase mod4-final433-eval437-saturation-ppo445，查RECORD448实际once/trialobjects；已record不重record/retag，后续ordinarysupplement，push失败续existingobjects。旧439commit013ee164aa11762e075152befcb7e1ecb2314f63、436object1b309d3b6fa4a8fa41496956df61f116bae2b6ab/peel1044a69fef42ace2dee82f2dcb229538dc029a9b及所有旧tags/peels/lqr5848b45a99b8c32af02eb61b507c3f95ab39e4ad保护。PT/NPZ/USD/media仅actualpathbytes已有SHA，不为归档读模型/跑physics；postGit验证只工具输出不追HEAD报告循环。'''
request=dict(id=cfg['id'],mode='update',kind=cfg['kind'],name=cfg['name'],prompt=prompt,rrule=cfg['rrule'],status=cfg['status'],targetThreadId=cfg['target_thread_id'],destination='thread')
if 'notification_policy'in cfg:request['notificationPolicy']=cfg['notification_policy']
put(R/'AUTOMATION447_ACTUAL437_FAIL_LIVE445_SOLE446_REQUEST.json',request)
print(json.dumps(dict(passed=True,workorder=str(work_path),request=str(R/'AUTOMATION447_ACTUAL437_FAIL_LIVE445_SOLE446_REQUEST.json'),sole446PID=launch['PID'],times=times)),flush=True)
