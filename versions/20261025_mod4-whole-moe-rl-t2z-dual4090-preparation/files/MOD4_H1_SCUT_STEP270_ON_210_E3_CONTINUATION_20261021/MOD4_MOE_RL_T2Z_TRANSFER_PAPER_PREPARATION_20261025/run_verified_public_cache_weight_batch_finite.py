"""One bounded anonymous download batch to72, original pinned content hashes."""
from pathlib import Path
import argparse,base64,hashlib,importlib.util,json,os,sys,time,traceback
Z=Path(__file__).resolve().parent;T=Z.parent;W=T.parent;R=Z/'reports'
p=argparse.ArgumentParser();p.add_argument('batch',choices=[str(i).zfill(2) for i in range(1,21)]);args=p.parse_args();batch=args.batch
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
CODE=r'''
from pathlib import Path
import base64,hashlib,json,os,shutil,subprocess,time
B=Path('/home/lc01/Zonglin Li/zonglin2/research/T2Z_MOE_RL_TRANSFER_PREP_20261025');R=B/'receipts';ID='VERIFIED_PUBLIC_CACHE_BATCH_'+v['batch']
assert B.resolve()==B and shutil.disk_usage(B).free>25*1024**3
with (R/(ID+'_STARTED.json')).open('x') as f:json.dump(dict(epoch=time.time(),bounded_seconds=300,max_new_bytes=8*1024**3,official_expected_hashes_unchanged=True),f,indent=2)
source=base64.b64decode(v['source']);assert hashlib.sha256(source).hexdigest()==v['SHA']
folder=B/'preparation_helpers/public_cache_v2';folder.mkdir(parents=True,exist_ok=True);script=folder/'download_verified_public_cache_fallback_v2.py'
if script.exists():assert script.read_bytes()==source
else:
 with script.open('xb') as f:f.write(source)
manifest=B/'engineering_bundle/WEIGHTS_MANIFEST.json';assert hashlib.sha256(manifest.read_bytes()).hexdigest()=='4f9cf65f3f42dae7c8897ea571898f923e93ebc8522c97940ce69568d30c5ca7'
before={p.name for p in R.glob('*_download_*.json')}
env={k:os.environ[k] for k in ('PATH','HOME','USER','LANG','LC_ALL','SSL_CERT_FILE','SSL_CERT_DIR') if k in os.environ};env.update(CUDA_VISIBLE_DEVICES='',NVIDIA_VISIBLE_DEVICES='none',PYTHONDONTWRITEBYTECODE='1',OMP_NUM_THREADS='1',HF_HUB_DISABLE_IMPLICIT_TOKEN='1')
cmd=['nice','-n','19',str(B/'run-t2z-python.sh'),'-B',str(script),'--manifest',str(manifest),'--max-seconds','300','--max-files','13','--max-new-bytes',str(8*1024**3)]
t=time.time()
try:
 p=subprocess.run(cmd,cwd=B,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=420);rc=p.returncode;raw=p.stdout
except subprocess.TimeoutExpired as e:rc=124;raw=e.stdout or b''
with (R/(ID+'_STDOUT_STDERR.log')).open('xb') as f:f.write(raw)
fresh=[p for p in R.glob('*_download_*.json') if p.name not in before]
value=dict(epoch=time.time(),actual_returncode=rc,elapsed_seconds=time.time()-t,new_download_receipt_count=len(fresh),no_model_load_GPU_training_or_budget_change=True,root=str(B))
if len(fresh)==1:value['downloader']=json.loads(fresh[0].read_bytes())
with (R/(ID+'_FINAL.json')).open('x') as f:json.dump(value,f,indent=2)
value['texts']=[]
for p in sorted(R.rglob('*')):
 if p.is_file() and p.suffix in ('.json','.jsonl','.log','.txt','.py','.md','.csv') and '__pycache__' not in p.parts:
  data=p.read_bytes();value['texts'].append(dict(relative=p.relative_to(R).as_posix(),path=str(p),bytes=len(data),SHA=hashlib.sha256(data).hexdigest(),base64=base64.b64encode(data).decode()))
print(json.dumps(value))
'''
try:
 put('HOST72_VERIFIED_PUBLIC_CACHE_BATCH_'+batch+'_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv))
 source=(Z/'root_preparation_sources/download_verified_public_cache_fallback_v2.py').read_bytes()
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 spec=importlib.util.spec_from_file_location('memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);secret=m.recover();c=d.connect72(secret);secret=None
 try:value=d.code(c,d.PY72,CODE,dict(batch=batch,source=base64.b64encode(source).decode(),SHA=hashlib.sha256(source).hexdigest()),timeout=480)
 finally:c.close()
 dest=Z/'actual_host72_preparation_texts'/('verified_public_cache_batch_'+batch);dest.mkdir()
 for row in value['texts']:
  data=base64.b64decode(row.pop('base64'));assert len(data)==row['bytes'] and hashlib.sha256(data).hexdigest()==row['SHA'];rel=Path(row['relative']);assert not rel.is_absolute() and '..' not in rel.parts;target=dest/rel;target.parent.mkdir(parents=True,exist_ok=True)
  with target.open('xb') as f:f.write(data)
  row['local_path']=str(target)
 put('HOST72_VERIFIED_PUBLIC_CACHE_BATCH_'+batch+'_RETURNED_ACTUAL.json',value);print(json.dumps({k:v for k,v in value.items() if k!='texts'}))
except BaseException:
 put('HOST72_VERIFIED_PUBLIC_CACHE_BATCH_'+batch+'_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc()));raise
