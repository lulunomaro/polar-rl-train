"""Unique record420 for final389 actualevaluation and actualtransitionRL repair416."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys
import time
import tomllib

P=Path(__file__).resolve().parent;T=P.parent;R=P/'reports';G=T.parent/'polar-rl-train'
ID='mod4-final389-eval404-actual-ppo416-repair'
TAG='trial-20261102-'+ID
BASE=G/'versions/20261102_mod4-final389-eval404-actual-ppo416-repair'
V=BASE/'record420_actual_RL_failure_and_staged_actual_PPO'
H=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
read=lambda path:json.loads(path.read_bytes())
def put(path,value):
 with path.open('x',encoding='utf8')as stream:json.dump(value,stream,indent=2,ensure_ascii=False,allow_nan=False)
def git(*args):return subprocess.run(['git','-C',str(G),*args],capture_output=True,text=True,encoding='utf8',check=True).stdout.strip()
def refs(text):return{row.split()[1]:row.split()[0]for row in text.splitlines()}
assert not git('status','--porcelain')and git('branch','--show-current')=='main'
assert not V.exists()and not(R/'RECORD420_ONCE_CONSUMED_BEFORE_GIT.json').exists()
assert not git('tag','--list',TAG)
oldrefs=refs(git('show-ref','--tags','-d'));remote=refs(git('ls-remote','--tags','origin'))
assert all(remote.get(key)==value for key,value in oldrefs.items())
lqr=git('ls-remote','origin','refs/heads/lqr').split()[0]
assert lqr=='5848b45a99b8c32af02eb61b507c3f95ab39e4ad'
req=read(R/'AUTOMATION419_FINAL389_EVAL_FAIL_ACTUALPPO416_STAGED418_REQUEST.json')
cfg=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text('utf8'))
assert cfg['prompt']==req['prompt']and cfg['rrule']==req['rrule']and cfg['status']==req['status']=='ACTIVE'and cfg['target_thread_id']==req['targetThreadId']
put(R/'AUTOMATION419_SAVED_CONFIG_VERIFIED.json',dict(epoch=time.time(),passed=True,
 requestSHA=H(R/'AUTOMATION419_FINAL389_EVAL_FAIL_ACTUALPPO416_STAGED418_REQUEST.json'),
 toolreceiptSHA=H(R/'AUTOMATION419_APP_UPDATE_ACTUAL_TOOL_RECEIPT.json'),samehourlyACTIVEthread=True))
put(R/'RECORD420_ONCE_CONSUMED_BEFORE_GIT.json',dict(epoch=time.time(),phase=ID,tag=TAG,
 oldrefs=oldrefs,remote_before=remote,lqr=lqr,pushretry='Continueexistingobjects;neverrerunrecord/retag',
 final389actualevaluated=True,actualPPO416GO=False,firstowner418unused=True))
note=R/'RECORD420_FINAL389_EVAL404_FAILURE_ACTUAL_PPO416_REPAIR.md'
note.write_text('''用户明确要求“我需要的是rl上台阶”。本阶段完成最终389实际RL评测/真实姿态回放、有限匹配残差对照，并根据失败实施真实on-policy奖励和终止反馈进入actor的PPO修复。不是以传统MPC成功替代RL交付。原3900/save3600/exit300、唯一canonical、400N工程k2000/50policy100feedback400physics/.0025TGS32-4/fullD0whitev3D1-D7/10mm闭链单envreset/.01mimic/原PD、D4和DCclip保持。historicalH1原exactproducer资产、计划参考59输入与暂定相机保持，非自主depth-only毕业。

原postround396在13:19:54进入normal389时本地CIMassert拒绝，未网络/SDK/模型读取/控制；原false/日志/CONSUMED保留。独立399准备首次closedfinal collection，新knowncontroller busy期间本地等待，Pair2实际释放且freshCIM/serialFREE后成功正式收回最终389。原owner1458549/node1458558/worker1458572均ownwaited、原锁free、canonicalNone，原fee3603.927095413208s，closingbalance364018.99313402176只是收集时历史snapshot。final32801003B SHA c760f8c2e3441756e1d4f6912d019c6bcdaafa456bdf6e48a9ce152395776f99；3571controls285680ownpairs、Pi3508critic3508/newWM3540total20419，actorAdam56144critic13204WM20419，teacher17Adam42940STD/三Adam/EMA/normRNG/origin完整。新CPU389单次必要finaldecode618finite通过，无CUDA，已消费不重复读PT。

独立400实际SDK初始化后wheel_geometry220缺包，0checkpointdecode/0control，环境关闭ownchildwaited/private_sharedreleased/SSHFREE；原SDK退出RC0不被冒称成功，parent仍false/resultnull。403独立补依赖，但新Pair2retentioncollector出现，本地CIM拒绝0网络；随后离线发现旧globalversionreplacement会改写前馈JSON数字子串（训练原SHA2c7e2c67c6e2fc764b2f3e9ffe2cdd943604fbb23c8c004464c5ef19a42c262c，eval400/403字节SHA不同），原错误保留，没有让错误前馈运行。404改为精确复制训练389source/前馈/reference二进制和历史wheelhelper，版本仅命名token变化，不重写数据；资源释放且freshCIM/CNone/private_shared后实际执行。

实际404同fixededge.8/270/newDRseed9137/80firstepisodes/400controls8s、3200physics/800feedback，最终RLactor+savedorigin同checkpoint一次decode+固定表，无在线MPC/训练/账。结果0/80strict、0整轮footprintclear、6轮前缘progress、77姿态终止、3跑满8s、mean1.375s/median.99s。闭链/mimic/basecontact/lowbase0。所有actual400Hz台顶manifold和首次飞行整轮clear独立测量；6leading不是越台成功。当前模型已view_image真实记录bodypose图：env0/40约.98s、1/41约.9-.94s台前腾空后强倾倒，没有台顶恢复。405全80事实、406保存动作/q/dq/targets/phase与原生视觉审查已落盘。所选四case前20控制步残差已非零且左右不对称，pitch>.2约.64-.76s；只是假设线索，不称残差唯一因果。

为决定是否应缩小残差，407有限新40matchedDRpairs，同最终389网络/前馈/物理/验收，仅比较fullscale1与quarter.25。复用已实际377匹配helper：mass/inertia/material/COM/drive/armature/forcecap和D0-D7memory实际readback配对0差，首次q/dq/root/policy0差，depth约1.96695e-6差明确。新9217seed/绝对100Hz反馈共噪声、80firstepisodes400controls，0更新/账。full0/40strict、0整轮clear、1leading、36orientation4full8s/mean1.7055；quarter0/40strict、1整轮clear、8leading、39orientation1full8s/mean1.121。配对mean寿命-.5845s，无strictdiscordance，不能称缩小残差修好。contact float32轨迹不保证逐位同plant。407全部安全关闭/transfer/nativeframes；当前模型已原生看过四case仍台前倾倒。408真实比较报告保留。决定不原样再训389，也不把quarter作为成功修复。

代码核对得到明确算法差异：389actor only通过WM预测H8trackingcost反传，实际ownreward/done只训练critic，actor又无learnedterminal值；因此不能把criticactualTD说成actor已通过真实终止学习。新的409候选实现真正actualon-policy残差PPO：Gaussian latent mean=actor103-origin103，固定探索std.15，动作fixedbaseline+tanh(latent)clip6；收集32controls/2560实际ownr/done/logprob，gamma.99/GAE.95，oneepochclip.2，actor和critic沿真实样本更新，terminal无nextbootstrap。原reward仍exp(-同weightedtrackingcost/5)，不新增力矩克隆/在线MPC/奖励。WMH32仍独立自身训练但不作为actor梯度。保留最终389全部网络/三Adam/EMA/normRNG与原savedorigin，原learnedSTD/teacher17Adam冻结，不reset网络/Adam，不回退2135actor。CPU409新算法一次必要final389完整read恢复通过，no-step2560synthetic actorgrad13.79187298/critic3.21039486有限非零，终止returns.6/100且无WM/origin梯度、Adamsteps仍56144/13204/20419。只是CPU准入，未当物理成功。

410原部分生产包unused保留；414完成真实PPOworker/contract/originalowner/normal/fullCPU与独立415结束评测链，静态发现Windows读写行尾使learner字节SHA与CPU409不同，AST同但launcher会拒绝；414unused冻结保留。独立416字节复制CPU409learner，SHA75eef9597271a74b3070234868853ad029c7596de0a7c4a01f986b10a4983a2c精确；生产416冻结INDEX b1e843c8fa3b3e091857a61bc669296a14a0ef5a98ff8076945d429e5e95caeb，worker4257ba795a62542db8951234244d5a8664f2a2691bc8fa96aa267505d3516c0a，runACTUAL_RESIDUAL_PPO416_1793602132213517800。原物理/预算和exact sourcefinal389保持。417单localprocess经runpy正常收尾/evaldispatcher，避免ownpostroundparent被CIM子检查拒绝；其它knowncontroller仍挡，忙则localwait。FIRST实际PPOgrad/native24/fullsave通过才bind唯一417，原normal900/fullsave安全退出/formaltransfer/newfullCPU offsets56144/13204/20419/新41780firstepisodes400controls/manifold/真实pose原生render，结果还需当前模型view_image后主动修复续训。

416实际launch发生于Pair3训练和retention真实退出释放之后，freshlocalCIM/serialFREE/firstCNone/selectedGPUprivate_shared准入通过，所有source/task/control/reference/feedforward正式部署并postcopy通过。14:51:59另一聊天Pair4 W35/SLOPE_INDEPENDENT50恰好claim，416在14:52:04 secondfreshCNone、originalowner创建前被拒绝，0owner/node/GO/SDK/modelread/优化账；不是RL训练失败，不重放launch416、不复制namespace。SSHfinallyclosed/SESSIONrestore/FREE。本轮准备独立418只完成尚未发生的首次owner/node创建，先freshlocalexactCIM/serialFREE、freshCNone、原namespace无owner/node/GO与manifestexact验证，再private/sharedGPU准入/secondCNone后唯一原owner/node。418尚unused，INDEX6a7b5ad051883fa0edd37394bed9da86f7aedb4dd31491b4dee06f960a74e1e9，绝不烧busyonce或双writer。

目前Pair4localcollector66532/create2026-11-02T14:52:23.889806+08持SSH，parent1466964/create1793602319.06。419工作单和现mod4-10经真实automation_update已更新为final389已评0of80/416staged/418unused资源等待。下一先读Pair4实际closed/后续retention和广exactCIM，所有controller释放后run418，再收FIRST并绑定417。无变化静默，原错误/once不重放，无新Goal/chat/automation，原成功标准整轮首飞越沿/双轮actualtopmanifold/.5s稳定不放宽。

本record420作为新actualtransitionRL修复阶段，包含上个389阶段收尾/评测失败与全部中间source/false/raw/reader错误/400403/actual404407/409CPU/410414unused/416stagedrace/418unused/419handoff/automation；各自ID与独立事实保留，不改历史false。全部文本完整或既有同SHA引用，>45MB文本按20MB分片保留总SHA/片SHA，PT/NPZ/USD/media只真实pathbytes已有SHA，不为Git读权重/跑physics。凭据沿原memory不输出/入Git，旧record393object4e77ba7807787c22df7e8661c2f7801042cfc896/peel938b9ee8458f09a47e369995c8bfb1064b052a1f、398commitf0705ed2366481a6c512449afa9a513a173980a1与全部oldtagobjects/peels/lqr5848b45a99b8c32af02eb61b507c3f95ab39e4ad保护，push失败续existingobjects不重record/retag，postGit验证只工具输出。
''',encoding='utf8')

names=('MPC_COMMAND_RESIDUAL_RL_V389_20261102','RESIDUAL_RL389_POSTROUND_V396_20261102',
 'RESIDUAL_RL389_INDEPENDENT_EVAL_V396_20261102','RL389_CLOSED_FINAL_RECOVERY_V399_20261102',
 'RL389_RECOVERED_FINAL_INDEPENDENT_EVAL_V400_20261102','RL389_FINAL_EVAL_DEPENDENCY_REPAIR_V403_20261102',
 'RL389_EXACT_FINAL_INDEPENDENT_EVAL_V404_20261102','RL389_MATCHED_RESIDUAL_SCALE_DIAG_V407_20261102',
 'RL_ACTUAL_TRANSITION_PPO_REPAIR_V409_20261102','RL_ACTUAL_RESIDUAL_PPO_PRODUCTION_V410_20261102',
 'RL_ACTUAL_RESIDUAL_PPO_PRODUCTION_V414_20261102','RL414_SINGLE_PROCESS_POSTROUND_V415_20261102',
 'RL414_FINAL_INDEPENDENT_EVAL_V415_20261102','RL_ACTUAL_RESIDUAL_PPO_PRODUCTION_V416_20261102',
 'RL416_SINGLE_PROCESS_POSTROUND_V417_20261102','RL416_FINAL_INDEPENDENT_EVAL_V417_20261102',
 'RL416_STAGED_FIRST_OWNER_RECOVERY_V418_20261102')
roots=[(P.name,P)]+[(name,T/name)for name in names]
F=Path('F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/POSTTRAIN_EIGHT_EXCLUDING_H1_20261102')
for name in('reports/ORIGINAL_AUTHORITY_RELEASE_AFTER389_WATCH_RESULT.json',
 'reports/PAIR2_GENERIC_V2_ACTUAL_FIRST_ADMISSION_SNAPSHOT.json','PAIR2_GENERIC_V2_ORIGINAL_OWNER_DISPATCH_ONCE.json',
 'PAIR2_GENERIC_V2_LATEST_CLOSED_RESULT_PATH.json','PAIR2_FROZEN_RETENTION_V1_DISPATCH_ONCE.json',
 'PAIR2_FROZEN_RETENTION_V1_LATEST_CLOSED_RESULT_PATH.json','PAIR3_GENERIC_V2_ORIGINAL_OWNER_DISPATCH_ONCE.json',
 'reports/PAIR3_GENERIC_V2_ACTUAL_FIRST_ADMISSION_SNAPSHOT.json','PAIR3_GENERIC_V2_LATEST_CLOSED_RESULT_PATH.json',
 'PAIR3_FROZEN_RETENTION_V1_DISPATCH_ONCE.json','PAIR3_FROZEN_RETENTION_V1_LATEST_CLOSED_RESULT_PATH.json',
 'PAIR4_GENERIC_V2_ORIGINAL_OWNER_DISPATCH_ONCE.json','reports/PAIR4_GENERIC_V2_ACTUAL_FIRST_ADMISSION_SNAPSHOT.json'):
 path=F/name
 if path.exists():roots.append(('resource_evidence',path))
for prefix in('PAIR2_GENERIC_V2','PAIR2_FROZEN_RETENTION_V1','PAIR3_GENERIC_V2','PAIR3_FROZEN_RETENTION_V1'):
 pointer=F/(prefix+'_LATEST_CLOSED_RESULT_PATH.json')
 if pointer.exists():roots.append(('resource_evidence',Path(read(pointer)['path'])))
known={};identities={}
for base in(G/'versions/20261102_mod4-residual-rl389-command-handoff',
 G/'versions/20261102_mod4-mpc-control-handoff339-349',
 G/'versions/20261102_mod4-init311-paired317-short-h4-tracking-repair324',
 G/'versions/20261102_mod4-final305-recovery-eval308-targeted-repair307'):
 for path in base.rglob('*CAPTURE_INDEX*.json'):
  for row in read(path).get('files',[]):
   if row.get('SHA')and row.get('Git_path')and(G/row['Git_path']).is_file()and row.get('capture')in('full_UTF8_byte_exact','full_same_SHA_reference'):
    known.setdefault(row['SHA'],row['Git_path'])
def collect(value,receipt):
 if isinstance(value,dict):
  sha=value.get('SHA')or value.get('sha256');size=value.get('bytes')
  if isinstance(sha,str)and len(sha)==64 and all(char in'0123456789abcdef'for char in sha)and isinstance(size,int):
   for key in('path','local_path','source','remote_path'):
    if isinstance(value.get(key),str):identities.setdefault((value[key].replace(chr(92),'/'),size),(sha,receipt))
  for item in value.values():collect(item,receipt)
 elif isinstance(value,list):
  for item in value:collect(item,receipt)
for label,root in roots:
 assert root.exists(),str(root)
 for path in([root]if root.is_file()else sorted(root.rglob('*.json'))):
  try:collect(read(path),str(path))
  except(ValueError,UnicodeDecodeError):pass
sys.path.insert(0,str(G/'archive_tools'));from capture_history import redact
binary={'.pt','.pth','.npz','.npy','.png','.jpg','.jpeg','.mp4','.usd','.usda','.usdc','.stl','.obj','.zip','.gz','.pyc'}
texts={'.py','.json','.md','.txt','.log','.xml','.toml','.sh','.ps1','.csv','.tsv','.yaml','.yml'}
V.mkdir(parents=True);(V/'.gitattributes').write_text('* -text\n',encoding='utf8');rows=[];heavy=[]
for label,root in roots:
 for path in([root]if root.is_file()else sorted(root.rglob('*'))):
  if not path.is_file()or'__pycache__'in path.parts:continue
  size=path.stat().st_size;relative=Path(label)/(path.name if root.is_file()else path.relative_to(root))
  if path.suffix.lower()in binary:
   item=identities.get((str(path).replace(chr(92),'/'),size));heavy.append(dict(path=str(path),bytes=size,
    SHA=item[0]if item else'unknown:noarchiveonlybinaryhash',SHA_receipt=item[1]if item else None,capture='metadata_only_no_content_or_hash_for_Git'));continue
  assert path.suffix.lower()in texts,str(path)
  raw=path.read_bytes();sha=hashlib.sha256(raw).hexdigest()
  if sha in known:rows.append(dict(path=str(path),bytes=len(raw),SHA=sha,Git_path=known[sha],capture='full_same_SHA_reference'));continue
  safe,count=redact(raw.decode('utf8'));data=raw if count==0 else safe.encode('utf8');dest=V/relative;dest.parent.mkdir(parents=True,exist_ok=True)
  if dest.exists():
   # Different resource folders can have CLOSED_RESULT.json basenames.
   dest=dest.with_name(dest.stem+'_'+sha[:12]+dest.suffix)
  if len(data)>45*1024*1024:
   parts=[]
   for i,start in enumerate(range(0,len(data),20*1024*1024)):
    b=data[start:start+20*1024*1024];part=dest.with_name(dest.name+f'.part{i:03d}.txt');part.write_bytes(b);parts.append(dict(Git_path=part.relative_to(G).as_posix(),bytes=len(b),SHA=hashlib.sha256(b).hexdigest()))
   rows.append(dict(path=str(path),bytes=len(raw),SHA=sha,archive_SHA=hashlib.sha256(data).hexdigest(),redactions=count,capture='full_UTF8_byte_sequence_chunked',parts=parts,reassemble='Concatenate listedparts and verify totalarchiveSHA'));continue
  dest.write_bytes(data);gp=dest.relative_to(G).as_posix();rows.append(dict(path=str(path),bytes=len(raw),SHA=sha,Git_path=gp,archive_SHA=hashlib.sha256(data).hexdigest(),redactions=count,capture='credential_pattern_redacted'if count else'full_UTF8_byte_exact'))
  if not count:known[sha]=gp
put(V/'CAPTURE_INDEX_RECORD420.json',dict(epoch=time.time(),phase=ID,files=rows,large_artifacts=heavy,
 oldrefs=oldrefs,remote_before=remote,lqr=lqr,all_saved_text_reports_full_sameSHA_or_completechunks=True,
 final389actualevaluated=True,actualPPO416GO=False,firstowner418unused=True,no_model_reads_for_archive=True))
files=[path.relative_to(G).as_posix()for path in sorted(V.rglob('*'))if path.is_file()]
import record_experiment
original_git=record_experiment.git
def exact_directory_add(*args):
 if len(args)>=2 and args[:2]==('add','--'):
  record=args[2];selected=set(args[3:]);assert selected==set(files)
  result=original_git('add','--',record,V.relative_to(G).as_posix())
  assert set(original_git('diff','--cached','--name-only').splitlines())==selected|{record}
  return result
 return original_git(*args)
record_experiment.git=exact_directory_add
sys.argv=['record_experiment.py','--id',ID,'--title','Evaluate final residual RL389 failure and prepare actual-transition PPO416 repair','--kind','repair','--note-file',str(note),
 '--validation','389closed618finite;404actual0of80strict/native reviewed;40740matchedpairsboth0strict/native reviewed;CPU409fullrestoreactualPPOgradterminalGAEnostep;416stagedauthorityracebeforeowner0GO;418unused;allerrorspreserved','--files',*files]
record_experiment.main()
head=git('rev-parse','HEAD');obj=git('rev-parse','refs/tags/'+TAG);peel=git('rev-parse','refs/tags/'+TAG+'^{}');assert peel==head
git('push','--atomic','origin','HEAD:refs/heads/main','refs/tags/'+TAG)
after=refs(git('show-ref','--tags','-d'));remote_after=refs(git('ls-remote','--tags','origin'))
assert all(after.get(key)==value and remote_after.get(key)==value for key,value in oldrefs.items())
assert all(remote_after.get(key)==value for key,value in remote.items())
assert remote_after['refs/tags/'+TAG]==obj and remote_after['refs/tags/'+TAG+'^{}']==head
assert git('ls-remote','origin','refs/heads/main').split()[0]==head
assert git('ls-remote','origin','refs/heads/lqr').split()[0]==lqr and not git('status','--porcelain')
print(json.dumps(dict(passed=True,HEAD=head,remote_main=head,tag=TAG,tagobject=obj,peel=peel,
 files=len(files),indexed=len(rows),heavy_metadata=len(heavy),chunked=sum(row['capture']=='full_UTF8_byte_sequence_chunked'for row in rows),
 oldrefsprotected=True,lqr=lqr,clean=True,final389actualstrict0=True,actual416GO=False,firstowner418unused=True)),flush=True)
