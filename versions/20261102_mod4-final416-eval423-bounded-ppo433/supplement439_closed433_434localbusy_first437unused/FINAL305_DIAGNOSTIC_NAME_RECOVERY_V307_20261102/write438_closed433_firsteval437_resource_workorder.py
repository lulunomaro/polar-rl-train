"""Local-only actual final433 closure/refusal/resource handoff; no SSH or model read."""
from pathlib import Path
import hashlib
import json
import subprocess
import time
import tomllib

P = Path(__file__).resolve().parent
T = P.parent
R = P / 'reports'
N = T / 'RL_BOUNDED_ACTUAL_PPO_PRODUCTION_V433_20261102'
E = T / 'RL433_FIRST_ACTUAL_INDEPENDENT_EVAL_V437_20261102'
OTHER = Path('F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102')
H = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
read = lambda path: json.loads(path.read_bytes())


def put(path, value):
    with path.open('x', encoding='utf8') as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False, allow_nan=False)


pattern = 'MOD4_H1|RMPOLAR|watch_|run_once_after_resume|E1collect|prepare_archive|single_gpu|collect_nine|collect_generic|collect_actual|PAIR|postround'
query = "Get-CimInstance Win32_Process -Filter \"Name='python.exe' OR Name='ssh.exe'\" | Where-Object { $_.CommandLine -match '" + pattern + "' } | Select-Object ProcessId,ParentProcessId,CreationDate,ExecutablePath,CommandLine | ConvertTo-Json -Depth 5 -Compress"
process = subprocess.run(['pwsh.exe', '-NoProfile', '-Command', query], capture_output=True, text=True, encoding='utf8', check=True)
assert not process.stderr.strip()
rows = json.loads(process.stdout) if process.stdout.strip() else []
rows = rows if isinstance(rows, list) else [rows]
import os
other_rows = [row for row in rows if row['ProcessId'] != os.getpid()]
local = dict(epoch=time.time(), exactCIM=rows, other_known_controllers=other_rows,
             serialFREE=not other_rows, SSH=0, network=0, no_second_watcher=True)
local_path = R / 'ACTUAL438_FRESH_LOCAL_KNOWN_CONTROLLERS.json'
put(local_path, local)
pointer_path = OTHER / 'SUPERMIMIC_EIGHT_V1_LATEST_METADATA_WATCH.json'
pointer = read(pointer_path)
current_path = Path(pointer['current'])
metadata = read(current_path)
current = metadata['parent_current']
resource = dict(epoch=time.time(), pointer_path=str(pointer_path), pointer=pointer,
                current_path=str(current_path), current_bytes=current_path.stat().st_size,
                metadata_epoch=metadata['epoch'], parent_current=current,
                parent_exit=metadata['parent_exit'], parent_error=metadata['parent_error'],
                local_known_controllers=other_rows, original_resource_wait=metadata.get('original_resource_wait'),
                independent_scope_canonical_snapshot_not_realtime=True, local_reads_only=True,
                full_metadata_not_republished_modelbytes_not_read=True)
resource_path = R / 'ACTUAL438_OTHER_ORIGINAL_SUPERMIMIC_RESOURCE_LOCAL_SNAPSHOT.json'
put(resource_path, resource)
closed_path = N / 'reports/ROOT433_COMPLETE_FINALS_OR_PARTIALS_ORIGINAL_COST_RETURNED_ACTUAL.json'
complete = read(closed_path)
normal_path = N / 'reports/ROOT433_NORMAL900_RECOVERY_JUMP_FULL_UTF8_AND_FORMAL_ACTUAL.json'
normal = read(normal_path)
cpu_path = N / 'reports/ROOT433_NEW_FINAL_WHOLE_CPU_RETURNED_ACTUAL.json'
cpu = read(cpu_path)
ssh_path = N / 'reports/ROOT433_NORMAL900_RECOVERY_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json'
assert complete['owner_closed']['canonical_None'] and complete['owner_closed']['shared_locks_free']
assert normal['original_node_exit']['all_own_children_waited'] and cpu['passed']
assert cpu['Pi'] == 161 and cpu['finite_tensors'] == 795
assert cpu['SHA'] == 'db6944ceca539106bb392a881185f1e85917efa5a9325bbeec72863f8240e04f'
index = E / 'INDEX437_SOURCE_TASK_CALLERS_FROZEN.json'
assert H(index) == '6c19b209a3e9f44c7153cbcb7794d73e839048fb67b66e46befa42f237c4500f'
assert not (E / 'reports/ROOT437_ONCE_CONSUMED_BEFORE_NETWORK.json').exists()
final = normal['final']
frozen_task = read(E / 'TASK437_FROZEN.json')
old_eval = T / 'RL433_FINAL_INDEPENDENT_EVAL_V434_20261102'
refusal = list((old_eval / 'reports').glob('ROOT434_ORIGINAL_ERROR_*.json'))
assert len(refusal) == 1 and 'assert not other' in read(refusal[0])['error']
work_path = R / 'CURRENT_ACTUAL438_FINAL433_CLOSED_434_LOCALBUSY_FIRST437_UNUSED_RESOURCE_WORK_ORDER_V1.json'
work = dict(epoch=time.time(), kind='FINAL433_CLOSED_FIRST_ACTUAL437_EVAL_UNUSED_RESOURCE_WAIT',
    latest_human='我需要的是rl上台阶', objective='RL actually jumps270mm and stablyrecovers; traditionalMPC is not delivery',
    supersedes='435 live433/434timer is historical;433fullclosedCPU795passed;434localbusy0network;437firstactualevalunused',
    final433=dict(modelSHA=cpu['SHA'], bytes=cpu['bytes'], final_model=complete['formals']['jump_72'],
        Pi=161, PPO=161, critic=161, newWM=5175, totalWM=30731, controls=5206, ownpairs=416480,
        actorAdam=56465, criticAdam=13525, teacher17Adam=42940, frozenSTD=True,
        allthreeAdam_EMA_normRNG_origin_complete=True, CPU=cpu,
        ownowner1474033_node1474042_worker1474057_closed=True, original_node_exit=normal['original_node_exit'],
        original_owner_closed=complete['owner_closed'], fee=3601.857589483261,
        historical_closingbalance=351806.0201497078, balance_not_current=True,
        allSSHclosed=read(ssh_path), normal_CPU_once_consumed_no_replay=True,
        receipts=[dict(path=str(path), bytes=path.stat().st_size, SHA=H(path)) for path in (closed_path, normal_path, cpu_path, ssh_path)],
        training_not_skill=dict(orientation_events=2645, timeouts=252,
            tracking_cost_last32=7.859204083681107, lastpostAdam=final['student']['actor_trust_step'])),
    original434=dict(refusal_path=str(refusal[0]), refusalSHA=H(refusal[0]), localCIMbusy=True,
        network=0, SDK=0, modelreads=0, physics=0, skill_result=None, not_zero_of80=True,
        originaltimer63108_closed=True, normal433_CPU433_already_succeeded=True,
        do_not_replay_434postround_normal_CPU_or_eval=True),
    first437=dict(root=str(E), task=str(E/'TASK437_FROZEN.json'), index=str(index), indexSHA=H(index),
        unused=True, modelSHA=cpu['SHA'], modelbytes=cpu['bytes'], expectedPi=161,
        CPU_receiptSHA=H(cpu_path), workerSHA=frozen_task['worker_SHA'],
        command=['C:/Users/lulu/AppData/Local/Programs/Python/Python314/python.exe','-B','-X','utf8',
                 str(E/'run437_eval_once.py'),'--caller-index-SHA',H(index)],
        protocol='80firstepisodes/400controls8s/seed9137/fixededge.8/270/newDR/actual400Hzmanifold',
        actor103='35proprio+9currentdepth+59plannedreference', critic106=True,
        fixed347processed50Hzfeedforward_plus_savedorigin_residual=True, onlineMPC=False, depthonly=False,
        copiedsource_and_data_exact=True, workerAST_same_under_namespace=True,
        no_new_checkpoint_decode_or_physics_at_preparation=True,
        result=str(E/'reports/ROOT437_EVALUATION_FULL_RETURNED.json'),
        replaytransfer=str(E/'reports/ROOT437_SELECTED_REPLAY_TRANSFERS.json'),
        image=str(E/'RECORDED437_NATIVE_FRAMES/ACTUAL437_RL_BODY_POSE_SEQUENCE.png'),
        renderer=str(E/'render437_recorded_frames.py'),
        execution_rule='FreshLOCALallknowncontrollersreleased/serialFREEthenunique437;parentfreshCNone/private/sharedadmission;finallySSHclosedSESSIONrestoreFREE',
        followup='Runfinite savedpose renderer then CURRENTMODELview_image; auditall80 wholeclear/topmanifold/strict .5s; decideandexecute targeted RL repairorjustifiedcontinuation',
        no_blind_433continuation_or_MPC_experiments=True),
    resource=dict(status='LOCAL_ONLY_RESOURCE_WAIT' if other_rows else 'LOCAL_SERIAL_FREE_REQUIRES_FRESH_PARENT_ADMISSION',
        snapshot=str(resource_path), freshCIM=str(local_path), other_known_controllers=other_rows,
        remote_originalroot=pointer['root'], metadata_epoch=metadata['epoch'], active_roles=[v['role'] for v in current.get('workers',{}).values()],
        pending_roles=current.get('pending_roles'), parent_exit=metadata['parent_exit'], no_new_waiter_or_SSH=True,
        release_required='ActualoriginalOWNER_EXIT/collectorclosedandfreshLOCALexactCIM; GPUidlenessdoesnotrelease sharedscope'),
    acceptance='Firstflightwholewheelrearfootprintclear/doublewheelactual400Hztopmanifold/nogroundedge_return/vxyvz<=.03m_s/rollpitch<=10deg/yaw<=.2rad/continuous>=.5s',
    physics='400Nengineeringk2000/50policy100feedback400physics/.0025TGS32-4/fullD0whitev3D1-D7/10mmperenvclosure/.01mimic/originalPD_DCclip_queue_solver/historicalH1exactproducer',
    budget='Originalsolecanonical3900/save3600/exit300strictreserve; no grantrefundcopyclearactiveorsecondwriter',
    historical='416actual4230of80allorientationmean.812nativeviewed;389actual404and407both0strictnativeviewed;345unusedno_start',
    native='Onlycurrentmodelnativevision,noLunaOpenRouter;84x48provisionalnotD435ihardwarecalibrationFPS',
    reader_tool_errors='Thisturnwrongcwdquery/missinghistoricalpreparefilename/oversizedrgpathsubstringmatcheswere readonly;correctactualfileslocated;noSDKmodelphysicsnetworksideeffects',
    next='Readfirst437results/onceandcurrentresource;whileknowncontrolleralive localonly. Onreleasefreshadmission runfirst437once,render/nativeauditthenproactiveRLdecision.',
    git=dict(phase='mod4-final416-eval423-bounded-ppo433', record436_done=True,
        tag='trial-20261102-mod4-final416-eval423-bounded-ppo433',
        tagobject='1b309d3b6fa4a8fa41496956df61f116bae2b6ab', peel='1044a69fef42ace2dee82f2dcb229538dc029a9b',
        ordinarysupplement439=True, do_not_record_or_retag=True, protect_alltags=True,
        lqr='5848b45a99b8c32af02eb61b507c3f95ab39e4ad', no_binaryreads_for_Git=True))
put(work_path, work)
cfg = tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text('utf8'))
prompt = f'''每小时继续本聊天MOD4跳270mm。人类明确“我需要的是rl上台阶”，交付为RL实际跳台并稳定，传统MPC不是交付。已授权新跟踪启动/继续看收尾然后修复。完整保存安全退出后立即独立RL评测和真实姿态回放，当前模型原生view_image审图/核manifold，再按证据主动定向修复或合理续训，不等催促，不原样续退化任务。保持ACTIVE/currentchat，不新Goal/chat/重复automation；无变化或不可行动静默，只通知实质进展、失败、完成、资源预算网络问题和必需用户行动。

首先读 {work_path.as_posix()}。实际冻结source/INDEX/ownreceipt/确切进程/结果优先。旧435live433/434timer过时。433已完整保存安全关闭/正式传回/CPU795finite通过，434只本地knowncontroller忙拒绝，0network/SDK/model/physics，不能写0/80技能失败。433从未完成实际独立评测。normal433/CPU433/434timer消费，绝不重放launch433/FIRST/bind/normal/CPU/postround434或run434。

final433=34402073B SHA{cpu['SHA']}，PPO=Pi=critic161/newWM5175total30731，5206controls416480ownpairs，actorAdam56465critic13525/WM30731、三Adam/teacher17Adam42940STD/EMA/normRNG/savedorigin完整。原owner1474033/create1793612811.2、node1474042/create1793612811.63、worker1474057/create1793612817.79已ownwaited，原private/shared released/SSHclosedSESSIONrestoredFREE。fee3601.857589483261s/closingbalance351806.0201497078s仅历史snapshot非实时。最终路径和完整回执见438，不为归档重读PT/重复验模。

唯一新独立437准备完成但unused：root={E.as_posix()}，INDEX437SHA={H(index)}。TASK437读取同final433一次actor+savedorigin、expectedPi161、CPUreceiptSHA={H(cpu_path)}。调用Python314 -B -X utf8 {str(E/'run437_eval_once.py').replace(chr(92),'/')} --caller-index-SHA {H(index)}。冻结源码与前馈/参考逐字节复用434，worker AST仅可逆namespace，index排除自身，原物理/动作/验收不改。先查ROOT437_ONCE_CONSUMED_BEFORE_NETWORK/ROOT437_EVALUATION_FULL_RETURNED及现有controller；已消费不重放。资源活着不烧437once/不加watcher或SSH。

当前阻塞另聊天SUPERMIMIC8原metadata collector PID65008/create2026-11-02T18:45:27.59644+08，Python314 -B F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/collect_actual_supermimic_run_metadata_once.py，parent55868。先读该目录SUPERMIMIC_EIGHT_V1_LATEST_METADATA_WATCH.json指向的CURRENT_METADATA和LATEST_CLOSED_RESULT_PATH。438时originalroot={pointer['root']}，E0/E2真实在训且后续6项pending，无OWNER_EXIT。活controller仅本地读，不第二watcher/SSH/抢锁/清active/kill/另GPU绕共享锁。只有actualoriginalOWNER_EXIT+collectorclosed且freshLOCAL广exactknownCIM/serialFREE后执行437；parent仍须freshCNone/private/shared原准入。freshCIM含MOD4_H1/RMPOLAR/watch/run_once_after_resume/E1collect/prepare_archive/single_gpu/collect_nine/collect_generic/collect_actual/PAIR及所有新collector。凭据只原memory不输出Git，finallySSHclosed/SESSIONrestored/FREE。

437是第一次实际final433 RL技能评测：80firstepisodes/400controls8s/seed9137同fixededge.8/270新DR，actor103=35proprio9currentdepth59plannedreference/critic106，347已保存processed50Hz电机前馈+1*tanh(actor-origin)，无onlineMPC/接管/力矩cloning，非自主depth-only。433训练是实际onpolicyPPO32controls2560samples/oneepochclip.2/gamma.99GAE.95/std.15，actualreward=exp(-同weightedtrackingcost/5)与done入actor，WMH32独立无actorWMgradient；每次postAdammeanKL<=.01/maxnormalizeddelta<=.05，完整还原拒绝proposalweightsAdam，只commit一次acceptedstep。该算法修复尚未经独立技能验证，2645orientation252timeouts只是训练重复episode，不能当80评测。

437结果={str(E/'reports/ROOT437_EVALUATION_FULL_RETURNED.json').replace(chr(92),'/')}，replay=ROOT437_SELECTED_REPLAY_TRANSFERS.json。安全关闭释放后运行有限{str(E/'render437_recorded_frames.py').replace(chr(92),'/')}，0NN/0新physics从真实bodyposes渲染；图={str(E/'RECORDED437_NATIVE_FRAMES/ACTUAL437_RL_BODY_POSE_SEQUENCE.png').replace(chr(92),'/')}。当前模型必须view_image原生审真实姿态，并读保存all80/manifold/motor/residual。严格成功首次飞行整轮rearfootprint越沿、双轮实际400Hz台顶manifold、无回地面退沿，vxy/vz<=.03m_s、rollpitch<=10deg/yaw<=.2rad连续>=.5s。loss/COM/腾空/leadingedge不毕业。按实际结果主动定向RL修复或合理续训，不只报结束、不接连传统控制实验。

历史416完整关闭/CPU747finite/actual423已完成0/80strict0wholeclear0leading80orientation0full8s/mean.812s；已原生审四case台前倾倒。389已完整关闭618finite/actual404及matched407都0strict已审。345仍unused不启动。417selfindex0network、426CUDAcpuRNG/427frozenSTDfixturefalse、428pass/429unused路径错误/431stalecontractpreSDKfalse、434localbusy原source/index/rawfalse/once全部保留不回写，不重放。

物理400Nengineeringk2000/50policy100feedback400physics2.5msTGS32-4/fullD0whitev3D1-D7/10mm单envclosure/.01mimic/原PD_DCclip_queue_solver/historicalH1exactproducer保持，不暗换newMOD4v1或冒称专家适配毕业；84x48暂定camera非D435i实机标定FPS。未来actualdepth/GTmap不入imagination。唯一原canonical3900save3600exit300strictreserve不grant/copy/refund/clearactive/第二writer。禁Luna/OpenRouter/unknownPID或GPUscan/kill，只当前模型原生视觉。

全部source/report/rawfalse/once/433close795CPU/434localbusy/437unused/438resourcehandoff/automation按根repoAGENTS与polar-rl-train/docs/ALL_TRIALS_AND_REPORTS_GIT_POLICY.md归档。同phase mod4-final416-eval423-bounded-ppo433已record436：trialobject1b309d3b6fa4a8fa41496956df61f116bae2b6ab/peel1044a69fef42ace2dee82f2dcb229538dc029a9b；本轮ordinarysupplement439，查实际commit/remote，不重record/retag，push失败续existingobjects。保护全部历史tags/peels及lqr5848b45a99b8c32af02eb61b507c3f95ab39e4ad。PT/NPZ/USD/media仅actualpathbytes已有SHA，不为归档读模型/跑physics；postGit验证只工具输出，不追HEAD报告循环。'''
request = dict(id=cfg['id'], mode='update', kind=cfg['kind'], name=cfg['name'], prompt=prompt,
               rrule=cfg['rrule'], status=cfg['status'], targetThreadId=cfg['target_thread_id'], destination='thread')
if 'notification_policy' in cfg:
    request['notificationPolicy'] = cfg['notification_policy']
put(R / 'AUTOMATION438_CLOSED433_FIRST437_RESOURCE_REQUEST.json', request)
print(json.dumps(dict(passed=True, workorder=str(work_path), request=str(R/'AUTOMATION438_CLOSED433_FIRST437_RESOURCE_REQUEST.json'),
                     other_controllers=[row['ProcessId'] for row in other_rows], modelreads=0, SDK=0, physics=0, SSH=0)), flush=True)
