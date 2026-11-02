"""Current actual local396 failure, prepared399/400, and external Pair2 resource wait."""
from pathlib import Path
import hashlib
import json
import subprocess
import time
import tomllib

P=Path(__file__).resolve().parent
T=P.parent
R=P/'reports'
N=T/'MPC_COMMAND_RESIDUAL_RL_V389_20261102'
C=T/'RL389_CLOSED_FINAL_RECOVERY_V399_20261102'
E=T/'RL389_RECOVERED_FINAL_INDEPENDENT_EVAL_V400_20261102'
F=Path('F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/POSTTRAIN_EIGHT_EXCLUDING_H1_20261102')
read=lambda path:json.loads(path.read_bytes())
H=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
def put(path,value):
 with path.open('x',encoding='utf8')as stream:json.dump(value,stream,indent=2,ensure_ascii=False,allow_nan=False)

prior=read(R/'CURRENT_ACTUAL397_LIVE_RL389_AND_POSTROUND396_WORK_ORDER_V1.json')
release=read(F/'reports/ORIGINAL_AUTHORITY_RELEASE_AFTER389_WATCH_RESULT.json')
pair=read(F/'reports/PAIR2_GENERIC_V2_ACTUAL_FIRST_ADMISSION_SNAPSHOT.json')
dispatch=read(F/'PAIR2_GENERIC_V2_ORIGINAL_OWNER_DISPATCH_ONCE.json')
pattern='MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021|RMPOLAR|run_once_after_resume|continue_clean_sequential|watch_|prepare_archive|collect_nine|deploy_nine|single_gpu|collect_e1|E1_actual|snapshot_adaptation|deploy_w35|launch_w35|collect_attempt2_wait_and_sdk|postround|run_ROOT|PAIR1|PAIR2|PAIR3|PAIR4'
query="Get-CimInstance Win32_Process -Filter \"Name='python.exe' OR Name='ssh.exe'\" | Where-Object { $_.CommandLine -match '"+pattern+"' } | Select-Object ProcessId,ParentProcessId,CreationDate,ExecutablePath,CommandLine | ConvertTo-Json -Depth 5 -Compress"
result=subprocess.run(['pwsh.exe','-NoProfile','-Command',query],capture_output=True,text=True,encoding='utf8',check=True)
rows=json.loads(result.stdout)if result.stdout.strip()else[]
rows=rows if isinstance(rows,list)else[rows]
own=[row for row in rows if row['ProcessId']==__import__('os').getpid()]
others=[row for row in rows if row['ProcessId']!=__import__('os').getpid()]
assert len(own)==1
assert not any(row['ProcessId']==54508 for row in rows)
assert not(N/'reports/ROOT389_NORMAL900_ONCE_CONSUMED.json').exists()
assert not(N/'reports/ROOT399_NORMAL900_RECOVERY_ONCE_CONSUMED.json').exists()
assert not(N/'reports/CPU389_NEW_FINAL_CONSUMED.json').exists()
assert not(E/'reports/ROOT400_ONCE_CONSUMED_BEFORE_NETWORK.json').exists()
put(R/'LOCAL401_EXACT_KNOWN_CONTROLLER_RESOURCE_SNAPSHOT.json',dict(epoch=time.time(),rows=rows,
    others=others,newSSH=0,no_unknown_PIDscan=True,serial_free=False if others else 'not yet assertedforfutureconnection'))
work=R/'CURRENT_ACTUAL401_RL389_POSTROUND_REFUSED_RECOVERY399_EVAL400_WORK_ORDER_V1.json'
value=dict(epoch=time.time(),kind='CURRENT_ACTUAL401_ORIGINAL389_RELEASE_OBSERVED_FINAL_UNCOLLECTED_LOCAL396FAILURE',
    latest_human='我需要的是rl上台阶',
    replaces='397livewaiter is obsolete; original397 and all396failure/raw kept',
    original389=prior['RL389'],
    current389_state='Original authority release observed in another exactscope at13:30:21; own formalFINAL/exit receiptsnotcollected yet, no newtrainingrunningclaim',
    original_run='REFERENCE_TRACKING389_1793592987357927500',
    source_initial_offsets=[52636,9696,16879],
    postround396=dict(pid54508_exited=True,consumed=True,
        error=read(N/'reports/POSTROUND396_ORIGINAL_ERROR_1793596794821639600.json'),
        normal_error=read(N/'reports/ROOT389_NORMAL900_ORIGINAL_ERROR_1793596794804750100.json'),
        timestamp='2026-11-02T13:19:54.804751+08:00',
        location='normal389line69 localCIMown/exe/nootherassert',
        no_exact_blocker_recorded_original=True,
        network=0,SDK=0,model_reads=0,physics=0,
        original_normal_once_not_consumed=True,
        CPU389_not_run=True,eval396_not_run=True,
        do_not_replay_original_normal_or_postround=True),
    external_release_evidence=dict(path=str(F/'reports/ORIGINAL_AUTHORITY_RELEASE_AFTER389_WATCH_RESULT.json'),
        receipt=release,classification='Only proves canonical owner1458549wentnull in thatscope; not own fullsavequalification/modelidentity/skillpass'),
    recovery399=dict(root=str(C),unused=True,
        task=str(C/'TASK399_FROZEN.json'),
        collector=str(C/'collect399_original389_closed_final_once.py'),
        INDEX_SHA=H(C/'INDEX399_RECOVERY_SOURCE_TASK_CALLER_FROZEN.json'),
        scope='Independentnewcollectionofsameoriginal389closedowner/node/formal once;0GO/optimizer/accountwrites',
        fixes='FreshbroadCIMsnapshotbeforeassert/normalizedWindowsexepaths; preserveoriginalremoteidentity/locks/segments/finalclassificationandCPUchecks',
        CPU_after='Originalunconsumedreview389_NEW_final_whole_CPU_UNUSED_once.py onceafterfirstformaltransfer'),
    eval400=dict(root=str(E),unused=True,ready_noSDK_noPT=True,
        preparation_INDEX_SHA=H(E/'INDEX400_UNUSED_EVALUATION_PREPARATION_FROZEN.json'),
        bind=str(E/'bind400_actual_final_identity_once.py'),
        runner=str(E/'run400_eval_once.py'),
        final_INDEX='GeneratedonceafteractualrecoveredfinalCPUidentity; no pretensecurrentplaceholderisfinal',
        scope='FinalRL389actor+savedorigin/fixedfeedforward/noonlineMPC;80firstepisodes400controls8s/newDRseed9137samefixededge.8/270;actual400Hzcontactmanifold',
        render=str(E/'render400_recorded_frames.py'),
        image=str(E/'RECORDED400_NATIVE_FRAMES/ACTUAL400_RL_BODY_POSE_SEQUENCE.png'),
        CPUonlyrender=True,native_review_required=True),
    resource=dict(local_exact_CIM=rows,
        active_known_controller=others,
        latestlocaldispatch=dispatch,
        latestlocalsnapshot=str(F/'reports/PAIR2_GENERIC_V2_ACTUAL_FIRST_ADMISSION_SNAPSHOT.json'),
        other_ownerPID=1462128,other_ownercreate=1793597883.97,
        other_remote_root=dispatch['root'],
        other_actual_go_E2=pair['roles/E2/GO_PRODUCTION.json'],
        other_actual_go_CURB=pair['roles/CURB_INDEPENDENT113/GO_PRODUCTION.json'],
        serial_free=False if others else 'mustbefreshlyadmitted',
        readlocalfirst=str(F/'PAIR2_GENERIC_V2_LATEST_CLOSED_RESULT_PATH.json'),
        no_new_watcher_no_finiteSSH=True),
    next='Whileknowncollector42604activeonlylocalread/prep/Git. Afterallknowncontrollersactualreleased/freshlocalCIM/serialFREE,rununiqueunused399withpinnedindex;ownCNone/private/sharedmustpass. ThenoriginalCPU389once,new400bind/index,run400once,render/viewactualposes/auditmanifoldandproactivelyrepairorcontinueRLfromfacts.',
    actual389_independent_skill_evaluation_done=False,
    failure_not_0of80_skill_result=True,
    acceptance=prior['acceptance'],physical_constraints=prior['physical_constraints'],budget=prior['budget'],
    git=dict(phase='mod4-residual-rl389-command-handoff',
        trialobject='4e77ba7807787c22df7e8661c2f7801042cfc896',
        peel='938b9ee8458f09a47e369995c8bfb1064b052a1f',
        supplement398='f0705ed2366481a6c512449afa9a513a173980a1',
        next='ordinarysupplement402;no record/retag;pushretryexistingobjects',
        lqr='5848b45a99b8c32af02eb61b507c3f95ab39e4ad'),
    automation='sameexistingmod4-10ACTIVE/hourly/currentchat;notifyfailureresourcewaitonce;unchangedquiet')
put(work,value)
prompt=f'''每小时继续本聊天MOD4跳270mm。人类明确“我需要的是rl上台阶”，交付是RL实际跳台稳定，传统MPC数字不是交付；不再盲目接连传统实验。已授权新跟踪启动/继续看收尾然后修复，完整保存安全退出立即独立RL评测和真实姿态回放，再主动定向修复/合理续训。不新Goal/chat/重复automation，保持ACTIVE/currentchat；无变化不可行动静默，只通知实质进展、失败、完成、资源/预算/网络问题、必需用户行动。

首先读 {work.as_posix()}。实际冻结source/INDEX/ownreceipt/确切进程与结果优先。旧397livewaiter过时：postround396 PID54508已经退出，2026-11-02 13:19:54原normal389line69本地CIMassert失败，未网络/SDK/模型读取/物理。原396/normal389false/日志/CONSUMED完整保留，不能重放；这不是RL0/80失败。final389尚未被本聊天正式收回/CPU/独立技能评测，不能说已评或训练仍在进行。

原RL389runREFERENCE_TRACKING389_1793592987357927500，root={N.as_posix()}，owner1458549/create1793593787.61/node1458558/create1793593788.04/worker1458572/create1793593794.18，完整exe/argv/jobroot见397与原launch。GO2026-11-02T12:29:51.567860+08，SAVE13:29:51.567860、NOMINAL13:34:51.567860。另一精确scope本地ORIGINAL_AUTHORITY_RELEASE_AFTER389_WATCH_RESULT.json于13:30:21记录owner1458549变null，余额366358.20469999313仅该时历史snapshot；不是owncompleteFINAL/fee/lockqualification。不能据此伪造finalSHA/计数。START/FIRST/BIND已消费，训练不restart/hotpatch/再launch。冻结INDEX389SHA57fa0b19306db14a451fcbf1efe272beb8304f68c1c907bc6b3d13cd7aa9411c/workerSHAd1e7277ab7c2910353ed0d1e1e486f7cf65a6925fdc499272f9f8afa7415323e保持。

下一唯一unused399收尾恢复目录={C.as_posix()}，TASK399_FROZEN.json/INDEX399_RECOVERY_SOURCE_TASK_CALLER_FROZEN.json SHA {H(C/'INDEX399_RECOVERY_SOURCE_TASK_CALLER_FROZEN.json')}。脚本collect399_original389_closed_final_once.py，新purpose首次收回原389closedfinal，不重跑原normal389；freshbroadlocalCIM先记录再assert/Windows路径归一化，原exactowner/go/node/final/segments/locks准入保持，不放行其它controller。0新GO/优化/账写。命令Python314 -B -X utf8 {(C/'collect399_original389_closed_final_once.py').as_posix()} --root-lease-label ROOT399_EXCLUSIVE_NORMAL900_RECOVERY_unique --auth-provider C:/Users/lulu/Desktop/claude/mjcf/MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py --additional-control-pattern 'MOD4_H1|RMPOLAR|collect_generic_training_pair|PAIR2|PAIR3|PAIR4|watch_|postround' --caller-index-SHA {H(C/'INDEX399_RECOVERY_SOURCE_TASK_CALLER_FROZEN.json')}。先查ROOT399_NORMAL900_RECOVERY_ONCE_CONSUMED和ROOT389_COMPLETE_FINALS_OR_PARTIALS_ORIGINAL_COST_RETURNED_ACTUAL，已消费只读不得重放。

本轮资源实际另聊天Pair2持唯一canonical两卡：local42604/create2026-11-02T13:39:59.877578+08，F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/POSTTRAIN_EIGHT_EXCLUDING_H1_20261102/collect_generic_training_pair_once.py --pair2保持SSH；parent1462128/create1793597883.97，job={dispatch['root']}。实际E2GO13:38:05.109651/Curb113GO13:38:06.224455，原SAVE14:38:05/06、NOMINAL14:43:05/06，max20updates可能提前完整保存退出。先读该目录PAIR2_GENERIC_V2_LATEST_CLOSED_RESULT_PATH.json、reports最新terminal和后续Pair3/4dispatch；活controller只读本地，不新SSH/第二watcher/抢锁/kill/clearactive，也不烧399once。全knownactualreleased后freshLOCAL广范围exactCIM包括MOD4_H1/RMPOLAR/watch/run_once_after_resume/E1collect/prepare_archive/single_gpu/collect_nine/collect_generic_training_pair/PAIR等，并serialFREE，才执行unused399；parent再freshCNone/private/shared准入。不能因另一GPU闲绕共享锁。

399成功正式fulltransfer且原owner/nodelocks/账fullclose通过后，用原尚未消费CPU389在CPU环境Python C:/Users/lulu/miniconda3/envs/env_isaaclab/python.exe -B -X utf8 {(N/'review389_NEW_final_whole_CPU_UNUSED_once.py').as_posix()} 单次新final完整decode，offset52636/9696/16879，teacher17Adam42940/STD/三Adam/EMA/normRNG/originactor都核。未取得qualifiedformal不跑CPU。CPU389已消费则不重跑。

随后独立unused400评测目录={E.as_posix()}，准备INDEXSHA{H(E/'INDEX400_UNUSED_EVALUATION_PREPARATION_FROZEN.json')}；Python314执行bind400_actual_final_identity_once.py生成真实finalTASK400/INDEX400_SOURCE_TASK_CALLERS_FROZEN.json，再run400_eval_once.py --caller-index-SHA实际INDEXSHA，直接caller无ownwatchparent，必须freshallknownCIM/serialFREE/CNone/private/shared准入。80firstepisodes/400controls8s/seed9137新DR/同fixededge.8/270，finalRLactor+savedorigin同checkpoint一次decode+固定命令前馈，无onlineMPC/训练/优化/账写。400是第一次final389技能评测，不是重放396。成功返回立即render400_recorded_frames.py有限已记录bodypose0NN/0physics，currentmodel view_image {E.as_posix()}/RECORDED400_NATIVE_FRAMES/ACTUAL400_RL_BODY_POSE_SEQUENCE.png，读取实际RL误差/寿命/终止/整轮clear/topmanifold后主动修复或合理续训，不只报结束。若新有限任务失败保留once并独立版本修复，不消费重放。收尾/评测活controller期间仅本地读。

方法389固定347processed电机位置/轮速50Hz前馈+1*tanh(actor103-origin103同input)RL残差，无在线MPC/力矩cloning；actor103=35proprio9depth59plannedreference、critic106仍非depth-only。完整恢复final324SHA841dd4080ae41558645f98f1105652517716772b8b1f177df8cf8af89a0cc050/actorAdam52636critic9696WM16879/teacher17Adam42940STD/三AdamEMA/normRNG，freshplanned347fullstate+actualqheldqueue+3IMUcache/resetfullD0-D7。ownWMH32/actorH8directsameweightedcost/5 terminal0，criticactualownTDHuberEMA.01/exp(-cost/5)保留。FIRST64controls/Pi1critic1/newWM33total16912/gradient.905439913terminal0/native24/首完整32800939B SHA09b5d743a92ff8859c88e995229923bf6c31ab6667ada6e42c53923685b12ec9不是final/技能评测。旧324已closeCPU609finite/339实际0of80已原生审，345unused不启动；传统373377不算RL毕业。

成功仍firstflight整轮rearfootprint越沿、双轮实际400Hzsolver台顶manifold、无回地面/退沿、vxy/vz<=.03m/s rollpitch10deg yaw.2rad连续.5s。loss/COM/腾空/leadingedge不毕业。物理400Nengineeringk2000/50policy100feedback400physics2.5msTGS32-4/fullD0whitev3D1-D7/10mm单envclosure/.01mimic/原PD/DCclip/queue/solver/historicalH1exactproducer保持，不能暗换newMOD4v1/称新专家毕业，84x48camera暂定非D435i标定FPS。原唯一canonical3900/save3600/exit300strictreserve不grant/copy/refund/clearactive/第二writer。futureactualdepth/GTmap不进imagination。禁Luna/OpenRouter/unknownPID或GPUscan/kill，凭据仅原memory不输出Git；SSHfinallyclosed/SESSIONrestored/FREE。

所有source/false/raw/once/396localrefusal/399400unused/401workorder/automation入Git同phase mod4-residual-rl389-command-handoff ordinarysupplement402；已record393trialobject4e77ba7807787c22df7e8661c2f7801042cfc896/peel938b9ee8458f09a47e369995c8bfb1064b052a1f，398mainf0705ed2366481a6c512449afa9a513a173980a1。查402实际commit/remote，已commit不record/retag，push失败续existingobjects。全部历史tags/peels及lqr5848b45a99b8c32af02eb61b507c3f95ab39e4ad保护。PT/NPZ/USD/media仅实际pathbytes已有SHA，不为归档读模型/跑physics；postGit验证只工具输出，不追HEAD报告循环。'''
cfg=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text('utf8'))
request=dict(id=cfg['id'],mode='update',kind=cfg['kind'],name=cfg['name'],prompt=prompt,
    status=cfg['status'],rrule=cfg['rrule'],targetThreadId=cfg['target_thread_id'])
put(R/'AUTOMATION401_RECOVERY399_EVAL400_UPDATE_REQUEST.json',request)
print(json.dumps(dict(passed=True,workorder=str(work),request=str(R/'AUTOMATION401_RECOVERY399_EVAL400_UPDATE_REQUEST.json'),
    resourcebusy=bool(others),newSSH=0,modelreads=0,actualskillnotyetevaluated=True)))
