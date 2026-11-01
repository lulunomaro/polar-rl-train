from pathlib import Path
import importlib.util,json,os,subprocess,sys,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports'
def read(p):return json.loads(Path(p).read_bytes())
def put(n,v):
 with(R/n).open('x',encoding='utf8')as f:json.dump(v,f,indent=2,allow_nan=False)
def module(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
def main():
 assert sys.version_info[:2]==(3,14)
 launch=read(R/'ROOT276_ORIGINAL_SOLO_OWNER_LAUNCH_ACTUAL.json');first=read(R/'ROOT276_FIRST_NEW_WM_OR_ORIGINAL_ERROR_RETURNED_ACTUAL.json');state=read(R/'ROOT276_ORIGINAL_OWNER_AND_CANONICAL_AFTER_FIRST_ACTUAL.json');go=state['current']['go'];assert set(go)=={'jump_72'}and first['native24']['passed']and first['source_restore']['passed']and first['first']is None
 assert any('Actual native24 must precede first WM update'in x['UTF8']for x in first['full_selected_UTF8']if x['path'].endswith('/ORIGINAL_ERROR.json'))
 pattern='close276|read276_|launch276_|collect276_|run_ROOT274_|run_ROOT272_|collect270_exact_|run_ROOT267_|collect240_|start240_|run_actual'
 query="Get-CimInstance Win32_Process -Filter \"Name='python.exe' OR Name='ssh.exe'\" | Where-Object { $_.CommandLine -match '"+pattern+"' } | Select-Object Name,ProcessId,CreationDate,ExecutablePath,CommandLine | ConvertTo-Json -Depth 5 -Compress"
 p=subprocess.run(['pwsh.exe','-NoProfile','-Command',query],capture_output=True,text=True,encoding='utf8',check=True);rows=json.loads(p.stdout)if p.stdout.strip()else[];rows=rows if isinstance(rows,list)else[rows];assert len(rows)==1 and rows[0]['ProcessId']==os.getpid()and rows[0]['CreationDate']and rows[0]['ExecutablePath'].lower()==sys.executable.lower()and str(Path(__file__).resolve()).lower().replace('\\','/')in rows[0]['CommandLine'].lower().replace('\\','/')
 put('ROOT276V2_RECEIPT_FAILURE_CLOSURE_ONE_ORIGINAL_RAW_FEE_PURPOSE_CONSUMED.json',dict(epoch=time.time(),exact_LOCAL_CIM=rows,original_owner=launch['owner'],original_GO=go,no_new_model_raw_or_GPU_read=True,one_original_fee_SUMONCE=True,no_refund_grant_signal=True))
 client=transport=previous=secret=None
 try:
  transport,previous=module('root276v2_close_transport',T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v227.py').install();sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
  secret=module('root276v2_close_memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py').recover();client=d.connect72(secret);secret=None
  code="""from pathlib import Path
import fcntl,hashlib,json,psutil,time
C=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json');c=json.loads(C.read_bytes());assert c['authority_generation']=='MOD4_SINGLE_WRITER72_20261026'and(c['active_segment']is None or c['active_segment']['owner_parent_pid']==v['owner']['pid'])
O=Path(v['owner']['root']);J=Path(v['spec']['job_root']);B=J/'control276';current=json.loads((O/'OWNER_CURRENT.json').read_bytes());assert current['go']==v['go']and v['go']['jump_72']['run_id']==v['spec']['run_id']
end=time.time()+60
while time.time()<end and not(O/'OWNER_EXIT_ACTUAL.json').is_file():time.sleep(1)
final=json.loads((O/'COHORT_FINAL.json').read_bytes());exit=json.loads((O/'OWNER_EXIT_ACTUAL.json').read_bytes());assert final['go']==v['go']and final['original_cost_settled']and exit['original_cost_settled']
oi=json.loads((O/'OWNER_IDENTITY.json').read_bytes());ni=json.loads((B/'NODE_IDENTITY.json').read_bytes());wi=json.loads((B/'WORKER_ORIGINAL_IDENTITY_BEFORE_WAIT.json').read_bytes());assert oi['pid']==v['owner']['pid']and oi['creation']==v['owner']['creation']
def running(x):
 try:p=psutil.Process(x['pid']);return p.create_time()==x['creation']and p.status()!=psutil.STATUS_ZOMBIE
 except psutil.NoSuchProcess:return False
assert not running(oi)and not running(ni)and not running(wi)
ne=json.loads((B/'NODE_EXIT_ACTUAL.json').read_bytes());assert ne['all_own_children_waited']and ne['private_EX_released']and ne['terminal_owner_ack']
for path in(C.parent/'native_floor_supervisor.lock',C.parent/'autonomy_controller.lock',Path(v['spec']['private_lock'])):
 with path.open('rb+')as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
c=json.loads(C.read_bytes());assert c['active_segment']is None
segments=[s for s in c['completed_segments']if s.get('owner_parent_pid')==oi['pid']];assert len(segments)==1;s=segments[0];x=s['experts']['jump_72'];g=v['go']['jump_72'];assert x['started_epoch']==g['learning_started_epoch']and x['ended_epoch']>=x['started_epoch']and x['duration_bound_passed']and final['rows']['jump_72']['terminal_all_own_children_waited']
rawfee=x['charged_seconds'];assert abs(s['charged_expert_seconds']-rawfee)<1e-5
texts=[]
for root in(O,B,J/'production'):
 for p in sorted(root.iterdir()):
  if p.is_file()and p.suffix in('.json','.log'):
   b=p.read_bytes();texts.append(dict(path=str(p),bytes=len(b),SHA=hashlib.sha256(b).hexdigest(),UTF8=b.decode('utf8','replace')))
latest=json.loads((J/'production/latest_complete.json').read_bytes());assert latest['saved_WM_updates']==1 and latest['teacher_Adam_step']==42940 and latest['save_epoch']<g['save_deadline']
print(json.dumps(dict(passed=True,epoch=time.time(),original_owner_node_worker_all_OUT=True,canonical_None=True,shared_and_private_EX_free=True,original_GO=v['go'],original_one_owner_segment=s,original_raw_fee_SUMONCE=rawfee,closing_balance_snapshot=c['remaining_training_seconds'],one_actual_WM_update_before_receipt_failure=True,partial_checkpoint_metadata_only=latest,qualified_formal=False,model_transfer_hash_decode=0,full_UTF8=texts,no_account_writes=True)))"""
  actual=d.code(client,d.PY72,code,dict(owner=launch['owner'],spec=launch['specs']['jump_72'],go=go),timeout=100);put('ROOT276V2_RECEIPT_FAILURE_ALL_CLOSED_ONE_ORIGINAL_RAW_FEE_RETURNED_ACTUAL.json',actual);print(json.dumps({k:v for k,v in actual.items()if k not in('full_UTF8','original_one_owner_segment','original_GO')}))
 finally:
  secret=None
  if client is not None:client.close();client=None
  if transport is not None:transport.SESSION=previous
  put('ROOT276V2_FAILED_CLOSURE_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json',dict(epoch=time.time(),all_owned_SSH_closed=client is None,SESSION_restored=transport is None or transport.SESSION is previous,global_serial_control_client_lease='FREE'))
if __name__=='__main__':
 try:main()
 except BaseException:put('ROOT276V2_FAILURE_CLOSURE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_signal_or_automatic_retry=True));raise
