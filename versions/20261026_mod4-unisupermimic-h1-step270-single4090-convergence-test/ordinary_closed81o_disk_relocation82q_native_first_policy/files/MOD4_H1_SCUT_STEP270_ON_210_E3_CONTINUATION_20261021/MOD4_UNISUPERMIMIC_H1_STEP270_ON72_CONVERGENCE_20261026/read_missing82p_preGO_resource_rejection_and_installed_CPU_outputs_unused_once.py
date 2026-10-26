from pathlib import Path
import base64,hashlib,importlib.util,json,os,sys,time,traceback
H=Path(__file__).resolve().parent;T=H.parent;W=T.parent;F=T/'H1_STEP270_MIXED_UNISUPERMIMIC_RESOURCE_V82P_20261026';R=F/'reports'
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
SOURCE=r'''
from pathlib import Path
import json,os,psutil,shutil,subprocess,time
base=Path('/mnt/mod4_linux_durable_20261013/H1step270_mixed_supermimic_2610v82p');C=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');c=json.loads(C.read_bytes());assert c['active_segment'] is None and not (base/'owner/OWNER_IDENTITY.json').exists() and not (base/'h1/NODE_IDENTITY.json').exists() and not (base/'h1/GO_PRODUCTION.json').exists()
assert not any(p.pid!=os.getpid() and any(x.startswith(str(base)+'/') for x in p.info['cmdline'] or []) for p in psutil.process_iter(['pid','cmdline']))
owned=Path('/mnt/mod4_linux_durable_20261013');disk=shutil.disk_usage(owned);ram=psutil.virtual_memory();gpu=next(x for x in subprocess.check_output(['nvidia-smi','--query-gpu=uuid,memory.free','--format=csv,noheader,nounits'],text=True).splitlines() if '937bdb0b-0d8f-aa3d-a10e-1b24969a5d4e' in x);compute=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits'],text=True)
print(json.dumps(dict(epoch=time.time(),original_canonicalNone=True,remaining_closed_snapshot=c['remaining_training_seconds'],no82P_owner_node_GO_or_own_process=True,durable=dict(total=disk.total,used=disk.used,free=disk.free,original25GiB_passed=disk.free>25*1024**3),RAM_available=ram.available,original8GiB_passed=ram.available>8*1024**3,H1_GPU_line=gpu,H1_GPU_compute_empty=not any('937bdb0b-0d8f-aa3d-a10e-1b24969a5d4e' in x for x in compute.splitlines()),original15669_passed=int(gpu.split(',')[-1])>15669,no_unknown_process_identity_or_file_cleanup=True)))
'''
TARGET=r'''
from pathlib import Path
import base64,hashlib,json,os,psutil,time
base=Path('/home/lc01/Zonglin Li/zonglin2/tasks/H1step270_mixed_supermimic_2610v82p');files=[]
for key in ('e2','recovery'):
 B=base/key;assert not (B/'NODE_IDENTITY.json').exists() and not (B/'job0/GO_PRODUCTION.json').exists() and not (B/'job0/production_STARTED_ACTUAL.json').exists()
 assert not any(p.pid!=os.getpid() and any(x.startswith(str(B)+'/') for x in p.info['cmdline'] or []) for p in psutil.process_iter(['pid','cmdline']))
 prior={r['relative'] for r in json.loads((B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes())['files']}
 for p in B.rglob('*'):
  if not p.is_file() or p.is_symlink() or '__pycache__' in p.parts:continue
  rel=p.relative_to(B).as_posix()
  if rel in prior or rel=='THREE_SLOT_COMPLETE_MANIFEST_V1.json' or p.suffix not in ('.json','.log','.txt'):continue
  raw=p.read_bytes();assert len(raw)<16*1024**2;files.append(dict(path=str(p),relative=key+'/'+rel,bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),base64=base64.b64encode(raw).decode()))
print(json.dumps(dict(epoch=time.time(),exact82P_partial_noNODE_noGO_actual_out=True,files=files)))
'''
try:
 put('MISSING82P_PREGO_BOUNDARY_READER_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv))
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 sys.path.insert(0,str(T/'MOD4_MOE_T2Z_SINGLE4090_QUANTIZED_PREPARATION_20261025'));import strict_user_forwarded_original210_transport_v1 as route
 c=route.connect()
 try:a=d.code(c,route.PY,SOURCE,{},timeout=45)
 finally:c.close()
 sp=importlib.util.spec_from_file_location('memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);c=d.connect72(m.recover())
 try:b=d.code(c,d.PY72,TARGET,{},timeout=90)
 finally:c.close()
 rows=[]
 for row in b['files']:
  raw=base64.b64decode(row.pop('base64'));assert len(raw)==row['bytes'] and hashlib.sha256(raw).hexdigest()==row['SHA'];p=F/'partial_remote_CPU_outputs'/row['relative'];p.parent.mkdir(parents=True,exist_ok=True)
  with p.open('xb') as f:f.write(raw)
  rows.append(dict(row,local_path=str(p)))
 b['files']=rows;result=dict(epoch=time.time(),actual_finite_returned=True,source210=a,target72=b,preGO_rejection_not_native_training_failure=True,no_new_fee_or_cleanup=True)
 put('ACTUAL82P_PREGO_RESOURCE_BOUNDARY_AND_PARTIAL_CPU_OUTPUTS_RETURNED.json',result);print(json.dumps(a))
except BaseException:
 put('MISSING82P_BOUNDARY_READER_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc()));raise
