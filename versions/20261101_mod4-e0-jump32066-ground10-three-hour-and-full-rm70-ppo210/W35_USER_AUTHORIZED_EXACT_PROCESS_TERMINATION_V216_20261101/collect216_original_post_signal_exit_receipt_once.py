"""Read-only continuation after post-signal identity changed during shutdown.
Do not replay the termination entry or send another signal.
"""
from pathlib import Path
import hashlib,importlib.util,json,os,subprocess,sys,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports';S=T/'E0_JUMP32066_GROUND10_THREE_HOUR_V210_20261031'
F=T/'W35_MATERIAL_FAILURE_OWNED_STOP_V215_20261101'
def read(p):return json.loads(Path(p).read_bytes())
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,ensure_ascii=False,allow_nan=False)
def module(name,p):
 q=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(q);sys.modules[name]=m;q.loader.exec_module(m);return m
CODE="""from pathlib import Path
import json,psutil,fcntl,time,hashlib
O=Path(v['owner']['root']);J=Path(v['spec']['job_root']);C=J/'control210v2';P=J/'production';x=v['worker']
c=json.loads(Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json').read_bytes());cur=json.loads((O/'OWNER_CURRENT.json').read_bytes())
assert c['active_segment']['owner_parent_pid']==v['owner']['pid'] and cur['go']==v['go']
def status():
 try:
  p=psutil.Process(x['pid']);creation=p.create_time()
  if creation!=x['creation']:return dict(original_out=True,PID_reused_not_inspected=True)
  st=p.status()
  if st==psutil.STATUS_ZOMBIE:return dict(original_out=True,status='zombie_original')
  return dict(original_out=False,pid=p.pid,creation=creation,status=st,exe=p.exe(),argv=p.cmdline(),cwd=p.cwd())
 except psutil.NoSuchProcess:return dict(original_out=True,reason='original_process_out')
end=time.time()+180;row=status()
while time.time()<end and (not row['original_out'] or not (C/'NODE_EXIT_ACTUAL.json').is_file()):time.sleep(2);row=status()
node_exit=json.loads((C/'NODE_EXIT_ACTUAL.json').read_bytes()) if (C/'NODE_EXIT_ACTUAL.json').is_file() else None
terminal=json.loads((C/'NODE_TERMINAL_ACTUAL.json').read_bytes()) if (C/'NODE_TERMINAL_ACTUAL.json').is_file() else None
free=False
if row['original_out'] and node_exit and node_exit.get('all_own_children_waited') and node_exit.get('private_EX_released'):
 with Path(v['spec']['private_lock']).open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
 free=True
texts=[];tails=[]
for root in (C,P):
 for path in sorted(root.rglob('*')):
  if not path.is_file() or 'kit_isolation' in path.relative_to(root).parts or path.suffix not in ('.json','.log'):continue
  old=v['previous'].get(str(path));size=path.stat().st_size
  if old and path.suffix=='.log':
   if size<=old['bytes']:continue
   with path.open('rb') as f:f.seek(old['bytes']);raw=f.read(size-old['bytes'])
   tails.append(dict(path=str(path),byte_range=[old['bytes'],size],bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),UTF8=raw.decode('utf8','replace')))
  elif not old or path.name in ('NODE_CURRENT.json',):
   raw=path.read_bytes();texts.append(dict(path=str(path),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),UTF8=raw.decode('utf8','replace')))
cur=json.loads((O/'OWNER_CURRENT.json').read_bytes())
print(json.dumps(dict(epoch=time.time(),passed_exit_collection=True,original_worker_status=row,original_node_exit=node_exit,original_node_terminal=terminal,
 private_EX_free=free,E0_not_modified=True,additional_signals=0,current_owner_rows=cur['rows'],full_NEW_UTF8=texts,new_log_ranges_only=tails,
 canonical_write=False,model_raw_GPU_query_reads=0)))
"""
def main():
 assert read(R/'ROOT216_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json')['global_serial_control_client_lease']=='FREE'
 launch=read(S/'reports/ROOT210_ORIGINAL_UNIFIED_OWNER_LAUNCH_ACTUAL.json');state=read(S/'reports/ROOT210_UNIFIED_OWNER_AND_CANONICAL_AFTER_FIRST_ACTUAL.json')
 previous={r['path']:dict(bytes=r['bytes'],SHA=r['SHA']) for r in read(F/'reports/ROOT215_ORIGINAL_W35_STARTUP_STOP_AND_FULL_ERRORS_RETURNED_ACTUAL.json')['full_UTF8']}
 query=r'''Get-CimInstance Win32_Process -Filter "Name='python.exe' OR Name='ssh.exe'" | Where-Object { $_.CommandLine -match 'collect216_original_post_signal_exit_receipt_once|terminate216_only_|stop215_exact_|launch210_|collect210_' } | Select-Object Name,ProcessId,CreationDate,ExecutablePath,CommandLine | ConvertTo-Json -Depth 5 -Compress'''
 p=subprocess.run(['pwsh.exe','-NoProfile','-Command',query],capture_output=True,text=True,encoding='utf8',check=True);rows=json.loads(p.stdout) if p.stdout.strip() else [];rows=rows if isinstance(rows,list) else [rows]
 own=[x for x in rows if x['ProcessId']==os.getpid()];others=[x for x in rows if x['ProcessId']!=os.getpid()]
 put('ROOT216_EXIT_COLLECTION_FRESH_LOCAL_EXACT_CIM.json',dict(epoch=time.time(),PID=os.getpid(),exe=sys.executable,argv=sys.argv,rows=rows,others=others))
 assert len(own)==1 and own[0]['ExecutablePath'].lower()==sys.executable.lower() and own[0]['CreationDate'] and not others
 assert str(Path(__file__).resolve()).lower().replace('\\','/') in own[0]['CommandLine'].lower().replace('\\','/')
 put('ROOT216_POST_SIGNAL_READONLY_CONTINUATION_ONCE_PURPOSE.json',dict(epoch=time.time(),original_false='termination script remote line26 post-signal get_original exe/argv/cwd assertion',
  source_control_signals_not_replayed=True,additional_signals=0,known_PID990366_only=True,model_raw_GPU_PID_scan=0,new_log_bytes_only=True))
 wrapper=module('exit216_transport',T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v227.py');sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 client=None;transport=None;prior=None;secret=None
 try:
  transport,prior=wrapper.install();sec=module('exit216_memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');secret=sec.recover();client=d.connect72(secret);secret=None
  result=d.code(client,d.PY72,CODE,dict(owner=launch['owner'],spec=launch['specs']['w35_72'],go=state['current']['go'],worker=state['current']['rows']['w35_72']['worker'],previous=previous),timeout=240)
  put('ROOT216_ORIGINAL_POST_SIGNAL_EXIT_AND_NODE_RECEIPTS_ACTUAL.json',result)
  print(json.dumps(dict(original_status=result['original_worker_status'],node_exit=result['original_node_exit'],private_EX_free=result['private_EX_free'],additional_signals=0,E0_untouched=True)),flush=True)
 finally:
  secret=None
  if client is not None:client.close();client=None
  if transport is not None:transport.SESSION=prior
  put('ROOT216_EXIT_COLLECTION_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json',dict(epoch=time.time(),all_owned_SSH_closed=client is None,SESSION_restored=transport is None or transport.SESSION is prior,global_serial_control_client_lease='FREE'))
if __name__=='__main__':
 try:main()
 except BaseException:put('ROOT216_EXIT_COLLECTION_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_automatic_replay=True));raise
