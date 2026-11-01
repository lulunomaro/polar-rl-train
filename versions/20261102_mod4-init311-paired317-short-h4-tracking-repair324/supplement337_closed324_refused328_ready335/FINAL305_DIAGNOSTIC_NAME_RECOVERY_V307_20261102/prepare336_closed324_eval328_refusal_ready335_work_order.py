"""Save truthful closed324/refused328/unused335 state and update existing heartbeat request."""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib, json, subprocess, time, tomllib

P=Path(__file__).resolve().parent
T=P.parent
N=T/'REFERENCE_H4_TRACKING_REPAIR_V324_20261102'
A=T/'REFERENCE_TRACKING324_POSTROUND_EVAL_V328_20261102'
E=T/'FINAL324_RESOURCE_RECOVERY_EVAL_V335_20261102'
R=P/'reports'
read=lambda p:json.loads(p.read_bytes())
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def put(name,value):
    with (R/name).open('x',encoding='utf8') as f:json.dump(value,f,ensure_ascii=False,indent=2,allow_nan=False)

complete=read(N/'reports/ROOT324_COMPLETE_FINALS_OR_PARTIALS_ORIGINAL_COST_RETURNED_ACTUAL.json')
full=read(N/'reports/ROOT324_NEW_FINAL_WHOLE_CPU_RETURNED_ACTUAL.json')
owner=complete['owner_closed']
assert full['passed'] and complete['roles']['jump_72']['qualified_formal']
assert owner['canonical_None'] and owner['shared_locks_free']
assert owner['cohort_final']['rows']['jump_72']['terminal_all_own_children_waited']
failure=read(A/'reports/ROOT328_EVALUATION_FULL_RETURNED.json')
assert failure['result'] is None
parts={Path(row['path']).name:json.loads(row['UTF8']) for row in failure['full_UTF8'] if row['path'].endswith('.json')}
assert 'BlockingIOError' in parts['ACTUAL328_ORIGINAL_PARENT_ERROR.json']['error']
assert parts['ACTUAL328_ALL_WAITED_PRIVATE_SHARED_EX_RELEASED.json']['all_owned_locks_released']
assert 'ACTUAL328_WORKER_IDENTITY_BEFORE_WAIT.json' not in parts
ready=read(R/'STATIC335_NEW_FINAL324_EVAL_AFTER328_RESOURCE_REFUSAL.json')
assert ready['passed'] and H(E/'INDEX335_EVAL_SOURCE_TASK_CALLERS_FROZEN.json')==ready['INDEX_SHA']
assert not (E/'reports/ROOT335_ONCE_CONSUMED_BEFORE_NETWORK.json').exists()
query="Get-CimInstance Win32_Process | Where-Object { $_.Name -match '^(python|pythonw|ssh|plink).*' -and $_.CommandLine -match 'watch_|collect_attempt|snapshot_|deploy_|launch_|postround|MOD4|mod4|F:\\\\RMPOLAR' } | Select-Object ProcessId,ParentProcessId,CreationDate,ExecutablePath,CommandLine | ConvertTo-Json -Depth 4 -Compress"
proc=subprocess.run(['pwsh.exe','-NoProfile','-Command',query],capture_output=True,text=True,encoding='utf8',check=True)
processes=json.loads(proc.stdout) if proc.stdout.strip() else []
if isinstance(processes,dict):processes=[processes]
assert not any(row['ProcessId'] in (59952,54784,60040) for row in processes)
assert any(row['ProcessId']==30080 and 'watch_w35_resume89aca_wait_actual_boundaries.py' in row['CommandLine'] for row in processes)
put('LOCAL336_EXACT_CONTROLLERS_324328_EXITED_W35_STILL_LIVE.json',dict(epoch=time.time(),processes=processes,owned324_normal_CPU_postround_eval_local_processes_exited=True,newSSH=False,newwatcher=False))
workpath=R/'CURRENT_ACTUAL336_CLOSED324_REFUSED328_READY335_WORK_ORDER_V1.json'
work=dict(epoch=time.time(),status='FINAL324_COMPLETE_CPU609PASS_EVAL328_RESOURCE_REFUSED_335_UNUSED_READY_OTHER_CONTROLLERS_LIVE',
    previous=str(R/'CURRENT_ACTUAL331_LIVE324_AND_POSTROUND328_WORK_ORDER_V1.json'),
    final324=dict(complete=True,training_running=False,source=complete['roles']['jump_72']['formal'],CPU=full,
        exact_Pi4379_critic4379_newWM4411_total16879=True,actorAdam52636_critic9696_WM16879=True,
        controls=4442,ownpairs=355360,full17teacherAdam42940_EMA_STD_norm_RNG_preserved=True,
        normal324_consumed=True,CPU324_consumed=True,postround328_consumed=True,
        original_fee_seconds=owner['raw_fee_sum_once'],closing_balance_snapshot=owner['closing_balance_snapshot'],canonical_None_at_original_close=True,original_locks_released=True,
        actual_independent_final324_skill_evaluation=False,actual_final324_replay=False),
    refused328=dict(root=str(A),job=failure['job'],original_error=parts['ACTUAL328_ORIGINAL_PARENT_ERROR.json'],original_release=parts['ACTUAL328_ALL_WAITED_PRIVATE_SHARED_EX_RELEASED.json'],
        original328source_task_reports_once_unchanged=True,worker_started=False,SDK=0,model_reads=0,physics=0,GO=0,
        result=None,strict_or_cross_counts='unmeasured;nevercall0/80forpreSDKrefusal',no_replay=True,
        SSHfinally=read(A/'reports/ROOT328_ALL_SSH_CLOSED_FREE.json')),
    current_controllers=dict(local_snapshot=str(R/'LOCAL336_EXACT_CONTROLLERS_324328_EXITED_W35_STILL_LIVE.json'),processes=processes,
        shared_lock_actual_owner='unknown_from328nonblockinglockrefusal;do_notinfer_fromGPUutilization',
        W35dispatch='F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/reports/W35_resume89aca_wait_dispatch_20261102_054158.json',
        W35_remote_job='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_W35_RESUME89ACA_WAIT_V4_20261102_054158_1793569318385718000',
        W35_remote_original_parent142='1431521/create1793569326.9 from dispatch;actualGO not yet claimed by that snapshot',
        no_concurrent_finiteSSH_while_local_controller_live=True),
    next_unused335=ready,
    execute_after_release=dict(command='Python314 -B -X utf8 '+str(E/'run335_eval_once.py')+' --caller-index-SHA '+ready['INDEX_SHA'],
        preconditions='localW35latestactualexit/release;freshbroadexactCIMallknowncontrollers;serialFREE;originalparentCNone/privateEX/sharedEX/actualselectedGPU admission. If stillbusy,dolocalpreparationandquiet;do not burn335onanotherpredictable refusal.',
        no_new_cpu_validation='reuse actual324609finitefullCPU;noarchiveonlymodelread',
        after_eval='ROOT335_EVALUATION_FULL_RETURNED + ROOT335_SELECTED_REPLAY_TRANSFERS;run render335_recorded_frames.py;nativeview_image actualRECORDED335_NATIVE_FRAMES/ACTUAL335_FINAL324_BODY_POSE_SEQUENCE.png;run analyze335_saved_first_episode_facts.py and choose continuation/targetedrepair from actualfacts',
        no_unchanged324_repeat_before_actual_eval=True),
    source_diagnostic_only=dict(final_training_tracking_cost_last32=33.079493165016174,final_imagined_position_component=33.90883541107178,flight_environment_controls=0,meaning='savedtrainingstatistics,noindependenteval/no causalgradientclaim;do_notcallskillfailureorfixverifiedfromthisalone'),
    historical='305complete/307CPU/308actual0/80crossstrict70orientation10full8s nativereviewed;311referenceinitnotfix;317truepairedH32.340485m/H4.0218681m;oldonceallpreserved',
    constraints='actor103critic106/reference59/H4puretrackingterminal0/WMH32/actualTDcriticEMA/PPO0/Fudanfalse;MPCplannedstateonly/noforeignactioncloning/noautonomousdepthclaim.400Nengineeringk2000/50policy100feedback400physics2.5msTGS32/4/fullD0whitev3D1-D7/10mmperenvclosure/mimic.01.Originalsinglecanonical/3900save3600exit300/strictreserve,noincrease/grant/copy/refund/clearactive/secondwriter;historicalassetfrozen,notnewMOD4v1adaptation.84x48provisionalcamera. Nativevisiononly/noLuna. SSHfinallyclosed/SESSIONrestored/serialFREE before nextfinitecontrol.',
    Git=dict(existing_phase='mod4-init311-paired317-short-h4-tracking-repair324',latest_actual333_supplement='403c7001bd747ab42831d0a44101903341f80678',existing_tagobject='d2e4c479f7ecd7a2974f022a0571c826746fe225',existing_peel='b4412bafb86d7f7e4f350feafc7a6bed6c45591e',new_reports='334unusedanalyzer/324normalfullCPUclose/328refusal/335independentrepair/336workorderautomation: pending ordinary supplement337 of samephase;do_not_record_or_retag',preserve_all_oldtags_and_lqr=True,heavy='actualpathbytesexistingSHAonly/noarchiveonlymodelreads'))
put(workpath.name,work)
put('LOCAL336_READER_WRONG_DYNAMIC_REPORT_FILENAME_PRESERVED.json',dict(epoch=time.time(),passed=False,error='Get-Content could not find POSTROUND328_ORIGINAL_ERROR_1793570374912045400.json; actualdynamicfilename POSTROUND328_ORIGINAL_ERROR_1793570374740472300.json subsequently read in full',scope='localreaderfilenameonly',model_reads=0,SDK=0,network=0,training_affected=False,raw_actual_error_preserved=True))
config=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text('utf8'))
put('AUTOMATION336_PRIOR_CONFIG.json',config)
prompt=f'''每小时继续本聊天MOD4参考轨迹跟踪与定向修复。人类已授权“新跟踪启动”“继续看收尾然后修复”：完整保存安全退出后立即独立评测并真实姿态回放，依据实际结果主动修复/续训，不等催促。ACTIVE/currentchat，无新Goal/重复automation；无变化或不可行动静默，仅通知实质进展、失败、完成、资源/预算/网络问题和必需用户行动。

首先读取 {str(workpath).replace(chr(92),'/')}。真实文件/冻结INDEX/ownreceipt/确切进程优先。324已经完整保存关闭，不能再称训练中；正常收尾324、fullCPU324、postround328、eval328都已消费退出，不再运行。旧331live工作单保留但不再是当前状态。

最终324 runREFERENCE_TRACKING324_1793557830531817900，原owner1429205/node1429214已完整退出结算，final32698221B SHA841dd4080ae41558645f98f1105652517716772b8b1f177df8cf8af89a0cc050，Pi4379/critic4379/newWM4411/total16879，4442controls/355360ownpairs，actorAdam52636/critic9696/WM16879、teacher17Adam42940/STD/EMA/norm/RNG完整。新fullCPU324单次读609finite通过，原fee3605.186907529831s、closingbalance376025.45960092545s只是原close历史snapshot，CNone/ownchildrenwaited/原locksfree。不要为归档或重复验模再读PT。当前final324尚无实际独立技能评测/回放，不能把328拒绝说0/80失败或已评测。

328在2026-11-02 05:59:34被parent第63行private/shared非阻塞锁拒绝BlockingIOError，0worker/SDK/model/physics/GO，resultnull。实际未取得两把锁，allownedlocksreleasedtrue；原namespace/sourceTask/false/raw/CONSUMED和postround328失败完整保留。local328waiterPID59952、normal54784、eval60040均已退出，SSHfinallyclosed/SESSIONrestored/FREE。不能重跑328/normal324/CPU324或旧unused325/326。

独立新unused335已准备：{str(E).replace(chr(92),'/')}，TASK335_FROZEN.json、INDEX335_EVAL_SOURCE_TASK_CALLERS_FROZEN.json SHA{ready['INDEX_SHA']}；run335_eval_once.py --caller-index-SHA {ready['INDEX_SHA']}。同final324/sourceCPUreceipt/seed9137/80firstepisodes/400controls/同固定edge.8/270，模型完整不改；parentcontract335/evaluate335/RESULT335，先精确核private/shared/原currentauthorityCNone，再SDK和一次actor模型读取，0训练/优化/账写。独立335不是重放328once。静态所有pyAST/模型kind324完整保留/Task/referenceSHA通过，尚无网络部署/SDK/模型读取/评测动作。旧334是未执行本地结果分析器，不能当结果。

资源：先读F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/reports本地最新W35resume89aca_wait退出/first/fullsave和后续评测dispatch。已知localwatchPID30080/create2026-11-02T05:43:59.591873+08:00、scriptwatch_w35_resume89aca_wait_actual_boundaries.py保持SSH；另localrun_once_after_resume_settled_full32.py PID54524/create2026-11-02T06:02:42.627688+08只localtimer，之后可能启动新SSH。W35remotejob/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_W35_RESUME89ACA_WAIT_V4_20261102_054158_1793569318385718000，原parent1431521/create1793569326.9；该dispatch尚未claim实际GO，不能凭它声称已训练。共享锁拒绝未识别实际持锁者，勿从GPU利用率/本地watch猜测。活controller期间只读本地，不第二watcher/新finiteSSH，不kill/抢锁/清active。SLOPE135原GPU0有限任务本地05:54:50terminal已释放，不等于W35当前已释放。

所有已知controller真实释放+freshLOCAL广范围exactCIM含watch_w35_resume89aca/run_once_after_resume_settled_full32/E1collect等+serialFREE后，才执行唯一unused335；先查CONSUMED/现有result，busy时不重复拒绝/不烧once。335parent会再freshCNone和原private/shared准入；预算owner活着则继续本地准备/等待，不双开。335成功返回后立刻用Python314执行render335_recorded_frames.py（已记录bodypose有限渲染0NN/0physics），当前模型view_image原生审RECORDED335_NATIVE_FRAMES/ACTUAL335_FINAL324_BODY_POSE_SEQUENCE.png，再执行analyze335_saved_first_episode_facts.py比较305/308寿命、orientation/full8s/cross与各项tracking误差，然后主动选择并执行针对性修复或合理续训，不仅报告结束，不原样重复退化任务。若候选成功，核首次腾空越沿/整轮footprint顶面/.5s稳定及实际contactmanifold；loss/COM/腾空不毕业。错误保留，独立版本修复，已消费once不重放。

方法仍actor103=35proprio+9currentdepth+59plannedreference/critic106，actorH4=80ms纯tracking/learnedterminal0，WM训练H32、原norm/优化器，criticactualownTD/Huber+EMA.01，PPO0/Fudanfalse；exp(-weightedtrackingcost/5)和weights保持，315末段rest、312最终报告分类修复。MPC只是计划state参考，不是可任意查询PhysX动作teacher、不力矩cloning，非自主depth-only学生；起点已观察anchor+预测pose，过去同episode实测anchor可用，未来actualdepth/GTmap不进imagination。final训练last32cost33.079/imaginedposition33.909/flight0仅训练诊断，不当独立评测或单一因果证据。历史305/307恢复/308实际0/80与回放已审、311referenceinit未修好、317真正pairedWMH32.340485m/H4.0218681m及全部false/raw/once保留。

400Nengineeringk2000/50policy100feedback400physics2.5msTGS32/4/fullD0whitev3D1-D7/闭链10mm单envreset/mimic.01、原唯一canonical/3900save3600exit300/strictreserve保持，无grant/copy/refund/clearactive/第二writer。遵根/repoAGENTS新MOD4v1注册表；历史H1资产不暗换、不称新USD适配毕业。84x48暂定mount非D435i实机标定/FPS。禁止Luna/OpenRouter、unknownPID/GPUscan/kill。凭据仅原memory不输出入Git，finiteSSHfinallyclose/SESSIONrestore/FREE。

Git遵polar-rl-train/docs/ALL_TRIALS_AND_REPORTS_GIT_POLICY.md：全部source/report/false/raw/once/交接/automation入Git。现phase mod4-init311-paired317-short-h4-tracking-repair324已有trialobjectd2e4c479f7ecd7a2974f022a0571c826746fe225/peelb4412bafb86d7f7e4f350feafc7a6bed6c45591e，实际启动补充403c7001bd747ab42831d0a44101903341f80678。本轮324lateclose/609CPU/328refusal/335unused/336handoff/automation按同phaseordinary补充337，不重新record/retag；查实际Git提交，push失败续objects。保护全部历史tags/peels和lqr5848b45a99b8c32af02eb61b507c3f95ab39e4ad。PT/NPZ/USD/媒体仅实际pathbytes已有SHA索引，不为Git读模型/重跑物理。postGit验证工具输出，不追HEAD报告循环。'''
request=dict(mode='update',id='mod4-10',kind=config['kind'],name=config['name'],prompt=prompt,rrule=config['rrule'],status=config['status'],targetThreadId=config['target_thread_id'])
if 'notification_policy' in config:request['notificationPolicy']=config['notification_policy']
put('AUTOMATION336_UPDATE_REQUEST.json',request)
print(json.dumps(dict(passed=True,workorder=str(workpath),automation_request=str(R/'AUTOMATION336_UPDATE_REQUEST.json'),final324=full['SHA'],independent_actual_evaluation=False,unused335=True,known_controllers=[row['ProcessId']for row in processes],model_reads=0,SSH=0)))
