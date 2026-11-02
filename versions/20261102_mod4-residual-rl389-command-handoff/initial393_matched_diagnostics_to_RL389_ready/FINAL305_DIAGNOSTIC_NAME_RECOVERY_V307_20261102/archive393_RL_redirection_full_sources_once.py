"""New human-directed RL phase: unique annotated record393; old trial objects immutable."""
from pathlib import Path
import hashlib,json,subprocess,sys,time,tomllib
P=Path(__file__).resolve().parent;T=P.parent;R=P/'reports';G=T.parent/'polar-rl-train'
BASE=G/'versions/20261102_mod4-residual-rl389-command-handoff';V=BASE/'initial393_matched_diagnostics_to_RL389_ready'
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_bytes())
def put(p,v):
 with p.open('x',encoding='utf8')as f:json.dump(v,f,indent=2,ensure_ascii=False,allow_nan=False)
def git(*a):return subprocess.run(['git','-C',str(G),*a],capture_output=True,text=True,encoding='utf8',check=True).stdout.strip()
def refs(s):return{r.split()[1]:r.split()[0]for r in s.splitlines()}
assert not git('status','--porcelain')and git('branch','--show-current')=='main'
assert not V.exists()and not(R/'RECORD393_ONCE_CONSUMED_BEFORE_GIT.json').exists()
TAG='trial-20261102-mod4-residual-rl389-command-handoff';assert not git('tag','--list',TAG)
oldrefs=refs(git('show-ref','--tags','-d'));remote=refs(git('ls-remote','--tags','origin'));assert all(remote.get(k)==v for k,v in oldrefs.items())
lqr=git('ls-remote','origin','refs/heads/lqr').split()[0];assert lqr=='5848b45a99b8c32af02eb61b507c3f95ab39e4ad'
cfg=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text('utf8'));req=read(R/'AUTOMATION392_RL_REDIRECTION_UPDATE_REQUEST.json')
assert cfg['prompt']==req['prompt']and cfg['status']==req['status']=='ACTIVE'and cfg['target_thread_id']==req['targetThreadId']and cfg['rrule']==req['rrule']
put(R/'AUTOMATION392_SAVED_CONFIG_VERIFIED.json',dict(epoch=time.time(),passed=True,requestSHA=H(R/'AUTOMATION392_RL_REDIRECTION_UPDATE_REQUEST.json'),toolreceiptSHA=H(R/'AUTOMATION392_APP_UPDATE_ACTUAL_TOOL_RECEIPT.json'),same_existing_hourly_ACTIVE_thread=True))
put(R/'RECORD393_ONCE_CONSUMED_BEFORE_GIT.json',dict(epoch=time.time(),phase='mod4-residual-rl389-command-handoff',tag=TAG,oldrefs=oldrefs,remote_before=remote,lqr=lqr,push_retry='Continue existing objects; never rerun record or retag',actualRL389_START=False))
note=R/'RECORD393_RL389_PREPARED_HUMAN_REDIRECTION.md'
note.write_text('''人类本轮明确“我需要的是rl上台阶”。本阶段据此停止以传统MPC实验接续替代RL交付，将目标落实为学习策略实际跳上270mm平台并稳定恢复。324参考跟踪RL此前已完整保存关闭、609finiteCPU通过，339独立0/80已回放；传统MPC数字不能算RL毕业。

本轮先完成上一工作单的有限诊断：372只读保存368的起跳状态和D0-D7，观察成功/失败延迟分布混杂；373新80首episode/40匹配对，实际backend mass/inertia/material/COM/drive/armature/forcecap，电机gain/D2/D3/D4/D5/D6/D7和每100Hz反馈tick共享D1噪声均核一致。0NN/优化/账写，250controls/2000physics/500feedback，源2/40strict、12full5s/28orientation/mean2.3885，bounded12/40strict、18full/22orientation/mean3.059，14个actual firstflight wholefootprint/topmanifold/.5s候选通过；native图env1/7倒，41/47站台。375原报告/p.006保留，但实际首control state IMU差.08173/target.37878，不能当单干预干净因果。

376核SDKtimestamped root_com_ang_vel_b/projected_gravity_b缓存：plannedroot/q写入不推进simtime，373helper只清root_link_ang_vel_b，旧派生值可残留。独立377刷新这三缓存后原D1-D3，实际全部40pair首观测state和target0差，原373不回写。377同80/250/2000/500真实执行，源5/40strict、17full5s/23orientation/mean2.839；bounded7/40strict、21full/19orientation/mean3.342，总12实际manifold成功。pair both1/sourceonly4/boundedonly6/bothfail29，p.754，平均寿命+.503s，未证明稳健胜出；第二20ms接触运动已分歧，匹配参数不等于逐位同plant。378/379独立savedfacts核12候选真实接触，native图源7站台而bounded47倒，源11倒而bounded51站台。两实验都ownchildwaited/locksreleased/SSHclosed/sessionrestoreFREE，旧once永不重跑。380CPU仅时序代数：pushfor.090896s源100Hz10命令最后alpha.99014 vs50Hz5命令.88012；两者对齐起跳后都100ms发firstflight，不称持续翻倍/减半。源100Hz时序研究被人类最新RL交付要求覆盖，不再自动开传统对照。

新残差RL生产方案：固定已保存347 processed电机位置/轮速度命令表取偶数50Hz作为前馈，真实Actor103当前35proprio+9depth+59plannedgoal输出相对冻结源Actor103同输入的残差，action=baseline+1*tanh(actor-origin)。初始残差0、原actor/critic/STD/三Adam/EMA/normRNG/WM16879完整恢复，actorAdam52636/critic9696，teacher17Adam42940冻结；不resetAdam或回退2135teacher actor。origin只冻结参数、保留对想象state的输入导数，零残差state导数0但actor参数梯度非零。运行时没有MPC求解或闭环MPC接管，没有力矩克隆loss；它是计划参考条件残差RL，尚非depth-only。学习仍ownPhysXWMH32、actorH8直接同weightedtrackingcost/5、terminal0/noalivecostdeletion/noexpattenuation，criticactualownTDHuber/EMA.01/实际exp(-cost/5)保留。freshsource347fullplannedq/dq/root+actualqqueuehold+每reset派生IMU刷新，原D0-D7随机复位保持。原50/100/400Hz/.0025TGS32-4/400N-k2000/10mmepisodeclosure/.01mimic/PD/DCclip和唯一canonical3900save3600exit300strictreserve不改；无预算增加/复制/refund/clearactive/第二writer。

CPU384一次必要final324读完整恢复通过，actor/critic/STD/三Adam/targetEMA准确，no-steptrackinggrad6.11395有限非零terminal0，doneTD=.6无bootstrap；初始动作等fixedbaseline，origin冻结与输入梯度测试通过。不是物理技能成功。原383源命令JSON缺joint_names的KeyError在0网络SDK模型GO前；384改用已qualified含catalog计划包，CPU成功后static发现TaskJSON全串版本替换误改GPUUUID，384完整冻结拒绝不用，0START/deploy/GO。386postroundpreparer缺H NameError原源保留，387本地完成但作为384关联仍unused。独立389保护UUID/hashes，用真实GPU-c27eecbd-6838-7290-1cd2-37e34522213d，命名映射行为复用实际CPU384，不重读PT。389preparer错误要求common存在literalGPU而实际GPUS由SCHEDULE动态获得，原assert/false保留；391核动态绑定与Task正确后完成新INDEX。另381writer invalid609finiteCPU语法错误原源保留，v2修正。全部原source/rawfalse与修复并列。

当前唯一可启动包MPC_COMMAND_RESIDUAL_RL_V389_20261102，runREFERENCE_TRACKING389_1793592987357927500，INDEX57fa0b19306db14a451fcbf1efe272beb8304f68c1c907bc6b3d13cd7aa9411c，worker d1e7277ab7c2910353ed0d1e1e486f7cf65a6925fdc499272f9f8afa7415323e。115文件冻结核对/AST/Task/CPUlearnerSHA一致。尚无START消费、部署或GO。RESIDUAL_RL389_POSTROUND_V390_20261102/INDEX c8dcc6ae9aeb703f39edd58587f93504085a09a3e02059cb07be148697b18cb3已准备：实际FIRST完整保存/gradient/native24确认后才bind388并启动唯一localtimer；原normal900收尾/formaltransfer/fullCPU/newfinal一次decode，独立80firstepisodes/400controls/seed9137/newDR同edge.8/270，actor+savedorigin+固定表推理，无onlineMPC，实际400Hzmanifold和记录bodypose原生回放。结果只报告RL策略技能，不能以前馈或传统MPC成功冒充学习效果。currentworkorder392和现automation经工具更新，仍ACTIVE/hourly/samechat。

当前资源限制实际存在：另一聊天POSTTRAIN_EIGHT_EXCLUDING_H1 Pair1V4原owner1457086，GPU0 E0 worker1457100、GPU1 Curb8781457109，实际12:02:15/16GO，原SAVE13:02:15/16、NOMINAL13:07:15/16+08。localcollector64352/create12:03:19.968538持SSH。12:14:34本地原发布E0 new9完整save、Curb32945/full20k restore，非终止。新H1 RL未抢占、未burn389once/SSH，无第二watcher；仅本地准备与归档。资源实际全释放、freshLOCALexactCIM/serialFREE和parentfreshcanonicalNone/private/sharedselectedGPU准入后，唯一unused389启动；不为了GPU利用率双开writer。

本阶段是人类最新RL方向的新真实修复，record393唯一annotatedtrial；包括此前尚未归档372..381有限诊断、全部拒绝/reader/source错误，以及新RL ready389/390/392。原MPCphase trialobjectf63c76d9c064a26e6261b544304c7f92a5bbdf76/peela6c59be6408153875b36ed851d59d3767f8e5709及全部旧tags/peels/lqr5848b45a99b8c32af02eb61b507c3f95ab39e4ad保护。所有文本报告完整或同SHA引用，>45MB文本按20MB字节片保留总SHA/片SHA，PT/NPZ/USD/media只实际path/bytes/已存在producerSHA索引，不为Git读模型或重跑physics。凭据脱敏不输出，postGit验证只工具输出，不产生追HEAD循环。push失败只续existingobjects不重record/retag。
''',encoding='utf8')
names=('MPC_MATCHED_DR_AIR_REQUEST_V373_20261102','MPC_MATCHED_INITIAL_IMU_AIR_REQUEST_V377_20261102','MPC_COMMAND_RESIDUAL_RL_V383_20261102','MPC_COMMAND_RESIDUAL_RL_V384_20261102','RESIDUAL_RL384_POSTROUND_V386_20261102','RESIDUAL_RL384_INDEPENDENT_EVAL_V386_20261102','MPC_COMMAND_RESIDUAL_RL_V389_20261102','RESIDUAL_RL389_POSTROUND_V390_20261102','RESIDUAL_RL389_INDEPENDENT_EVAL_V390_20261102')
roots=[(P.name,P)]+[(n,T/n)for n in names]+[('loose',T/'residual_policy383_TEMP.txt')]
ext=Path('F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/POSTTRAIN_EIGHT_EXCLUDING_H1_20261102')
for name in('PAIR1_V4_STAGE_DISPATCH_RESULT.json','PAIR1_V4_COLLECTOR_ONCE.json','reports/PAIR1_V4_ADMISSION_STATUS_20261102_120602.json','reports/PAIR1_V4_PUBLISHED_PPO_COUNTS_20261102_121434.json'):roots.append(('resource_evidence',ext/name))
known={};identities={}
for root in (G/'versions/20261102_mod4-mpc-control-handoff339-349',G/'versions/20261102_mod4-init311-paired317-short-h4-tracking-repair324',G/'versions/20261102_mod4-final305-recovery-eval308-targeted-repair307'):
 for p in root.rglob('*CAPTURE_INDEX*.json'):
  for row in read(p).get('files',[]):
   if row.get('SHA')and row.get('Git_path')and(G/row['Git_path']).is_file()and row.get('capture')in('full_UTF8_byte_exact','full_same_SHA_reference'):known.setdefault(row['SHA'],row['Git_path'])
def collect(v,receipt):
 if isinstance(v,dict):
  sha=v.get('SHA')or v.get('sha256');size=v.get('bytes')
  if isinstance(sha,str)and len(sha)==64 and all(c in'0123456789abcdef'for c in sha)and isinstance(size,int):
   for key in('path','local_path','source','remote_path'):
    if isinstance(v.get(key),str):identities.setdefault((v[key].replace('\\','/'),size),(sha,receipt))
  for q in v.values():collect(q,receipt)
 elif isinstance(v,list):
  for q in v:collect(q,receipt)
for label,root in roots:
 for p in([root]if root.is_file()else sorted(root.rglob('*.json'))):
  try:collect(read(p),str(p))
  except(ValueError,UnicodeDecodeError):pass
sys.path.insert(0,str(G/'archive_tools'));from capture_history import redact
binary={'.pt','.pth','.npz','.npy','.png','.jpg','.jpeg','.mp4','.usd','.usda','.usdc','.stl','.obj','.zip','.gz','.pyc'}
texts={'.py','.json','.md','.txt','.log','.xml','.toml','.sh','.ps1','.csv','.tsv','.yaml','.yml'}
V.mkdir(parents=True);(V/'.gitattributes').write_text('* -text\n',encoding='utf8');rows=[];heavy=[];chunksize=20*1024*1024
for label,root in roots:
 for p in([root]if root.is_file()else sorted(root.rglob('*'))):
  if not p.is_file()or'__pycache__'in p.parts:continue
  size=p.stat().st_size;relative=Path(label)/(p.name if root.is_file()else p.relative_to(root))
  if p.suffix.lower()in binary:
   item=identities.get((str(p).replace('\\','/'),size));heavy.append(dict(path=str(p),bytes=size,SHA=item[0]if item else'unknown:noarchiveonlybinaryhash',SHA_receipt=item[1]if item else None,capture='metadata_only_no_content_or_hash_for_Git'));continue
  assert p.suffix.lower()in texts,str(p)
  raw=p.read_bytes();sha=hashlib.sha256(raw).hexdigest()
  if sha in known:rows.append(dict(path=str(p),bytes=size,SHA=sha,Git_path=known[sha],capture='full_same_SHA_reference'));continue
  safe,count=redact(raw.decode('utf8'));data=raw if count==0 else safe.encode('utf8');dest=V/relative;dest.parent.mkdir(parents=True,exist_ok=True)
  if len(data)>45*1024*1024:
   parts=[]
   for i,start in enumerate(range(0,len(data),chunksize)):
    b=data[start:start+chunksize];part=dest.with_name(dest.name+f'.part{i:03d}.txt');part.write_bytes(b);parts.append(dict(Git_path=part.relative_to(G).as_posix(),bytes=len(b),SHA=hashlib.sha256(b).hexdigest()))
   rows.append(dict(path=str(p),bytes=size,SHA=sha,archive_SHA=hashlib.sha256(data).hexdigest(),redactions=count,capture='full_UTF8_byte_sequence_chunked',reassemble='concatenate chunks in listedorder; totalarchiveSHA verifiescomplete',parts=parts));continue
  dest.write_bytes(data);gp=dest.relative_to(G).as_posix();rows.append(dict(path=str(p),bytes=size,SHA=sha,Git_path=gp,archive_SHA=hashlib.sha256(data).hexdigest(),redactions=count,capture='credential_pattern_redacted'if count else'full_UTF8_byte_exact'))
  if not count:known[sha]=gp
put(V/'CAPTURE_INDEX_RECORD393.json',dict(epoch=time.time(),phase='mod4-residual-rl389-command-handoff',files=rows,large_artifacts=heavy,oldrefs=oldrefs,remote_before=remote,lqr=lqr,RL389_not_STARTED=True,resource_busy_local_evidence_only=True,all_saved_reports_full_sameSHA_or_completechunks=True,no_archive_modelreads=True))
files=[p.relative_to(G).as_posix()for p in sorted(V.rglob('*'))if p.is_file()]
import record_experiment
original_git=record_experiment.git
def exact_directory_add(*args):
 if len(args)>=2 and args[:2]==('add','--'):
  record=args[2];selected=set(args[3:]);assert selected==set(files)and all(Path(f).is_relative_to(V.relative_to(G))for f in selected)
  result=original_git('add','--',record,V.relative_to(G).as_posix());staged=set(original_git('diff','--cached','--name-only').splitlines());assert staged==selected|{record};return result
 return original_git(*args)
record_experiment.git=exact_directory_add
sys.argv=['record_experiment.py','--id','mod4-residual-rl389-command-handoff','--title','Prepare learned residual RL for270mm step; retain matched MPC diagnostics and reset repairs','--kind','repair','--note-file',str(note),'--validation','CPU384onefullsourceRead exactactorcriticSTDthreeAdamEMA/grad6.11395/terminal0/no-step;389readyunused/index115;actoronly390evalprepared;resourceoccupiedotheroriginalowner;373377allclosed/manifold/native reviewed;allfailuresretained','--files',*files]
record_experiment.main()
head=git('rev-parse','HEAD');obj=git('rev-parse','refs/tags/'+TAG);peel=git('rev-parse','refs/tags/'+TAG+'^{}');assert peel==head
git('push','--atomic','origin','HEAD:refs/heads/main','refs/tags/'+TAG)
after=refs(git('show-ref','--tags','-d'));remote_after=refs(git('ls-remote','--tags','origin'))
assert all(after.get(k)==v and remote_after.get(k)==v for k,v in oldrefs.items())and all(remote_after.get(k)==v for k,v in remote.items())
assert git('ls-remote','origin','refs/heads/main').split()[0]==head and remote_after['refs/tags/'+TAG]==obj and remote_after['refs/tags/'+TAG+'^{}']==head
assert git('ls-remote','origin','refs/heads/lqr').split()[0]==lqr and not git('status','--porcelain')
print(json.dumps(dict(passed=True,HEAD=head,remote_main=head,tag=TAG,tagobject=obj,peel=peel,files=len(files),indexrows=len(rows),binary_metadata=len(heavy),chunked=sum(r['capture']=='full_UTF8_byte_sequence_chunked'for r in rows),oldrefsprotected=True,lqr=lqr,clean=True,RL389_STARTED=False)),flush=True)
