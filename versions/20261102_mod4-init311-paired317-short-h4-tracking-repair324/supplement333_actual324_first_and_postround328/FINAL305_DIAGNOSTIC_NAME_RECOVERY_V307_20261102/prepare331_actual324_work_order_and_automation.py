"""Capture actual324 FIRST and the already running328 timer without SSH/model reads."""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib, importlib.util, json, subprocess, time, tomllib

P = Path(__file__).resolve().parent
T = P.parent
N = T / 'REFERENCE_H4_TRACKING_REPAIR_V324_20261102'
R = P / 'reports'
read = lambda p: json.loads(p.read_bytes())
H = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()

def put(name, value):
    with (R / name).open('x', encoding='utf8') as f:
        json.dump(value, f, ensure_ascii=False, indent=2, allow_nan=False)

task = read(N / 'TASK324_FROZEN.json')
snapshot = read(N / 'reports/ROOT324_STATUS_FIRST_UPDATED.json')
files = {Path(row['path']).name: json.loads(row['UTF8']) for row in snapshot['full_selected_UTF8']}
go = files['GO_PRODUCTION.json']
first = files['FIRST_ACTUAL_TEACHER_DEPTH_STUDENT324_UPDATE.json']
spec = importlib.util.spec_from_file_location('review331_protocol', N / 'teacher_task324.py')
protocol = importlib.util.module_from_spec(spec)
spec.loader.exec_module(protocol)
assert protocol.validate_first(first, task, go)
grad = first['student']['first_actual_gradient_components']
assert grad['tracking_only'] > 0 and grad['terminal_only'] == 0
binding = read(N / 'reports/ROOT324_LIVE_FIRST_VALIDATED_AND_OWNER_BINDING.json')
assert binding['passed'] and binding['current']['go']['jump_72'] == go
waiter = read(N / 'reports/POSTROUND328_WAITER_LAUNCH.json')
consumed = read(N / 'reports/POSTROUND328_ONCE_CONSUMED.json')
assert consumed['pid'] == waiter['pid']
query = "Get-CimInstance Win32_Process -Filter 'ProcessId=" + str(waiter['pid']) + "' | Select-Object ProcessId,ParentProcessId,CreationDate,ExecutablePath,CommandLine | ConvertTo-Json -Depth 4 -Compress"
proc = subprocess.run(['pwsh.exe', '-NoProfile', '-Command', query], capture_output=True, text=True, encoding='utf8', check=True)
cim = json.loads(proc.stdout)
assert cim['ProcessId'] == waiter['pid'] and cim['CreationDate'] and 'postround328_finalize324_replay_eval_once.py' in cim['CommandLine']
assert (N / 'reports/POSTROUND328_LOCAL_STDERR.log').stat().st_size == 0
put('LOCAL331_EXACT_POSTROUND328_CIM.json', dict(epoch=time.time(), passed=True, process=cim, scope='localtimer until originalnormal900; no SSH/model/GO'))
zone = timezone(timedelta(hours=8))
local = lambda epoch: datetime.fromtimestamp(epoch, zone).isoformat()
workpath = R / 'CURRENT_ACTUAL331_LIVE324_AND_POSTROUND328_WORK_ORDER_V1.json'
work = dict(
    epoch=time.time(), status='ACTUAL324_H4_TRACKING_LIVE_FIRST_VALIDATED_SOLE328_POSTROUND_TIMER',
    previous_work_order=str(R / 'CURRENT_ACTUAL330_311_317_H4_REPAIR324_WORK_ORDER_V1.json'),
    source305=dict(complete=True, SHA=task['source_SHA'], evaluated308=True, cross=0, strict=0, orientation70=True, full8s10=True, native_replay_reviewed=True, all_old_once_consumed=True),
    resource_release=dict(W35_settled='F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/reports/W35_actual_settled_original_budget_20261102_032329.json', W35_postadapt_exit='F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/reports/W35_postadapt_terminal_watch_20261102_041116.json', W35_trace_exit='F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/reports/W35_motion_trace_terminal_20261102_045423.json', fresh_original_authority=str(N/'reports/ROOT324_FRESH_AUTHORITY_BEFORE_OWNER.json'), CNone_before324=True, original_remaining_snapshot_seconds=379630.6465084553, fresh_selectedGPU_private_shared_passed=True, startup_checks_consumed=True),
    actual324=dict(root=str(N), run_id=task['run_id'], task=str(N/'TASK324_FROZEN.json'), frozen_INDEX_SHA='b56674585d4dd26d53ac68ff5fefb637e1ecbb6e78c0ce6065eeac6352a46c2a', owner=read(N/'reports/ROOT324_ORIGINAL_OWNER_LAUNCH_ACTUAL.json')['owner'], node=read(N/'reports/ROOT324_ORIGINAL_NODE_LAUNCH_ACTUAL.json')['node'], GO=go, GOlocal=local(go['learning_started_epoch']), SAVE=local(go['save_deadline']), NOMINAL=local(go['nominal_end_epoch']), normal900_earliest=local(go['nominal_end_epoch']-900), launch_once_consumed=True, FIRST_status_once_consumed=True, first=first, latest_observed_progress=files['LATEST_PROGRESS.json'], snapshot_epoch=snapshot['epoch'], no_skill_graduation_claim=True),
    method=dict(actor='103=35proprio+9currentdepth+59plannedreference', critic=106, actor_policy_H=4, WM_training_H=32, actor_learned_terminal_bootstrap=False, critic='actual own TD/Huber + EMA.01, complete save', same_tracking_cost=True, Fudan_objective=False, PPO=0, exact_final305_all_state=True, actorAdam48257_critic5317_WM12468_offsets=True, fresh_physical_DR_queues_replay_episodes=True, terminal315_rest_hold=True, finalclassification312_included=True, no_MPC_torque_cloning=True, not_autonomous_depth_only=True, future_actual_depth_or_GTmap=False),
    postround=dict(root=str(T/'REFERENCE324_POSTROUND_CORRECTION_V328_20261102'), script=waiter['script'], INDEX_SHA='567eef627db7182e794f9f85e2db66ce6ad25a1225c942f9d3e8ab8553476459', actual_cim=cim, consumed=consumed, binding=str(N/'reports/ROOT324_LIVE_FIRST_VALIDATED_AND_OWNER_BINDING.json'), result=str(N/'reports/POSTROUND324_REPLAY_EVAL_DECISION.json'), evalroot=str(T/'REFERENCE_TRACKING324_POSTROUND_EVAL_V328_20261102'), sequence='solelocaltimer -> originalnormal324/fullsaveclose/formaltransfer -> newfullCPU -> eval328seed9137samefixededge.8/27080firstepisodes400controls -> actualrecordedbodyposerender;currentmodelnativeviewthenact', old325_326_never_execute=True, original_waiter_scope_string_new325_is_stale_prose=True, actual_script_and_parent_are328=True, no_duplicate_normal_CPU_eval_or_watcher=True),
    next='Read this workorder and current localwaiter/children/consumed/results first. Do not restart324/hotpatch/recheckstartup. When sole328timer entersclose/eval,readlocalonly untilcontrollerreleased. When result exists,nativelyview actualposeimage,reviewfirstepisodecross/lifetime/trackingerrors and choose targetedrepair or continuation within originalbudget; do not repeatdegradedtask or stopat ended. Failure:preserveoriginal,independentversionfix,noreplayonce.',
    constraints='400Nengineeringk2000/50policy100feedback400physics/2.5msTGS32/4/fullD0whitev3D1-D7/closure10mmperenv/mimic.01;oneoriginalcanonical3900save3600exit300/strictreserve;noincrease/grant/copy/refund/clearactive/secondwriter. historicalH1asset remains frozen,not newMOD4v1adaptation. FreshLOCALallknownexactcontrollers/serialFREE before finiteSSH;no unknownPIDscan/kill. SSHfinallyclosed/SESSIONrestored/FREE. Nativevisiononly/noLuna.',
    evidence_limits='FIRST is a full snapshot and validupdate,not FINAL or270skill. Latestobserved132controls/69Pi/138orientationevents are trainingwithrepeatedepisodes,not80independenteval.317actualH32drift.340485m/H4.0218681m is realWMdiagnostic,not skill/gradientproof.311referenceinitnotfix;315restholdnotearlyfallcausalproof. Successfulcandidate requiresfirstflightcross/fullwheelfootprinttopcontact/.5sstable/manifold.',
    Git=dict(phase='mod4-init311-paired317-short-h4-tracking-repair324', existing_trial='trial-20261102-mod4-init311-paired317-short-h4-tracking-repair324', tagobject='d2e4c479f7ecd7a2974f022a0571c826746fe225', peel='b4412bafb86d7f7e4f350feafc7a6bed6c45591e', this_followup='ordinarysupplement;do_not_record_or_retag_existing_phase', reports_pending_this_supplement=True, all_false_raw_source_reports_automation_required=True, heavy_artifacts='path/bytes/existingSHAonly;noarchiveonlymodelreads', protected_lqr='5848b45a99b8c32af02eb61b507c3f95ab39e4ad'))
put(workpath.name, work)
config = tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text('utf8'))
put('AUTOMATION331_PRIOR_CONFIG.json', config)
prompt = f'''每小时继续本聊天MOD4参考轨迹跟踪与定向修复。人类已授权“新跟踪启动”“继续看收尾然后修复”：每轮完整保存安全退出后立即独立评测并真实姿态回放，依据结果主动修复/续训，不等催促。保持ACTIVE/currentchat，无新Goal/重复automation；无变化或不可行动静默，只通知实质进展、失败、完成、资源/预算/网络问题和必需用户行动。

首先读取 {str(workpath).replace(chr(92), '/')}。真实冻结源码/INDEX/ownreceipt/确切进程/GO优先。旧330工作单的324unused/W35active已过时，原报告保留。W35训练已完整结算，postadapt评测和运动trace均退出释放；324启动前freshcanonicalNone/余额379630.6465084553s只是该时snapshot，selectedGPU/private/shared准入通过。不能因过时W35状态等待或再次launch324。

当前实际324 run={task['run_id']}，唯一原72ownerPID1429205/create1793566729.45，node1429214/create1793566729.87。完整exe/argv/controlcwd/jobroot见工作单和原launch。GPU-c27eecbd-6838-7290-1cd2-37e34522213d。GO={local(go['learning_started_epoch'])}，SAVE={local(go['save_deadline'])}，NOMINAL={local(go['nominal_end_epoch'])}，normal最早={local(go['nominal_end_epoch']-900)}。原3900/save3600/exit300/唯一canonical总额不改。launch324、FIRST_UPDATED已消费；不健康重启/hotpatch/重跑startup资源检查或模型验证。

324完整恢复final305SHA02b6de0af7da488ea459ef01da36e1cfec1cd72009ed9399e9e02f9646020958的actor103/critic106/STD/三Adam/EMA/norm/RNG/WM12468，actorAdam48257/critic5317，原teacher17Adam42940冻结；physical/DR/queue/replay/episode明确fresh。actorH4=80ms纯轨迹tracking，learnedterminalbootstrap0；WM训练H32/原优化器；criticactualownTD+Huber/EMA.01。exp(-weightedtrackingcost/5)与weights保留，PPO0/Fudanfalse。315末段pose保持且速度0、312最终报告误分类修复已纳入。103=35proprio+9currentdepth+59plannedreference，106critic；连续episodephase/末段停稳。MPC轨迹仅计划state参考，不能查询PhysX动作teacher，不克隆力矩；尚非自主depth-only学生。起点真实已观察anchor+预测pose，过去同episodeanchor可用，未来实际depth/GTmap不进actor/imagination。

实际FIRST64controls/5120ownpairs/512physics/128feedback，Pi1/Critic1/newWM33total12501；native24通过，真实tracking/combinedgradient1.31281519有限非零，terminal0。完整32698221B SHA4522f4165a0028a97d7614974f09afc8162c06c603dba56265be1364093bcf7a，actorAdam48258/critic5318/WM12501。后续snapshot132controls/Pi69/critic69/WM12569/138orientation事件，训练多episode计数不是独立80评测。FIRST非FINAL/技能毕业，不能据loss称成功。

唯一localpostround328 PID{waiter['pid']}/Start{cim['CreationDate']}，完整path/argv见工作单和POSTROUND328_WAITER_LAUNCH。它只localtimer到原normal900，调用唯一normal324完整收尾/fullformaltransfer/新fullCPU offsets48257/5317/12468，再独立328 samefixededge.8/270、新9137DR/80firstepisodes/400controls评测和有限真实记录bodypose原生渲染。冻结INDEX328SHA567eef627db7182e794f9f85e2db66ce6ad25a1225c942f9d3e8ab8553476459。实际脚本postround328_finalize324_replay_eval_once.py/parentcontract328/evaluate328；launchreceipt的new325eval只是旧scope文字，实际328已核。原unused325/326禁止执行。

先读waiter/children/CONSUMED/results。活着绝不重复normal/CPU/eval/第二watcher；close/eval期间只读本地直至controller释放。结果 {str(N/'reports/POSTROUND324_REPLAY_EVAL_DECISION.json').replace(chr(92), '/')}，evalroot {str(T/'REFERENCE_TRACKING324_POSTROUND_EVAL_V328_20261102').replace(chr(92), '/')}。结果出来必须view_image当前模型原生审真实pose图，再按实际tracking误差/寿命/越沿决定并执行续训或针对性修复；不只报结束、不原样重复退化任务。若候选成功，核首次腾空越沿、整轮footprint顶面接触、稳定.5s及实际contactmanifold。loss/COM高/腾空不算毕业。失败保留原报告，独立版本定向修复，once永不重放。

历史305已完整保存关闭、307CPU609finite通过、308实际0/80cross/strict/70orientation10full8s及原生回放已审；绝不能称待评测。311actualreferenceinit/directplannedq/dq两组都未稳定，默认组q非零且rawkind误称保留；315末rest修复不解释早倒。317真正actualpairedWM无更新，单步positionRMSE.00604888m、H4.0218681m、H32末步.340485m/allmasked.1647766m；不是技能评测/重建context/梯度可靠性证明。CPU319terminal梯度约56xtracking，CPU320纯H4无step通过；324是真实部署后的首次测试。旧305false/307恢复、全部297/286/289/290/291/309/310/311/316/317及旧321/325等原失败/once全保留。

400Nengineeringk2000/50policy100feedback400physics2.5msTGS32/4/fullD0whitev3D1-D7/闭链10mm单envreset/mimic.01保持。原singlecanonical与strictreserve，无grant/copy/refund/clearactive/第二writer。遵根AGENTS新MOD4v1注册表；当前historicalH1不暗换资产，不冒称新USD适配毕业。84x48暂定mount非D435i实机标定/FPS。任何新finiteSSH前freshLOCALexactCIM识别全部已知controller并leaseFREE，finallySSHclosed/SESSIONrestored/FREE；不能凭过时regex遗漏watch_postadapt/watch_w35_adaptation_exit等。禁止unknownPID/GPUscan/kill、Luna/OpenRouter。

遵根/repoAGENTS和polar-rl-train/docs/ALL_TRIALS_AND_REPORTS_GIT_POLICY.md：所有source/false/raw/once/report/交接/automation入Git。phase mod4-init311-paired317-short-h4-tracking-repair324已record：trial-20261102-mod4-init311-paired317-short-h4-tracking-repair324 objectd2e4c479f7ecd7a2974f022a0571c826746fe225/peelb4412bafb86d7f7e4f350feafc7a6bed6c45591e；本次实际324启动/FIRST/timer331用ordinary补充，不重record/retag。查Git实际本轮提交，push失败续已有objects。保护所有旧tagobjects/peels及lqr5848b45a99b8c32af02eb61b507c3f95ab39e4ad。PT/NPZ/USD/媒体只实际pathbytes已有SHA索引，不为归档读模型/重跑physics。凭据仅原memory不输出入Git。postGit验证工具输出，不追HEAD无限报告。'''
request = dict(mode='update', id='mod4-10', kind=config['kind'], name=config['name'], prompt=prompt, rrule=config['rrule'], status=config['status'], targetThreadId=config['target_thread_id'])
if 'notification_policy' in config:
    request['notificationPolicy'] = config['notification_policy']
put('AUTOMATION331_UPDATE_REQUEST.json', request)
print(json.dumps(dict(passed=True, workorder=str(workpath), automation_request=str(R/'AUTOMATION331_UPDATE_REQUEST.json'), GO=local(go['learning_started_epoch']), SAVE=local(go['save_deadline']), NOMINAL=local(go['nominal_end_epoch']), timerPID=waiter['pid'], no_model_or_SSH_reads=True)))
