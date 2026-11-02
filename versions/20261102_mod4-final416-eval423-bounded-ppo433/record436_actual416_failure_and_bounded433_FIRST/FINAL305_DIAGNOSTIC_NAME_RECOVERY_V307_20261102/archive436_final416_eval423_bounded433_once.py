"""Unique record436 for actual416failure and boundedactualPPO433repair, allerrorskept."""
from pathlib import Path
import hashlib,json,subprocess,sys,time,tomllib
P=Path(__file__).resolve().parent;T=P.parent;R=P/'reports';G=T.parent/'polar-rl-train'
ID='mod4-final416-eval423-bounded-ppo433';TAG='trial-20261102-'+ID
BASE=G/('versions/20261102_'+ID);V=BASE/'record436_actual416_failure_and_bounded433_FIRST'
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_bytes())
def put(p,v):
 with p.open('x',encoding='utf8')as f:json.dump(v,f,indent=2,ensure_ascii=False,allow_nan=False)
def git(*args):return subprocess.run(['git','-C',str(G),*args],capture_output=True,text=True,encoding='utf8',check=True).stdout.strip()
def refs(s):return{r.split()[1]:r.split()[0]for r in s.splitlines()}
assert not git('status','--porcelain')and git('branch','--show-current')=='main'
assert not V.exists()and not(R/'RECORD436_ONCE_CONSUMED_BEFORE_GIT.json').exists()
assert not git('tag','--list',TAG)
oldrefs=refs(git('show-ref','--tags','-d'));remote=refs(git('ls-remote','--tags','origin'))
assert all(remote.get(k)==v for k,v in oldrefs.items())
lqr=git('ls-remote','origin','refs/heads/lqr').split()[0];assert lqr=='5848b45a99b8c32af02eb61b507c3f95ab39e4ad'
reqpath=R/'AUTOMATION435_FINAL416_EVALFAIL_LIVE433_434_REQUEST.json';req=read(reqpath)
cfg=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text('utf8'))
assert cfg['prompt']==req['prompt']and cfg['rrule']==req['rrule']and cfg['status']==req['status']=='ACTIVE'and cfg['target_thread_id']==req['targetThreadId']
receiptpath=R/'AUTOMATION435_APP_UPDATE_ACTUAL_TOOL_RECEIPT.json';assert not read(receiptpath).get('isError')
put(R/'AUTOMATION435_SAVED_CONFIG_VERIFIED.json',dict(epoch=time.time(),passed=True,requestSHA=H(reqpath),actual_toolreceiptSHA=H(receiptpath),samehourlyACTIVEthread=True))
work=read(R/'CURRENT_ACTUAL435_FINAL416_EVAL423_FAIL_LIVE_BOUNDED433_SOLE434_WORK_ORDER_V1.json')
assert work['actual423']['strict']==0 and work['actual433']['FIRST']['passed']and work['postround434']['launch']['PID']==63108
put(R/'RECORD436_ONCE_CONSUMED_BEFORE_GIT.json',dict(epoch=time.time(),phase=ID,tag=TAG,oldrefs=oldrefs,remote_before=remote,lqr=lqr,pushretry='Continueexistingobjectsneverrerunrecordorretag',actual433_GO=True,FIRST_complete=True,sole434PID=63108,modelreads_for_archive=0))
note=R/'RECORD436_FINAL416_EVAL423_FAILURE_BOUNDED433_ACTUAL_FIRST.md'
note.write_text('''人类明确“我需要的是rl上台阶”。本阶段完成416原窗口完整保存与安全结算、747finite完整CPU、独立423真实RL首episode评测和原生姿态审查；根据实际失败实施postAdam策略步幅限制的真实PPO修复，并已启动433、通过实际FIRST/完整首保存、绑定唯一434收尾评测。传统MPC不当RL交付，loss/COM/腾空/leadingedge都不当270技能。

416已完整关闭，原normal416/传回/CPU均消费。最终33964153B SHA8365d243006ef5ed6818d01298003107808f918347ad929f4ea936544f96e01a，5168controls413440ownpairs、PPO=Pi=critic160/newWM5137total25556，actorAdam56304critic13364WM25556、teacher17Adam42940STD、三Adam/EMA/normRNG/savedorigin完整。CPU747finite一次必要finaldecode通过。原owner1470022/node1470031/worker1470045已ownwaited、原锁free/canonicalNone、fee3602.5654861927032s/closingbalance355413.7456231117s仅当时snapshot不当实时余额。不为归档再次读PT/跑physics。

417唯一timer正常收尾416后，eval在本地index校验失败：INDEX417在openx时把自身空0bytes/SHAe3b0纳入，文件写完33080bytes后必定自校验不匹配。0网络/SDK/模型/物理，不是技能0/80。原index/source/postroundrawfalse/error/once全部保留，normal/CPU417链不重跑。独立423复制原同模型/seed9137/同fixededge.8/270/80firstepisodes400controls8s协议，index完整列清单先于创建index，修localcallerWindows斜杠身份比较，不改实际物理或动作逻辑，actualparent再freshCNone/private/shared准入后执行。

实际423全80在45controls360physics结束：0/80strict、0整轮footprintclear、0leadingcross、74曾腾空、80orientation、0full8s、mean.812s/median.82s。不是待评测。闭链/mimic/basecontact/lowbase0。allownwaited/private共享释放/SSHfinallyclosed/SESSIONrestore/FREE。实际recordedbodypose有限原生渲染0NN/0physics，当前模型view_image已审所选四case：env0/40/1/41台前.80-.84s倾倒，无整轮上台或台顶恢复。424保存全80tracking/manifold事实；425读取已保存motorq/dq/target/root/action/reference，first20左右残差偏置且pitch>.2在.22-.24s；仅实际描述，不当唯一因果。389/404历史0/80/mean1.375s，协议同seed但非exactmatchedcontacttrajectory，不做配对因果结论。没有原样继续416或缩小残差冒称修好。

针对算法代码核对：416actualPPO每batch只oneepoch，preAdamratio约1，pre-stepPPOclip不能限制更新后实际policy改变量。提出保持同actualreward/done/GAE和源完整权重/Adam，只约束postAdam实际meanKL<=.01/maxnormalizedtanhresidualdelta<=.05。同一proposal失败时恢复全部actorweights与Adam，再缩LR重提，最多12backtracks只commit一次acceptedstep；critic原更新、WMH32独立无actorWMgradient，原reward/物理/目标/验收不变。不是宣称PPO无效或stepsize唯一原因，不reset源网络/Adam、savedorigin或直接所有残差缩小。

CPU426必要final416单次decode后尝试将16byteCUDA RNG装CPUgenerator，原RuntimeError保留，候选未update。独立427 fixture保留savedGPU RNGopaque并显式CPUfixturegenerator；同生产learnerGPU恢复代码不变。它完成候选update后对所有actorAdam统一要求56305，误包含冻结STD原42940，故原assert失败；未把失败当pass或重跑once。428独立只修fixture具名STD断言，learnerbytes与427一致SHA24a8f422ea1c8555232f16fc047e5cef73ee20e38ed1a637513853b14e60d496。一次必要final416读取，网络/全部Adam/EMA/origin准确恢复，16保存实际rollout行重复为32controls只作CPU算法fixture不冒充新onpolicy物理数据。原nominalAdam后KL.0212391652/maxdelta.05395630；candidate半LR后KL.0053031030/delta.02658665。CPU候选weightsAdam全部恢复，0生产优化/SDK/physics/预算，原STD仍42940，WM25556不变，terminalGAE返回.6/100无nextbootstrap，deterministic evalplainMLP对训练MLPModel输出差0。CPU准入不当物理技能。

独立429生产包与430postround冻结unused，静态发现postround相对N指向RL_ACTUAL_RESIDUAL_PPO_PRODUCTION_V429而实际root为RL_BOUNDED_ACTUAL_PPO_PRODUCTION_V429，原缺陷保留不执行。独立431修路径且contract要求actualtrustreceipt，通过静态Task/AST/源dataSHA。实际freshCIM/serialFREE/CNone/private/shared/postcopy/secondCNone后launch431，GO17:42:42.8949256；worker首次Taskvalidate从source/teacher_task431加载到旧final389SHA，因此启动前拒绝，0SDK/模型/physics/controls/优化。原owner1473805/node1473814及workerownwaited/costsettled/锁free，原FIRSTlabel收null不是技能评测，未bind432，原source/freeze/false/raw/once不改不重跑。433独立把root/control/source/tracking四份实际导入contract字节统一并每个独立路径validate_task通过，CPU428learner逐字节复用、不再读PT验证，原物理和唯一canonical保持。

433实际run ACTUAL_RESIDUAL_PPO433_1793612747872965000，owner1474033/create1793612811.2、node1474042/create1793612811.63，完整worker身份/exe/argv/controlcwd/jobroot见435/actualsnapshot，GPU-c27eecbd-6838-7290-1cd2-37e34522213d。GO2026-11-02T17:46:55.192029+08:00，SAVE18:46:55.192029/NOMINAL18:51:55.192029/normal最早18:36:55.192029；原3900save3600exit300窗口不改。INDEX433SHA718982f7d9a743cef02903c0531a1861c100f39f737e5e14b9220ee571dc0df4，完整来源final416offset56304/13364/25556、三Adam/teacherSTD/EMA/normRNG/savedorigin恢复，GPU残差RNG从保存16B同设备真实恢复，freshphysicalDRqueue/replay。仍actor103=35proprio9currentdepth59reference/critic106、固定347processed50Hz表+1*tanh(actor-origin)，非自主depth-only/noonlineMPC/无力矩克隆，actualPPO32controls2560samplesoneepochclip.2/gamma.99GAE.95/std.15，WMH32独立、futureactualdepth/GTmap不入imagination。

真实433FIRST64controls5120ownpairs512physics128feedback，Pi=PPO=critic1/newWM33total25589、native24通过，actorgrad9.8601894/critic39.820083有限非零。实际acceptedLR2.5e-5/factor.25/3proposals、postAdamKL.00741470/maxdelta.0177232，一次committedAdamstep、terminal0/actualdoneGAEtrue/actorWMgradfalse。首完整32805945B SHAead9f3fc17d860794fb12db6b748dc583d1c9edd0ba208494b4ce68e891510c3，actorAdam56305critic13365WM25589，teacherAdam42940。snapshot83controls/PPO1/WM25608/143orientation是训练多episode事实不是80独立eval；FIRST不是final或技能。

确认真实FIRST后唯一bind434已消费，localpostroundPID63108/create见435exactCIM，stderr0，INDEX434SHA3207db1395f171028a550244d7b212efb11a919eb4045d4697394b68f93c52eb。它localtimer到原normal900，忙则localwait，同processrunpy原normal433fullsave/安全退出/fullformaltransfer/newCPUoffsets56304/13364/25556，再独立43480首episode400controls8s/seed9137samefixed270newDR/actual400Hzcontactmanifold/有限真实pose渲染，evalindex已排除自身。结果Nreports/POSTROUND433_RL_REPLAY_EVAL_DECISION.json后当前模型必须view_image原生审姿态与manifold，按真实RL越台稳定结果主动定向修复或合理续训，不能只报结束。活timer不第二watcher/normal/CPU/eval/新SSH，不hotpatch/restart/repeatedstartupchecks。

根repoAGENTS保持：400Nengineeringk2000/policy50feedback100physics400/.0025TGS32-4/fullD0whitev3D1-D7/10mm单envclosure/.01mimic/原PD_DCclip_queue_solver/historicalH1exactproducer，84x48暂定非D435i实机标定FPS；成功首次飞行整轮rearfootprint越沿/双轮actual400Hz台顶manifold/无回地面退沿/vxyvz.03/rollpitch10deg/yaw.2连续.5s不放宽。无grantcopyrefundclearactive第二writer，原singlecanonicalstrictreserve；native视觉禁Luna/OpenRouter、unknownPID/GPUscan/kill。每finiteSSH前fresh广exactCIM/serialFREE、parentCNone/private共享，finallyclosed/SESSIONrestore/FREE。当前434活着仅本地，不加SSH。

本阶段全部source/report/rawfalse/once/416close747CPU/417index拒绝/实际423+native/424425/426427CPU原错误/428通过/429unused/431preSDK失败/433启动FIRST/434timer/435交接及现有mod4-10实际更新回执进入本record436。只更新原ACTIVE/hourly/currentchatautomation，无新Goal/chat/automation。只读路径查询的缺失文件/rg拒绝访问报错保留在工具记录；本记录如实说明无模型或物理副作用，实际源定位后继续。已归档同SHA全文或分片引用原Gitpaths；PT/NPZ/USD/media只actualpathbytes已有SHA索引，未知SHA明示，不为Git读模型/跑physics。所有旧tagobjects/peels、420object111385802593206df921feeadd119824ff6949a1/peel412d5d5dcc12d725502849c0dc109367c61452bc、422commit31132dbf2207e96e64c5eddbf16f27dfecbb5a17、lqr5848b45a99b8c32af02eb61b507c3f95ab39e4ad保护。push失败只续objects不重record/retag，postGit验证只工具输出不追HEAD报告循环。
''',encoding='utf8')
names=('RL_ACTUAL_RESIDUAL_PPO_PRODUCTION_V416_20261102','RL416_SINGLE_PROCESS_POSTROUND_V417_20261102','RL416_FINAL_INDEPENDENT_EVAL_V417_20261102',
 'RL416_FINAL_INDEX_REPAIRED_EVAL_V423_20261102','RL_ACTUAL_PPO_TRUST_STEP_REPAIR_V426_20261102','RL_ACTUAL_PPO_TRUST_STEP_REPAIR_V427_20261102','RL_ACTUAL_PPO_TRUST_STEP_REPAIR_V428_20261102',
 'RL_BOUNDED_ACTUAL_PPO_PRODUCTION_V429_20261102','RL429_SINGLE_PROCESS_POSTROUND_V430_20261102','RL429_FINAL_INDEPENDENT_EVAL_V430_20261102',
 'RL_BOUNDED_ACTUAL_PPO_PRODUCTION_V431_20261102','RL431_SINGLE_PROCESS_POSTROUND_V432_20261102','RL431_FINAL_INDEPENDENT_EVAL_V432_20261102',
 'RL_BOUNDED_ACTUAL_PPO_PRODUCTION_V433_20261102','RL433_SINGLE_PROCESS_POSTROUND_V434_20261102','RL433_FINAL_INDEPENDENT_EVAL_V434_20261102')
roots=[(P.name,P)]+[(name,T/name)for name in names]
known={};identities={}
for base in(G/'versions/20261102_mod4-final389-eval404-actual-ppo416-repair',G/'versions/20261102_mod4-residual-rl389-command-handoff',G/'versions/20261102_mod4-mpc-control-handoff339-349',G/'versions/20261102_mod4-init311-paired317-short-h4-tracking-repair324',G/'versions/20261102_mod4-final305-recovery-eval308-targeted-repair307'):
 for p in base.rglob('*CAPTURE_INDEX*.json'):
  for row in read(p).get('files',[]):
   if row.get('SHA')and row.get('Git_path')and(G/row['Git_path']).is_file()and row.get('capture')in('full_UTF8_byte_exact','full_same_SHA_reference'):
    known.setdefault(row['SHA'],dict(Git_path=row['Git_path'],capture='full_same_SHA_reference'))
   elif row.get('SHA')and row.get('capture')in('full_UTF8_byte_sequence_chunked','full_same_SHA_chunk_sequence_reference')and row.get('redactions',0)==0:
    assert all((G/x['Git_path']).is_file()for x in row['parts'])
    known.setdefault(row['SHA'],dict(capture='full_same_SHA_chunk_sequence_reference',parts=row['parts'],archive_SHA=row['archive_SHA'],original_index=p.relative_to(G).as_posix()))
def collect(v,receipt):
 if isinstance(v,dict):
  sha=v.get('SHA')or v.get('sha256');size=v.get('bytes')
  if isinstance(sha,str)and len(sha)==64 and all(c in'0123456789abcdef'for c in sha)and isinstance(size,int):
   for k in('path','local_path','source','remote_path'):
    if isinstance(v.get(k),str):identities.setdefault((v[k].replace(chr(92),'/'),size),(sha,receipt))
  for x in v.values():collect(x,receipt)
 elif isinstance(v,list):
  for x in v:collect(x,receipt)
for label,root in roots:
 assert root.exists(),str(root)
 for p in sorted(root.rglob('*.json')):
  try:collect(read(p),str(p))
  except(ValueError,UnicodeDecodeError):pass
sys.path.insert(0,str(G/'archive_tools'));from capture_history import redact
binary={'.pt','.pth','.npz','.npy','.png','.jpg','.jpeg','.mp4','.usd','.usda','.usdc','.stl','.obj','.zip','.gz','.pyc'}
texts={'.py','.json','.md','.txt','.log','.xml','.toml','.sh','.ps1','.csv','.tsv','.yaml','.yml'}
V.mkdir(parents=True);(V/'.gitattributes').write_text('* -text\n',encoding='utf8');rows=[];heavy=[]
for label,root in roots:
 for p in sorted(root.rglob('*')):
  if not p.is_file()or'__pycache__'in p.parts:continue
  size=p.stat().st_size;relative=Path(label)/p.relative_to(root)
  if p.suffix.lower()in binary:
   item=identities.get((str(p).replace(chr(92),'/'),size));heavy.append(dict(path=str(p),bytes=size,SHA=item[0]if item else'unknown:noarchiveonlybinaryhash',SHA_receipt=item[1]if item else None,capture='metadata_only_no_content_or_hash_for_Git'));continue
  assert p.suffix.lower()in texts,str(p)
  raw=p.read_bytes();sha=hashlib.sha256(raw).hexdigest()
  if sha in known:rows.append(dict(path=str(p),bytes=len(raw),SHA=sha,**known[sha]));continue
  safe,count=redact(raw.decode('utf8'));data=raw if count==0 else safe.encode('utf8');dest=V/relative;dest.parent.mkdir(parents=True,exist_ok=True)
  if len(data)>45*1024*1024:
   parts=[]
   for i,start in enumerate(range(0,len(data),20*1024*1024)):
    part=data[start:start+20*1024*1024];target=dest.with_name(dest.name+f'.part{i:03d}.txt');target.write_bytes(part);parts.append(dict(Git_path=target.relative_to(G).as_posix(),bytes=len(part),SHA=hashlib.sha256(part).hexdigest()))
   rows.append(dict(path=str(p),bytes=len(raw),SHA=sha,archive_SHA=hashlib.sha256(data).hexdigest(),redactions=count,capture='full_UTF8_byte_sequence_chunked',parts=parts,reassemble='ConcatenateallpartsandverifytotalarchiveSHA'));continue
  dest.write_bytes(data);gp=dest.relative_to(G).as_posix();rows.append(dict(path=str(p),bytes=len(raw),SHA=sha,Git_path=gp,archive_SHA=hashlib.sha256(data).hexdigest(),redactions=count,capture='credential_pattern_redacted'if count else'full_UTF8_byte_exact'))
  if not count:known[sha]=dict(Git_path=gp,capture='full_same_SHA_reference')
put(V/'CAPTURE_INDEX_RECORD436.json',dict(epoch=time.time(),phase=ID,files=rows,large_artifacts=heavy,oldrefs=oldrefs,remote_before=remote,lqr=lqr,all_saved_text_full_or_sameSHA_or_completechunks=True,final416actualstrict0=True,actual433GO=True,FIRSTcomplete=True,sole434PID=63108,no_modelreads_for_archive=True))
files=[p.relative_to(G).as_posix()for p in sorted(V.rglob('*'))if p.is_file()]
import record_experiment
original_git=record_experiment.git
def exact_directory_add(*args):
 if len(args)>=2 and args[:2]==('add','--'):
  record=args[2];selected=set(args[3:]);assert selected==set(files)
  result=original_git('add','--',record,V.relative_to(G).as_posix());assert set(original_git('diff','--cached','--name-only').splitlines())==selected|{record};return result
 return original_git(*args)
record_experiment.git=exact_directory_add
sys.argv=['record_experiment.py','--id',ID,'--title','Evaluate final PPO416 failure and launch bounded actual PPO433 repair','--kind','repair','--note-file',str(note),'--validation','416fullclose747finite;417localselfindex0network;423actual0of80/native reviewed;426427CPUerrorspreserved;428trustfixturepass;429unused431preSDKfalse;433actualFIRSTpostAdamKL.0074147delta.0177232fullsave;sole434timer','--files',*files]
record_experiment.main()
head=git('rev-parse','HEAD');obj=git('rev-parse','refs/tags/'+TAG);peel=git('rev-parse','refs/tags/'+TAG+'^{}');assert peel==head
git('push','--atomic','origin','HEAD:refs/heads/main','refs/tags/'+TAG)
after=refs(git('show-ref','--tags','-d'));remote_after=refs(git('ls-remote','--tags','origin'))
assert all(after.get(k)==v and remote_after.get(k)==v for k,v in oldrefs.items())
assert all(remote_after.get(k)==v for k,v in remote.items())
assert remote_after['refs/tags/'+TAG]==obj and remote_after['refs/tags/'+TAG+'^{}']==head
assert git('ls-remote','origin','refs/heads/main').split()[0]==head
assert git('ls-remote','origin','refs/heads/lqr').split()[0]==lqr and not git('status','--porcelain')
print(json.dumps(dict(passed=True,HEAD=head,remote_main=head,tag=TAG,tagobject=obj,peel=peel,files=len(files),indexed=len(rows),heavy_metadata=len(heavy),oldrefsprotected=True,lqr=lqr,clean=True,actual433GO=True,sole434PID=63108)),flush=True)
