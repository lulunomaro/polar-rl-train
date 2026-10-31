"""Read-only original219 pre-GO failure closure; no signals or repeat FIRST."""
from pathlib import Path
import hashlib,importlib.util,json,os,subprocess,sys,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports'
def read(p):return json.loads(Path(p).read_bytes())
def put(n,v):
 with(R/n).open('x',encoding='utf8')as f:json.dump(v,f,indent=2,allow_nan=False)
def module(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
CODE="""from pathlib import Path
import json,time,hashlib,psutil,fcntl
O=Path(v['owner']['root']);C=Path(v['spec']['job_root'])/'control219'
def out(x):
 try:
  p=psutil.Process(x['pid'])
  if p.create_time()!=x['creation']:return True
  return p.status()==psutil.STATUS_ZOMBIE
 except psutil.NoSuchProcess:return True
end=time.time()+180
while time.time()<end and (not(O/'OWNER_EXIT_ACTUAL.json').is_file()or not(C/'NODE_EXIT_ACTUAL.json').is_file()or not out(v['owner'])or not out(v['node'])):time.sleep(2)
oe=json.loads((O/'OWNER_EXIT_ACTUAL.json').read_bytes());ne=json.loads((C/'NODE_EXIT_ACTUAL.json').read_bytes())
cur=json.loads((O/'OWNER_CURRENT.json').read_bytes())
assert cur['go']=={} and oe['original_cost_settled'] and ne['all_own_children_waited']and ne['private_EX_released']
assert out(v['owner'])and out(v['node'])
P=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json');raw=P.read_bytes();c=json.loads(raw)
assert c['active_segment']is None and c['authority_generation']=='MOD4_SINGLE_WRITER72_20261026'
with Path(v['spec']['private_lock']).open('rb+')as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
texts=[]
for root in(O,C):
 for p in sorted(root.iterdir()):
  if p.is_file()and p.suffix in('.json','.log'):
   b=p.read_bytes();texts.append(dict(path=str(p),bytes=len(b),SHA=hashlib.sha256(b).hexdigest(),UTF8=b.decode('utf8','replace')))
print(json.dumps(dict(epoch=time.time(),passed=True,original_owner_out=True,original_node_out=True,empty_GO=True,no_training_fee_segment_created=True,
 canonical_None=True,canonical_SHA=hashlib.sha256(raw).hexdigest(),remaining_snapshot=c['remaining_training_seconds'],private_EX_free=True,
 original_owner_exit=oe,original_node_exit=ne,full_UTF8=texts,model_raw_GPU_query_or_signal_or_account_writes=0)))
"""
def main():
 assert not read(R/'ROOT219_W35_FIRST_OR_ORIGINAL_ERROR_RETURNED_ACTUAL.json')['passed']
 assert read(R/'ROOT219_START_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json')['global_serial_control_client_lease']=='FREE'
 l=read(R/'ROOT219_ORIGINAL_SOLO_OWNER_LAUNCH_ACTUAL.json');node=read(R/'ROOT219_ORIGINAL_W35_NODE_LAUNCH_ACTUAL.json')['node']
 query=r'''Get-CimInstance Win32_Process -Filter "Name='python.exe' OR Name='ssh.exe'" | Where-Object { $_.CommandLine -match 'collect219_pre_GO_role_refusal_original_exit_once|launch219V2_|launch219V3_|launch219_|collect210_|collect219_' } | Select-Object Name,ProcessId,CreationDate,ExecutablePath,CommandLine | ConvertTo-Json -Depth 5 -Compress'''
 p=subprocess.run(['pwsh.exe','-NoProfile','-Command',query],capture_output=True,text=True,encoding='utf8',check=True);rows=json.loads(p.stdout)if p.stdout.strip()else[];rows=rows if isinstance(rows,list)else[rows]
 own=[x for x in rows if x['ProcessId']==os.getpid()];others=[x for x in rows if x['ProcessId']!=os.getpid()]
 put('ROOT219_PRE_GO_EXIT_FRESH_LOCAL_EXACT_CIM.json',dict(epoch=time.time(),PID=os.getpid(),exe=sys.executable,argv=sys.argv,rows=rows,others=others))
 assert len(own)==1 and own[0]['CreationDate']and own[0]['ExecutablePath'].lower()==sys.executable.lower()and not others
 assert str(Path(__file__).resolve()).lower().replace('\\','/')in own[0]['CommandLine'].lower().replace('\\','/')
 put('ROOT219_PRE_GO_ORIGINAL_EXIT_READONLY_ONCE_CONSUMED.json',dict(epoch=time.time(),owner=l['owner'],node=node,model_or_signals_or_GO=0,only_original_120s_startup_timeout_no_new_stop=True))
 wrapper=module('close219_transport',T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v227.py')
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 client=transport=prior=secret=None
 try:
  transport,prior=wrapper.install();sec=module('close219_memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');secret=sec.recover();client=d.connect72(secret);secret=None
  result=d.code(client,d.PY72,CODE,dict(owner=l['owner'],node=node,spec=l['specs']['w35_72']),timeout=240)
  put('ROOT219_PRE_GO_ROLE_REFUSAL_ORIGINAL_EXIT_ACTUAL.json',result)
  print(json.dumps({k:result[k]for k in('passed','empty_GO','canonical_None','private_EX_free','original_owner_out','original_node_out')}),flush=True)
 finally:
  secret=None
  if client is not None:client.close();client=None
  if transport is not None:transport.SESSION=prior
  put('ROOT219_PRE_GO_EXIT_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json',dict(epoch=time.time(),all_owned_SSH_closed=client is None,SESSION_restored=transport is None or transport.SESSION is prior,global_serial_control_client_lease='FREE'))
if __name__=='__main__':
 try:main()
 except BaseException:put('ROOT219_PRE_GO_EXIT_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_auto_retry=True));raise
