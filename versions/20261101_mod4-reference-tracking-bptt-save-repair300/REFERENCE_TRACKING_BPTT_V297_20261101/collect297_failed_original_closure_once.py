from pathlib import Path
import hashlib,importlib.util,json,os,subprocess,sys,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports'
def put(n,v):
    with(R/n).open('x',encoding='utf8')as f:json.dump(v,f,indent=2)
def module(n,p):
    s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
task=json.loads((N/'TASK297_FROZEN.json').read_bytes());launch=json.loads((R/'ROOT297_ORIGINAL_OWNER_LAUNCH_ACTUAL.json').read_bytes())
query="Get-CimInstance Win32_Process -Filter \"Name='python.exe' OR Name='ssh.exe'\" | Where-Object { $_.CommandLine -match 'collect297_|launch297_|run299_eval|collect292_|run293_eval' } | Select-Object ProcessId,CreationDate,ExecutablePath,CommandLine | ConvertTo-Json -Compress"
q=subprocess.run(['pwsh.exe','-NoProfile','-Command',query],capture_output=True,text=True,encoding='utf8',check=True);rows=json.loads(q.stdout)if q.stdout.strip()else[];rows=rows if isinstance(rows,list)else[rows]
assert len(rows)==1 and rows[0]['ProcessId']==os.getpid()
put('ROOT297_FAILURE_CLOSURE_CIM.json',dict(epoch=time.time(),rows=rows))
sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
transport=previous=client=secret=None
try:
    transport,previous=module('close297transport',T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v227.py').install()
    secret=module('close297memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py').recover();client=d.connect72(secret);secret=None
    code='''from pathlib import Path
import fcntl,hashlib,json,time,psutil
B=Path(v['task']['job_root']);O=Path(v['task']['owner_root']);C=B/'control297'
end=time.time()+90
while time.time()<end and not(O/'OWNER_EXIT_ACTUAL.json').exists():time.sleep(1)
def read(p):return json.loads(p.read_bytes())
owner=read(O/'OWNER_IDENTITY.json');assert owner['pid']==v['owner']['pid']and owner['creation']==v['owner']['creation']
assert read(O/'OWNER_EXIT_ACTUAL.json')['original_cost_settled']and read(C/'NODE_EXIT_ACTUAL.json')['all_own_children_waited']
for x in(owner,read(C/'NODE_IDENTITY.json')):
 try:p=psutil.Process(x['pid']);assert p.create_time()!=x['creation']or p.status()==psutil.STATUS_ZOMBIE
 except psutil.NoSuchProcess:pass
canonical=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json');c=read(canonical);assert c['active_segment']is None
segments=[x for x in c['completed_segments']if x.get('owner_parent_pid')==owner['pid']];assert len(segments)==1
segment=segments[0];fee=sum(x['charged_seconds']for x in segment['experts'].values());assert abs(fee-segment['charged_expert_seconds'])<1e-5
for p in(canonical.parent/'native_floor_supervisor.lock',canonical.parent/'autonomy_controller.lock',Path(v['private_lock'])):
 with p.open('rb+')as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
texts=[];models=[]
for root in(O,C,B/'production'):
 for p in sorted(root.rglob('*')):
  if not p.is_file()or'kit_isolation'in p.parts:continue
  if p.suffix=='.pt':models.append(dict(path=str(p),bytes=p.stat().st_size,SHA='unknown; not promoted/no readforarchive'));continue
  if p.suffix not in('.json','.log'):continue
  raw=p.read_bytes();texts.append(dict(path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),UTF8=raw.decode('utf8','replace')))
print(json.dumps(dict(passed=True,epoch=time.time(),canonical_None=True,all_owned_children_waited=True,all_private_shared_locks_free=True,raw_fee_sum_once=fee,closing_balance_snapshot=c['remaining_training_seconds'],original_segment=segment,full_UTF8=texts,partial_models_metadata_only=models,modelreads=0,accountwrites=0)))'''
    result=d.code(client,d.PY72,code,dict(task=task,owner=launch['owner'],private_lock=launch['specs']['jump_72']['private_lock']),timeout=120)
    put('ROOT297_FAILED_ORIGINAL_CLOSED_COST_FULL_RETURNED.json',result);print(json.dumps({k:result[k]for k in('passed','canonical_None','raw_fee_sum_once','closing_balance_snapshot')}))
finally:
    secret=None
    if client is not None:client.close();client=None
    if transport is not None:transport.SESSION=previous
    put('ROOT297_FAILURE_CLOSURE_ALL_SSH_FREE.json',dict(epoch=time.time(),all_SSH_closed=client is None,SESSION_restored=transport is None or transport.SESSION is previous,global_serial_control_client_lease='FREE'))
