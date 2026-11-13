"""Append specialist-stage evidence and user-authorized complete ordinary PT blobs."""
from pathlib import Path
import sys,json,hashlib,tempfile,subprocess,argparse,time
T=Path(__file__).resolve().parent;R=T.parents[2]
a=argparse.ArgumentParser();a.add_argument('--phase',choices=['freeze','launch','complete','student-launch','student-complete'],required=True);phase=a.parse_args().phase
ID='mod4-stair-specialist-'+phase+'-01';TAG='trial-20261113-'+ID;SYNC_ID=ID+'-sync';SYNC_TAG='trial-20261113-'+SYNC_ID
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
main_before=refs()['refs/heads/main'];files=[]
for p in sorted(T.rglob('*')):
 if not p.is_file() or '__pycache__' in p.parts or p.suffix in {'.pyc','.partial'} or 'kit_isolation' in p.parts:continue
 rel=p.relative_to(T).as_posix()
 if rel.startswith(('runtime/','cache/','tmp/')) or p.name.endswith(('_error.log','_worker.log')) or rel in {'monitor.log','monitor_error.log','evidence/finalize.log'} or p.name.startswith('ARCHIVE_'):continue
 if phase=='freeze' and not (rel.startswith('frozen_parent/') or rel in {'README.md','archive_run.py'}):continue
 if p.name==f'GIT_{phase.upper()}_RECEIPT.json':continue
 if phase=='launch' and (rel.startswith('evidence/training/') or rel.startswith('evidence/checkpoint_evals/') or rel in {'evidence/MONITOR_STATUS.json','evidence/MODEL_COLLECTION.json','evidence/EVALUATION_QUEUE.json','evidence/INSPECTIONS.jsonl'}):continue
 files.append(p)
if phase!='freeze':
 for extra in ['README.md','docs/DR_TRAINING_INDEX_20261111.md','sources/local/MOD4V3_DR_TRAINING_RECORDS_20261111/MODEL_REGISTRY.json','sources/local/MOD4V3_DR_TRAINING_RECORDS_20261111/README.md']:
  if (R/extra).is_file():files.append(R/extra)
binary=[p.relative_to(R).as_posix() for p in files if p.suffix.lower() in {'.pt','.pth','.npz','.npy','.onnx','.png','.jpg','.usd','.usda','.stl','.obj'}]
text=[p.relative_to(R).as_posix() for p in files if p.relative_to(R).as_posix() not in binary]
sys.path.insert(0,str(R.parent/'tmp/step7_archive_helper'));import record_experiment as rec
original=rec.git;record=R/'history/experiments'/('20261113-'+ID+'.json');active_binary=binary.copy()
def proxy(*args):
 if args[0]=='add':
  if active_binary:
   data=json.loads(record.read_text(encoding='utf8'))
   for name in active_binary:data['source_and_evidence_sha256'][name]=hashlib.sha256((R/name).read_bytes()).hexdigest()
   data['artifact_storage']='Explicit user request: actual complete ordinary PT blobs, never LFS pointers; physical assets/interfaces unchanged.';record.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
  names=[s for s in args[1:] if s!='--']+active_binary
  with tempfile.NamedTemporaryFile(mode='wb',prefix='specialist-archive-',dir=R.parent/'tmp',delete=False) as f:
   for name in dict.fromkeys(names):f.write(name.encode('utf8')+b'\0')
   spec=Path(f.name)
  try:return original('--literal-pathspecs','-c','http.proxy=http://127.0.0.1:7897','-c','http.sslVerify=true','add','--sparse','-f','--pathspec-from-file='+str(spec),'--pathspec-file-nul')
  finally:spec.unlink()
 if args[0]=='tag' and '-m' in args:
  index=args.index('-m')
  with tempfile.NamedTemporaryFile(mode='w',encoding='utf8',newline='\n',prefix='specialist-tag-',dir=R.parent/'tmp',delete=False) as f:f.write(args[index+1]);message_file=Path(f.name)
  try:return original('-c','http.proxy=http://127.0.0.1:7897','-c','http.sslVerify=true',*args[:index],'-F',str(message_file),*args[index+2:])
  finally:message_file.unlink()
 return original('-c','http.proxy=http://127.0.0.1:7897','-c','http.sslVerify=true',*args)
rec.git=proxy
note=T/('FINAL_REPORT.md' if phase=='complete' else 'README.md')
validation='Frozen comprehensive parent db6e9ccf iter25331 preserved as full PPO; separate200mmx2 stair specialist with genuine oblique approach; same approved MOD4/35-78-6/fullDR/controller/2mm per-env protection;40m budget and5m full checkpoints; see stage evidence for actual executed status'
sys.argv=['record_experiment.py','--id',ID,'--title','MOD4 stair specialist '+phase+' and frozen best parent','--kind','training','--note-file',str(note),'--validation',validation,'--files',*text];rec.main();source=git('rev-parse','HEAD');assert git('rev-parse',TAG+'^{}')==source
git('push','--atomic','origin','HEAD','refs/tags/'+TAG);remote=refs(TAG);assert remote['refs/heads/'+branch]==source and remote['refs/tags/'+TAG]==git('rev-parse',TAG) and remote['refs/tags/'+TAG+'^{}']==source and remote['refs/heads/main']==main_before
verified=[]
for name in binary:
 raw=subprocess.run([*BASE,'show',source+':'+name],capture_output=True,check=True).stdout;assert hashlib.sha256(raw).digest()==hashlib.sha256((R/name).read_bytes()).digest(),name;assert not raw.startswith(b'version https://git-lfs.github.com/spec/');verified.append(dict(path=name,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),ordinary_full_blob=True))
receipt=T/'evidence'/f'GIT_{phase.upper()}_RECEIPT.json';receipt.write_text(json.dumps(dict(epoch=time.time(),phase=phase,payload_commit=source,tag=TAG,proxy='http://127.0.0.1:7897',TLS_verify=True,remote_refs=remote,main_before=main_before,main_after=remote['refs/heads/main'],full_binary_artifacts=verified),ensure_ascii=False,indent=2)+'\n',encoding='utf8')
active_binary=[];sys.argv=['record_experiment.py','--id',SYNC_ID,'--title','Record verified stair specialist '+phase+' upload','--kind','training','--note-file',str(receipt),'--validation','Branch/tag/peeled plus complete ordinary binary blobs verified through7897proxy;main preserved','--files',receipt.relative_to(R).as_posix(),'--push'];rec.main();sync=git('rev-parse','HEAD');remote=refs(TAG,SYNC_TAG);assert remote['refs/heads/'+branch]==sync and remote['refs/tags/'+TAG+'^{}']==source and remote['refs/tags/'+SYNC_TAG+'^{}']==sync and remote['refs/heads/main']==main_before
print(json.dumps(dict(phase=phase,payload_commit=source,sync_commit=sync,verified_full_PT=sum(x['path'].endswith('.pt') for x in verified),remote_refs=remote),ensure_ascii=False),flush=True)
