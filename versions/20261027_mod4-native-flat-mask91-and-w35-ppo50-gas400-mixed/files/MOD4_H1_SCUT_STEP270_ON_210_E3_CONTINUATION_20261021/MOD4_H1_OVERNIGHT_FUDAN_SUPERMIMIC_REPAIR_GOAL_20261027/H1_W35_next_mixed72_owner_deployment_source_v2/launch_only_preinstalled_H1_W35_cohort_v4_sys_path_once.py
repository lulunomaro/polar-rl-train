from pathlib import Path
import json,sys,time,os,traceback,importlib.util
HERE=Path(__file__).resolve().parent;W=HERE.parents[2];R=HERE/'reports'
CODE=r"""from pathlib import Path
import sys,json,time,io,runpy,fcntl,subprocess,psutil,shutil,hashlib,socket
r=v['request'];B=Path(r['owner_root']);C=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json');c=json.loads(C.read_bytes())
assert c['active_segment'] is None and c['remaining_training_seconds']==554499.7579419613 and c['authority_generation']=='MOD4_SINGLE_WRITER72_20261026' and c.get('budget_mode',c.get('mode'))=='finite_original_limits_restored_after_single4090_return'
with socket.socket() as sock:sock.bind(('127.0.0.1',29754))
for name in ['MIXED_LAUNCH_ENTERED_ACTUAL.json','owner_CONSOLE.log','OWNER_IDENTITY.json']:assert not (B/name).exists()
for node,go in [(Path(r['h1_node_root']),Path(r['h1_spec']['job_root'])/'job0/GO_PRODUCTION.json'),(Path(r['w35_request']['node_root']),Path('/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_W35_PPO50_GAS400_2610v91/w35/GO_PRODUCTION.json'))]:
 assert not (node/'NODE_IDENTITY.json').exists() and not (node/'node_CONSOLE.log').exists() and not go.exists()
for p in [C.parent/'native_floor_supervisor.lock',C.parent/'autonomy_controller.lock',Path('/home/lc01/Zonglin Li/zonglin2/state/finite_environment_validation.lock')]:
 with p.open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
for gpu in ['GPU-c27eecbd-6838-7290-1cd2-37e34522213d','GPU-16828f91-2b45-b646-8dc0-9481138e2842']:
 lock=Path('/home/lc01/Zonglin Li/zonglin2/state/three_expert_v2_'+gpu+'.lock')
 with lock.open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
 line=subprocess.check_output(['nvidia-smi','-i',gpu,'--query-gpu=uuid,name,memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True).strip();apps=subprocess.check_output(['nvidia-smi','-i',gpu,'--query-compute-apps=gpu_uuid','--format=csv,noheader,nounits'],text=True);a=[x.strip() for x in line.split(',')];assert a[0]==gpu and a[1]=='NVIDIA GeForce RTX 4090' and int(a[2])>15669 and gpu not in apps
assert psutil.virtual_memory().available>32*1024**3 and shutil.disk_usage(B).free>25*1024**3
reg=json.loads((B/'ACTUAL_MIXED72_SOURCE_REGISTRATION_PASSED.json').read_bytes());assert reg['passed'] is True and reg['run_id']==r['run_id'] and reg['keys']==['h1','w35']
sys.path.insert(0,str(B))
sys.stdin=io.StringIO(json.dumps(r)+chr(10))
runpy.run_path(str(B/'mixed72_next_detached_launcher_v1.py'),run_name='__main__')
"""
def save(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
def main():
 assert len(sys.argv)==1;save('MIXED72_MISSING_LAUNCH_ONLY_ENTERED_ACTUAL_V4.json',dict(epoch=time.time(),own_pid=os.getpid(),script=str(Path(__file__).resolve()),no_install_Task_or_CPU_replay=True))
 request=json.loads((HERE/'ACTUAL_MIXED72_PUBLIC_REQUEST_POSIX_SEALED_V3.json').read_bytes())
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 sp=importlib.util.spec_from_file_location('same_authorized72_memory_missing_launch_only_v4',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');sec=importlib.util.module_from_spec(sp);sp.loader.exec_module(sec)
 secret=sec.recover();c=None
 try:
  c=d.connect72(secret);secret=None;result=d.code(c,d.PY72,CODE,dict(request=request),timeout=110);save('MIXED72_ONE_OWNER_TWO_NODES_LAUNCHED_ACTUAL_V4.json',result);print(json.dumps(result))
 finally:
  secret=None
  if c:c.close()
if __name__=='__main__':
 try:main()
 except BaseException:save('MIXED72_MISSING_LAUNCH_ONLY_ORIGINAL_ERROR_ACTUAL_V4.json',dict(epoch=time.time(),error=traceback.format_exc(),no_retry_or_Cclear=True));raise
