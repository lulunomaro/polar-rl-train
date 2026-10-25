"""Human requested current three-GPU occupancy. Device totals, only exact own worker identity."""
from pathlib import Path
import importlib.util,json,os,sys,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports'
def put(name,v):
 with (R/name).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
CODE=r'''
import csv,io,json,subprocess,time,psutil
raw=subprocess.check_output(['nvidia-smi','--query-gpu=uuid,name,memory.total,memory.used,utilization.gpu,utilization.memory,pstate','--format=csv,noheader,nounits'],text=True,timeout=15)
rows=[]
for r in csv.reader(io.StringIO(raw)):
 r=[x.strip() for x in r];assert len(r)==7
 rows.append(dict(GPU_UUID=r[0],name=r[1],memory_total_MiB=int(r[2]),memory_used_MiB=int(r[3]),GPU_utilization_percent=int(r[4]),memory_utilization_percent=int(r[5]),pstate=r[6],our_scheduled_GPU=r[0]==v['own_GPU_UUID']))
expected=v['worker'];identity=dict(expected_pid=expected['pid'],exact_own_worker_alive=False)
try:
 p=psutil.Process(expected['pid'])
 if p.create_time()!=expected['creation']:identity['reason']='Original PID creation mismatch; no new identity details queried'
 else:identity.update(exact_own_worker_alive=p.is_running() and p.status()!=psutil.STATUS_ZOMBIE and p.cmdline()==expected['argv'] and p.exe()==expected['exe'])
except psutil.NoSuchProcess:identity['reason']='Original own worker absent'
print(json.dumps(dict(epoch=time.time(),devices=rows,own_worker_identity=identity,no_compute_process_or_unknown_peer_identity_query=True,resource_snapshot_not_permanent=True)))
'''
try:
 p=json.loads((R/'PAIR_ACTUAL_GO_POSITIVE_PPO_UUID_CREATE_ARGV_VERIFIED_ACTUAL.json').read_bytes());assert p['passed'] and p['actual_finite_returned']
 put('HUMAN_THREE_GPU_RESOURCE_SNAPSHOT_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,scope='Current nvidia-smi device utilization/memory only; check only two exact original own worker identities. No unknown-peer PID/argv/process names or modification.'))
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 sys.path.insert(0,str(T/'MOD4_MOE_T2Z_SINGLE4090_QUANTIZED_PREPARATION_20261025'));import strict_user_forwarded_original210_transport_v1 as route
 c=route.connect()
 try:a=d.code(c,route.PY,CODE,dict(own_GPU_UUID='GPU-937bdb0b-0d8f-aa3d-a10e-1b24969a5d4e',worker=p['source210']['H1_worker']),timeout=25)
 finally:c.close()
 s=W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py';sp=importlib.util.spec_from_file_location('memory',s);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);secret=m.recover();c=d.connect72(secret);secret=None
 try:b=d.code(c,d.PY72,CODE,dict(own_GPU_UUID='GPU-c27eecbd-6838-7290-1cd2-37e34522213d',worker=p['source72']['worker']),timeout=25)
 finally:c.close()
 assert len(a['devices'])==1 and len(b['devices'])==2
 result=dict(epoch=time.time(),source210=a,host72=b,actual_finite_returned=True,no_training_budget_or_unknown_peer_action=True)
 put('HUMAN_THREE_GPU_RESOURCE_SNAPSHOT_RETURNED_ACTUAL.json',result)
 print(json.dumps(result,ensure_ascii=False))
except BaseException:
 put('HUMAN_THREE_GPU_RESOURCE_SNAPSHOT_ORIGINAL_ERROR_ACTUAL.json',dict(epoch=time.time(),error=traceback.format_exc(),no_retry_same_once_or_peer_action=True));raise
