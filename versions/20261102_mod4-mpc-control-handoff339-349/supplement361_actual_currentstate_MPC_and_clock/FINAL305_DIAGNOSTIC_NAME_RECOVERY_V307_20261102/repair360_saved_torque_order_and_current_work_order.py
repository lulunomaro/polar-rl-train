"""Correct saved359 analysis permutation and preserve real355/357 outcomes for continuation."""
from pathlib import Path
import hashlib,json,subprocess,time,tomllib
import numpy as np
P=Path(__file__).resolve().parent;T=P.parent;R=P/'reports';read=lambda p:json.loads(p.read_bytes());H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def put(p,v):
    with p.open('x',encoding='utf8')as f:json.dump(v,f,indent=2,ensure_ascii=False,allow_nan=False)
old=read(R/'ACTUAL359_SOURCE_POSTURE_AND_SAVED_PHYSX_MOTOR_TORQUE.json')
fixed=[]
for phase in(355,357):
    root=T/('MPC_CURRENT_STATE_EVENT_PHYSX_COMPARISON_V355_20261102'if phase==355 else'MPC_ACTUAL20MS_PREDICTION_CLOCK_V357_20261102')
    full=read(root/f'reports/ROOT{phase}_EVALUATION_FULL_RETURNED.json');s=full['result'];assert s['passed']and s['strict_successes']==0
    trace=next(json.loads(v['UTF8'])for v in full['full_UTF8']if v['path'].endswith(f'ACTUAL{phase}_CURRENT_STATE_MPC_CONTROL_TRACE.json'))
    for case in read(root/f'reports/ROOT{phase}_SELECTED_REPLAY_TRANSFERS.json')['cases']:
        env=case['env'];controlrows=[dict(control=r['control'],**v)for r in trace['rows']for v in r['rows']if v['env']==env]
        out=[]
        for c in controlrows:
            ticks=[p for p in trace['physics_selected']if(c['control']-1)*8<p['tick']<=c['control']*8]
            if not ticks:continue
            i=ticks[0]['selected_envs'].index(env)
            applied=np.mean([p['actual_applied_torque6'][i]for p in ticks],axis=0)[[1,0,4,3,2,5]]
            out.append(dict(control=c['control'],phase=c['phase'],requested=c['tau_requested'],actual_applied_tau_mean=applied.tolist(),absolute_difference=np.abs(applied-np.array(c['tau_requested'])).tolist()))
        fixed.append(dict(phase=phase,env=env,first10=out[:10],last=out[-1]if out else None))
put(R/'ACTUAL360_CORRECTED359_TORQUE_PERMUTATION.json',dict(epoch=time.time(),passed=True,original359_report=str(R/'ACTUAL359_SOURCE_POSTURE_AND_SAVED_PHYSX_MOTOR_TORQUE.json'),original359SHA=H(R/'ACTUAL359_SOURCE_POSTURE_AND_SAVED_PHYSX_MOTOR_TORQUE.json'),originalfalse_preserved=True,error='359 diagnostic used [1,0,4,2,3,5] so right hip/crank reversed in the saved torque comparison only. Actual355/357 physicalcontroller inversePD/order was correct and is unchanged.',correct_permutation=[1,0,4,3,2,5],from_order=['left_crank','left_hip','right_crank','right_hip','left_wheel_spin','right_wheel_spin'],to_order=['left_hip','left_crank','left_wheel_spin','right_hip','right_crank','right_wheel_spin'],corrected_selected=fixed,NN=0,SDK=0,network=0,physics=0,optimizer=0,no_actualskill_results_changed=True))
groups355=read(T/'MPC_CURRENT_STATE_EVENT_PHYSX_COMPARISON_V355_20261102/reports/ROOT355_EVALUATION_FULL_RETURNED.json')['result']['comparisons']
groups357=read(T/'MPC_ACTUAL20MS_PREDICTION_CLOCK_V357_20261102/reports/ROOT357_EVALUATION_FULL_RETURNED.json')['result']['comparisons']
for version,name in((355,'MPC_CURRENT_STATE_EVENT_PHYSX_COMPARISON_V355_20261102'),(357,'MPC_ACTUAL20MS_PREDICTION_CLOCK_V357_20261102')):
    assert read(T/name/f'reports/ROOT{version}_ALL_SSH_CLOSED_FREE.json')['all_owned_SSH_closed']
query="Get-CimInstance Win32_Process -Filter \"Name='python.exe' OR Name='ssh.exe'\" | Where-Object { $_.CommandLine -match 'MOD4_H1_SCUT_STEP270|RMPOLAR|watch_|run_once_after_resume|continue_clean_sequential|E1_actual|collect_e1|run_ROOT|prepare_archive|single_gpu|collect_nine|deploy_nine' } | Select-Object ProcessId,CreationDate,ExecutablePath,CommandLine | ConvertTo-Json -Depth 4 -Compress"
q=subprocess.run(['pwsh.exe','-NoProfile','-Command',query],capture_output=True,text=True,encoding='utf8',check=True);assert not q.stderr.strip();rows=json.loads(q.stdout)if q.stdout.strip()else[];rows=rows if isinstance(rows,list)else[rows]
put(R/'LOCAL360_POST357_EXACT_CONTROLLERS.json',dict(epoch=time.time(),rows=rows,scope='localknowncontrollers snapshot only; no remoteprocessscan'))
work=dict(epoch=time.time(),kind='CURRENT_ACTUAL360_CLOSED_LOOP_MPC_TRANSFER_AND_LANDING_REPAIR',
    replaces='CURRENT_ACTUAL350; all historical350facts preserved but actualMPCcomparison now executed',
    human_authorization='newtrackingstart/continueclose_thenrepair; fulltunedMPCmotortrajectorytransfer before moreblindtraining',
    actual355=dict(root=str(T/'MPC_CURRENT_STATE_EVENT_PHYSX_COMPARISON_V355_20261102'),groups=groups355,NN=0,training=0,account=0,source_event_controller_currentstate_feedback=True,target_hz=50,sourceprediction_dt=.01,all_closed=True,viewed=True),
    actual357=dict(root=str(T/'MPC_ACTUAL20MS_PREDICTION_CLOCK_V357_20261102'),groups=groups357,NN=0,training=0,account=0,group_prediction_dt=[.01,.02],group_horizon=[15,8],originalqueue_control_us=20000,physical_dt=.0025,all_closed=True,viewed=True),
    source353=dict(root=str(T/'MPC_CURRENT_STATE_EVENT_BRIDGE_V353_20261102'),CPU_no_step_pass=True,sourcephase_equations7fixtures_exacttau=True,nominalgain_extracted_0physics=True,currentstateprivileged_xyvx_yaw_declared=True,not_actor_or_depthautonomous=True),
    failure354=dict(root=str(T/'MPC_CURRENT_STATE_EVENT_PHYSX_COMPARISON_V354_20261102'),consumed=True,SDKconstructed=True,controls=0,NN=0,error='policyterm.scaleTensor JSONserialization beforecontrol0',allownwaited_locksreleased=True,repaired_independent355=True),
    saved_diagnostics352_356_358_359_360=dict(target_application_selected_error='max~5.4e-6in349,originalmappingapplied',phase='355 all40launched19enteredrecover;357 source.01group13recover andactual.02group20recover',
        correction='first_flight_both_cross is front/leadingwheelcollisionbound passingedge,not wholefootprint or stablejump; allrawflags preserved.37/40 meansfrontedgeprogress,0strict.',
        latest=str(R/'ACTUAL358_SAVED357_PHASE_FULL_FOOTPRINT_DIAGNOSIS.json'),posture=str(R/'ACTUAL359_SOURCE_POSTURE_AND_SAVED_PHYSX_MOTOR_TORQUE.json'),torque_correction=str(R/'ACTUAL360_CORRECTED359_TORQUE_PERMUTATION.json'),
        source_upright_minRzz=.9934473534581317,source_never_needed_relaxed_orientation=True,actualselectedRzz95_first='~.7-1.0s push/flight; sourceMPC staysupright',no_new_model_orphysics_for_analysis=True),
    decision='SourceMPCcurrentstate/event control materially increases leadingedgeprogress; remaining failure is footprint/flightposture/landingrecovery. Timingadaptation alone no stablecase. No blind345training and no identicalcontroller retry. Next independently designed finitecomparison must inspect firstposturedeviation and originalperenvDR/actualnominalplant, record requested/appliedmotortargets andcorrecttorqueorder, alignsourcefeedback/events without silentlyaltering50Hzqueue/PD/physics/asset. Preserve nativeview and strictcontactmanifoldgraduation.',
    next_stage_prepared=False,training345GO=False,training345consumed=False,source324alreadyfullsavedclosed=True,eval339completed0strict=True,
    oldphase=dict(id='mod4-mpc-control-handoff339-349',tag='trial-20261102-mod4-mpc-control-handoff339-349',tagobject='f63c76d9c064a26e6261b544304c7f92a5bbdf76',peel='a6c59be6408153875b36ed851d59d3767f8e5709',record351alreadycomplete=True),
    archive='Current353gainbridge/354false/355actual/357actual/352356358359360diagnostics/automation append ordinarysupplement361 toexistingphase,not re-record/retag. Allsource/rawfalse/reports capture; binaryonlypathbytesexistingSHA; noextraPTread.',
    resource='355357allownclosedSSHfinally/sessionrestored/FREE; priorotherchatNINEV2closedallchildren/private/sharedreleased; anynewfiniteSSHneedsfreshlocalbroadexactCIMplusoriginalCNoneprivate/sharedadmission,not snapshotalone; nosecondwatcher/kill/unknownPIDscan',
    constraints='400Nengineeringk2000/policy50feedback100physics400/2.5msTGS32-4/fullD0whitev3D1-D7/10mmepisodeclosure/.01mimic/originalsinglecanonicalbudget3900save3600exit300strictreserve,no grantcopyrefundclearactiveorsecondwriter;historicalH1assetnotnewMOD4v1; nativevisiononly,noLunaOpenRouter',
    success='frontedgeprogress is insufficient. Wholewheelfootprintfirstflight/topcontact/stable.5s and actualmanifold required. Sourcecriteria .3m/s is notcurrentstrict .03m/s; keep strictcriteria,do notrelax tocallskill.',
    automation='mod4-10ACTIVEhourlysamechat; noGoal/noextraautomation; unchangednonactionablestatequiet')
path=R/'CURRENT_ACTUAL360_CLOSED_LOOP_MPC_LANDING_REPAIR_WORK_ORDER_V1.json';put(path,work)
config=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text('utf8'));put(R/'AUTOMATION360_PRIOR_CONFIG.json',dict(epoch=time.time(),config=config))
prompt='''每小时继续本聊天MOD4跳270mm/MPC控制交接修复。人类授权新跟踪启动、继续看收尾然后修复，最新追问完整调好MPC/电机轨迹为何跳不上；不要盲目只改horizon/reward续训。每轮完整保存安全退出后立即独立评测和实际姿态回放，按真实结果主动修复/合理续训。保持ACTIVE/currentchat，不新Goal/重复automation。无变化不可行动静默，仅通知实质进展、失败、完成、资源/预算/网络问题和必需用户行动。

首先读 '''+str(path).replace('\\','/')+'''。真实冻结source/INDEX/ownreceipt/确切进程优先。旧350尚未执行currentstateMPC状态过时。324完整结束CPU609finite通过，finalSHA841dd4080ae41558645f98f1105652517716772b8b1f177df8cf8af89a0cc050/Pi4379/WM16879/actorAdam52636critic9696。339独立技能评测0/80strictfrontcross56orientation24full8s已完成且原生回放已审；不可称待评测。345H8direct生产包仍unused，START/GO/postround均无，不盲启。

346发现状态reference丢弃MPCtau/control：源100Hz闭环desiredtorque->inversePD->processedtargets->D4/PD/DCclip，原311只复制jointstate-as-target不是忠实MPC。347为提取缺失control做一次localMuJoCo，成功stable3.02s，500controls/10000physics/0NNGPU网络账，本机3.15原3.12非逐点复现。完整processed100Hztrace保留。349实际50Hzopenlooppdgainqueue原封：state-as-target0/40frontcross40orientation0full5s；processedtarget13/40frontcross33orientation7full5s，strict都0。两组DR非paired，不能说唯一原因。

本轮353独立CPU0physics提取source nominal A/B/Q/R/gains，复用成功hybrid起跳/flight/recover实际公式，7fixturesrequestedtau完全一致；它是currentstate诊断控制器，privilegedtranslation/vx/yaw明确，不是learneddepthactor。354实际新SDK启动后在首次control前policyterm.scale为Tensor，JSONserialization失败，0NN/controls/优化账，原false/source/consumed保留，ownchildwaited/private_shared释放/SSHFREE。独立355将实际scale转plainwidthlist且CPUtensorserialization/unscale验证后执行；不重跑354。

实际355已完成、安全关闭并原生审pose。目录MPC_CURRENT_STATE_EVENT_PHYSX_COMPARISON_V355_20261102：同50Hztarget/fullDR/同plannedinitial80，0..39openloopprocessedsource：6/40frontedgeprogress、37orientation、3full5s、mean1.2705；40..79currentstate/sourceeventMPC：37/40frontedgeprogress、28orientation、12full5s、mean2.299；strict两组0。40MPC全部真实起跳触发，19进入recover。sourceMPC原predictiondt.01但实际hold.02已明示；原queue.control_us20000、feedback100/physics400/PD/limiter不变。

独立357按实际hold20ms重离散同continuousA/B，group0..39sourceprediction.01/H15，40..79actualprediction.02/H8（.15s对.16s时域）；都currentstate/eventMPC50Hz，0NN/训练账。CPU0step验证Ad确实改变后实际执行完成。目录MPC_ACTUAL20MS_PREDICTION_CLOCK_V357_20261102：source.01组33/40frontedgeprogress33orientation7full5smean1.8495；actual.02组32/40frontedgeprogress27orientation13full5smean2.471，strict0both。各13/20进入recover。两组DR同分布非exactpaired，不能断言clock单因果或修好。355357fullreturned/recordedposes/nativeframes和allSSHclosedFREE完整。当前模型已view_image原生审两图：仍台沿附近前倾，部分full5s站回地面，不是站台毕业。

352实际349selectedmotortarget应用误差max约5.4e-6单位原rad/rad_s，未发现selected4简单映射/应用错；不泛化全部。356/358/359已读保存数据诊断而0新NN/SDK/physics。要纠正表述：所有rawfirst_flight_both_cross是每轮leadingcollisionbound越过edge，不是整个footprint；13/37/32均只称前缘进展，不称完整越台/成功跳。完整footprint/topcontact/stable.5s/contactmanifold仍需。355env41跑满5s但末rootz.2625/x.530在台前地面，不能当台顶成功。source成功轨迹minRzz.99345，当前selected约.7-1.0s出现Rzz<.95；不是.75rad终止误杀，不放宽原orientation。359仅离线torquecomparison误permute右hip/crank，原raw保留，360用[1,0,4,3,2,5]修正；actual355357控制映射本身未改变。

当前决定：不续345/324，不原样重复355/357。先依据真实push/flight姿态及footprint/landing数据，设计下一独立有限对照，核实际nominalplant与每envfullDR/首偏离时刻/电机requested-vs-appliedtau/target/反馈phase。sourceclosedloop已大幅增加前缘进展，但落地未稳定；不能就此乱调PD/solver/终止/奖励。source100Hz控制忠实复现尚未完成，现保持50Hz；不得静默把queue100Hz或直接forcebypass，MPC不当可任意查询的actionoracle/无限制torquecloning。所有consumed353CPU/354/355/357与旧once永不重放；下一phase先查已有新报告/冻结unused再行动。

任何finiteSSH先freshLOCAL广范围exactCIM含MOD4_H1/RMPOLAR/watch/run_once_after_resume/E1collect/prepare_archive/single_gpu等knowncontroller并serialFREE，parent再freshCNone/private共享锁准入；活controller只读本地不第二watcher，不unknownPID/GPUscan/kill/清active。355357已allownwaited/locksreleased/SSHfinallyclosed/SESSIONrestored/FREE。另一聊天NINEV2原9:15闭账报告只证该scope释放，不替代fresh准入。

保持400Nengineeringk2000/50policy100feedback400physics2.5msTGS32-4/fullD0whitev3D1-D7/10mm单envclosure/.01mimic/唯一原canonical3900save3600exit300strictreserve，不grant/copy/refund/clearactive/第二writer。historicalH1不暗换newMOD4v1资产，不称新专家毕业；84x48暂定mount非实机D435i。禁Luna/OpenRouter，只当前模型原生视觉。

所有rawfalse/source/report/once/回放决策/automation入Git。phase mod4-mpc-control-handoff339-349已record351：trial-20261102-mod4-mpc-control-handoff339-349 objectf63c76d9c064a26e6261b544304c7f92a5bbdf76/peela6c59be6408153875b36ed851d59d3767f8e5709；本轮352..360按同修复阶段ordinarysupplement361，不再record/retag，查实际commit/push。保留所有旧tagobject/peels与lqr5848b45a99b8c32af02eb61b507c3f95ab39e4ad。PT/NPZ/USD/media只实际pathbytes已有SHA索引，不为Git读模型重跑physics；凭据只原memory不输出入Git。postGit验证工具输出，不追HEAD无限报告。'''
request=dict(id='mod4-10',mode='update',kind=config['kind'],name=config['name'],prompt=prompt,status=config['status'],rrule=config['rrule'],targetThreadId=config['target_thread_id'])
if'notification_policy'in config:request['notificationPolicy']=config['notification_policy']
put(R/'AUTOMATION360_UPDATE_REQUEST.json',request)
print(json.dumps(dict(passed=True,workorder=str(path),actual355=groups355,actual357=groups357,allownclosed=True,training345GO=False)))
