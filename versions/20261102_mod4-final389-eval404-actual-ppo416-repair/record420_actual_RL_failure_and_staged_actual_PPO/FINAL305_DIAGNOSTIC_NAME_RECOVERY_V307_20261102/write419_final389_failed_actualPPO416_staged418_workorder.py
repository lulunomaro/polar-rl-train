"""Actual closed389 evaluation and newactualPPO416staged/418pending resource handoff."""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import time
import tomllib

P=Path(__file__).resolve().parent;T=P.parent;R=P/'reports'
N=T/'RL_ACTUAL_RESIDUAL_PPO_PRODUCTION_V416_20261102'
C=T/'RL416_STAGED_FIRST_OWNER_RECOVERY_V418_20261102'
Q=T/'RL416_SINGLE_PROCESS_POSTROUND_V417_20261102'
E=T/'RL416_FINAL_INDEPENDENT_EVAL_V417_20261102'
F=Path('F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/POSTTRAIN_EIGHT_EXCLUDING_H1_20261102')
read=lambda path:json.loads(path.read_bytes())
H=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
def put(path,value):
 with path.open('x',encoding='utf8')as stream:json.dump(value,stream,indent=2,ensure_ascii=False,allow_nan=False)
task=read(N/'TASK416_FROZEN.json');final=read(T/'MPC_COMMAND_RESIDUAL_RL_V389_20261102/reports/ROOT389_NEW_FINAL_WHOLE_CPU_RETURNED_ACTUAL.json')
facts=read(R/'ANALYSIS405_ACTUAL_FINAL389_EVAL404_FACTS_AND_MANIFOLD.json')
contrast=read(R/'ANALYSIS408_ACTUAL407_RL_MATCHED_RESIDUAL_SCALE_FACTS.json')
cpu=read(T/'RL_ACTUAL_TRANSITION_PPO_REPAIR_V409_20261102/reports/CPU409_REAL_TRANSITION_RL_NO_STEP_ADMISSION.json')
dispatch=read(F/'PAIR4_GENERIC_V2_ORIGINAL_OWNER_DISPATCH_ONCE.json')
query="Get-CimInstance Win32_Process -Filter \"Name='python.exe' OR Name='ssh.exe'\" | Where-Object { $_.CommandLine -match 'MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021|RMPOLAR|watch_|collect_generic|run_once_after_resume|prepare_archive|single_gpu|collect_nine|collect_e1|E1_actual|PAIR1|PAIR2|PAIR3|PAIR4' } | Select-Object ProcessId,CreationDate,ExecutablePath,CommandLine | ConvertTo-Json -Compress"
out=subprocess.run(['pwsh.exe','-NoProfile','-Command',query],capture_output=True,text=True,encoding='utf8',check=True)
rows=json.loads(out.stdout)if out.stdout.strip()else[];rows=rows if isinstance(rows,list)else[rows]
others=[row for row in rows if row['ProcessId']!=os.getpid()]
assert not(N/'reports/ROOT416_ORIGINAL_OWNER_LAUNCH_ACTUAL.json').exists()
assert not(N/'reports/ROOT416_ORIGINAL_NODE_LAUNCH_ACTUAL.json').exists()
assert not(N/'reports/ROOT418_STAGED_FIRST_OWNER_ONCE_CONSUMED.json').exists()
work=R/'CURRENT_ACTUAL419_FINAL389_EVAL404_FAIL_REALPPO416_STAGED418_WAIT_WORK_ORDER_V1.json'
value=dict(epoch=time.time(),kind='CURRENT_ACTUAL419_FINAL389_EVALDONE0OF80_REALPPO416STAGED_FIRSTOWNER418UNUSED',
 latest_human='我需要的是rl上台阶',objective='LearnedRLactuallyup270andstable;traditionalMPCnotdelivery',
 final389=dict(closed=True,normal399_consumed=True,CPU389_consumed=True,fullCPU=final,
  controls=3571,ownpairs=285680,Pi=3508,critic=3508,newWM=3540,totalWM=20419,actorAdam=56144,criticAdam=13204,
  fee_seconds=3603.927095413208,closing_balance_snapshot=364018.99313402176,snapshot_not_current=True),
 actual404=facts,actual407=contrast,
 native_review=dict(actual404viewed=True,actual407viewed=True,
  actual404image=str(T/'RL389_EXACT_FINAL_INDEPENDENT_EVAL_V404_20261102/RECORDED404_NATIVE_FRAMES/ACTUAL404_RL_BODY_POSE_SEQUENCE.png'),
  actual407image=str(T/'RL389_MATCHED_RESIDUAL_SCALE_DIAG_V407_20261102/RECORDED407_NATIVE_FRAMES/ACTUAL407_RL_BODY_POSE_SEQUENCE.png'),
  observation='Selected4inboth actualsequences tip stronglyaround.8-1.0sbeforetoplanding;80resultseparately measured',
  training_skill=False),
 decision='Do notrepeat389imaginedH8actororquarterresidual:0strictin404andboth407groups. NewactualtransitionPPO lets actualreward/done trainactor; preservephysical/reward/fullstate.',
 CPU409=cpu,
 actual416=dict(root=str(N),run=task['run_id'],taskSHA=H(N/'TASK416_FROZEN.json'),
  INDEX_SHA=H(N/'INDEX416_SOURCE_TASK_CALLERS_FROZEN.json'),workerSHA=task['worker_SHA'],GPU=task['GPU_UUID'],
  sourcefinalSHA=task['model_SHA'],source_offsets=[56144,13204,20419],
  sourceCPU409learnerSHA=cpu['learnerSHA'],learnerbyteexact=True,
  algorithm='ActualownonpolicyGaussianlatentresidualPPO;32controls2560samples,oneepoch,clip.2,gamma.99lambda.95,latentstd.15; actualreward/doneGAE; actornoWMgradient',
  actorSTD_teacher17Adam_frozen=True,fullsaved389origin_preserved=True,
  actor103critic106=True,plannedreference59_notdepthonly=True,WM20419trainedseparately=True,
  reward='Unchangedexp(-sameweightedtrackingcost/5)',
  physical='Unchanged400Nengineeringk2000/50policy100feedback400physics/.0025TGS32-4/fullD0-D7/10mmclosure/.01mimic',
  freshphysicalDRqueue_replay=True,
  originallaunch416_consumed=True,staged_source_exact=True,
  namespace=task['job_root'],ownerroot=task['owner_root'],
  first_CNone=True,firstGPU_private_shared_admitted=True,
  second_fresh_CNone_beforeowner_refused=True,
  originalerror=read(N/'reports/ROOT416_START_ORIGINAL_CALLER_ERROR_1793602324719070900.json'),
  owner_created=False,node_created=False,GO=False,SDK=False,modelreads=0,
  original416_no_replay=True,SSHfinallyclosed=read(N/'reports/ROOT416_START_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json')),
 recovery418=dict(root=str(C),unused=True,
  task=str(C/'TASK418_FROZEN.json'),INDEX_SHA=H(C/'INDEX418_STAGED_OWNER_RECOVERY_FROZEN.json'),
  script=str(C/'finish418_staged416_first_original_owner_once.py'),
  scope='Onlyfirstowner/nodeofexactalready-staged416afteractualallresourcesreleased;freshCNone/noowner-node-GOandmanifestverify/reselectedresources/secondCNone',
  forbidden='Do notrerunlaunch416/redecodeCPU409 or duplicateowner; consumed418notreplay'),
 postround417=dict(root=str(Q),indexSHA=H(Q/'INDEX417_POSTROUND_FOR416_FROZEN.json'),
  started=False,bind=str(Q/'bind417_actual_FIRST_and_launch_once.py'),
  script=str(Q/'postround417_close_actual416_eval_once.py'),
  scope='AfteractualFIRSTfullsave/realPPOgrad/native24,one localtimer. Sameprocessrunpy normaland eval toavoidownparentCIMconflict; locallywaitothers beforeSSH.',
  evalroot=str(E),actualeval='80firstepisodes/400controls/9137newDR/fixededge.8/270/manifoldandbodyposerender',
  result=str(N/'reports/POSTROUND416_RL_REPLAY_EVAL_DECISION.json')),
 resource=dict(local_exact_CIM=rows,others=others,serialFREE=False if others else 'recheckbeforefiniteSSH',
  pair4dispatch=dispatch,localcontrollerPID=66532,localcontrollercreate='2026-11-02T14:52:23.889806+08:00',
  readlocalfirst=str(F/'PAIR4_GENERIC_V2_LATEST_CLOSED_RESULT_PATH.json'),
  do_not_infer_actual_GO_fromdispatch=True,no_secondwatcher=True),
 failures_preserved=['396localCIMbeforeSSH','399independentfinalcollectionsuccess','400SDKmissingwheelhelper0PT0control',
  '403localCIMbusy0network;globalversionreplacementfeedforwardcorruptionidentified0model',
  '404exactdatafirstactualRLskill0of80','407matchedscalephysical0of80','410partialunused','414byteSHAlineendingsunused',
  '416stagedthenauthorityracebeforeowner0GO','418unusedfirstownerrecovery'],
 next='ReadlocalPair4release andallknownexactCIM;oncefree executeuniqueunused418withpinnedindex,collect416FIRST_UPDATEDonceandbind417onlyafterrealupdate/fullsave. Ifstillbusylocalonly/Git;notrainingGOclaimed.',
 acceptance='firstflightwholewheelrearfootprintclear/actualdoublewheeltopmanifold/.03m_svxyvz/10degrollpitch/.2yaw/continuous.5s/noreturngroundoredge',
 budget='Originalsolecanonical3900save3600exit300strictreserve;nograntcopyrefundclearactiveorsecondwriter',
 git=dict(previousRLphase='mod4-residual-rl389-command-handoff',record393object='4e77ba7807787c22df7e8661c2f7801042cfc896',record393peel='938b9ee8458f09a47e369995c8bfb1064b052a1f',
  supplement398='f0705ed2366481a6c512449afa9a513a173980a1',newphase='mod4-final389-eval404-actual-ppo416-repair',
  record420='Checkactualonce/tagobjects;uniqueannotatedtrialfornewactualRLrepairphase,thenordinarysupplementonly',
  lqr='5848b45a99b8c32af02eb61b507c3f95ab39e4ad'))
put(work,value)
prompt=f'''每小时继续本聊天MOD4跳270mm。人类明确“我需要的是rl上台阶”，交付为RL实际跳台稳定，传统MPC成功不是交付。已授权新跟踪启动/继续看收尾然后修复。完整保存安全退出后立即独立RL评测/实际姿态回放，按证据主动定向修复或合理续训。不新Goal/chat/重复automation，保持ACTIVE/currentchat；无变化不可行动静默，只通知实质进展、失败、完成、资源/预算/网络问题和必需用户行动。

首先读 {work.as_posix()}。实际文件/冻结INDEX/ownreceipt/确切进程优先。旧397389live和401399unused已过时。389已完整结束，399独立首次正式传回成功，新CPU389单次decode618finite通过。final32801003B SHA{final['SHA']}，Pi3508critic3508/newWM3540total20419，3571controls285680ownpairs，actorAdam56144critic13204/WM20419、teacher17Adam42940STD/EMA/normRNG/origin完整。原owner1458549/node1458558/worker1458572ownwaited/锁free/原fee3603.927095413208s，closingbalance364018.99313402176仅历史snapshot。normal399/CPU389已消费，不再读PT归档或验模。

389独立实际404已完成80firstepisodes/400controls8s/seed9137新DR同fixededge.8/270：0/80strict、0wholefootprintclear、6leadingedgeprogress、77orientation、3full8s、mean1.375s。不是待评测；当前模型已原生view_image实际pose图，4cases台前.9-.98s腾空倾倒。有限407同finalactorfullresidualvsquarter40matchedDRpairs已完成：full0strict0wholeclear/1leading/36orientation4full8smean1.7055，quarter0strict1wholeclear/8leading/39orientation1full8smean1.121；全actualbackendDR/initialq/dq/root/policy配对0差，depth最大1.97e-6。不是逐位同contactplant，quarter不是修好。407原生回放已审。两者allownwaited/locksreleased/SSHclosedSESSIONrestoreFREE，所有consumed永不重跑。

定向修复是新actualonpolicy残差PPO。389actor只有imaginedH8trackinggradient，实际r/done只入critic且actor无terminalvalue，因此不能把critic真TD称actor已学真实终止。新CPU409必要final389一次读：actor/critic/三Adam/EMA/origin/teacherSTD完整恢复56144/13204/20419，无step，actualPPO2560synthetic样本actorgrad13.79187/critic3.21039有限非零，terminalGAE returns.6/100无nextbootstrap、WM与origin无actorgrad。只是CPU无step准入，尚非物理技能通过。新生产416 actor仍103=35proprio9currentdepth59plannedreference/critic106，固定347processed50Hz前馈+1*tanh(actor-origin)；保留saved389origin、不reset网络/Adam，latentGaussianstd.15固定且原learnedSTD冻结，32controls/2560samples一epochPPOclip.2 gamma.99 GAE.95，实际同exp(-weightedtrackingcost/5)和done入actor，WMH32仍原训练但无actorWMgradient，无onlineMPC/力矩cloning，非depth-only。physics/DR/reward/acceptance不改。

416生产目录={N.as_posix()}，run={task['run_id']}，TASK416_FROZEN.json/INDEX416_SOURCE_TASK_CALLERS_FROZEN.json SHA{H(N/'INDEX416_SOURCE_TASK_CALLERS_FROZEN.json')}，workerSHA{task['worker_SHA']}，GPU={task['GPU_UUID']}。CPU409learner字节SHA{cpu['learnerSHA']}准确复用，无新PT读。launch416已消费并真实将源码/Task/前馈/控制完整部署且postcopy核通过，第一freshCNone和资源通过；2026-11-02 14:52:04第二freshCNone在owner创建前被拒绝，因为另一聊天Pair4刚claim。416无owner/node/GO/SDK/模型读取，不能说训练中，也不能重跑launch416或重造训练namespace。原错误/once/部署全部保留。

唯一unused418恢复只完成尚未发生的首次owner/node创建：root={C.as_posix()}，TASK418_FROZEN.json/INDEX418_STAGED_OWNER_RECOVERY_FROZEN.json SHA{H(C/'INDEX418_STAGED_OWNER_RECOVERY_FROZEN.json')}；Python314 -B -X utf8 {(C/'finish418_staged416_first_original_owner_once.py').as_posix()} --caller-index-SHA {H(C/'INDEX418_STAGED_OWNER_RECOVERY_FROZEN.json')}。先查ROOT418_STAGED_FIRST_OWNER_ONCE_CONSUMED、ROOT416_ORIGINAL_OWNER_LAUNCH_ACTUAL/node/现有GO；已消费不重放。418先freshLOCALexactCIM只有自身/serialFREE，再freshCNone、原stagedmanifest+Task完整/无owner-node-GO、原GPUprivate/shared资源/第二CNone，随后唯一原owner/node。0训练模型读取由parent；worker首次source读取按原准入。不得热改416或复制canonical/第二writer。

当前资源另聊天Pair4 W35+SLOPE_INDEPENDENT50：localcollectorPID66532/create2026-11-02T14:52:23.889806+08，F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/POSTTRAIN_EIGHT_EXCLUDING_H1_20261102/collect_generic_training_pair_once.py --pair4保持SSH；parent1466964/create1793602319.06，remotejob{dispatch['root']}，dispatch14:51:59仅派发不是GO；需读最新actualGO/first/closed。先读该目录PAIR4_GENERIC_V2_LATEST_CLOSED_RESULT_PATH.json/reports与后续retentiondispatch。活controller只读本地，不SSH/第二watcher/抢锁/kill/清active，不烧418once。实际全knowncontroller释放后freshLOCAL广范围exactCIM含MOD4_H1/RMPOLAR/watch/run_once_after_resume/E1collect/prepare_archive/single_gpu/collect_nine/collect_generic/PAIR等且serialFREE才run418；不能用另一GPU闲绕共享锁。

416真实启动后只收collect416_status_readonly.py --label FIRST_UPDATED一次；确认actualPPO=Pi=critic1/2560onpolicy/actorgrad>0/WMnative24/首完整保存，再执行{(Q/'bind417_actual_FIRST_and_launch_once.py').as_posix()}绑定唯一postround417。冻结INDEX417SHA{H(Q/'INDEX417_POSTROUND_FOR416_FROZEN.json')}，scriptpostround417_close_actual416_eval_once.py，evalroot={E.as_posix()}。417同一个本地process经runpy正常收尾和evaldispatcher，避免396父子CIM互拒；timer到原normal900，若其它controller忙只localwait，原normal416fullsave/安全退出/fullformaltransfer/newCPUoffsets56144/13204/20419，再独立41780firstepisodes/400controls/seed9137same270新DR、actualmanifold/真实pose有限render。原3900save3600exit300窗口不变。结果416reports/POSTROUND416_RL_REPLAY_EVAL_DECISION.json，图evalroot/RECORDED417_NATIVE_FRAMES/ACTUAL417_RL_BODY_POSE_SEQUENCE.png。先查waiter/children/once/results，活着不重复normal/CPU/eval；结果出来currentmodel必须view_image原生审图和manifold，按真实RL结果主动修复/合理续训，不只报结束。

失败历史保留：396localCIM0network；400SDK缺wheel_geometry220，0checkpoint/control、已close；403localCIMbusy0network，且旧globalversionreplacement改前馈数字字节被静态识别；404逐字节训练source+feedforward和exacthelper修复后实际评测成功执行；410部分unused、414lineendingbyteSHA不符冻结unused，416复制CPU409原bytes复用通过；416authorityrace无GO，418unused。旧freeze/false/raw/once永不回写重放。345unused不启动，传统MPC不算RL毕业。

成功仍首次飞行整轮rearfootprint越沿/双轮真实400Hz台顶manifold/无回地面退沿/vxyvz.03m_s rollpitch10deg yaw.2rad连续.5s，loss/COM/腾空/leadingedge不毕业。保持400Nengineeringk2000/50policy100feedback400physics2.5msTGS32-4/fullD0whitev3D1-D7/10mm单envclosure/.01mimic/原PD/DCclip/queue/solver/historicalH1exactproducer，不暗换newMOD4v1也不冒称适配毕业；84x48camera暂定非D435i标定FPS。唯一原canonical/strictreserve无grant/copy/refund/clearactive/第二writer，未来actualdepth/GTmap不入imagination。禁Luna/OpenRouter/unknownPID或GPUscan/kill；凭据仅原memory不输出Git，SSHfinallyclosed/SESSIONrestored/FREE。

全部source/报告/原失败/raw/once/399close618CPU/400403拒绝/404407实际eval+native/409CPU/416stagedrace/418unused/419handoff/automation入Git新phase mod4-final389-eval404-actual-ppo416-repair，查RECORD420实际once/trialobjects；已record不重record/retag，后续ordinary补充，push失败续existingobjects。旧393trialobject4e77ba7807787c22df7e8661c2f7801042cfc896/peel938b9ee8458f09a47e369995c8bfb1064b052a1f、398mainf0705ed2366481a6c512449afa9a513a173980a1和全部旧tags/peels/lqr5848b45a99b8c32af02eb61b507c3f95ab39e4ad保护。PT/NPZ/USD/media仅actualpathbytes已有SHA，不为归档读模型/跑physics；postGit验证只工具输出不追HEAD循环。'''
cfg=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text('utf8'))
request=dict(id=cfg['id'],mode='update',kind=cfg['kind'],name=cfg['name'],prompt=prompt,status=cfg['status'],rrule=cfg['rrule'],targetThreadId=cfg['target_thread_id'])
put(R/'AUTOMATION419_FINAL389_EVAL_FAIL_ACTUALPPO416_STAGED418_REQUEST.json',request)
print(json.dumps(dict(passed=True,workorder=str(work),request=str(R/'AUTOMATION419_FINAL389_EVAL_FAIL_ACTUALPPO416_STAGED418_REQUEST.json'),RL389strict=0,new416GO=False,resourcebusy=bool(others))))
