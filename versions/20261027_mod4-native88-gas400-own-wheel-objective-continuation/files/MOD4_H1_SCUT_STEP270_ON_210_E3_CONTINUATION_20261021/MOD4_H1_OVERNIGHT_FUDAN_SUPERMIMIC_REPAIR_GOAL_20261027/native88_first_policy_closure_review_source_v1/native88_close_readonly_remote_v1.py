"""UNUSED remote close reader; pure protocol is prepended by collector."""
def _read_json(path):
 import json
 return json.loads(path.read_bytes())
def _recorded_out(record):
 import psutil
 require(isinstance(record,dict) and type(record.get('pid')) is int and record['pid']>0 and record.get('creation',0)>0,'recorded own pid/create required')
 try:p=psutil.Process(record['pid']);creation=p.create_time()
 except psutil.NoSuchProcess:return True
 # A recycled PID is out for this purpose; never inspect its exe/argv.
 return creation!=record['creation']
def _free_locks(paths):
 import fcntl
 rows=[]
 for path in dict.fromkeys(paths):
  with path.open('rb+') as stream:fcntl.flock(stream,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(stream,fcntl.LOCK_UN)
  rows.append(dict(path=str(path),actual_fcntl_free=True))
 return rows
def _texts(key,root):
 import hashlib
 rows=[]
 for path in root.rglob('*'):
  if path.is_file() and not path.is_symlink() and '__pycache__' not in path.parts and path.suffix in ('.py','.json','.jsonl','.log','.txt','.md','.sh','.yaml','.yml','.toml','.csv'):
   raw=path.read_bytes();rows.append(dict(path=str(path),relative=key+'/'+path.relative_to(root).as_posix(),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()))
 return rows
def _host_recorded(q,backend):
 # Actual deployer receipts only, never process enumeration or a PID guess.
 rows=[r for r in q.get('own_children',[]) if r['execution_backend']==backend]
 for r in rows:require(type(r['pid']) is int and r['pid']>0 and r['creation']>0,'own child receipt shape')
 return rows
def close_owner_readonly(v):
 from pathlib import Path
 import time
 q=v['q'];validate_detached(q);go=v['original_go'];closing_gate(go,time.time());validate_actual_GO_binding(go,q)
 assert max(x['nominal_end_epoch'] for x in go.values())-time.time()<=900,'Original <=900 closing boundary retained'
 owner=Path(q['owner_root']);until=time.monotonic()+850
 while not (owner/'COHORT_FINAL.json').exists() or not (owner/'OWNER_EXIT_ACTUAL.json').exists() or not _recorded_out(q['owner_identity']):
  assert time.monotonic()<until,'Actual72 owner closure incomplete; no scheduled FINAL';time.sleep(3)
 cohort=_read_json(owner/'COHORT_FINAL.json');exited=_read_json(owner/'OWNER_EXIT_ACTUAL.json')
 require(cohort['go']==go,'actual original signed GO differs')
 # Only target72 recorded own children are probed on72. Source210 pids are
 # not looked up on the wrong host, and unknown peer processes stay untouched.
 own72=_host_recorded(q,'target72')
 recovery_root=Path(q['roots']['recovery']);node72=_read_json(recovery_root/'NODE_IDENTITY.json')
 require(node72['pid']==q['nodes']['recovery']['detached_pid'],'actual deployed recovery node PID')
 own72.append(node72)
 if cohort['rows']['recovery'].get('worker'):own72.append(cohort['rows']['recovery']['worker'])
 while any(not _recorded_out(r) for r in own72):
  assert time.monotonic()<until,'actual recorded72 own children not out';time.sleep(3)
 for key in KEYS:require(cohort['rows'][key]['terminal_all_own_children_waited'] is True,'original node child-wait proof')
 C=Path(CANONICAL);c=_read_json(C)
 require(c['active_segment'] is None and c['authorized_training_seconds']==2268000 and c['historical_budget_extension_count']==9 and c['new_authority_budget_extensions']==[] and c['authority_generation']=='MOD4_SINGLE_WRITER72_20261026','sole72 original account schema/CNone')
 segments=[row for row in c['completed_segments'] if row.get('owner_parent_pid')==q['owner_identity']['pid'] and row['started_epoch']>=q['owner_identity']['creation']]
 require(len(segments)==1,'original owner segment not exactly once')
 result=dict(epoch=time.time(),cohort=cohort,owner_exit=exited,original_segment=segments[0],original_canonical_remaining=c['remaining_training_seconds'],
  original_locks=_free_locks([C.parent/'native_floor_supervisor.lock',C.parent/'autonomy_controller.lock']),all_authority72_owner_children_actual_out=True,
  canonical_path=str(C),canonical_active_segment=c['active_segment'],text_files=_texts('owner',owner),no_account_write_or_canonical_copy=True,
  actual_hostscoped_recorded_own_children=own72,unknown_processes_not_enumerated=True)
 try:result['original_fees_CPU_metadata']=validate_fees(result,go,q['owner_identity'])
 except Exception as error:result['original_fee_validation_error']=type(error).__name__+': '+str(error)
 return result
def close_node_readonly(v):
 from pathlib import Path
 import time
 q=v['q'];validate_detached(q);key=v['key'];require(key in KEYS,'active selected H1 node')
 root=Path(q['roots'][key]);until=time.monotonic()+180
 identity=_read_json(root/'NODE_IDENTITY.json');require(identity['pid']==q['nodes'][key]['detached_pid'],'actual deployed node receipt')
 backend='source210' if key=='h1' else 'target72';own=_host_recorded(q,backend)
 while not (root/'NODE_EXIT_ACTUAL.json').exists() or not _recorded_out(identity) or any(not _recorded_out(r) for r in own):
  assert time.monotonic()<until,'actual node/recorded own children closure incomplete';time.sleep(3)
 exited=_read_json(root/'NODE_EXIT_ACTUAL.json');terminal=_read_json(root/'NODE_TERMINAL_ACTUAL.json')
 require(exited['actual_all_own_children_waited'] is True and exited['validation_fcntl_released_if_acquired'] is True and terminal['row']['terminal_all_own_children_waited'] is True,'original node complete child wait')
 worker=terminal['row'].get('worker')
 if worker:require(_recorded_out(worker),'original worker actual out')
 paths=[Path(q['specs'][key]['private_lock'])]
 if key=='h1':
  if q.get('h1_lease_path'):paths.append(Path(q['h1_lease_path']))
 else:paths.append(Path('/home/lc01/Zonglin Li/zonglin2/state/finite_environment_validation.lock'))
 return dict(epoch=time.time(),key=key,node_exit=exited,node_terminal=terminal,locks=_free_locks(paths),H1_private_lease_checked=key=='h1',
  all_selected_target_processes_actual_out=True,text_files=_texts(key,root),no_account_read_or_write_on_node=True,
  actual_hostscoped_recorded_own_children=own,unknown_processes_not_enumerated=True)
