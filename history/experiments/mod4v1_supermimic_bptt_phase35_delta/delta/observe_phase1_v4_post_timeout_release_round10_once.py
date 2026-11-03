"""NEW bounded readonly release witness, after actual V4 zero-admission closure.
No native parent or lock acquisition; this does not extend any expired window.
"""
from pathlib import Path
import ast,json,hashlib,sys,time,shlex
R=Path(__file__).resolve().parent;guard=R/'PAPER_ALIGNED_REBUILD_20261103/PHASE1_V4_R10_READONLY_RELEASE_OBSERVER_STARTED_ONCE.json';out=R/'reports/PHASE1_V4_R10_RESOURCES_RELEASED_AFTER_ZERO_GO_TIMEOUT_V1.json';current=R/'reports/PHASE1_V4_R10_POST_TIMEOUT_RESOURCE_OBSERVER_CURRENT_V1.json';assert not guard.exists()and not out.exists()
v=json.loads((R/'reports/PHASE1_V4_ZERO_ADMISSION_CLOSED_TRUTH_V1.json').read_bytes());e=v['parent_exit_scope'];assert v['actual_group_admission']is None and e['child_waits']==[]and e['all_own_children_waited']and e['original_single_GPU_private_EX_released']and e['original_global_finite_EX_released']and v['outer_actual_wait']['actual_parent_p_wait_returned']and v['outer_actual_wait']['returncode']==1
oldsha=v['closed_result']['SHA256'];original=R/'observe_bound_probe_resources_after_zero_admission_timeout_once.py';src=original.read_bytes();node=next(n for n in ast.parse(src).body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='code'for t in n.targets));code=ast.literal_eval(node.value);assert type(code)is str;ast.parse(code)
with guard.open('x',encoding='utf-8')as f:json.dump(dict(epoch=time.time(),old_root=v['root'],old_closed_epoch=e['epoch'],old_closed_metadata_SHA=oldsha,source_readonly_code=original.name,source_readonly_code_SHA256=hashlib.sha256(src).hexdigest(),observer_only_no_parent_retry=True,cap_seconds=1800,interval_seconds=20),f,indent=2)
sys.path.insert(0,str(R.parent/'mod4v1_experts_fulldr_rm70_20261101'));from project_connector import connect72
c=connect72();deadline=time.monotonic()+1800;last=None
try:
 while True:
  i,o,err=c.exec_command(shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -B -c '+shlex.quote(code),timeout=60);i.close();text=o.read().decode();error=err.read().decode();rc=o.channel.recv_exit_status();assert rc==0,error;a=json.loads(text);assert a['epoch']>=e['epoch'];record=dict(kind='READONLY_POST_PHASE1_V4_ZERO_GO_RELEASE_WITNESS_NOT_ADMISSION_R10',old_root=v['root'],old_closed_epoch=e['epoch'],old_closed_metadata_SHA=oldsha,actual=a,observer_only=True,old_parent_wait_not_extended=True)
  current.write_text(json.dumps(record,indent=2),encoding='utf-8');active=a['canonical_summary'].get('active_segment');state=(a['original_relevant_leases_clear'],a['original_frozen_resources_observed_clear'],active.get('owner_run_id')if isinstance(active,dict)else None)
  if state!=last:print('PHASE1_V4_R10_READONLY_RESOURCE_STATE '+json.dumps(dict(ready=state[1],leases_clear=state[0],owner=state[2],epoch=a['epoch'])),flush=True);last=state
  if a['original_frozen_resources_observed_clear']or time.monotonic()>=deadline:
   record.update(resource_release_observed=a['original_frozen_resources_observed_clear'],observer_timed_out=not a['original_frozen_resources_observed_clear']);out.write_text(json.dumps(record,indent=2),encoding='utf-8');print('READONLY_RELEASE_WITNESS '+str(out));break
  time.sleep(min(20,max(0,deadline-time.monotonic())))
finally:c.close()
