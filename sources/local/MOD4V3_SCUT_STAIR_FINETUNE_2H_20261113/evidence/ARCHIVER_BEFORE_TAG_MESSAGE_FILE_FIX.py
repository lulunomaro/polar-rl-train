"""Archive this authorized run's source/evidence and ordinary full checkpoint blobs."""
from pathlib import Path
import sys,json,hashlib,tempfile,subprocess,argparse,time
T=Path(__file__).resolve().parent;R=T.parents[2];a=argparse.ArgumentParser();a.add_argument('--phase',choices=['launch','complete'],required=True);phase=a.parse_args().phase
ID='mod4-scut-stair-finetune-2h-'+phase+'-01';TAG='trial-20261113-'+ID;SYNC_ID='mod4-scut-stair-finetune-2h-'+phase+'-sync-01';SYNC_TAG='trial-20261113-'+SYNC_ID
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
files=[]
for p in sorted(T.rglob('*')):
 if not p.is_file() or '__pycache__' in p.parts or p.suffix in {'.pyc','.partial'} or 'kit_isolation' in p.parts:continue
 rel=p.relative_to(T)
 if rel.as_posix() in {'monitor.log','monitor_error.log','start.log','start_error.log','evidence/finalize.log','evidence/ARCHIVE_COMPLETE.log','evidence/ARCHIVE_LAUNCH.log'}:continue
 if p.name in {f'ARCHIVE_MANIFEST_{phase.upper()}.json',f'GIT_{phase.upper()}_RECEIPT.json'}:continue
 if phase=='launch' and rel.as_posix() in {'evidence/MONITOR_STATUS.json','evidence/MODEL_COLLECTION.json','evidence/EVALUATION_QUEUE.json','evidence/INSPECTIONS.jsonl'}:continue
 if phase=='launch':
  keep=(len(rel.parts)==1 or rel.parts[0] in {'support','retention_eval_terrain','reference','weights'} or (rel.parts[0]=='evidence' and len(rel.parts)>1 and rel.parts[1] not in {'training','inspections','checkpoint_evals'}))
  if not keep:continue
 files.append(p)
# Include every immutable original-segment model/source/report, including failed probes.
previous=R/json.loads((T/'PLAN.json').read_text(encoding='utf8'))['previous_stage']
for item in sorted(previous.rglob('*')):
 if not item.is_file() or '__pycache__' in item.parts or item.suffix in {'.pyc','.partial'} or 'kit_isolation' in item.parts:continue
 if item.relative_to(previous).as_posix() in {'monitor.log','monitor_error.log','evidence/finalize.log','evidence/ARCHIVE_COMPLETE.log','evidence/ARCHIVE_LAUNCH.log'}:continue
 files.append(item)
files += [R/'README.md',R/'docs/DR_TRAINING_INDEX_20261111.md']
if phase=='complete':files += [R/'sources/local/MOD4V3_DR_TRAINING_RECORDS_20261111/MODEL_REGISTRY.json',R/'sources/local/MOD4V3_DR_TRAINING_RECORDS_20261111/MODELS.md']
rows=[dict(path=p.relative_to(R).as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in files]
manifest=T/'evidence'/f'ARCHIVE_MANIFEST_{phase.upper()}.json';manifest.write_text(json.dumps(dict(phase=phase,files=rows,total_bytes=sum(r['bytes'] for r in rows),excluded='derived caches/partial files/active collector stdout/future receipt; launch excludes live progression/evals'),ensure_ascii=False,indent=2)+'\n',encoding='utf8');files.append(manifest)
binary=[p.relative_to(R).as_posix() for p in files if p.suffix in {'.pt','.pth','.npz','.npy','.png','.gif','.msh'}];text=[p.relative_to(R).as_posix() for p in files if p.relative_to(R).as_posix() not in binary]
sys.path.insert(0,str(R.parent/'tmp/step7_archive_helper'));import record_experiment as rec
original=rec.git;record=R/'history/experiments'/('20261113-'+ID+'.json');active_binary=binary.copy()
def proxy(*args):
 if args[0]=='add':
  if active_binary:
   data=json.loads(record.read_text(encoding='utf8'))
   for name in active_binary:data['source_and_evidence_sha256'][name]=hashlib.sha256((R/name).read_bytes()).hexdigest()
   data['artifact_storage']='Human-authorized ordinary complete PT/NPZ/mesh/figure blobs; actual full PPO files, no LFS pointers. Source, successful/failed probes and raw trajectories retained.';record.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
  names=[s for s in args[1:] if s!='--']+active_binary
  with tempfile.NamedTemporaryFile(mode='wb',prefix='continuous-stair-archive-',dir=R.parent/'tmp',delete=False) as f:
   for name in dict.fromkeys(names):f.write(name.encode('utf8')+b'\0')
   spec=Path(f.name)
  try:return original('--literal-pathspecs','-c','http.proxy=http://127.0.0.1:7897','-c','http.sslVerify=true','add','--sparse','-f','--pathspec-from-file='+str(spec),'--pathspec-file-nul')
  finally:spec.unlink()
 return original('-c','http.proxy=http://127.0.0.1:7897','-c','http.sslVerify=true',*args)
rec.git=proxy
note=T/('README.md' if phase=='launch' else 'FINAL_REPORT.md')
validation=('Fresh SCUT-method7200s from iter24692 network/STD weights with newAdam/seed/iteration0;13.33wide/66.67otherRough/20flat; wide uses saved successful-stair reward and no-air mask; shaping diagnostics only; new2048env native functional probe; original plant/controller/perenvguards; no graduation claim' if phase=='launch' else 'Fresh bounded7200s round and every fullPT; fixed stair/flat60 and originalRough paired retention with failures and incomplete cases reported; superseded prior experiment archived separately; no automatic promotion')
sys.argv=['record_experiment.py','--id',ID,'--title',('Launch' if phase=='launch' else 'Archive')+' SCUT-method7200s stair finetune with original Rough-v1 retention','--kind','training','--note-file',str(note),'--validation',validation,'--files',*text];rec.main();source=git('rev-parse','HEAD');assert git('rev-parse',TAG+'^{}')==source
git('push','--atomic','origin','HEAD','refs/tags/'+TAG);remote=refs(TAG);assert remote['refs/heads/'+branch]==source and remote['refs/tags/'+TAG]==git('rev-parse',TAG) and remote['refs/tags/'+TAG+'^{}']==source and remote['refs/heads/main']==main_before
verified=[]
for name in binary:
 raw=subprocess.run([*BASE,'show',source+':'+name],capture_output=True,check=True).stdout;assert len(raw)==(R/name).stat().st_size and hashlib.sha256(raw).digest()==hashlib.sha256((R/name).read_bytes()).digest(),name;assert not raw.startswith(b'version https://git-lfs.github.com/spec/');verified.append(dict(path=name,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),ordinary_full_blob=True))
receipt=T/'evidence'/f'GIT_{phase.upper()}_RECEIPT.json';receipt.write_text(json.dumps(dict(epoch=time.time(),phase=phase,payload_commit=source,tag=TAG,proxy='http://127.0.0.1:7897',TLS_verify=True,remote_refs=remote,main_before=main_before,main_after=remote['refs/heads/main'],full_binary_artifacts=verified,training_state='running' if phase=='launch' else 'closed; see final report'),ensure_ascii=False,indent=2)+'\n',encoding='utf8')
active_binary=[];sys.argv=['record_experiment.py','--id',SYNC_ID,'--title','Record verified stair plus Rough-v1 retention '+phase+' upload','--kind','training','--note-file',str(receipt),'--validation','Branch/tag/peeled and complete ordinary binary blobs verified;7897proxy/TLS;main unchanged','--files',receipt.relative_to(R).as_posix(),'--push'];rec.main();sync=git('rev-parse','HEAD');remote=refs(TAG,SYNC_TAG);assert remote['refs/heads/'+branch]==sync and remote['refs/tags/'+TAG+'^{}']==source and remote['refs/tags/'+SYNC_TAG+'^{}']==sync and remote['refs/heads/main']==main_before
print(json.dumps(dict(phase=phase,payload_commit=source,sync_commit=sync,payload_tag=TAG,sync_tag=SYNC_TAG,verified_full_PT=sum(x['path'].endswith('.pt') for x in verified),verified_binary=len(verified),remote_refs=remote),ensure_ascii=False),flush=True)
