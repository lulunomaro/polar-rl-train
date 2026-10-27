"""UNEXECUTED remote read-only helper; collector concatenates pure protocol first."""


def _read_json(path):
 import json
 return json.loads(path.read_bytes())


def _own_processes(roots):
 import os,psutil
 found=[]
 for p in psutil.process_iter(['pid','cmdline','create_time']):
  try:
   if p.pid!=os.getpid() and any(arg.startswith(tuple(str(root)+'/' for root in roots)) for arg in p.info['cmdline'] or []):found.append(p.info)
  except psutil.Error:pass
 return found


def _free_locks(paths):
 import fcntl
 rows=[]
 for path in dict.fromkeys(paths):
  with path.open('rb+') as stream:
   fcntl.flock(stream,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(stream,fcntl.LOCK_UN)
  rows.append(dict(path=str(path),actual_fcntl_free=True))
 return rows


def _texts(key,root):
 import hashlib
 rows=[]
 for path in root.rglob('*'):
  if path.is_file() and not path.is_symlink() and '__pycache__' not in path.parts and path.suffix in ('.py','.json','.jsonl','.log','.txt','.md','.sh','.yaml','.yml','.toml','.csv'):
   raw=path.read_bytes();rows.append(dict(path=str(path),relative=key+'/'+path.relative_to(root).as_posix(),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()))
 return rows


def close_owner_readonly(v):
 from pathlib import Path
 import time
 q=v['q'];validate_detached(q);original_go=v['original_go'];require(set(original_go)==set(q['specs']),'Active GO schedule differs');closing_gate(original_go,time.time());validate_actual_GO_binding(original_go,q)
 # The second original900-second gate is deliberately inside the actual72
 # process before waiting, canonical reads, text or model collection.
 assert max(x['nominal_end_epoch'] for x in original_go.values())-time.time()<=900,'Original <=900 closing boundary retained'
 owner=Path(q['owner_root']);until=time.monotonic()+850
 while not (owner/'COHORT_FINAL.json').exists() or not (owner/'OWNER_EXIT_ACTUAL.json').exists() or _own_processes([owner]):
  assert time.monotonic()<until,'Actual72 owner closure incomplete; no scheduled FINAL'
  time.sleep(3)
 cohort=_read_json(owner/'COHORT_FINAL.json');exited=_read_json(owner/'OWNER_EXIT_ACTUAL.json')
 require(cohort['go']==original_go,'Actual owner signed GO differs from original observer')
 require(all(row['run_id']==q['run_id'] and row['original_owner_pid']==q['owner_identity']['pid']
  and row['original_owner_creation']==q['owner_identity']['creation'] for row in cohort['go'].values()),'Actual owner identity differs')
 C=Path(CANONICAL);c=_read_json(C)
 require(c['active_segment'] is None and c['authorized_training_seconds']==2268000
  and c['historical_budget_extension_count']==9 and c['new_authority_budget_extensions']==[]
  and c['authority_generation']=='MOD4_SINGLE_WRITER72_20261026','Sole72 original account schema/active state differs')
 segments=[row for row in c['completed_segments'] if row.get('owner_parent_pid')==q['owner_identity']['pid']
  and row['started_epoch']>=q['owner_identity']['creation']]
 require(len(segments)==1,'Original owner segment is not exactly once')
 locks=_free_locks([C.parent/'native_floor_supervisor.lock',C.parent/'autonomy_controller.lock'])
 result=dict(epoch=time.time(),cohort=cohort,owner_exit=exited,original_segment=segments[0],
  original_canonical_remaining=c['remaining_training_seconds'],original_locks=locks,
  all_authority72_owner_children_actual_out=True,canonical_path=str(C),canonical_active_segment=c['active_segment'],
  text_files=_texts('owner',owner),no_account_write_or_canonical_copy=True)
 # Keep false duration flags intact. Readback is still retained even when an
 # independent fee check rejects; the CPU reviewer classifies it separately.
 try:result['original_fees_CPU_metadata']=validate_fees(result,original_go,q['owner_identity'])
 except Exception as error:result['original_fee_validation_error']=type(error).__name__+': '+str(error)
 return result


def close_node_readonly(v):
 from pathlib import Path
 import time
 q=v['q'];validate_detached(q);key=v['key'];require(key in active_keys(q),'Invalid active node key')
 root=Path(q['roots'][key]);until=time.monotonic()+180
 while not (root/'NODE_EXIT_ACTUAL.json').exists() or _own_processes([root]):
  assert time.monotonic()<until,'Actual node/children closure incomplete'
  time.sleep(3)
 exited=_read_json(root/'NODE_EXIT_ACTUAL.json');terminal=_read_json(root/'NODE_TERMINAL_ACTUAL.json')
 require(exited['actual_all_own_children_waited'] and exited['validation_fcntl_released_if_acquired'],'Node original exit incomplete')
 paths=[Path(q['specs'][key]['private_lock'])]
 if key=='h1':
  # Original H1 OWN_SOURCE_GPU_NATIVE_ONLY.lock is its private lease.
  if q.get('h1_lease_path'):paths.append(Path(q['h1_lease_path']))
 else:paths.append(Path('/home/lc01/Zonglin Li/zonglin2/state/finite_environment_validation.lock'))
 return dict(epoch=time.time(),key=key,node_exit=exited,node_terminal=terminal,locks=_free_locks(paths),
  H1_private_lease_checked=key=='h1',all_selected_target_processes_actual_out=True,
  text_files=_texts(key,root),no_account_read_or_write_on_node=True)
