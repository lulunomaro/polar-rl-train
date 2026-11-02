"""Bounded READ-ONLY resource release witness after actual prior zero-GO timeout.
No locks acquired/cleared, no source model/SDK/GO/canonical mutation or owner run.
"""
from pathlib import Path
import sys,json,shlex,time
R=Path(__file__).resolve().parent;out=R/'reports/A1_V6_RELEASE_OBSERVED_AFTER_TIMEOUT_V2.json';once=R/'A1_V6_RESOURCE_RELEASE_OBSERVER_V2_ONCE.json';assert not once.exists()and not out.exists();p=json.loads((R/'A1_NATIVE_V6_LATEST_CLOSED_RESULT_PATH.json').read_bytes());closed=json.loads(Path(p['path']).read_bytes());ex=closed['parent_exit'];assert ex and all(ex[k]is True for k in('all_own_children_waited','original_cost_settled','original_leases_released'));assert all(r['status']=='CLOSED_UNSTARTED'and r.get('actual_GO')is None and r.get('startup')is None for r in closed['rows'])and len(closed['rows'])==8;assert'Original preGOresourcewait1800expired'in json.dumps(ex['errors']);once.write_text(json.dumps(dict(prior_root=closed['root'],prior_exit=ex['epoch'],started=time.time(),max_readonly_observation_seconds=1800,not_an_extension_of_any_native_parent=True),indent=2),encoding='utf-8')
sys.path.insert(0,str(R.parent/'mod4v1_experts_fulldr_rm70_20261101'));from project_connector import connect72
code=r'''
from pathlib import Path
import os,json,time,subprocess
B=Path('/home/lc01/Zonglin Li/zonglin2');D=B/'state/mod4_single_canonical_authority_20261026';paths=[D/'native_floor_supervisor.lock',D/'autonomy_controller.lock',B/'state/finite_environment_validation.lock']+[B/('state/three_expert_v2_'+u+'.lock')for u in('GPU-16828f91-2b45-b646-8dc0-9481138e2842','GPU-c27eecbd-6838-7290-1cd2-37e34522213d')];until=time.monotonic()+1800;last=None
while time.monotonic()<until:
 c=json.loads((D/'TRAINING_BUDGET_10H.json').read_bytes());kernel=Path('/proc/locks').read_text().splitlines();rows=[]
 for p in paths:
  st=p.stat();key=f'{os.major(st.st_dev):02x}:{os.minor(st.st_dev):02x}:{st.st_ino}';matches=[x for x in kernel if key in x];rows.append(dict(path=str(p),kernel_records=matches))
 clear=c['active_segment']is None and all((not any(' WRITE 'in x for x in r['kernel_records']))if r['path'].endswith('finite_environment_validation.lock')else not r['kernel_records']for r in rows)
 value=dict(kind='READONLY_ORIGINAL_RESOURCE_RELEASE_NOT_ADMISSION',epoch=time.time(),canonical_active=c['active_segment'],remaining_training_seconds=c['remaining_training_seconds'],lock_records=rows,original_canonical_and_authority_private_locks_observed_clear=clear,no_lock_acquisition_or_Cwrite_or_signals=True)
 sig=(json.dumps(c['active_segment'].get('owner_parent_pid',c['active_segment'].get('pid')))if c['active_segment']else None,tuple(tuple(x.split()[1:6])for r in rows for x in r['kernel_records']),clear)
 if sig!=last or clear:print(json.dumps(value),flush=True);last=sig
 if clear:break
 time.sleep(20)
else:raise TimeoutError('Readonly resource-release observation cap; no parent started or signalled')
'''
c=connect72();last=None
try:
 i,o,e=c.exec_command(shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -u -B -c '+shlex.quote(code),timeout=1900);i.close()
 for line in o:
  if not line.strip():continue
  last=json.loads(line);(R/'reports/A1_V6_RELEASE_OBSERVER_CURRENT_V2.json').write_text(json.dumps(last,indent=2),encoding='utf-8');print('ORIGINAL_RESOURCE_RELEASE_OBSERVER '+json.dumps(last),flush=True)
 err=e.read().decode(errors='replace');rc=o.channel.recv_exit_status();value=dict(kind='ACTUAL_READONLY_RELEASE_WITNESS_AFTER_V6_ALL8_ZERO_GO_TIMEOUT',prior_root=closed['root'],prior_exit=ex,returncode=rc,stderr=err,actual=last,original_canonical_and_authority_private_locks_observed_clear=rc==0 and bool(last)and last['original_canonical_and_authority_private_locks_observed_clear'],no_native_parent_extension_or_ledger_mutation=True);out.write_text(json.dumps(value,indent=2),encoding='utf-8');print(json.dumps(value,indent=2));assert rc==0,(rc,err)
finally:c.close()
