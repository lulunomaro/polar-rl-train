"""Necessary original pre-GO closure and one different known GPU resource probe."""
from pathlib import Path
import hashlib,importlib.util,json,os,subprocess,sys,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports'
def read(p):return json.loads(Path(p).read_bytes())
def put(n,v):
 with(R/n).open('x',encoding='utf8')as f:json.dump(v,f,indent=2,allow_nan=False)
def module(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
def main():
 assert sys.version_info[:2]==(3,14)
 launch=read(R/'ROOT276_ORIGINAL_SOLO_OWNER_LAUNCH_ACTUAL.json');first=read(R/'ROOT276_FIRST_NEW_WM_OR_ORIGINAL_ERROR_RETURNED_ACTUAL.json');assert not first['passed']and first['first']is None and first['source_restore']is None
 resource=next(json.loads(x['UTF8'])for x in first['full_selected_UTF8']if x['path'].endswith('/ACTUAL_COLD_START_RESOURCE_PRIVATE_EX.json'));assert int(resource['GPU_line'].split(',')[-1])==45
 pattern='read276_|launch276_|collect276_|run_ROOT274_|run_ROOT272_|collect270_exact_|run_ROOT267_|collect240_|start240_|run_actual'
 query="Get-CimInstance Win32_Process -Filter \"Name='python.exe' OR Name='ssh.exe'\" | Where-Object { $_.CommandLine -match '"+pattern+"' } | Select-Object Name,ProcessId,CreationDate,ExecutablePath,CommandLine | ConvertTo-Json -Depth 5 -Compress"
 p=subprocess.run(['pwsh.exe','-NoProfile','-Command',query],capture_output=True,text=True,encoding='utf8',check=True);rows=json.loads(p.stdout)if p.stdout.strip()else[];rows=rows if isinstance(rows,list)else[rows];assert len(rows)==1 and rows[0]['ProcessId']==os.getpid()and rows[0]['CreationDate']and rows[0]['ExecutablePath'].lower()==sys.executable.lower()and str(Path(__file__).resolve()).lower().replace('\\','/')in rows[0]['CommandLine'].lower().replace('\\','/')
 put('ROOT276_PREGO_CLOSURE_AND_DIFFERENT_GPU_PURPOSE_CONSUMED.json',dict(epoch=time.time(),fresh_LOCAL_exact_CIM=rows,original_owner=launch['owner'],only_different_candidate_GPU='GPU-c27eecbd-6838-7290-1cd2-37e34522213d',old168_startup_recheck=False,model_raw_SDK_GO_account=0))
 client=transport=previous=secret=None
 try:
  transport,previous=module('root276_close_transport',T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v227.py').install();sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
  secret=module('root276_close_memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py').recover();client=d.connect72(secret);secret=None
  code="""from pathlib import Path
import fcntl,hashlib,json,psutil,subprocess,time
C=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json');c=json.loads(C.read_bytes());assert c['active_segment']is None and c['authority_generation']=='MOD4_SINGLE_WRITER72_20261026'
O=Path(v['owner']['root']);J=Path(v['spec']['job_root']);B=J/'control276';end=time.time()+60
while time.time()<end and not(O/'OWNER_EXIT_ACTUAL.json').is_file():time.sleep(1)
final=json.loads((O/'COHORT_FINAL.json').read_bytes());exit=json.loads((O/'OWNER_EXIT_ACTUAL.json').read_bytes());assert final['go']=={} and final['original_cost_settled']and exit['original_cost_settled']
ni=json.loads((B/'NODE_IDENTITY.json').read_bytes());oi=json.loads((O/'OWNER_IDENTITY.json').read_bytes());assert oi['pid']==v['owner']['pid']and oi['creation']==v['owner']['creation']
def running(x):
 try:p=psutil.Process(x['pid']);return p.create_time()==x['creation']and p.status()!=psutil.STATUS_ZOMBIE
 except psutil.NoSuchProcess:return False
assert not running(ni)and not running(oi)
nodeexit=json.loads((B/'NODE_EXIT_ACTUAL.json').read_bytes());assert nodeexit['all_own_children_waited']and nodeexit['private_EX_released']and nodeexit['terminal_owner_ack']
for path in(C.parent/'native_floor_supervisor.lock',C.parent/'autonomy_controller.lock',Path(v['spec']['private_lock'])):
 with path.open('rb+')as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
c=json.loads(C.read_bytes());assert c['active_segment']is None and not[s for s in c['completed_segments']if s.get('owner_parent_pid')==oi['pid']]
gpu='GPU-c27eecbd-6838-7290-1cd2-37e34522213d';locks=[]
try:
 for path in(C.parent.parent/('three_expert_v2_'+gpu+'.lock'),C.parent.parent/'finite_environment_validation.lock'):
  f=path.open('rb+');fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);locks.append(f)
 line=subprocess.check_output(['nvidia-smi','-i',gpu,'--query-gpu=uuid,name,memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True).strip();a=[x.strip()for x in line.split(',')];candidate_passed=a[0]==gpu and a[1]=='NVIDIA GeForce RTX 4090'and int(a[2])>15669 and int(a[3])<=30
finally:
 for f in reversed(locks):fcntl.flock(f,fcntl.LOCK_UN);f.close()
texts=[]
for root in(O,B):
 for p in sorted(root.iterdir()):
  if p.is_file()and p.suffix in('.json','.log'):
   b=p.read_bytes();texts.append(dict(path=str(p),bytes=len(b),SHA=hashlib.sha256(b).hexdigest(),UTF8=b.decode('utf8','replace')))
print(json.dumps(dict(passed=True,epoch=time.time(),original_owner_node_OUT=True,original_empty_GO=True,canonical_None=True,original_no_fee_segment=True,original_shared_and_private_EX_free=True,different_candidate_GPU_line=line,candidate_passed=candidate_passed,candidate_probe_locks_released=True,full_UTF8=texts,no_SDK_model_raw_account_writes=True)))"""
  result=d.code(client,d.PY72,code,dict(owner=launch['owner'],spec=launch['specs']['jump_72']),timeout=100);put('ROOT276_ACTUAL_PREGO_EMPTY_GO_CLOSED_AND_C27_RESOURCE_RETURNED.json',result);print(json.dumps({k:v for k,v in result.items()if k!='full_UTF8'}))
 finally:
  secret=None
  if client is not None:client.close();client=None
  if transport is not None:transport.SESSION=previous
  put('ROOT276_PREGO_CLOSURE_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json',dict(epoch=time.time(),all_owned_SSH_closed=client is None,SESSION_restored=transport is None or transport.SESSION is previous,global_serial_control_client_lease='FREE'))
if __name__=='__main__':
 try:main()
 except BaseException:put('ROOT276_PREGO_CLOSURE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_signal_or_automatic_retry=True));raise
