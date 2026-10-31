"""ROOT fresh219-authorized CPU only:ONE NPZ byte/hash pass/load,9members once."""
import os
os.environ['CUDA_VISIBLE_DEVICES']=''
from pathlib import Path
import argparse,hashlib,io,json,time,traceback
import numpy as np
PURPOSE='NEW221_ACTUAL220_SINGLE_NPZ_CPU_CLAMP_ORDER_Q_AND_ROOT_DIAGNOSTIC'
ARTIFACT='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_E0_NEW32341_N1_FLIGHT_20261101v220v2/case/actual_capture/ACTUAL220_NEW210_E0_BODY_POSES_AND_FLIGHT.npz'
BYTES=865215;SHA='16b81b77577aefe9eccf3a6aa2d70e68e807ac3d4c974ae112d9966d72e73bd4'
SELECTED=('raw_action6','original_reward_motor_actions6','q30','joint_names','authored_wheel_bottom_above_plane_m','root13','commands','original_reward_command4','control')
ORDER=[0,1,4,2,3,5]
POLICY_NAMES=('left_crank','left_hip','right_crank','right_hip','left_wheel_spin','right_wheel_spin')


def longest(mask,control):
 best=(0,None,None);start=None
 for i,v in enumerate(list(mask)+[False]):
  if v and start is None:start=i
  elif not v and start is not None:
   if i-start>best[0]:best=(i-start,int(control[start]),int(control[i-1]))
   start=None
 return dict(endpoint_count=best[0],start_control=best[1],end_control=best[2],observed_command_endpoint_span_s=max(0,best[0]-1)*.02)


def analyze(d):
 raw=d['raw_action6'];recorded=d['original_reward_motor_actions6'];q=d['q30'];root=d['root13'];control=d['control']
 cmd=d['commands'];rcmd=d['original_reward_command4'];bottom=d['authored_wheel_bottom_above_plane_m']
 names=[x.decode() if isinstance(x,bytes) else str(x) for x in d['joint_names']]
 residual=recorded-np.clip(raw,-6.,6.)[:,ORDER];channels=[];comparison=[];qs=[]
 for i,name in enumerate(POLICY_NAMES):
  v=raw[:,i];sat=np.abs(v)>6.;pos=v>6.;neg=v< -6.
  channels.append(dict(policy_channel=i,joint=name,raw_min=float(v.min()),raw_max=float(v.max()),raw_abs_max=float(np.abs(v).max()),
   raw_abs_gt6_fraction=float(sat.mean()),positive_gt6_fraction=float(pos.mean()),negative_lt_minus6_fraction=float(neg.mean()),
   longest_abs_gt6_run=longest(sat,control),longest_positive_run=longest(pos,control),longest_negative_run=longest(neg,control)))
 for i,k in enumerate(ORDER):
  comparison.append(dict(reward_motor_channel=i,joint=POLICY_NAMES[k],source_policy_channel=k,
   recorded_min=float(recorded[:,i].min()),recorded_max=float(recorded[:,i].max()),
   clip6_reordered_max_abs_residual=float(np.abs(residual[:,i]).max()),clip6_reordered_mean_abs_residual=float(np.abs(residual[:,i]).mean()),
   unclipped_reordered_reference_max_abs_residual=float(np.abs(recorded[:,i]-raw[:,k]).max())))
 for i,name in enumerate(names):
  v=q[:,i]
  qs.append(dict(q_channel=i,joint=name,first=float(v[0]),last=float(v[-1]),minimum=float(v.min()),maximum=float(v.max()),
   range=float(v.max()-v.min()),last_minus_first=float(v[-1]-v[0]),maximum_abs_consecutive_change=float(np.abs(np.diff(v)).max())))
 known=np.isfinite(bottom).all(1);delta=root[-1,:3]-root[0,:3]
 return dict(controls=len(control),denominator='One first-episode control record,not population rate',
  raw_action_policy_order=list(POLICY_NAMES),raw_action_channels=channels,raw_action_absolute_max=float(np.abs(raw).max()),
  clip6_policy_to_reward_permutation=ORDER,recorded_action_comparison=comparison,
  clip6_reordered_global_max_abs_residual=float(np.abs(residual).max()),
  recorded_clip6_order_matches_within_numeric_atol1e_6=bool(np.allclose(residual,0.,rtol=0.,atol=1e-6)),
  q_channels=qs,q_scope='Stored joint_pos radians and adjacent change;no wrapping/limit/torque inference',
  root_reference=dict(first_position_world_m=root[0,:3].tolist(),last_position_world_m=root[-1,:3].tolist(),
   net_displacement_world_m=delta.tolist(),net_horizontal_displacement_m=float(np.linalg.norm(delta[:2])),
   first_to_last_endpoint_span_s=float(control[-1]-control[0])*.02,
   first_recorded_linear_velocity_world_m_s=root[0,7:10].tolist(),last_recorded_linear_velocity_world_m_s=root[-1,7:10].tolist(),
   mean_recorded_linear_velocity_world_m_s=root[:,7:10].mean(0).tolist(),scope='PRE-reset root13 SDK velocity reference,not torque or t0-to20s displacement'),
  commands=dict(vx_range=[float(cmd[:,0].min()),float(cmd[:,0].max())],yaw_range_rad_s=[float(cmd[:,2].min()),float(cmd[:,2].max())],
   original_reward_yaw_range_rad_s=[float(rcmd[:,1].min()),float(rcmd[:,1].max())],original_reward_height_range_m=[float(rcmd[:,2].min()),float(rcmd[:,2].max())]),
  authored_bottom_reference=dict(known_rows=int(known.sum()),common_authored_collision_bottom_peak_m=float(bottom[known].min(1).max()) if known.any() else None,
   flight_force_mask_and_maximum_flight_run_not_recomputed=True),
  no_motor_torque_unique_cause_STD_reward_guard_or_skill_conclusion=True)


def put(p,v):
 with p.open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)


def main():
 p=argparse.ArgumentParser();p.add_argument('--out-new',type=Path,required=True);a=p.parse_args()
 a.out_new.mkdir(parents=True,exist_ok=False);out=a.out_new
 counts=dict(physical_file_byte_passes=0,np_loads=0,member_accesses={k:0 for k in SELECTED})
 put(out/'CPU221_ONCE_CONSUMED_BEFORE_ARTIFACT.json',dict(epoch=time.time(),purpose_id=PURPOSE,authority_scope='ROOT caller must supply fresh219 exactowner/GO and serialSSH;reader does not query authority',no_retry=True))
 try:
  with Path(ARTIFACT).open('rb') as f:raw=f.read()
  counts['physical_file_byte_passes']=1
  assert len(raw)==BYTES and hashlib.sha256(raw).hexdigest()==SHA
  counts['np_loads']=1
  with np.load(io.BytesIO(raw),allow_pickle=False) as z:
   d={}
   for name in SELECTED:d[name]=z[name];counts['member_accesses'][name]+=1
  del raw
  shapes=dict(raw_action6=(1000,6),original_reward_motor_actions6=(1000,6),q30=(1000,30),joint_names=(30,),
   authored_wheel_bottom_above_plane_m=(1000,2),root13=(1000,13),commands=(1000,3),original_reward_command4=(1000,4),control=(1000,))
  for name,shape in shapes.items():assert d[name].shape==shape,name
  assert np.array_equal(d['control'],np.arange(1,1001))
  for name in ('raw_action6','original_reward_motor_actions6','q30','root13','commands','original_reward_command4'):assert np.isfinite(d[name]).all(),name
  result=dict(epoch=time.time(),purpose_id=PURPOSE,diagnostic_execution_passed=True,artifact=dict(path=ARTIFACT,bytes=BYTES,SHA=SHA),actual_read_counts=counts,
   analysis=analyze(d),original220_parent_false_preserved=True,input_physical_result_passed=True,
   original_parent_failure='APP220_CLOSED missing;ROOT preserved actualwaitRC0/allownOUT/EXrelease',
   original_reported_flight_candidates=0,original_reported_confirmed_flight_runs=0,
   model_or_SDK_GPU_calls=0,copies_downloads=0,rollout_replays=0,account_writes=0,GUI=False)
  put(out/'ACTUAL221_ACTION_CLAMP_Q_ROOT_NUMERIC.json',result);print(json.dumps(result,allow_nan=False))
 except BaseException:
  put(out/'ORIGINAL221_CPU_DIAGNOSTIC_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),actual_read_counts=counts,no_automatic_retry=True));raise


if __name__=='__main__':main()
