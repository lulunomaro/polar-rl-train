from pathlib import Path
import hashlib,json,time,traceback
import numpy as np
import torch
from policy_factor import apply_factor,FACTOR_ID
D=Path(__file__).resolve().parent;W=D.parents[1]
C=W/'MOD4_LOCAL_WAVE50_CONTINUE_20261013/runtime/isaac/mod4'
B=W/'MOD4_E1_WAVE50_ROUTE_SECOND_BOUNDED_20261012/reports/cases/clk2500-closure-episode-d3-153-e1-wave50-route-lifecycle-repair-terrain-flat'
F=W/'MOD4_E1_WAVE35_SECOND_BOUNDED_20261011/wave50_worldmesh_scope/frozen_history_flat_WAVE50_WORLDMESH.py'
def idx(p):return dict(path=str(p),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def dump(name,v):
 p=D/name;assert not p.exists();p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8');return p
def main():
 t=(C/'mod4_task.py').read_text(encoding='utf-8');f=F.read_text(encoding='utf-8')
 assert 'clip_actions=6.0' in f and 'vec.step(action)' in f
 assert 'joint_pos={".*": 0.0}' in t
 contract=W/'MOD4_LOCAL_WAVE50_CONTINUE_20261013/runtime/assets/import_contract.json'
 cc=json.loads(contract.read_bytes());lo=cc['training_window']['input_difference_min_rad'];hi=.85
 p=json.loads((B/'probe.json').read_bytes());names=p['initial']['reset']['full_joint_names'];ids=[names.index(n) for n in ['left_crank','left_hip','right_crank','right_hip']]
 with np.load(B/'route_raw.npz',allow_pickle=False) as z:
  a=z['action'];q=z['q'];episode=z['episode'];cl=np.clip(a,-6,6)
  target=cl[:,:,:4]*.5
  # Formula reconstruction before action-delay queue. These are NOT saved physical targets.
  rawdiff=np.stack((target[:,:,0]-target[:,:,1],target[:,:,2]-target[:,:,3]),-1)
  guarded=np.clip(rawdiff,lo,hi)
  result=[]
  for g,name in [(0,'forward'),(1,'reverse')]:
   mask=(episode==0)&((np.arange(80)%3==g)[None,:]);ar=a[mask];rr=rawdiff[mask];gq=q[:,:,ids][mask]
   result.append(dict(group=name,controls=int(mask.sum()),
      raw_actor_action_abs_mean=np.abs(ar).mean(0).tolist(),
      requested_action_outside_clip6_fraction=(np.abs(ar)>6).mean(0).tolist(),
      reconstructed_pre_delay_upper_input_difference_guard_fraction=(rr>hi).mean(0).tolist(),
      reconstructed_pre_delay_lower_input_difference_guard_fraction=(rr<lo).mean(0).tolist(),
      actual_joint_position_mean=gq.mean(0).tolist(),
      actual_joint_input_difference_mean=[float((gq[:,0]-gq[:,1]).mean()),float((gq[:,2]-gq[:,3]).mean())],
      actual_joint_input_difference_minmax=[[float((gq[:,j]-gq[:,j+1]).min()),float((gq[:,j]-gq[:,j+1]).max())] for j in [0,2]]))
  # Pure CPU fixture applies exact one-column factor to saved requests.
  fixture=torch.tensor(cl.reshape(-1,6)[::997].copy())
  corrected=apply_factor(fixture,diff_min=lo,diff_max=hi)
  assert torch.equal(corrected[:,1:],fixture[:,1:]) and torch.isfinite(corrected).all()
  fi=corrected.numpy();gt=fi[:,:4]*.5
  compare=np.clip(gt[:,0]-gt[:,1],lo,hi)-np.clip(gt[:,2]-gt[:,3],lo,hi)
  # Numerical float32 reconstruction, not physical equivalence.
  assert np.abs(compare).max()<1e-6
  assert not torch.cuda.is_initialized()
 report=dict(epoch=time.time(),passed=True,CPU_only=True,inputs=[idx(x) for x in [C/'mod4_task.py',F,contract,B/'route_raw.npz',B/'probe.json',D/'policy_factor.py']],
   action_order=['left_crank','left_hip','right_crank','right_hip','left_wheel_spin','right_wheel_spin'],
   clip6_present_both_training_and_actual_frozen_eval=True,
   original_hypothesis_eval_clip6_missing_rejected=True,
   rejected_hypothesis_evidence='Actual frozen50 source wraps RslRlVecEnvWrapper clip_actions6 then calls vec.step; raw saved action is actor output before wrapper clipping.',
   observations=result,difference_limits_rad=[lo,hi],
   reconstructed_targets_are_requested_pre_delay_formula_not_actual_saved_queue_or_target=True,
   cpu_candidate_factor=FACTOR_ID,candidate_fixture_changed_only_column0=True,candidate_guarded_difference_max_mismatch_rad=float(np.abs(compare).max()),
   candidate_not_GPU_tested_or_production_repair=True,
   hypothesis='Original learned left-crank request is continuously driven to the upper motor-input-difference guard while right leg is not; paired one-column diagnostic can test how much that policy shape contributes to heading/forward passage.',
   no_unique_mechanical_or_reward_cause_claim=True)
 path=dump('ACTION_SATURATION_CPU_ACTUAL_REVIEW.json',report)
 print(json.dumps(dict(report=str(path),passed=True,limits=[lo,hi],observations=result,fixture_mismatch=float(np.abs(compare).max()))))
if __name__=='__main__':
 try:main()
 except BaseException:
  dump('ACTION_ORIGINAL_CPU_READER_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),not_GPU=True));raise
