"""Immutable observer for a completed root-leased frozen baseline, CPU only."""
from pathlib import Path
import argparse,hashlib,json,time,traceback
import numpy as np
D=Path(__file__).resolve().parent
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):
 assert not p.exists();p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',required=True);args=p.parse_args();O=Path(args.output)
 receipt=json.loads((O/'COMPLETE_ACTUAL.json').read_bytes())
 assert receipt['passed_data_contract'] and receipt['no_PPO'] and not receipt['factor']['policy_factor']
 assert (O/'EXIT_NATURAL.json').exists() and not (O/'ORIGINAL_ERROR.json').exists()
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
    current_checkpoint_sha256=receipt['checkpoint_sha256'],raw=receipt['raw'],case_id=receipt['case_id'],
    action_order=['left_crank','left_hip','right_crank','right_hip','left_wheel_spin','right_wheel_spin'],
    original_actor_requested_then_wrapper_clip6_exact=True,actual_per_env=rows,
    left_crank_request_always_outside_clip6=left_saturated,left_crank_guarded_target_lower_boundary_above99percent=lower,
    policy_factor_priority='retain single-left-crank case' if left_saturated and lower else 'lower priority; old153 saturation cannot be assumed for this model',
    physical_stop_contact_not_inferred_from_requested_target=True,
    subset_seconds=receipt['physical_seconds'],not_complete_route_or_qualified50=True)
 dest=D/('CURRENT_BASELINE_'+receipt['case_id']+'_CPU_ACTUAL_REVIEW.json');write(dest,report)
 print(json.dumps(dict(report=str(dest),checkpoint_sha256=receipt['checkpoint_sha256'],left_always_saturated=left_saturated,left_lower99=lower,rows=rows)))
if __name__=='__main__':
 try:main()
 except BaseException:
  p=D/('CURRENT_BASELINE_ORIGINAL_CPU_ERROR_'+str(time.time_ns())+'.json');write(p,dict(epoch=time.time(),error=traceback.format_exc(),no_GPU=True));raise
