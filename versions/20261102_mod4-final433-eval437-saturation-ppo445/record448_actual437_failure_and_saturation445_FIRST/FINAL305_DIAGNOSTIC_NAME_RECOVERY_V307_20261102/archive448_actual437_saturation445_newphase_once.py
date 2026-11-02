"""Unique record448 for actual416failure and boundedactualPPO433repair, allerrorskept."""
from pathlib import Path
import hashlib,json,subprocess,sys,time,tomllib
P=Path(__file__).resolve().parent;T=P.parent;R=P/'reports';G=T.parent/'polar-rl-train'
ID='mod4-final433-eval437-saturation-ppo445';TAG='trial-20261102-'+ID
BASE=G/('versions/20261102_'+ID);V=BASE/'record448_actual437_failure_and_saturation445_FIRST'
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_bytes())
def put(p,v):
 with p.open('x',encoding='utf8')as f:json.dump(v,f,indent=2,ensure_ascii=False,allow_nan=False)
def git(*args):return subprocess.run(['git','-C',str(G),*args],capture_output=True,text=True,encoding='utf8',check=True).stdout.strip()
def refs(s):return{r.split()[1]:r.split()[0]for r in s.splitlines()}
assert not git('status','--porcelain')and git('branch','--show-current')=='main'
assert not V.exists()and not(R/'RECORD448_ONCE_CONSUMED_BEFORE_GIT.json').exists()
assert not git('tag','--list',TAG)
oldrefs=refs(git('show-ref','--tags','-d'));remote=refs(git('ls-remote','--tags','origin'))
assert all(remote.get(k)==v for k,v in oldrefs.items())
lqr=git('ls-remote','origin','refs/heads/lqr').split()[0];assert lqr=='5848b45a99b8c32af02eb61b507c3f95ab39e4ad'
reqpath=R/'AUTOMATION447_ACTUAL437_FAIL_LIVE445_SOLE446_REQUEST.json';req=read(reqpath)
cfg=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text('utf8'))
assert cfg['prompt']==req['prompt']and cfg['rrule']==req['rrule']and cfg['status']==req['status']=='ACTIVE'and cfg['target_thread_id']==req['targetThreadId']
receiptpath=R/'AUTOMATION447_ACTUAL_APP_UPDATE_TOOL_RECEIPT.json';assert not read(receiptpath).get('isError')
put(R/'AUTOMATION447_SAVED_CONFIG_VERIFIED.json',dict(epoch=time.time(),passed=True,requestSHA=H(reqpath),actual_toolreceiptSHA=H(receiptpath),samehourlyACTIVEthread=True))
work=read(R/'CURRENT_ACTUAL447_FINAL433_EVAL437_FAIL_LIVE_SATURATION445_SOLE446_WORK_ORDER_V1.json')
assert work['actual437']['strict']==0 and work['actual445']['FIRST']['passed']and work['postround446']['launch']['PID']==46516
put(R/'RECORD448_ONCE_CONSUMED_BEFORE_GIT.json',dict(epoch=time.time(),phase=ID,tag=TAG,oldrefs=oldrefs,remote_before=remote,lqr=lqr,pushretry='Continueexistingobjectsneverrerunrecordorretag',actual445_GO=True,FIRST_complete=True,sole446PID=46516,modelreads_for_archive=0))
note=R/'RECORD448_FINAL433_EVAL437_FAIL_SATURATION445_ACTUAL_FIRST.md'
note.write_text("""人类目标是RL实际跳上270mm并稳定，传统MPC不作交付。此阶段完成final433实际独立437评测与真实记录bodypose原生审查，依据失败保留全部数据，修复训练残差饱和后的探索分布并已经启动实际445PPO；唯一446收尾评测绑定。未把CPU/启动FIRST称物理技能通过。

433原normal/fulltransfer/CPU795finite均已消费并安全关闭。最终34402073B SHAdb6944ceca539106bb392a881185f1e85917efa5a9325bbeec72863f8240e04f，Pi161critic161/WM30731、actorAdam56465critic13525及三Adam/STD/teacher17Adam42940/EMA/normRNG/savedorigin完整。旧434本地busy拒绝0network/SDK/model/physics原false保留；它不是0/80技能失败，不重跑434或原normalCPU。

另聊天SUPERMIMIC8发布原owner_exit/allownwaited/costsettled/leasesreleased、metadata collector65008已退出，本地fresh广exactCIMFREE后才唯一run437。437实际samefinal/80firstepisodes400controls8s/seed9137新DR/fixededge.8/270完成3200physics：0/80strict、0wholefootprintclear、0leadingedgecross、80everairborne、44orientation、36full8s、mean4.30925s/median1.57s、longesttopmanifold0。allownchildrenwaited/private共享锁释放/SSHfinallyclosed/SESSIONrestore/FREE，原回执与全部返回UTF8完整保存。不是待评测。有限savedpose渲染0NN/0新physics，当前模型view_image原生已审env0/40/1/41：前三个短case台前/台边倾倒；env1跑满8s仍斜卡台前下方，没有台顶恢复。full8s不能当跳台。440all80/manifold核实，441motor/target/root/residual分析保留，oldtelemetryMPClabel不等于在线MPC。

441实际selected长caseenv1左右轮residual各354/400拍abs>.95，末rootx.563/z.295，参考x1.38/z.536。原fixedGaussianlatentstd.15经tanh在mean3时实际residualstd约.00158194，mean4约.00021519；这是饱和时动作探索衰减的数学事实，非全部物理失败的唯一因果证据。没有原样继续433、缩小全部残差或改PD/solver/reward/horizon。

442独立候选只改训练探索分布为perchannel latentGaussian sigma=min(2,sqrt(.15^2+(.6*mean)^2))，actualPPOlikelihood与更新后KL均完整Gaussian；mean/variance依赖当前policy，确定性eval仍同固定347processed50Hz前馈+1*tanh(actor-origin)。原learnedSTD42940冻结、source网络/Adam/origin不reset，actualrewardexp(-同weightedtrackingcost/5)/done/GAE32/.99/.95/oneepochclip.2和WMH32独立训练保持。std变化只是已声明训练探索，不是物理DR或电机限幅改动。

442必要final433一次CPUdecode完整恢复所有源state，CUDA16B samplingRNG保留opaque、CPUfixture单独generator。22保存坐标/奖励行重复为32controls并新合成latent/logprob，只是CPU算法fixture而非新实际onpolicy样本；继承learnerdiagnostic actual_onpolicy_samples2560字段的CPU语义已追加澄清报告，原report不回写。TorchNormal logprob误差1.9e-6/fullGaussianKL误差9.3e-9，ratio1，actorgrad2.7074critic3.4837，acceptedhalfLR/KL.00220768/maxdelta.0368878。全部candidateweightsAdam恢复、生产优化0/SDK0/physics0，deterministicevalactor接口差0/动作差0、terminalGAE无nextbootstrap通过。CUDA生产restore代码不变，不重复PT验模。

443/444包准备在INDEXfreeze前因relativepostroundroot仍BOUNDED而实际SATURATION静态拒绝，0START/model/SDK/physics/network，原source/失败保留unused。独立445/446修bare rootname替换，root/control/source四个实际contract导入与Task一致、源来源SHA/bytes/Adamoffsets齐；CPU442learner字节SHAbe4b5eb43b622b6a3b3b60ba3934f91a38eb8a7e87dc6700da19a699b9d2904a准确复用。447unfrozenreportwriter曾因单引号apostropheSyntaxError在执行前失败，原错误单独报告保留，修writer文字后成功，无训练变化。

实际445run ACTUAL_RESIDUAL_PPO445_1793622221044727200，owner1482264/create1793622408.75、node1482274/create1793622409.15、ownworker1482287/create1793622415.32。worker即时Popenidentity见实际receipt为run-python.sh bashbeforeexec，不捏造后exec身份或扫描unknownPID。GPU-c27eecbd-6838-7290-1cd2-37e34522213d。GO2026-11-02T20:26:52.734772+08，SAVE21:26:52.734772/NOMINAL21:31:52.734772/normal最早21:16:52.734772。原3900save3600exit300单canonicalstrictreserve不变。INDEX445SHAb33b9481a7e9ca1f3722dbb4b3e264bbbe59bfa9ee57edc015850436a9778f11，workerSHA8e7d567c35a03dd57f37e736bf9405705189cfd6553a504fd381ae5544bf1f3a，sourcefinal433完整续56465/13525/30731、三Adam/teacherSTD/EMA/normRNG/savedorigin。freshphysicalDRqueue/replay、同GPU残差RNG真实恢复。actor103=35proprio9currentdepth59reference/critic106，非自主depth-only，无onlineMPC/接管/torquecloning。

445实际FIRST64controls5120ownpairs512physics128feedback，Pi=PPO=critic1/newWM33total30764/native24通过。actorgrad3.5483568critic9.6709728有限非零，实际latentstdmean.606573max2、acceptedLR5e-5/half/2proposals、postAdamfullGaussianKL.00597859/maxdelta.03330595、一次commit。首完整32808633B SHA71c7f022301be49a8a2198bd9adf0bd8660af418b3016b24977897558971f006/actorAdam56466critic13526WM30764、teacher42940冻结。snapshot92controls/PPO1/WM30792/40orientation是训练重复episode事件，不是独立80评测。FIRST不是FINAL或技能。

唯一446bind/timer已消费，localPID46516/create2026-11-02T20:28:20.059169+08/完整exactCIM见447，stderr0。INDEX446SHA60a98efa3f122f774bce09d38921e24b165f298aff469def01d5237ca2e8105f。localtimer到原normal900，忙仅本地wait，同一processrunpy原normal445fullsave/安全退出/fullformaltransfer、新CPUoffsets56465/13525/30731，再独立446同final一次actor+origin/80firstepisodes400controls8sseed9137same270newDR/actual400Hzmanifold/有限recordedposes渲染。index排除自身，normalclose后eval前再localCIMwait避免434竞态。活timer不第二watcher/SSH/normal/CPU/eval，不hotpatch或startupcheck重跑。最终当前模型必须view_image原生审实际pose/manifold后主动RL修复或合理续训，不只报结束。

物理400Nengineeringk2000/50policy100feedback400physics/.0025TGS32-4/fullD0whitev3D1-D7/10mm单envclosure/.01mimic/原PD_DCclip_queue_solver/historicalH1exactproducer保持；84x48仅暂定camera非D435i硬件标定FPS，futureactualdepth/GTmap不入imagination。成功首次飞行整轮rearfootprintclear/双轮actual400Hz台顶manifold/无groundedge返回/vxyvz.03/rollpitch10deg/yaw.2连续.5s不放宽。原singlecanonicalstrictreserve不grantcopyrefundclearactive第二writer，历史余额非实时。native视觉禁Luna/OpenRouter、unknownPID/GPUscan/kill。每finiteSSH前freshLOCALexactknownCIMFREE、parentCNone/private共享准入，finallyclosedSESSIONrestoreFREE，凭据不输出Git。

全部437actualsource/reports/raw/once/返回fullUTF8与native决定、440441/442CPU/source、443静态失败、445launchFIRST/446timer、447handoff/automation真实appreceipt与config验证进入新phase record448。大JSON完整bytechunk无截取；同SHA源复用已有Git引用。PT/NPZ/USD/media只实际pathbytes已有SHA，不为Git读模型或重跑physics。record436object1b309d3b6fa4a8fa41496956df61f116bae2b6ab/peel1044a69fef42ace2dee82f2dcb229538dc029a9b、439commit013ee164aa11762e075152befcb7e1ecb2314f63、所有旧tagobjects/peels及lqr5848b45a99b8c32af02eb61b507c3f95ab39e4ad保护。push失败仅续existingobjects，不重record/retag；postGit验证只工具输出不追HEAD报告循环。
""",encoding='utf8')
names=('RL_BOUNDED_ACTUAL_PPO_PRODUCTION_V433_20261102','RL433_SINGLE_PROCESS_POSTROUND_V434_20261102','RL433_FINAL_INDEPENDENT_EVAL_V434_20261102',
 'RL433_FIRST_ACTUAL_INDEPENDENT_EVAL_V437_20261102','RL_SATURATION_EXPLORATION_REPAIR_V442_20261102',
 'RL_SATURATION_ACTUAL_PPO_PRODUCTION_V443_20261102','RL443_SINGLE_PROCESS_POSTROUND_V444_20261102','RL443_FINAL_INDEPENDENT_EVAL_V444_20261102',
 'RL_SATURATION_ACTUAL_PPO_PRODUCTION_V445_20261102','RL445_SINGLE_PROCESS_POSTROUND_V446_20261102','RL445_FINAL_INDEPENDENT_EVAL_V446_20261102')
roots=[(P.name,P)]+[(name,T/name)for name in names]
known={};identities={}
for base in(G/'versions/20261102_mod4-final416-eval423-bounded-ppo433',G/'versions/20261102_mod4-final389-eval404-actual-ppo416-repair',G/'versions/20261102_mod4-residual-rl389-command-handoff',G/'versions/20261102_mod4-mpc-control-handoff339-349',G/'versions/20261102_mod4-init311-paired317-short-h4-tracking-repair324',G/'versions/20261102_mod4-final305-recovery-eval308-targeted-repair307'):
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
put(V/'CAPTURE_INDEX_RECORD448.json',dict(epoch=time.time(),phase=ID,files=rows,large_artifacts=heavy,oldrefs=oldrefs,remote_before=remote,lqr=lqr,all_saved_text_full_or_sameSHA_or_completechunks=True,final433actualstrict0=True,actual445GO=True,FIRSTcomplete=True,sole446PID=46516,no_modelreads_for_archive=True))
files=[p.relative_to(G).as_posix()for p in sorted(V.rglob('*'))if p.is_file()]
import record_experiment
original_git=record_experiment.git
def exact_directory_add(*args):
 if len(args)>=2 and args[:2]==('add','--'):
  record=args[2];selected=set(args[3:]);assert selected==set(files)
  result=original_git('add','--',record,V.relative_to(G).as_posix());assert set(original_git('diff','--cached','--name-only').splitlines())==selected|{record};return result
 return original_git(*args)
record_experiment.git=exact_directory_add
sys.argv=['record_experiment.py','--id',ID,'--title','Evaluate final PPO433 failure and launch saturation-aware actual PPO445 repair','--kind','repair','--note-file',str(note),'--validation','433fullclose795finite;437actual0of80wholeclear0/nativeviewed/36full8s;441saturation;442fullrestoreGaussiantestpass;443staticfalse;445actualFIRSTfullsave/KL.00597859delta.03330595;sole446timer','--files',*files]
record_experiment.main()
head=git('rev-parse','HEAD');obj=git('rev-parse','refs/tags/'+TAG);peel=git('rev-parse','refs/tags/'+TAG+'^{}');assert peel==head
git('push','--atomic','origin','HEAD:refs/heads/main','refs/tags/'+TAG)
after=refs(git('show-ref','--tags','-d'));remote_after=refs(git('ls-remote','--tags','origin'))
assert all(after.get(k)==v and remote_after.get(k)==v for k,v in oldrefs.items())
assert all(remote_after.get(k)==v for k,v in remote.items())
assert remote_after['refs/tags/'+TAG]==obj and remote_after['refs/tags/'+TAG+'^{}']==head
assert git('ls-remote','origin','refs/heads/main').split()[0]==head
assert git('ls-remote','origin','refs/heads/lqr').split()[0]==lqr and not git('status','--porcelain')
print(json.dumps(dict(passed=True,HEAD=head,remote_main=head,tag=TAG,tagobject=obj,peel=peel,files=len(files),indexed=len(rows),heavy_metadata=len(heavy),oldrefsprotected=True,lqr=lqr,clean=True,actual445GO=True,sole446PID=46516)),flush=True)
