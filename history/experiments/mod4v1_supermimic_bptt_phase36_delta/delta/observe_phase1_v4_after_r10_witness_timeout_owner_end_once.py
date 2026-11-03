"""NEW 900s readonly observation of the already-observed finite owner's end.
Prior readonly observer timed out and closed. No parent is active in our scope;
this neither extends a native/resource wait nor acquires or changes any lease.
Uses the entire original readonly resource query literal without modification.
"""
from pathlib import Path
import ast,json,hashlib,sys,time,shlex
R=Path(__file__).resolve().parent;prior_path=R/'reports/PHASE1_V4_R10_RESOURCES_RELEASED_AFTER_ZERO_GO_TIMEOUT_V1.json';prior_raw=prior_path.read_bytes();prior=json.loads(prior_raw);truth=json.loads((R/'reports/PHASE1_V4_ZERO_ADMISSION_CLOSED_TRUTH_V1.json').read_bytes());assert prior['observer_timed_out']and not prior['resource_release_observed']and not prior['actual']['original_frozen_resources_observed_clear'];assert prior['old_root']==truth['root']and prior['old_closed_metadata_SHA']==truth['closed_result']['SHA256']and prior['old_closed_epoch']==truth['parent_exit_scope']['epoch'];owner=prior['actual']['canonical_summary']['active_segment'];assert owner['owner_run_id']=='MOD4V1_SCUT_REPAIRED_E0_20000ENV_1H_1793723033230108600'and owner['pid']==1551922 and owner['experts']['scut_step270']['max_parent_seconds']==3900
marker=R/'PAPER_ALIGNED_REBUILD_20261103/PHASE1_V4_R10_FOLLOWUP_OWNER_END_OBSERVER_STARTED_ONCE.json';out=R/'reports/PHASE1_V4_R10_FOLLOWUP_OWNER_FINITE_END_RESOURCE_WITNESS_V1.json';current=R/'reports/PHASE1_V4_R10_FOLLOWUP_OWNER_END_RESOURCE_CURRENT_V1.json';assert not marker.exists()and not out.exists()
src=(R/'observe_bound_probe_resources_after_zero_admission_timeout_once.py').read_bytes();node=next(n for n in ast.parse(src).body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='code'for t in n.targets));code=ast.literal_eval(node.value);assert type(code)is str;ast.parse(code)
with marker.open('x',encoding='utf-8')as f:json.dump(dict(epoch=time.time(),prior_observer_final=str(prior_path),prior_final_SHA256=hashlib.sha256(prior_raw).hexdigest(),prior_observer_closed_timed_out=True,cap_seconds=900,interval_seconds=20,expected_owner_run_id=owner['owner_run_id'],expected_owner_pid=owner['pid'],original_readonly_code_source_SHA256=hashlib.sha256(src).hexdigest(),native_parent_or_original_wait_extension=False),f,indent=2)
sys.path.insert(0,str(R.parent/'mod4v1_experts_fulldr_rm70_20261101'));from project_connector import connect72
c=connect72();deadline=time.monotonic()+900;last=None
try:
 while True:
  i,o,err=c.exec_command(shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -B -c '+shlex.quote(code),timeout=60);i.close();text=o.read().decode();error=err.read().decode();rc=o.channel.recv_exit_status();assert rc==0,error;a=json.loads(text);assert a['epoch']>=prior['actual']['epoch'];active=a['canonical_summary']['active_segment'];changed=isinstance(active,dict)and(active.get('owner_run_id')!=owner['owner_run_id']or active.get('pid')!=owner['pid']);ready=a['original_frozen_resources_observed_clear'];record=dict(kind='READONLY_POST_PHASE1_V4_ZERO_GO_FINITE_OWNER_END_FOLLOWUP_NOT_ADMISSION_R10',old_root=truth['root'],old_closed_epoch=truth['parent_exit_scope']['epoch'],old_closed_metadata_SHA=truth['closed_result']['SHA256'],actual=a,prior_closed_observer_SHA256=hashlib.sha256(prior_raw).hexdigest(),observer_only=True,old_parent_wait_not_extended=True,owner_changed_to_different_active_segment=changed)
  current.write_text(json.dumps(record,indent=2),encoding='utf-8');state=(a['original_relevant_leases_clear'],ready,active.get('owner_run_id')if isinstance(active,dict)else None)
  if state!=last:print('PHASE1_V4_FINITE_OWNER_END_READONLY_STATE '+json.dumps(dict(ready=ready,leases_clear=state[0],owner=state[2],epoch=a['epoch'])),flush=True);last=state
  if ready or changed or time.monotonic()>=deadline:
   record.update(resource_release_observed=ready,observer_timed_out=not ready and not changed,stop_reason='actual_original_resources_clear'if ready else'different_owner_observed_no_following'if changed else'bounded_readonly_followup_expired')
   with out.open('x',encoding='utf-8')as f:json.dump(record,f,indent=2)
   print('FINITE_OWNER_END_READONLY_WITNESS '+str(out),flush=True);break
  time.sleep(min(20,max(0,deadline-time.monotonic())))
finally:c.close()
