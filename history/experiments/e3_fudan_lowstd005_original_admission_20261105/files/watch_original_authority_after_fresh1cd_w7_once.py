"""One bounded read-only release observer after actual zero-GO W7 close; no admission."""
from pathlib import Path
import json,time,sys,shlex
D=Path(__file__).resolve().parent
marker=D/'FDN_AFTER_FRESH1CD_W7_ORIGINAL_AUTHORITY_WATCH_ONCE.json';report=D/'FDN_AFTER_FRESH1CD_W7_ORIGINAL_AUTHORITY_WATCH_RESULT.json'
assert not marker.exists()and not report.exists()
closed=D/'reports/FDN_N20000_W7_FRESH1CD_20261105_005713/CLOSED_RESULT.json';v=json.loads(closed.read_bytes());m=v['metadata'];e=m['OWNER_EXIT_ACTUAL.json'];o=m['OUTER_OWNER_WAIT_ACTUAL.json']
assert v['closed']is True and all(e[k]is True for k in('all_own_children_waited','original_cost_settled','original_leases_released'))and o['original_owner_reaped']is True and o['actual_wait_returncode']==0 and o['original_owner_pid']==1625509 and o['controller_pid']==1625502
assert m['COHORT_FINAL.json']is None and all(value is None for key,value in m.items()if key.startswith('FDN_'))and 'Original preGOresourcewait1800expired'in json.dumps(e['errors'])
marker.write_text(json.dumps(dict(epoch=time.time(),purpose='observe original owner None after actual CLOSED zero-GO W7; not extension or replay of its expired parent',closed_result_pointer=str(closed),interval_seconds=30,max_observer_seconds=1800,read_only=True),indent=2),encoding='utf8')
sys.path.insert(0,str(D.parent/'mod4v1_experts_fulldr_rm70_20261101'));from project_connector import connect72
code='''from pathlib import Path
import json,time
p=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json');until=time.monotonic()+1800;last=None;gaps=0;v=None
while time.monotonic()<until:
 try:
  c=json.loads(p.read_bytes());assert c['authority_generation']=='MOD4_SINGLE_WRITER72_20261026';a=c['active_segment'];owner=None if a is None else {k:a[k]for k in('owner_run_id','owner_parent_pid','started_epoch')if k in a};v=dict(epoch=time.time(),owner=owner,remaining_training_seconds=c['remaining_training_seconds'],charged_training_seconds=c['charged_training_seconds']);key=json.dumps(owner,sort_keys=True)
  if key!=last:print(json.dumps(dict(event='OWNER_METADATA_CHANGE',**v)),flush=True);last=key
  if a is None:print(json.dumps(dict(event='FINAL',status='ORIGINAL_CANONICAL_OWNER_NONE_OBSERVED',**v,reader_gaps=gaps,read_only=True,locks_GPU_models_SDK_or_canonical_writes=0,does_not_prove_GPU_or_lock_eligibility=True)),flush=True);break
 except(json.JSONDecodeError,KeyError,AssertionError)as exc:
  gaps+=1
  if gaps>=3:raise RuntimeError('Original canonical schema/read integrity gap; never infer release')from exc
 time.sleep(30)
else:print(json.dumps(dict(event='FINAL',status='BOUNDED_READONLY_OBSERVER_EXPIRED',latest_metadata=v,reader_gaps=gaps,read_only=True,locks_GPU_models_SDK_or_canonical_writes=0)),flush=True)
'''
c=connect72();lines=[]
try:
 i,o,e=c.exec_command(shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -B -c '+shlex.quote(code),timeout=1900);i.close()
 for line in o:
  x=line.strip()
  if x:lines.append(x);print(x,flush=True)
 err=e.read().decode();rc=o.channel.recv_exit_status();report.write_text(json.dumps(dict(epoch=time.time(),returncode=rc,events=[json.loads(x)for x in lines],stderr=err,no_admission_or_training_dispatched=True),indent=2),encoding='utf8');print(json.dumps(dict(report=str(report),returncode=rc)),flush=True);assert rc==0,err
finally:c.close()
