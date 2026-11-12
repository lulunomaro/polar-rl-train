"""Archive the completed frozen motion audit and a separately committed upload receipt."""
from pathlib import Path
import json,hashlib,subprocess,sys,tempfile,time
T=Path(__file__).resolve().parent;R=T.parents[2];ID='mod4-stair-motion-audit-01';TAG='trial-20261113-'+ID;SYNC_ID='mod4-stair-motion-sync-01';SYNC_TAG='trial-20261113-'+SYNC_ID
BASE=['git','-C',str(R),'-c','http.proxy=http://127.0.0.1:7897','-c','http.sslVerify=true']
def git(*args):
 p=subprocess.run([*BASE,*args],capture_output=True,text=True,encoding='utf8',errors='replace')
 if p.returncode:raise RuntimeError('Git '+args[0]+': '+p.stderr)
 return p.stdout.strip()
branch=git('branch','--show-current');assert branch=='mod4v1-experts-fulldr-rm70'
def refs(*tags):
 names=['refs/heads/'+branch,'refs/heads/main']
 for tag in tags:names.extend(['refs/tags/'+tag,'refs/tags/'+tag+'^{}'])
 return {line.split()[1]:line.split()[0] for line in git('ls-remote','origin',*names).splitlines()}
main_before=refs()['refs/heads/main']
files=[p for p in sorted(T.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p.suffix not in {'.pyc','.partial'} and p.relative_to(T).as_posix() not in {'evidence/FULL_ARTIFACT_MANIFEST.json','evidence/GIT_PUSH_RECEIPT.json','SYNC_REPORT.md'}]
files += [R/'README.md',R/'docs/DR_TRAINING_INDEX_20261111.md']
rows=[dict(path=p.relative_to(R).as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in files]
manifest=T/'evidence/FULL_ARTIFACT_MANIFEST.json';manifest.write_text(json.dumps(dict(scope='Completed source,raw contact JSONL,all nominal success/failure trajectories,display-only figures,and navigation docs;self hash and future sync receipt excluded',files=rows,total_bytes=sum(x['bytes'] for x in rows),new_weights=0),ensure_ascii=False,indent=2)+'\n',encoding='utf8');files.append(manifest)
binary=[p.relative_to(R).as_posix() for p in files if p.suffix in {'.npz','.png','.gif','.msh','.npy'}]
text=[p.relative_to(R).as_posix() for p in files if p.relative_to(R).as_posix() not in binary]
sys.path.insert(0,str(R.parent/'tmp/step7_archive_helper'));import record_experiment as rec
original=rec.git
record_path=R/'history/experiments'/('20261113-'+ID+'.json')
active_binary=binary.copy()
def proxy(*args):
 if args[0]=='add':
  if active_binary:
   data=json.loads(record_path.read_text(encoding='utf8'))
   for name in active_binary:data['source_and_evidence_sha256'][name]=hashlib.sha256((R/name).read_bytes()).hexdigest()
   data['artifact_storage']='Human-authorized complete original NPZ trajectories/terrain,meshes,PNG and GIF as ordinary full Git blobs; all raw contact JSONL retained. No new PT; exact full selected PT already in earlier repair payload and linked by path/SHA.'
   record_path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
  names=[s for s in args[1:] if s!='--']+active_binary
  with tempfile.NamedTemporaryFile(mode='wb',prefix='motion-audit-',dir=R.parent/'tmp',delete=False) as f:
   for name in dict.fromkeys(names):f.write(name.encode('utf8')+b'\0')
   spec=Path(f.name)
  try:return original('--literal-pathspecs','-c','http.proxy=http://127.0.0.1:7897','-c','http.sslVerify=true','add','--sparse','-f','--pathspec-from-file='+str(spec),'--pathspec-file-nul')
  finally:spec.unlink()
 return original('-c','http.proxy=http://127.0.0.1:7897','-c','http.sslVerify=true',*args)
rec.git=proxy
sys.argv=['record_experiment.py','--id',ID,'--title','Analyze frozen continuous stair motion with contact forces and leg-wheel kinematics','--kind','diagnostic','--note-file',str(T/'REPORT.md'),'--validation','Four fixed nominal MuJoCo cases;2raisedfast pass,raisedslow/lowfast fail by12s;all0resets;original successful trajectories unchanged;front15mm guide wheels support,nose-down36deg,retract-land-recover-reaccelerate;minimum0.09m/s reclassified as climbing/landing;half-speedGIF,fullraw,25.8deg oldreward gate mismatch recorded;no optimizer or training;plant/PT unchanged','--files',*text,'--push']
rec.main();source=git('rev-parse','HEAD');assert git('rev-parse',TAG+'^{}')==source
remote=refs(TAG);assert remote['refs/heads/'+branch]==source and remote['refs/tags/'+TAG]==git('rev-parse',TAG) and remote['refs/tags/'+TAG+'^{}']==source and remote['refs/heads/main']==main_before
verified=[]
for name in binary:
 raw=subprocess.run([*BASE,'show',source+':'+name],capture_output=True,check=True).stdout
 assert len(raw)==(R/name).stat().st_size and hashlib.sha256(raw).digest()==hashlib.sha256((R/name).read_bytes()).digest(),name
 assert not raw.startswith(b'version https://git-lfs.github.com/spec/')
 verified.append(dict(path=name,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),ordinary_full_blob=True))
receipt=dict(epoch=time.time(),payload_commit=source,tag=TAG,branch=branch,proxy='http://127.0.0.1:7897',TLS_verify=True,remote_refs=remote,main_before=main_before,main_after=remote['refs/heads/main'],full_binary_artifacts=verified,no_training=True,robot_and_selected_PT_unchanged=True)
(T/'evidence/GIT_PUSH_RECEIPT.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
(T/'SYNC_REPORT.md').write_text(f'''# 连续上台阶动作调查同步回执

四例冻结回放的成功/失败、400Hz动作/接触/功率原始数组、完整contact JSONL、源码、源快照、曲线、八帧图和半速GIF均已通过7897代理上传，TLS开启。Payload提交{source}，annotated tag {TAG}。

远端branch/tag对象/peeled一致；{len(verified)}个二进制原件从Git提交对象完整读回，大小/SHA与原件一致，不是指针。main保持{main_before}。无训练或优化器更新，原权重和plant未修改，原成熟包与实验候选身份不变。

本回执单独提交并推送；最后远端核验仅作为工具输出保留。
''',encoding='utf8')
active_binary=[]
sys.argv=['record_experiment.py','--id',SYNC_ID,'--title','Record verified frozen stair motion audit upload','--kind','diagnostic','--note-file',str(T/'SYNC_REPORT.md'),'--validation','Remote branch/tag/peeled and full raw binary artifacts verified;7897proxy/TLS;main unchanged;no training;original plant and selected PT retained','--files',(T/'evidence/GIT_PUSH_RECEIPT.json').relative_to(R).as_posix(),(T/'SYNC_REPORT.md').relative_to(R).as_posix(),'--push']
rec.main();sync=git('rev-parse','HEAD');remote=refs(TAG,SYNC_TAG)
assert remote['refs/heads/'+branch]==sync and remote['refs/tags/'+TAG]==git('rev-parse',TAG) and remote['refs/tags/'+TAG+'^{}']==source
assert remote['refs/tags/'+SYNC_TAG]==git('rev-parse',SYNC_TAG) and remote['refs/tags/'+SYNC_TAG+'^{}']==sync and remote['refs/heads/main']==main_before
print(json.dumps(dict(payload_commit=source,sync_commit=sync,payload_tag=TAG,sync_tag=SYNC_TAG,full_binary_files=len(verified),remote_refs=remote),ensure_ascii=False),flush=True)
