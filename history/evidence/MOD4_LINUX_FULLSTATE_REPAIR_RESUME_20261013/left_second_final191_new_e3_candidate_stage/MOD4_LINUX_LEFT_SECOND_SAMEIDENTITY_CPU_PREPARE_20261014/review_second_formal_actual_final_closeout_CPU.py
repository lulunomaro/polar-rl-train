"""Actual completed own final and sole original cost check; no GPU/budget writes."""
from pathlib import Path
import json,time
import second_root_owned_transport_common_v1 as t
CODE=r'''
from pathlib import Path
import json,sys,torch,time,psutil,fcntl,hashlib
R=Path(CONTEXT['proposed_root']);sys.path.insert(0,str(R));a=R/'left_second_formal3600_v1'
from second_target_CPU_pure_guard_v2 import logical_fullsave,SOURCE_SHA,KEY,same,sha,B,LOCKS
from left_sameidentity_typed13_receipts import validate_set
ready=json.loads((R/'LEFT_SECOND_FORMAL_SAVED_REVIEW_READY.json').read_bytes());ex=json.loads((a/'EXIT_RECEIPT.json').read_bytes());m=json.loads((R/'LEFT_SECOND_SAMEIDENTITY_ADMISSION_MANIFEST.json').read_bytes())
assert ready['actual_second_formal_window'] is True and ready['actor9_changed'] is True and ready['qualified50'] is False
assert ex['returncode']==0 and ex['child_actually_absent'] and ex['canonical_cost_charged_once'] and not ex['physics_capacity_error']
assert not (R/'LEFT_SECOND_FORMAL_PARENT_ERROR.json').exists() and (R/'GUARDIAN_EXIT.json').is_file()
disp=json.loads((a/'DISPATCH_RECEIPT.json').read_bytes())
for row in [disp['parent'],disp['child']]:
 assert not psutil.pid_exists(row['pid']) or psutil.Process(row['pid']).create_time()!=row['created']
for p in psutil.process_iter(['pid','cmdline']):
 assert not any(str(R) in v for v in (p.info['cmdline'] or [])),dict(pid=p.pid,argv=p.info['cmdline'])
for lock in LOCKS:
 with lock.open('r+b') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
budget=json.loads(B.read_bytes());assert budget['active_segment'] is None and budget['authorized_training_seconds']==1188000 and len(budget['budget_extensions'])==7
segments=[s for s in budget['completed_segments'] if s['kind']==ex['canonical_unique_segment']];assert len(segments)==1
segment=segments[0];assert segment['owner_parent_pid']==disp['parent']['pid'] and segment['source_SHA']==SOURCE_SHA and segment['ended_epoch']>=segment['started_epoch']
assert abs((segment['ended_epoch']-segment['started_epoch'])-ex['parent_load_learn_save_exit_seconds'])<.1
for row in m['sourcefreeze']:assert sha(row['path'])==row['sha256']
assert len(m['sourcefreeze'])==541
path=Path(ready['own_checkpoint']);assert sha(path)==ready['checkpoint_sha256']==CONTEXT['own_final_SHA']
latest=json.loads((path.parent/'latest_complete.json').read_bytes());assert latest['checkpoint']==str(path) and latest['pid']==disp['child']['pid']
c=torch.load(path,map_location='cpu',weights_only=False);source=torch.load(m['source']['path'],map_location='cpu',weights_only=False);info=logical_fullsave(c)
assert same(c[KEY],source[KEY]) and m['source']['sha256']==SOURCE_SHA
delta=[float(c['optimizer_state_dict']['state'][i]['step'])-float(source['optimizer_state_dict']['state'][i]['step']) for i in range(17)];assert len(set(delta))==1 and delta[0]==ready['actual_saved_updates']*20==3820
assert ready['actual_saved_updates']==191 and ready['envsteps']==91680000 and ready['callbacks']==18336
typed=validate_set(list(path.parent.glob('*STARTUP*VERIFIED.json')),disp['child']['pid'],SOURCE_SHA)
health=json.loads((path.parent/'CLOCK_TRAINING_HEALTH.json').read_bytes());assert health==ready['health'] and health['control_steps']==4584 and health['actual_physics_callbacks']==18336 and health['integrity_task_reset_events']==health['unknown_task_reset_events']==0 and not health['nonfinite_observed'] and health['stop_reason'] is None
assert not torch.cuda.is_initialized()
print(json.dumps(dict(epoch=time.time(),passed=True,root=str(R),own_final=dict(path=str(path),bytes=path.stat().st_size,sha256=sha(path)),actual_fullstate=info,saved_updates=191,controls=4584,envsteps=91680000,callbacks=18336,optimizer_delta=delta[0],actor9_changed=True,initializer_metadata_exact_not_repeated=True,thirteen_typed_startup=typed,actual_sourcefreeze_count=len(m['sourcefreeze']),formal_final_ready_SHA=sha(R/'LEFT_SECOND_FORMAL_SAVED_REVIEW_READY.json'),exit_receipt_SHA=sha(a/'EXIT_RECEIPT.json'),unique_cost=ex,sole_original_segment=segment,actual_parent_guardian_child_exit=True,two_actual_fcntl_free=True,canonical_idle=True,remaining_training_seconds_snapshot=budget['remaining_training_seconds'],no_PPO_GPU_RNG_or_budgetwrite=True,qualification_claimed=False)))
'''
def main():
 c=t.connect()
 try:
  result=t.run(c,CODE,'LEFT_SECOND_OWN_FORMAL_FINAL_CLOSEOUT_CPU_ACTUAL',dict(proposed_root=t.ROOT,own_final_SHA='e3e825b1e24f11885f2f9d5b196d85cbce4a46363cd09b440e7efa2b846fd47c'))
  out=t.REPORTS/'LEFT_SECOND_OWN_FORMAL_FINAL_CLOSEOUT_CPU_VERIFIED.json';t.write_once(out,result)
  print(json.dumps(dict(report=str(out),passed=result['passed'],own_final=result['own_final'],updates=result['saved_updates'],actual_parent_cost=result['unique_cost']['parent_load_learn_save_exit_seconds'],idle=result['canonical_idle'])))
 finally:c.close()
if __name__=='__main__':main()
