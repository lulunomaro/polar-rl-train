from pathlib import Path
import importlib.util,json,time,traceback
B=Path(__file__).resolve().parent;R=B/'reports';W=B.parent
s=importlib.util.spec_from_file_location('strict210',W/'MOD4_TWO_LINUX_POLICY50_COHORT_49_20261021/strict_original_Linux_transport_memory.py');t=importlib.util.module_from_spec(s);s.loader.exec_module(t)
READ=r'''
from pathlib import Path
import fcntl,json,os,psutil,shutil,subprocess,time
C=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');c=json.loads(C.read_bytes());base=Path('/mnt/mod4_linux_durable_20261013/T2policy50_2010v49');root=base/'e2';owner=base/'owner';owned=base.parent;ram=psutil.virtual_memory().available;disk=shutil.disk_usage(owned).free;compute=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits'],text=True);gpus=subprocess.check_output(['nvidia-smi','--query-gpu=uuid,memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True);locks=[]
for p in (C.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock'),owned/'H125_1710n1/OWN_SOURCE_GPU_NATIVE_ONLY.lock'):
 with p.open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);locks.append(str(p));fcntl.flock(f,fcntl.LOCK_UN)
own=[dict(pid=p.pid,argv=p.info['cmdline'],creation=p.create_time()) for p in psutil.process_iter(['pid','cmdline']) if p.pid!=os.getpid() and any(x.startswith(str(base)+'/') for x in p.info['cmdline'] or [])];assert not own
print(json.dumps(dict(epoch=time.time(),RAM_available=ram,RAM_guard=ram>8*1024**3,durable_free=disk,disk_guard=disk>25*1024**3,E2_compute_rows=[x for x in compute.splitlines() if 'GPU-937bdb0b-0d8f-aa3d-a10e-1b24969a5d4e' in x],GPU_snapshot=gpus,e2_root_exists=root.exists(),owner_root_exists=owner.exists(),e2_GO_exists=(root/'job0/GO_PRODUCTION.json').exists(),owner_or_node_actual_alive=False,original_locks_actual_free=locks,canonical_active=c['active_segment'],canonical_total=c['authorized_training_seconds'],canonical_extensions=len(c['budget_extensions']),canonical_charged=c['charged_training_seconds'],canonical_remaining=c['remaining_training_seconds'],cohort49_new_interval_count=sum('T2policy50_2010v49' in str(x.get('log','')) for x in c['completed_segments']),no_new_GO_or_training_cost_claim=True,no_peer_identity_inspection_or_mutation=True)))
'''
try:
 with (R/'DIAGNOSE49_RESOURCE_STARTED.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time()),f)
 c=t.connect()
 try:v=t.code(c,READ,timeout=90)
 finally:c.close()
 with (R/'COHORT49_PREGO_RESOURCE_DIAGNOSIS_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
 print(json.dumps(v))
except BaseException:
 with (R/'DIAGNOSE49_ORIGINAL_ERROR.json').open('x',encoding='utf8') as f:json.dump(dict(error=traceback.format_exc(),no_replay=True),f)
 raise
