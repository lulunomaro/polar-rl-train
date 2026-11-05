"""Bounded read-only original-authority summary after actual closed zeroGO A3. Not a lease."""
from pathlib import Path
import json,sys,time
D=Path(__file__).resolve().parent;marker=D/'AFTER_ADMISSION3_WATCH_ONCE.json';out=D/'AFTER_ADMISSION3_AUTHORITY_WATCH_RESULT.json';assert not marker.exists()and not out.exists();t=json.loads((D/'ADMISSION3_RESOURCE_TIMEOUT_TRUTH.json').read_bytes());assert t['all9_actual_GO_SDK_PT_or_PPO']==0 and t['actual_outer_wait']['original_owner_reaped']is True and all(t['actual_owner_exit'][k]is True for k in('all_own_children_waited','original_cost_settled','original_private_finite_authority_leases_released'))
marker.write_text(json.dumps(dict(epoch=time.time(),prior_closed=t['closed_path'],read_only_original_summary_only=True,no_old_owner_restart=True)),encoding='utf8');sys.path.insert(0,str(D.parent/'mod4v1_experts_fulldr_rm70_20261101'));from project_connector import connect72
c=connect72();events=[];last=None;gaps=0;until=time.monotonic()+1800
code="""from pathlib import Path
import json,time
p=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json');v=json.loads(p.read_bytes());assert v['authority_generation']=='MOD4_SINGLE_WRITER72_20261026';a=v['active_segment'];print(json.dumps(dict(epoch=time.time(),owner=None if a is None else dict(run=a.get('owner_run_id'),pid=a.get('owner_parent_pid',a.get('pid')),started_epoch=a.get('started_epoch')),remaining_training_seconds=v['remaining_training_seconds'],reserve=v['finite_minimum_remaining_seconds'],snapshot_not_GPU_or_lock_lease=True,canonical_writes_or_copies_GPU_locks_models_signals=0)))"""
try:
 import shlex
 while time.monotonic()<until:
  try:
   i,o,e=c.exec_command(shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -B -c '+shlex.quote(code),timeout=25);i.close();text=o.read().decode();err=e.read().decode();rc=o.channel.recv_exit_status();assert rc==0,err;v=json.loads(text);assert v['reserve']==86412.86069250107;gaps=0;key=json.dumps(v['owner'],sort_keys=True)
   if key!=last:events.append(v);print(json.dumps(v),flush=True);last=key
   if v['owner']is None:
    events.append(dict(status='ORIGINAL_OWNER_NONE_OBSERVED_NOT_A_LEASE',epoch=time.time()));break
  except Exception as exc:
   gaps+=1;events.append(dict(epoch=time.time(),schema_or_read_gap=str(exc),consecutive=gaps));assert gaps<3,'Three read/schema gaps: stop without admission'
  time.sleep(30)
 else:events.append(dict(status='BOUNDED_READONLY_WAIT_EXPIRED_NO_ADMISSION',epoch=time.time()))
 out.write_text(json.dumps(dict(events=events,read_only=True,no_stage_dispatch_or_training=True,old_window_not_extended=True),indent=2),encoding='utf8');print(json.dumps(dict(result=str(out),final=events[-1])),flush=True)
finally:c.close()
