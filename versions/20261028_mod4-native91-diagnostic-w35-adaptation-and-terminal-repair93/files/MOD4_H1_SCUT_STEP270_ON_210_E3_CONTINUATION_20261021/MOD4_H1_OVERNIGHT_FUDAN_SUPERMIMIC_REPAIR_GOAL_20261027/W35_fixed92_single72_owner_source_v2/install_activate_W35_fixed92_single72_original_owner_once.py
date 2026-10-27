from pathlib import Path,PurePosixPath
import sys,json,time,os,hashlib,traceback,importlib.util
HERE=Path(__file__).resolve().parent;W=HERE.parents[2];R=HERE/'reports';sys.path.insert(0,str(HERE))
PRE=r"""from pathlib import Path
import json,time,fcntl,subprocess,socket,psutil,shutil
r=v['request'];B=Path(r['owner_root']);N=Path(r['node_root']);J=B.parent/'w35';assert not B.exists() and not N.exists() and J.is_dir() and not (J/'TASK.json').exists() and not (J/'GO_PRODUCTION.json').exists() and not (J/'adaptation').exists()
C=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json');c=json.loads(C.read_bytes());assert c['active_segment'] is None and c['remaining_training_seconds']==550398.7224562168 and c['authority_generation']=='MOD4_SINGLE_WRITER72_20261026' and c.get('budget_mode',c.get('mode'))=='finite_original_limits_restored_after_single4090_return' and c['authorized_training_seconds']==2268000 and c['historical_budget_extension_count']==9 and c['new_authority_budget_extensions']==[] and c['remaining_training_seconds']>86412.86069250107
for p in [C.parent/'native_floor_supervisor.lock',C.parent/'autonomy_controller.lock',Path('/home/lc01/Zonglin Li/zonglin2/state/finite_environment_validation.lock'),Path('/home/lc01/Zonglin Li/zonglin2/state/three_expert_v2_GPU-16828f91-2b45-b646-8dc0-9481138e2842.lock')]:
 with p.open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
with socket.socket() as sock:sock.bind(('127.0.0.1',29754))
gpu='GPU-16828f91-2b45-b646-8dc0-9481138e2842';line=subprocess.check_output(['nvidia-smi','-i',gpu,'--query-gpu=uuid,name,memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True).strip();apps=subprocess.check_output(['nvidia-smi','-i',gpu,'--query-compute-apps=gpu_uuid','--format=csv,noheader,nounits'],text=True);a=[x.strip() for x in line.split(',')];assert a[0]==gpu and a[1]=='NVIDIA GeForce RTX 4090' and int(a[2])>15669 and gpu not in apps
assert psutil.virtual_memory().available>8*1024**3 and shutil.disk_usage(B.parent).free>25*1024**3
B.mkdir();N.mkdir();print(json.dumps(dict(passed=True,CNone=True,remaining=c['remaining_training_seconds'],GPU_line=line,selected_compute_UUID_rows=0,original_private_shared_and_writer_locks_available=True,no_GPU_or_accountwrite=True)))
"""
ACTIVATE=r"""from pathlib import Path
import sys,json,io,runpy,hashlib,secrets,subprocess,time
r=v['request'];B=Path(r['owner_root']);N=Path(r['node_root']);sys.path.insert(0,str(B))
from W35_single72_bound_cfg_v2 import bound_cfgs
from W35_mixed72_bound_spec_v1 import bound_Task
from W35_mixed72_protocol_v1 import load_W35_preinstalled_CPU,validate_payload
cfg,spec=bound_cfgs(r,secrets.token_hex(32));closed=load_W35_preinstalled_CPU(spec,N)
for x in v['files']:
 p=Path(x['target']);assert p.stat().st_size==x['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==x['SHA']
gpu=spec['GPU_UUID'];line=subprocess.check_output(['nvidia-smi','-i',gpu,'--query-gpu=uuid,name,memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True).strip();apps=subprocess.check_output(['nvidia-smi','-i',gpu,'--query-compute-apps=gpu_uuid','--format=csv,noheader,nounits'],text=True);a=[x.strip() for x in line.split(',')];assert a[0]==gpu and a[1]=='NVIDIA GeForce RTX 4090' and int(a[2])>15669 and gpu not in apps
resource=dict(epoch=time.time(),GPU_UUID=gpu,GPU_name=a[1],GPU_line=line,compute_UUID_only_rows=0)
with (Path(spec['job_root'])/'TASK.json').open('x',encoding='utf8') as f:json.dump(bound_Task(spec,resource),f,ensure_ascii=False,indent=2)
validate_payload(spec,N)
with (B/'ACTUAL_W35_FIXED92_PUBLIC_REQUEST.json').open('x',encoding='utf8') as f:json.dump(r,f,ensure_ascii=False,indent=2)
sys.stdin=io.StringIO(json.dumps(r)+chr(10));runpy.run_path(str(B/'W35_single72_detached_launcher_v2.py'),run_name='__main__')
"""
def save(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
def main():
 assert len(sys.argv)==1;save('W35_FIXED92_ACTIVATION_ENTERED_ACTUAL.json',dict(epoch=time.time(),own_pid=os.getpid(),script=str(Path(__file__).resolve())))
 from W35_single72_install_manifest_v2 import OWNER_FILES,NODE_FILES,H
 request=json.loads((HERE/'ACTUAL_FIXED92_CPU_BOUND_REQUEST_TEMPLATE_V2.json').read_bytes());request['run_id']='W35_RETENTION_FIXED92_PPO50_GAS400_'+str(time.time_ns());save('W35_FIXED92_ACTUAL_PUBLIC_REQUEST.json',request)
 files=[]
 for root,names,manifest in [(request['owner_root'],OWNER_FILES,'W35_FIXED92_OWNER_COMPLETE_MANIFEST_V2.json'),(request['node_root'],NODE_FILES,'W35_NODE_CONTROLLER_MANIFEST_V1.json')]:
  for n in names+[manifest]:files.append(dict(local=str(HERE/n),target=root+'/'+n,bytes=(HERE/n).stat().st_size,SHA=H(HERE/n)))
 p=W/'MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021/H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v227.py';sp=importlib.util.spec_from_file_location('same_authorized_zstd_memory_fixed92_activate',p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);transport,previous=m.install()
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 sp=importlib.util.spec_from_file_location('same_authorized72_memory_only_fixed92_activate',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');sec=importlib.util.module_from_spec(sp);sp.loader.exec_module(sec);secret=sec.recover();c=None
 try:
  c=d.connect72(secret);secret=None;pre=d.code(c,d.PY72,PRE,dict(request=request),timeout=30);save('W35_FIXED92_ACTUAL_FRESH_RESOURCE_CNone_BEFORE_GO.json',pre)
  sf=c.open_sftp();sf.get_channel().settimeout(30)
  try:
   for x in files:
    with Path(x['local']).open('rb') as inp,sf.open(x['target'],'wx') as out:out.write(inp.read())
  finally:sf.close()
  actual=d.code(c,d.PY72,ACTIVATE,dict(request=request,files=[{k:x[k] for k in ['target','bytes','SHA']} for x in files]),timeout=90);actual['run_id']=request['run_id'];actual['owner_root']=request['owner_root'];actual['node_root']=request['node_root'];actual['source_CPU_SHA']=request['source_CPU_SHA'];save('W35_FIXED92_OWNER_NODE_LAUNCHED_ACTUAL.json',actual);print(json.dumps(actual))
 finally:
  secret=None
  if c:c.close()
  transport.SESSION=previous
if __name__=='__main__':
 try:main()
 except BaseException:save('W35_FIXED92_ACTIVATION_ORIGINAL_ERROR_ACTUAL.json',dict(epoch=time.time(),error=traceback.format_exc(),no_retry_rearm91_or_clearC=True));raise
