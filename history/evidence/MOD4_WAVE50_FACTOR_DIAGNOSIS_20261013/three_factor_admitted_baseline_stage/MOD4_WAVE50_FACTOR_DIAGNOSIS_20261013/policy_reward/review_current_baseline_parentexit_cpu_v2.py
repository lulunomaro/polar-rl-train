"""Independent observer binds actual parent EXIT0; absent app-close receipt retained."""
from pathlib import Path
import argparse,hashlib,json,time,traceback,psutil,msvcrt
import numpy as np
D=Path(__file__).resolve().parent;W=D.parents[1]
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):
 assert not p.exists();p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
def matching_alive(pid,creation):
 try:x=psutil.Process(pid);return abs(x.create_time()-creation)<.05
 except psutil.NoSuchProcess:return False
def main():
 p=argparse.ArgumentParser();p.add_argument('--attempt',required=True);args=p.parse_args();A=Path(args.attempt);O=A/'output'
 receipt=json.loads((O/'COMPLETE_ACTUAL.json').read_bytes())
 dispatch=json.loads((A/'DISPATCH_RECEIPT.json').read_bytes());end=json.loads((A/'PARENT_EXIT_RECEIPT.json').read_bytes())
 assert receipt['passed_data_contract'] and receipt['no_PPO'] and not receipt['factor']['policy_factor']
 assert end['exit_code']==0 and end['complete_data_contract_present'] and not end['original_error_present']
 assert not (O/'ORIGINAL_ERROR.json').exists()
 child_alive=matching_alive(dispatch['child_pid'],dispatch['child_creation']);parent_alive=matching_alive(dispatch['parent_pid'],dispatch['parent_creation'])
 assert not child_alive and not parent_alive, 'Actual owned parent and child must be exited'
 lock=W/'MOD4_LOCAL_WAVE50_TEMP_TRAIN_20261013/LOCAL_GPU_EXCLUSIVE.lock'
 with lock.open('r+b') as f:
  f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_NBLCK,1)
  f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_UNLCK,1)
 raw=Path(receipt['raw']['path']);assert raw.stat().st_size==receipt['raw']['bytes'] and H(raw)==receipt['raw']['sha256']
 with np.load(raw,allow_pickle=False) as z:
  a=z['action'];processed=z['processed_action'];g=z['guarded_leg_targets'];ep=z['episode'];groups=z['group_ids'];command=z['command']
  assert np.array_equal(processed,np.clip(a,-6,6)) and np.array_equal(z['factor_action'],a)
  assert a.shape[:2]==(receipt['steps'],receipt['num_envs']) and a.shape[-1]==6
  rows=[]
  for i in np.flatnonzero(groups!=2):
   ids=np.flatnonzero(ep[:,i]==0);v=a[ids,i];gd=g[ids,i];diff=np.stack((gd[:,0]-gd[:,1],gd[:,2]-gd[:,3]),-1)
   rows.append(dict(env=int(i),command_vx=float(command[0,i,0]),valid_initial_episode_controls=len(ids),
      requested_action_mean=v.mean(0).tolist(),requested_action_min=v.min(0).tolist(),requested_action_max=v.max(0).tolist(),
      requested_outside_clip6_fraction=(np.abs(v)>6).mean(0).tolist(),
      actual_saved_guarded_target_input_difference_mean=diff.mean(0).tolist(),
      actual_saved_guarded_target_lower_boundary_fraction=np.isclose(diff,-1.0843,atol=2e-6,rtol=0).mean(0).tolist(),
      actual_saved_guarded_target_upper_boundary_fraction=np.isclose(diff,.85,atol=2e-6,rtol=0).mean(0).tolist()))
  left_saturated=bool(all(x['requested_outside_clip6_fraction'][0]==1 for x in rows))
  lower=bool(all(x['actual_saved_guarded_target_lower_boundary_fraction'][0]>.99 for x in rows))
 report=dict(epoch=time.time(),passed=True,CPU_read_only_no_GPU=True,
    baseline_receipt=dict(path=str(O/'COMPLETE_ACTUAL.json'),sha256=H(O/'COMPLETE_ACTUAL.json')),
    actual_parent_EXIT=end,actual_parent_and_child_exited=True,shared_msvcrt_lock_free_verified=True,
    original_EXIT_NATURAL_receipt_present=(O/'EXIT_NATURAL.json').exists(),
    absent_natural_receipt_not_fabricated_or_original_parent_relabelled=True,
    current_checkpoint_sha256=receipt['checkpoint_sha256'],raw=receipt['raw'],case_id=receipt['case_id'],
    action_order=['left_crank','left_hip','right_crank','right_hip','left_wheel_spin','right_wheel_spin'],
    original_actor_requested_then_wrapper_clip6_exact=True,actual_per_env=rows,
    left_crank_request_always_outside_clip6=left_saturated,left_crank_guarded_target_lower_boundary_above99percent=lower,
    policy_factor_priority='retain single-left-crank case' if left_saturated and lower else 'lower priority; old153 saturation cannot be assumed for this model',
    physical_stop_contact_not_inferred_from_requested_target=True,
    subset_seconds=receipt['physical_seconds'],not_complete_route_or_qualified50=True)
 dest=D/('CURRENT_BASELINE_'+receipt['case_id']+'_PARENTEXIT_CPU_V2_ACTUAL_REVIEW.json');write(dest,report)
 print(json.dumps(dict(report=str(dest),checkpoint_sha256=receipt['checkpoint_sha256'],left_always_saturated=left_saturated,left_lower99=lower,rows=rows)))
if __name__=='__main__':
 try:main()
 except BaseException:
  p=D/('CURRENT_BASELINE_PARENTEXIT_V2_ORIGINAL_CPU_ERROR_'+str(time.time_ns())+'.json');write(p,dict(epoch=time.time(),error=traceback.format_exc(),no_GPU=True));raise
