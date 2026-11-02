"""Actual435: final416closed/evalfailed, boundedPPO433FIRSTandsole434; localonly."""
from pathlib import Path
from datetime import datetime,timedelta,timezone
import hashlib,json,subprocess,time
P=Path(__file__).resolve().parent;T=P.parent;R=P/'reports'
OLD=T/'RL_ACTUAL_RESIDUAL_PPO_PRODUCTION_V416_20261102'
N=T/'RL_BOUNDED_ACTUAL_PPO_PRODUCTION_V433_20261102';NR=N/'reports'
Q=T/'RL433_SINGLE_PROCESS_POSTROUND_V434_20261102';E=T/'RL433_FINAL_INDEPENDENT_EVAL_V434_20261102'
read=lambda p:json.loads(p.read_bytes())
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def put(p,v):
 with p.open('x',encoding='utf8')as f:json.dump(v,f,indent=2,ensure_ascii=False,allow_nan=False)
snapshot=read(NR/'ROOT433_STATUS_FIRST_UPDATED.json')
f={Path(x['path']).name:json.loads(x['UTF8'])for x in snapshot['full_selected_UTF8']}
go=f['GO_PRODUCTION.json'];first=f['FIRST_ACTUAL_TEACHER_DEPTH_STUDENT433_UPDATE.json']
assert first['passed']and first['actual_new_PPO_updates']==1
trust=first['student']['actor_trust_step'];assert trust['actual_KL']<=.01 and trust['actual_max_action_delta']<=.05
waiter=read(NR/'POSTROUND434_WAITER_LAUNCH.json')
assert read(NR/'POSTROUND434_ONCE_CONSUMED.json')['PID']==waiter['PID']
pattern='MOD4_H1|RMPOLAR|watch_|collect_generic|run_once_after_resume|prepare_archive|single_gpu|singleGPU|collect_nine|collect_e1|E1collect|E1_actual|POSTTRAIN_EIGHT|PAIR[0-9]|postround'
query="Get-CimInstance Win32_Process -Filter \"Name='python.exe' OR Name='pythonw.exe' OR Name='ssh.exe'\" | Where-Object { $_.CommandLine -match '"+pattern+"' } | Select-Object ProcessId,ParentProcessId,CreationDate,ExecutablePath,CommandLine | ConvertTo-Json -Depth 4 -Compress"
native=subprocess.run(['pwsh.exe','-NoProfile','-Command',query],capture_output=True,text=True,encoding='utf8',check=True)
rows=json.loads(native.stdout)if native.stdout.strip()else[];rows=rows if isinstance(rows,list)else[rows]
own=[x for x in rows if x['ProcessId']==waiter['PID']]
assert len(own)==1 and 'postround434_close_actual433_eval_once.py'in own[0]['CommandLine']
assert own[0]['ExecutablePath'].replace(chr(92),'/').lower()=='c:/users/lulu/appdata/local/programs/python/python314/python.exe'
assert (NR/'POSTROUND434_STDERR.log').stat().st_size==0
put(R/'ACTUAL435_SOLE434_LOCAL_TIMER_EXACT_CIM.json',dict(epoch=time.time(),rows=rows,sole434=own[0],network=0,modelreads=0,physics=0))
complete=read(OLD/'reports/ROOT416_COMPLETE_FINALS_OR_PARTIALS_ORIGINAL_COST_RETURNED_ACTUAL.json')
cpu=read(OLD/'reports/ROOT416_NEW_FINAL_WHOLE_CPU_RETURNED_ACTUAL.json')
role=complete['roles']['jump_72'];final=role['final'];formal=role['formal']
tz=timezone(timedelta(hours=8));iso=lambda x:datetime.fromtimestamp(x,tz).isoformat()
times={key:iso(go[key])for key in('learning_started_epoch','save_deadline','nominal_end_epoch')};times['normal_earliest']=iso(go['nominal_end_epoch']-900)
task=read(N/'TASK433_FROZEN.json');static=read(R/'STATIC433_WORKER_ROOT_CONTROL_CONTRACT_IDENTICAL.json')
old431=T/'RL_BOUNDED_ACTUAL_PPO_PRODUCTION_V431_20261102'
refusal=read(old431/'reports/ROOT431_STATUS_FIRST_UPDATED.json');rf={Path(x['path']).name:json.loads(x['UTF8'])for x in refusal['full_selected_UTF8']}
value=dict(epoch=time.time(),kind='CURRENT_ACTUAL435_FINAL416_EVAL423_0OF80_BOUNDED_RL433_LIVE_SOLE434',
 latest_human='我需要的是rl上台阶',objective='RL actuallyup270mmwithstablerecovery;traditionalMPCnotdelivery',
 supersedes='CURRENT421416live/417timer is historical;416closed and417localindexfailed,actual423done,433nowlive',
 final416=dict(closed=True,normal416_consumed=True,fullCPU416_consumed=True,
  modelSHA=cpu['SHA'],bytes=cpu['bytes'],CPU=cpu,controls=final['controls'],ownpairs=final['new_environment_transitions'],
  PPO=final['actual_new_PPO_updates'],Pi=final['actual_new_Pi_updates'],critic=final['actual_new_critic_updates'],
  newWM=final['actual_new_WM_updates'],totalWM=final['total_WM_updates'],actorAdam=56304,criticAdam=13364,teacherAdam=42940,
  savedorigin_STD_EMA_norm_RNG_fullthreeAdam=True,formal=formal,node_exit=role['original_node_exit'],
  originalfee=complete['owner_closed']['raw_fee_sum_once'],closingbalance_snapshot=complete['owner_closed']['closing_balance_snapshot'],balance_not_current=True,
  owner_original_exited=complete['owner_closed']['original_owner_out_or_original_nonexecuting_zombie'],canonical_None_atclose=True,allownwaited_locksfree=True,
  no_PTread_for_archive_or_repeatvalidation=True),
 refusal417=dict(local_only=True,network_SDK_model_physics=0,
  cause='Indexincludesitselfatopenxempty0bytesSHAe3b0;afterwritten33080bytesSHAdiff',
  originalindex=str(T/'RL416_FINAL_INDEPENDENT_EVAL_V417_20261102/INDEX417_SOURCE_TASK_CALLERS_FROZEN.json'),
  indexSHA='0f18c99bbfd73ce8567e388f1c301c4b0534e7025ff85797c339dae9e5a69afd',
  originalpostrounderror=list(str(p)for p in(OLD/'reports').glob('POSTROUND417_ORIGINAL_ERROR_*.json')),do_not_rerun417_normal_or_CPU=True),
 actual423=read(R/'ANALYSIS424_FINALPPO416_ACTUAL423_FACTS_AND_MANIFOLD.json'),
 native423_review=read(R/'DIAG425_ACTUAL_RL416_EARLY_MOTOR_RESIDUAL_PHASE_AND_NATIVE_REVIEW.json')['native_review'],
 diagnostic425=str(R/'DIAG425_ACTUAL_RL416_EARLY_MOTOR_RESIDUAL_PHASE_AND_NATIVE_REVIEW.json'),
 targeted_decision='No unchanged416continuation:4230strict/all80orientation/.812smean. SameactualPPO/reward with actualpostAdamKL/residualdelta bounded, notonlyprestepPPOclip. Notclaimedsolecausality.',
 CPU428=read(T/'RL_ACTUAL_PPO_TRUST_STEP_REPAIR_V428_20261102/reports/CPU428_ACTUAL_SAVED_ROLLOUT_TRUST_STEP_ADMISSION.json'),
 preserved_newfailures=dict(CPU426='SavedCUDA16byteRNGcannotloadCPUgenerator; failedbeforecandidateupdate',
  CPU427='FixturewronglyexpectedfrozenSTDAdam56305; originalSTD42940retained,algorithmunchanged428fixturepasses',
  unused429='PostroundNrelativepathwrong,allfreezeunusedpreserved',
  actual431=dict(preSDK=True,modelreads=0,physics=0,controls=0,optimizersteps=0,
   cause='Worker source/teacher_task431 remainedoldfinal389SHAwhile root/controlcorrect',
   rawstatus=str(old431/'reports/ROOT431_STATUS_FIRST_UPDATED.json'),GO=rf['GO_PRODUCTION.json'],
   node_exit=rf['NODE_EXIT_ACTUAL.json'],owner_exit=rf['OWNER_EXIT_ACTUAL.json'],oldonce_no_replay=True)),
 actual433=dict(root=str(N),run=task['run_id'],task=str(N/'TASK433_FROZEN.json'),indexSHA=static['indexSHA'],workerSHA=task['worker_SHA'],
  learnerSHA=static['CPU428learner_exact']and H(N/'source/actual_transition_learner427.py'),
  source_modelSHA=task['model_SHA'],source_offsets=[56304,13364,25556],GPU=task['GPU_UUID'],namespace=task['job_root'],ownerroot=task['owner_root'],
  owner=read(NR/'ROOT433_ORIGINAL_OWNER_LAUNCH_ACTUAL.json')['owner'],node=read(NR/'ROOT433_ORIGINAL_NODE_LAUNCH_ACTUAL.json')['node'],
  worker=f['NODE_CURRENT.json']['row']['worker'],GO=go,times_Asia_Shanghai=times,
  algorithm='SameactualonpolicyresidualPPO32controls/2560samplesoneepochclip.2gamma.99GAE.95std.15; postAdammeanKL<=.01andmaxnormalizedresidualdelta<=.05; restoreallrejectedcandidateweightsAdam/oneacceptedstep',
  unchanged_actor103critic106_goal59_fixed347feedforward_radius1_origin=True,fullstate_source416_no_resetrollback=True,
  policy_not_depthonly=True,no_onlineMPC_or_torquecloning=True,WM_H32_no_actorWMgradient=True,
  fullsameCUDAresidualRNG_restored=True,physicalDRqueue_replay_fresh=True,
  FIRST=first,subsequent_snapshot=f['LATEST_PROGRESS.json'],native24=f['NATIVE24_TEACHER433_ACTUAL.json'],
  launch_FIRST_consumed=True,FIRST_not_skill_eval_or_final=True,trainingtermination_events_not80eval=True,
  allSSHclosed=read(NR/'ROOT433_STATUS_FIRST_UPDATED_SSH_FREE.json')),
 postround434=dict(root=str(Q),indexSHA=static['postindexSHA'],bind_once_consumed=True,timer_once_consumed=True,
  launch=waiter,exact_local_process=own[0],script=str(Q/'postround434_close_actual433_eval_once.py'),
  evalroot=str(E),result=str(NR/'POSTROUND433_RL_REPLAY_EVAL_DECISION.json'),image=str(E/'RECORDED434_NATIVE_FRAMES/ACTUAL434_RL_BODY_POSE_SEQUENCE.png'),
  normal_earliest=times['normal_earliest'],
  scope='Singleprocessrunpy originalnormal433fullsave/safeclose/fulltransfer/newCPUoffsets56304/13364/25556; actual43480firstepisodes400controls8sseed9137same270newDRandmanifold/render;evalindexselfexcluded',
  active_means_no_secondSSH_normal_CPU_eval_watcher=True,
  onresult='Currentmodelmustview_image nativeactualpose/manifold and proactivelytargetedrepairorreasonableRLcontinuation'),
 historical389='Closed618finiteCPU;404actual0/80and407matchedfullquarter0strict,allnativeviewed;notpendingeval',
 unused345_no_start=True,acceptance='Firstflightwholewheelrearfootprintclear/doublewheelactual400Hztopmanifold/nogroundedge_return/vxyvz.03m_s/rollpitch10deg/yaw.2/continuous.5s',
 physical='400Nengineeringk2000/50policy100feedback400physics/.0025TGS32-4/fullD0whitev3D1-D7/10mmperenvclosure/.01mimic/originalPD_DCclip_queue_solver/historicalH1exactproducerasset',
 budget='Originalsinglecanonical3900save3600exit300strictreserve;nograntcopyrefundclearactiveorsecondwriter',
 sensors='84x48provisionalmountnotD435ihardwarecalibrationFPS; nofutureactualdepthorGTmapinimagination',
 resource='EverynewfiniteSSHfreshLOCALbroadexactknownCIM/serialFREE,parentCNoneprivate/sharedadmission;alivecontrollerlocalonly;finallySSHclosedSESSIONrestoredFREE;no unknownPIDGPUscan kill',
 next='Readlocal434timer/once/resultfirst;whileliveonlylocal. No rerun433launchFIRSTbindorold416normalCPU417423/426427428431. OnfinalreviewactualposeandmanifoldthenactonRLresult.',
 git=dict(prior420object='111385802593206df921feeadd119824ff6949a1',prior420peel='412d5d5dcc12d725502849c0dc109367c61452bc',supplement422='31132dbf2207e96e64c5eddbf16f27dfecbb5a17',
  phase='mod4-final416-eval423-bounded-ppo433',record436='Checkactualonce/tagobjects;oneannotatednewrepairphase then ordinarysupplements;pushretryexistingobjects',
  lqr='5848b45a99b8c32af02eb61b507c3f95ab39e4ad',no_archive_modelreads_or_physics=True))
dest=R/'CURRENT_ACTUAL435_FINAL416_EVAL423_FAIL_LIVE_BOUNDED433_SOLE434_WORK_ORDER_V1.json';put(dest,value)
print(json.dumps(dict(passed=True,path=str(dest),GO=times,FIRSTtrust=trust,timerPID=waiter['PID'],localonly=True)))
