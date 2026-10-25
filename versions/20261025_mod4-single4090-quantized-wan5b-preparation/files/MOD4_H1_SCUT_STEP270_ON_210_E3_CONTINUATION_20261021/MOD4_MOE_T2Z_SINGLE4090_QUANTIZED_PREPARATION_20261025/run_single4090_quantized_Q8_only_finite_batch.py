"""Root's sole serial72 transport, exact600second single quantized file batch."""
from pathlib import Path
import argparse,base64,hashlib,importlib.util,json,os,sys,time,traceback
Q=Path(__file__).resolve().parent;T=Q.parent;W=T.parent;R=Q/'reports'
p=argparse.ArgumentParser();p.add_argument('batch',choices=[str(i).zfill(2) for i in range(1,11)]);a=p.parse_args();batch=a.batch
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
CODE=r'''
from pathlib import Path
import base64,hashlib,json,os,shutil,subprocess,time
B=Path('/home/lc01/Zonglin Li/zonglin2/research/T2Z_MOE_RL_TRANSFER_PREP_20261025');R=B/'receipts'
assert B.resolve()==B and shutil.disk_usage(B).free>25*1024**3
marker=B/'FULL13_DOWNLOAD_CANCELLED_BY_HUMAN_20261025.json'
if not marker.exists():
 with marker.open('x') as f:json.dump(dict(epoch=time.time(),human='Only one quantized model suitable for a single4090; no full13 weight download',no_future_subagents=True),f,indent=2)
data=base64.b64decode(v['source']);assert hashlib.sha256(data).hexdigest()==v['SHA']
D=B/'preparation_helpers/single4090_quantized_v1';D.mkdir(parents=True,exist_ok=True);script=D/'download_exact_Wan5B_Q8_0_only_v1.py'
if script.exists():assert script.read_bytes()==data
else:
 with script.open('xb') as f:f.write(data)
ID='SINGLE4090_Q8_ONLY_BATCH_'+v['batch'];assert not (R/(ID+'_STARTED.json')).exists()
env={k:os.environ[k] for k in ('PATH','HOME','USER','LANG','LC_ALL','SSL_CERT_FILE','SSL_CERT_DIR') if k in os.environ};env.update(CUDA_VISIBLE_DEVICES='',PYTHONDONTWRITEBYTECODE='1',OMP_NUM_THREADS='1')
try:
 p=subprocess.run(['nice','-n','19',str(B/'run-t2z-python.sh'),'-B',str(script),'--batch',v['batch']],cwd=B,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=720);rc=p.returncode;raw=p.stdout
except subprocess.TimeoutExpired as e:rc=124;raw=e.stdout or b''
with (R/(ID+'_ROOT_STDOUT_STDERR.log')).open('xb') as f:f.write(raw)
result=dict(epoch=time.time(),actual_returncode=rc,root=str(B),full13_cancel_marker=True,download_result=json.loads((R/(ID+'_FINAL.json')).read_bytes()) if (R/(ID+'_FINAL.json')).exists() else None,texts=[])
for p in [marker,*sorted(R.glob(ID+'*'))]:
 if p.is_file():
  data=p.read_bytes();result['texts'].append(dict(name=p.name,path=str(p),bytes=len(data),SHA=hashlib.sha256(data).hexdigest(),base64=base64.b64encode(data).decode()))
print(json.dumps(result))
'''
try:
 put('SINGLE4090_Q8_BATCH_'+batch+'_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,old_full13_plan_overridden=True))
 source=(Q/'download_exact_Wan5B_Q8_0_only_v1.py').read_bytes()
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 spec=importlib.util.spec_from_file_location('memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);secret=m.recover();c=d.connect72(secret);secret=None
 try:value=d.code(c,d.PY72,CODE,dict(batch=batch,source=base64.b64encode(source).decode(),SHA=hashlib.sha256(source).hexdigest()),timeout=780)
 finally:c.close()
 dest=Q/'actual72_download_receipts'/batch;dest.mkdir(parents=True)
 for row in value['texts']:
  data=base64.b64decode(row.pop('base64'));assert len(data)==row['bytes'] and hashlib.sha256(data).hexdigest()==row['SHA']
  with (dest/row['name']).open('xb') as f:f.write(data)
  row['local_path']=str(dest/row['name'])
 put('SINGLE4090_Q8_BATCH_'+batch+'_RETURNED_ACTUAL.json',value);print(json.dumps({k:v for k,v in value.items() if k!='texts'}))
except BaseException:
 put('SINGLE4090_Q8_BATCH_'+batch+'_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_training_or_canonical_change=True));raise
