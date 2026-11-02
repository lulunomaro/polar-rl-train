"""Actual live RL389 handoff and update request for the existing hourly heartbeat."""
from pathlib import Path
from datetime import datetime, timedelta, timezone
import hashlib
import json
import subprocess
import time
import tomllib

P = Path(__file__).resolve().parent
T = P.parent
R = P / 'reports'
N = T / 'MPC_COMMAND_RESIDUAL_RL_V389_20261102'
Q = T / 'RESIDUAL_RL389_POSTROUND_V396_20261102'
E = T / 'RESIDUAL_RL389_INDEPENDENT_EVAL_V396_20261102'
read = lambda path: json.loads(path.read_bytes())
H = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()

def put(path, value):
    with path.open('x', encoding='utf8') as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False, allow_nan=False)

task = read(N / 'TASK389_FROZEN.json')
binding = read(N / 'reports/ROOT389_LIVE_FIRST_VALIDATED_AND_OWNER_BINDING.json')
waiter = read(N / 'reports/POSTROUND396_WAITER_LAUNCH.json')
consumed = read(N / 'reports/POSTROUND396_ONCE_CONSUMED.json')
assert waiter['pid'] == consumed['pid'] == 54508
query = 'Get-CimInstance Win32_Process -Filter "ProcessId=54508" | Select-Object ProcessId,CreationDate,ExecutablePath,CommandLine | ConvertTo-Json -Compress'
cim = json.loads(subprocess.run(['pwsh.exe','-NoProfile','-Command',query],
    capture_output=True, text=True, encoding='utf8', check=True).stdout)
assert cim['CreationDate'] == '2026-11-02T12:41:05.031687+08:00'
assert str(Q / 'postround396_close_RL389_eval_once.py').replace(chr(92),'/').lower() in cim['CommandLine'].replace(chr(92),'/').lower()
assert cim['ExecutablePath'].replace(chr(92),'/').lower() == 'C:/Users/lulu/AppData/Local/Programs/Python/Python314/python.exe'.lower()
assert (N / 'reports/POSTROUND396_LOCAL_STDERR.log').stat().st_size == 0
assert not list((N / 'reports').glob('POSTROUND396_ORIGINAL_ERROR*'))
assert H(Q / 'INDEX396_POSTROUND_FOR389_FROZEN.json') == '8491426e50a1bda5451f99f5a3b099bb99ed397648efa45fb734ed3eeb7fb4fc'
go = binding['current']['go']['jump_72']
first = binding['first']
assert go['residual_RL'] and not go['online_MPC']
assert first['student']['first_actual_gradient_components']['combined'] > 0
assert first['student']['first_actual_gradient_components']['terminal_only'] == 0
assert first['native24_before_first_WM_step_passed']
tz = timezone(timedelta(hours=8))
iso = lambda epoch: datetime.fromtimestamp(epoch, tz).isoformat()
times = dict(GO=iso(go['learning_started_epoch']), SAVE=iso(go['save_deadline']),
             NOMINAL=iso(go['nominal_end_epoch']), normal900_earliest=iso(go['nominal_end_epoch']-900))
work = R / 'CURRENT_ACTUAL397_LIVE_RL389_AND_POSTROUND396_WORK_ORDER_V1.json'
value = dict(epoch=time.time(), kind='CURRENT_ACTUAL397_LIVE_RESIDUAL_RL389_WITH_SOLE_POSTROUND396',
    latest_human='我需要的是rl上台阶',
    objective='Learned RL policy must jump onto270mm platform and stably recover; traditional MPC diagnostics are not the deliverable',
    replaces='392unused/resourcewait/390 are obsolete; originals retained',
    RL389=dict(root=str(N), run=task['run_id'], START_consumed=True, FIRST_UPDATED_consumed=True,
        GO=True, deployed=True, owner=binding['exact_original_owner'],
        node=read(N / 'reports/ROOT389_ORIGINAL_NODE_LAUNCH_ACTUAL.json'),
        worker=binding['current']['rows']['jump_72']['worker'],
        GPU=task['GPU_UUID'], INDEX_SHA=H(N / 'INDEX389_SOURCE_TASK_CALLERS_FROZEN.json'),
        worker_SHA=task['worker_SHA'], original_go=go, original_times=times,
        source_model_SHA=task['model_SHA'], full_source_offsets=[52636,9696,16879],
        source_teacher17Adam42940_STD_frozen=True,
        actor103_critic106_threeAdam_EMA_norm_RNG_complete=True,
        action='saved347processed50Hzfeedforward+1*tanh(actor103-origin_actor103);noonlineMPC',
        input='35proprio+9currentdepth+59plannedreference;notdepthonly',
        learning='ownPhysXWMH32/actorH8directweightedtrackingcost/criticactualownTDHuberEMA.01;terminal0',
        fresh_physical_DR_queues_replay=True),
    actual_FIRST=dict(receipt=str(N / 'reports/ROOT389_STATUS_FIRST_UPDATED.json'),
        controls=first['controls'], ownpairs=first['new_environment_transitions'],
        physics=first['physics_callbacks'], feedback=first['feedback_samples'],
        Pi=first['actual_new_Pi_updates'], critic=first['actual_new_critic_updates'],
        newWM=first['actual_new_WM_updates'], totalWM=first['total_WM_updates'],
        gradients=first['student']['first_actual_gradient_components'],
        first_complete=first['first_complete'], native24=True,
        later_progress=binding['files']['LATEST_PROGRESS.json'],
        later_student=binding['files']['LATEST_STUDENT389.json'],
        skill_not_yet_measured=True, not_independent_80episode_eval=True),
    postround396=dict(root=str(Q), evalroot=str(E), indexSHA=H(Q / 'INDEX396_POSTROUND_FOR389_FROZEN.json'),
        bound_and_started=True, launch=waiter, consumed=consumed, exact_local_CIM=cim,
        local_stdout_bytes=(N/'reports/POSTROUND396_LOCAL_STDOUT.log').stat().st_size,
        local_stderr_bytes=0, SSH_before_normal900=False,
        script=str(Q / 'postround396_close_RL389_eval_once.py'),
        scope='Localtimer until originalnormal900; unique normal389 fullsave/safeexit/formaltransfer/newfullCPU/independentfinalRL396eval/nativebodyposerender',
        fullCPU_offsets=[52636,9696,16879],
        independent_eval='80firstepisodes/400controls/8s/seed9137/newDR/samefixededge.8/270;finalactor+savedorigin+fixedtable;noonlineMPC',
        result=str(N / 'reports/POSTROUND389_RL_REPLAY_EVAL_DECISION.json'),
        image=str(E / 'RECORDED396_NATIVE_FRAMES/ACTUAL396_RL_BODY_POSE_SEQUENCE.png'),
        native_review_required=True),
    preserved_unused=dict(postround390='Python314missingpsutil',
        generator394='SyntaxError invalid390unusedpreserved keyword; original did not execute; missingbind preserved',
        postround394='static Windows slash comparison error; frozen unused',
        postround395='static mixed-case parent script token error; frozen unused',
        postround396='independent normalizedWindowspath and directparentcasefixtures passed; solely launched',
        training389_changed=False, no_training_restart=True),
    resources=dict(before389='OtherPair1V4actuallyclosed and allknownlocalcontrollersreleased before389freshadmission',
        canonical_snapshot_before389='369962.13179540634s historical snapshot only',
        current_budget_owner='Original RL389owner1458549; no secondwriter',
        latest_start_lease_receipt=read(N / 'reports/ROOT389_START_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json'),
        latest_status_lease_receipt=read(N / 'reports/ROOT389_STATUS_FIRST_UPDATED_SSH_FREE.json')),
    next='Read local waiter/children/once/results first. Live waiter means no duplicate normal/CPU/eval/watch/SSH. At returned finaleval currentmodel must view actualrecordedposes and auditmanifold, then proactively repair or reasonablycontinue RL from actualevidence.',
    acceptance='firstflight whole rearfootprint clears edge; doublewheel actualtopmanifold; no returnground/retreatedge; vxy/vz<=.03m/s,rollpitch<=10deg,yaw<=.2rad,continuous>=.5s',
    physical_constraints='400Nengineeringk2000/policy50feedback100physics400/2.5msTGS32-4/fullD0whitev3D1-D7/10mmepisodeclosure/.01mimic/historicalH1exactproducer/unchangedPDqueueDCclip',
    budget='sole originalcanonical3900/save3600/exit300strictreserve;nograntcopyrefundclearactiveorsecondwriter',
    history='324fullclose609finiteCPU/339RL0of80alreadyreviewed;345unused;373377traditionalMPCnotRLskill;alloncepreserved',
    git=dict(phase='mod4-residual-rl389-command-handoff', record393_done=True,
        trial='trial-20261102-mod4-residual-rl389-command-handoff',
        object='4e77ba7807787c22df7e8661c2f7801042cfc896',
        peel='938b9ee8458f09a47e369995c8bfb1064b052a1f',
        next='ordinarysupplement398 for launchFIRST and394..397 repairs/workorder/automation; never rerecord/retag',
        lqr='5848b45a99b8c32af02eb61b507c3f95ab39e4ad'),
    automation='Existingmod4-10ACTIVE/hourly/currentchat; meaningfulchangesonly; no new Goal/chat/automation')
put(work, value)
prompt = f'''每小时继续本聊天MOD4跳270mm。人类最新明确“我需要的是rl上台阶”，交付必须是RL策略实际跳台并稳定；传统MPC成功不是交付，不再接连传统控制实验拖延RL。人类已授权新跟踪启动/继续看收尾然后修复。每轮完整保存安全退出后立即独立RL评测与真实姿态回放，按实际结果主动修复/合理续训，不等催促。ACTIVE/currentchat，不新Goal/chat/重复automation；无变化不可行动静默，只通知实质进展、失败、完成、资源/预算/网络问题和必需用户行动。

首先读 {work.as_posix()}。实际冻结源码/INDEX/ownreceipt/确切进程与结果优先。旧392的unused389/resourcewait/390已过时，原报告保留；389真实训练已启动，绝不能再launch/FIRST/bind。传统373/377不是RL毕业，324已完整关闭CPU609finite、339独立0/80已评/已原生审，345仍unused不启动。

实际RL389 run={task['run_id']}，root={N.as_posix()}。原唯一ownerPID1458549/create1793593787.61、node1458558/create1793593788.04、worker1458572/create1793593794.18；完整exe/argv/jobroot/controlcwd见工作单和原launch。GPU={task['GPU_UUID']}。GO={times['GO']}，SAVE={times['SAVE']}，NOMINAL={times['NOMINAL']}，normal最早={times['normal900_earliest']}。原3900/save3600/exit300/唯一canonicalstrictreserve保持；START/FIRST_UPDATED/BIND388已消费，健康不restart/hotpatch/重跑startup资源或模型验证。冻结INDEX389SHA={H(N/'INDEX389_SOURCE_TASK_CALLERS_FROZEN.json')}，workerSHA={task['worker_SHA']}。

389是学习残差RL：347已保存processed电机位置/轮速表偶数采样50Hz前馈，加1*tanh(onlineactor103-frozenorigin103同input)。初始残差0，运行时无在线MPC求解/闭环MPC接管，无力矩cloning。actor103=35proprio+9currentdepth+59plannedreference，仍非自主depth-only；critic106。完整恢复final324SHA{task['model_SHA']}，actorAdam52636/critic9696/WM16879、三Adam/STD/EMA/normRNG，teacher17Adam42940冻结，不resetAdam/回退2135actor。physicalDRqueue/replayfresh，planned347fullq/dq/root+actualqheldqueue+3派生IMUcache每reset刷新，原D0-D7保持。actorH8direct同weightedtrackingcost/5、terminal0/noexpattenuation/noalive删除，WMH32原优化器normRNG，criticactualownTDHuber/EMA.01/实际exp(-cost/5)保留。futureactualdepth/GTmap不进imagination。50Hz保存表不谎称忠实100HzMPC。

实际FIRST64controls/5120ownpairs/512physics/128feedback，Pi1/critic1/newWM33total16912，真实trackingcombinedgradient0.9054399132728577有限非零、terminal0、native24通过；首完整32800939B/SHA09b5d743a92ff8859c88e995229923bf6c31ab6667ada6e42c53923685b12ec9，actorAdam52637/critic9697/WM16912。后续已取snapshot到Pi43/critic43/newWM75total16954/106controls，124orientation是训练多episode事件，不是独立80评测。FIRST不是FINAL/技能成功。

唯一localpostround396已实际绑定启动：PID54508/create2026-11-02T12:41:05.031687+08:00，脚本{(Q/'postround396_close_RL389_eval_once.py').as_posix()}，完整exe/argv见POSTROUND396_WAITER_LAUNCH及397exactCIM。冻结INDEX396SHA={H(Q/'INDEX396_POSTROUND_FOR389_FROZEN.json')}。它只localtimer到原normal900，然后唯一normal389完整保存安全退出/fullformaltransfer/newfullCPU offsets52636/9696/16879，独立RL396读取同final一次actor+origin+固定前馈，80firstepisodes/400controls/8s/seed9137新DR/同固定edge.8/270，actual400Hzcontactmanifold/有限记录真实bodyposes原生渲染。evalroot={E.as_posix()}，结果={(N/'reports/POSTROUND389_RL_REPLAY_EVAL_DECISION.json').as_posix()}，图={(E/'RECORDED396_NATIVE_FRAMES/ACTUAL396_RL_BODY_POSE_SEQUENCE.png').as_posix()}。

先查waiter/children/CONSUMED/results；活着不重复normal/CPU/eval/第二watcher。close/eval期间只读本地直至controller释放；不要再次SSH。结果出来currentmodel必须view_image原生看实际pose并核真实manifold，再按RL真实误差/寿命/跨台/稳定结果主动定向修复或合理续训，不只报结束、不原样继续退化任务。若资源被其它originalowner占用，等待真实释放，不清active/抢锁/kill/第二writer。新finiteSSH前freshLOCAL广范围exactknownCIM含MOD4_H1/RMPOLAR/watch/run_once_after_resume/E1collect/prepare_archive/single_gpu/collect_nine及全新collector，并serialFREE；parent再freshCNone/private/shared准入，finallySSHclosed/SESSIONrestored/FREE。只允许同步ownpostroundparent以exactPID/create/exe/argv/directparent身份通过本地检查。

390因Python314无psutil冻结unused；394生成器SyntaxError及missingbind原失败保留，v2完成后静态发现Windows路径斜杠比较拒绝；395独立修斜杠后静态发现lowercasecommandline对mixedcaseRL389token拒绝；396独立修并CPUfixture通过且已唯一启动。所有390/394/395冻结源和rawfalse保留不执行，不改变训练389。不要安装依赖/热改训练/重跑once。

技能成功须首次飞行整轮rearfootprint越沿、双轮实际solver台顶manifold、无回地面/退沿，vxy/vz<=.03m/s、rollpitch<=10deg/yaw<=.2rad连续>=.5s。loss/COM/腾空/leadingedge与传统MPC不是RL毕业。保持400Nengineeringk2000/policy50feedback100physics400/2.5msTGS32-4/fullD0whitev3D1-D7/10mm单envclosure/.01mimic，原PD/DCclip/queue/solver与historicalH1exactproducer资产不暗改，不称newMOD4v1专家适配毕业；84x48camera暂定非D435i标定FPS。原singlecanonical3900/save3600/exit300strictreserve不grant/copy/refund/clearactive/第二writer，余额历史snapshot不当实时。禁Luna/OpenRouter/unknownPID或GPUscan/kill。

所有source/report/rawfalse/once/actuallaunchFIRST/394..397/回放决定/automation按polar-rl-train/docs/ALL_TRIALS_AND_REPORTS_GIT_POLICY.md归档。当前phase mod4-residual-rl389-command-handoff已record393，trialobject4e77ba7807787c22df7e8661c2f7801042cfc896/peel938b9ee8458f09a47e369995c8bfb1064b052a1f；查supplement398实际commit与远端，已commit不重record/retag，push失败只续existingobjects。保护所有历史tagobjects/peels及lqr5848b45a99b8c32af02eb61b507c3f95ab39e4ad。PT/NPZ/USD/media只pathbytes已有SHA，不为归档读模型/跑physics；凭据仅原memory不输出入Git。postGit验证只工具输出不无限HEAD报告。'''
cfg = tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text('utf8'))
request = dict(id=cfg['id'], mode='update', kind=cfg['kind'], name=cfg['name'],
    prompt=prompt, status=cfg['status'], rrule=cfg['rrule'], targetThreadId=cfg['target_thread_id'])
put(R / 'AUTOMATION397_LIVE_RL389_POSTROUND396_UPDATE_REQUEST.json', request)
print(json.dumps(dict(passed=True, current_workorder=str(work), request=str(R / 'AUTOMATION397_LIVE_RL389_POSTROUND396_UPDATE_REQUEST.json'), actual_RL=True, waiterPID=cim['ProcessId'])))
