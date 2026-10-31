"""SUPERSEDED DRAFT NOT EXECUTED;ROOT requested a minimal reader,not authority code.

One physical byte read/hash, one np.load(BytesIO), nine selected members once.
Original220 parent false/physical result are preserved; no rollout is replayed.
"""
import os
os.environ['CUDA_VISIBLE_DEVICES']=''
from pathlib import Path
import argparse,hashlib,io,json,time,traceback
import numpy as np

PURPOSE='NEW221_ACTUAL220_SINGLE_NPZ_CPU_CLAMP_ORDER_Q_AND_ROOT_DIAGNOSTIC'
ARTIFACT='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_E0_NEW32341_N1_FLIGHT_20261101v220v2/case/actual_capture/ACTUAL220_NEW210_E0_BODY_POSES_AND_FLIGHT.npz'
BYTES=865215
SHA='16b81b77577aefe9eccf3a6aa2d70e68e807ac3d4c974ae112d9966d72e73bd4'
SELECTED=('raw_action6','original_reward_motor_actions6','q30','joint_names',
 'authored_wheel_bottom_above_plane_m','root13','commands','original_reward_command4','control')
ORDER=np.asarray([0,1,4,2,3,5],dtype=np.int64)
POLICY_NAMES=('left_crank','left_hip','right_crank','right_hip','left_wheel_spin','right_wheel_spin')
REWARD_NAMES=tuple(POLICY_NAMES[k] for k in ORDER)
GENERATION='MOD4_SINGLE_WRITER72_20261026'


def read(path):return json.loads(Path(path).read_bytes())
def put(path,value):
 with Path(path).open('x',encoding='utf8') as f:json.dump(value,f,indent=2,allow_nan=False)


def longest(mask,control):
 best=(0,None,None);begin=None
 for i,value in enumerate(list(mask)+[False]):
  if value and begin is None:begin=i
  elif not value and begin is not None:
   count=i-begin
   if count>best[0]:best=(count,int(control[begin]),int(control[i-1]))
   begin=None
 return dict(endpoint_count=best[0],start_control=best[1],end_control=best[2],
  observed_command_endpoint_span_s=0. if best[0]==0 else (best[0]-1)*.02,
  scope='Raw policy commands at50Hz,not measured physical motor effort or torque')


def analyze(data):
 raw=np.asarray(data['raw_action6'],dtype=np.float32)
 recorded=np.asarray(data['original_reward_motor_actions6'],dtype=np.float32)
 q=np.asarray(data['q30'],dtype=np.float32);root=np.asarray(data['root13'],dtype=np.float32)
 command=np.asarray(data['commands'],dtype=np.float32);rewardcmd=np.asarray(data['original_reward_command4'],dtype=np.float32)
 control=np.asarray(data['control']);bottom=np.asarray(data['authored_wheel_bottom_above_plane_m'],dtype=np.float32)
 names=[x.decode('utf8') if isinstance(x,bytes) else str(x) for x in np.asarray(data['joint_names'])]
 expected=np.clip(raw,-6.,6.)[:,ORDER];residual=recorded-expected
 unclipped=recorded-raw[:,ORDER];channels=[]
 for i,name in enumerate(POLICY_NAMES):
  v=raw[:,i];positive=v>6.;negative=v< -6.;saturated=np.abs(v)>6.
  channels.append(dict(policy_channel=i,joint=name,raw_min=float(v.min()),raw_max=float(v.max()),
   raw_abs_max=float(np.abs(v).max()),raw_abs_gt6_count=int(saturated.sum()),raw_abs_gt6_fraction=float(saturated.mean()),
   positive_gt6_count=int(positive.sum()),positive_gt6_fraction=float(positive.mean()),
   negative_lt_minus6_count=int(negative.sum()),negative_lt_minus6_fraction=float(negative.mean()),
   exact_plus6_count=int((v==6.).sum()),exact_minus6_count=int((v== -6.).sum()),
   longest_abs_gt6_run=longest(saturated,control),longest_positive_run=longest(positive,control),
   longest_negative_run=longest(negative,control)))
 clip=[]
 for i,name in enumerate(REWARD_NAMES):
  e=residual[:,i];r=recorded[:,i]
  clip.append(dict(reward_motor_channel=i,joint=name,source_policy_channel=int(ORDER[i]),
   recorded_min=float(r.min()),recorded_max=float(r.max()),
   recorded_positive_rail6_count=int(np.isclose(r,6.,rtol=0.,atol=1e-6).sum()),
   recorded_negative_rail_minus6_count=int(np.isclose(r,-6.,rtol=0.,atol=1e-6).sum()),
   clip6_reordered_max_abs_residual=float(np.abs(e).max()),clip6_reordered_mean_abs_residual=float(np.abs(e).mean()),
   unclipped_reordered_reference_max_abs_residual=float(np.abs(unclipped[:,i]).max())))
 qs=[]
 for i,name in enumerate(names):
  v=q[:,i];delta=np.diff(v)
  qs.append(dict(q_channel=i,joint=name,first=float(v[0]),last=float(v[-1]),
   minimum=float(v.min()),maximum=float(v.max()),range=float(v.max()-v.min()),last_minus_first=float(v[-1]-v[0]),
   maximum_abs_consecutive_change=0. if len(delta)==0 else float(np.abs(delta).max()),
   mean_abs_consecutive_change=0. if len(delta)==0 else float(np.abs(delta).mean()),
   scope='Recorded joint_pos coordinate,rad;no wrapping/limit/torque inference'))
 known=np.isfinite(bottom).all(1);common=bottom[known].min(1) if known.any() else None
 net=root[-1,:3]-root[0,:3];velocity=root[:,7:10]
 return dict(controls=len(control),control_first=int(control[0]),control_last=int(control[-1]),
  denominator='Controls/endpoints of this one recorded first episode;not population rate',
  raw_action_policy_order=list(POLICY_NAMES),raw_action_channels=channels,
  raw_action_absolute_max=float(np.abs(raw).max()),
  any_raw_channel_abs_gt6_count=int((np.abs(raw)>6.).any(1).sum()),
  reward_action_order=list(REWARD_NAMES),clip6_policy_to_reward_permutation=ORDER.tolist(),
  recorded_action_comparison=clip,clip6_reordered_global_max_abs_residual=float(np.abs(residual).max()),
  recorded_clip6_order_matches_within_numeric_atol1e_6=bool(np.allclose(recorded,expected,rtol=0.,atol=1e-6)),
  numeric_comparison_is_not_a_new_physics_training_or_skill_gate=True,
  q_channels=qs,
  root_reference=dict(recording='50Hz PRE-RESET root13;xyz,SDKxyzw,world linear xyz,world angular xyz',
   first_position_world_m=root[0,:3].tolist(),last_position_world_m=root[-1,:3].tolist(),
   net_displacement_world_m=net.tolist(),net_horizontal_displacement_m=float(np.linalg.norm(net[:2])),
   first_to_last_endpoint_span_s=float((control[-1]-control[0])*.02),
   not_t0_to_final20s_displacement=True,
   first_recorded_linear_velocity_world_m_s=velocity[0].tolist(),last_recorded_linear_velocity_world_m_s=velocity[-1].tolist(),
   mean_recorded_linear_velocity_world_m_s=velocity.mean(0).tolist(),
   max_abs_recorded_linear_velocity_world_m_s=np.abs(velocity).max(0).tolist(),
   state_velocity_reference_not_measured_motor_effort=True),
  commands=dict(vx_range=[float(command[:,0].min()),float(command[:,0].max())],
   vy_range=[float(command[:,1].min()),float(command[:,1].max())],
   yaw_range_rad_s=[float(command[:,2].min()),float(command[:,2].max())],
   original_reward_vx_range=[float(rewardcmd[:,0].min()),float(rewardcmd[:,0].max())],
   original_reward_yaw_range_rad_s=[float(rewardcmd[:,1].min()),float(rewardcmd[:,1].max())],
   original_reward_height_range_m=[float(rewardcmd[:,2].min()),float(rewardcmd[:,2].max())],
   before_step_vs_reward_vx_max_abs_residual=float(np.abs(command[:,0]-rewardcmd[:,0]).max()),
   before_step_vs_reward_yaw_max_abs_residual=float(np.abs(command[:,2]-rewardcmd[:,1]).max())),
  authored_bottom_reference=dict(known_rows=int(known.sum()),unknown_rows=int((~known).sum()),
   common_authored_collision_bottom_peak_m=None if common is None else float(common.max()),
   clearance_alone_not_flight_or_cooked_depth=True,
   flight_force_mask_and_maximum_flight_run_not_recomputed=True),
  forbidden_inferences=['motor_torque','PD_or_hardware_effort_saturation','single_cause_of_no_flight','STD_or_reward_or_guard_tuning'],
  mean_actor_ELU_is_ROOT_source_checked_not_retested=True)


def require_fresh_original219(task):
 binding=task['current_original219_binding'];owner=binding['owner'];go=binding['go']
 c=read('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json')
 assert c['authority_generation']==GENERATION and c['active_segment'] is not None
 assert c['active_segment']['owner_parent_pid']==owner['pid']
 identity=read(Path(owner['root'])/'OWNER_IDENTITY.json');current=read(Path(owner['root'])/'OWNER_CURRENT.json')
 assert identity['pid']==owner['pid'] and identity['creation']==owner['creation']
 assert set(current['go'])=={'w35_72'} and current['go']['w35_72']==go
 assert go['run_id']==binding['run_id'] and go['original_owner_pid']==owner['pid'] and go['original_owner_creation']==owner['creation']
 assert go['role_key']=='w35_72' and go['source_model_SHA']=='ad504fec819b22f10fd1caf7befc59c1988c7609fe15373ab8851ef95942df3f'
 return dict(epoch=time.time(),passed=True,current_run_id=binding['run_id'],owner_PID=owner['pid'],
  owner_creation=owner['creation'],GO_source_CPU_SHA=go['source_CPU_SHA'],account_writes=0)


def main():
 p=argparse.ArgumentParser();p.add_argument('--task',type=Path,required=True);p.add_argument('--out-new',type=Path,required=True);a=p.parse_args()
 task=read(a.task);assert task['purpose_id']==PURPOSE and task['artifact']==dict(path=ARTIFACT,bytes=BYTES,SHA=SHA)
 assert task['selected_members']==list(SELECTED)
 assert task['counts']==dict(physical_file_byte_passes=1,np_loads=1,selected_member_accesses_each=1,model_reads=0,SDK_GPU_calls=0,copies_downloads=0)
 authority=require_fresh_original219(task)  #No artifact bytes before fresh exact owner/GO.
 a.out_new.mkdir(parents=True,exist_ok=False);out=a.out_new
 counts=dict(physical_file_byte_passes=0,np_loads=0,member_accesses={k:0 for k in SELECTED},model_reads=0,SDK_GPU_calls=0,copies_downloads=0)
 put(out/'CPU221_ONCE_CONSUMED_BEFORE_ARTIFACT.json',dict(epoch=time.time(),purpose_id=PURPOSE,authority=authority,requested_counts=task['counts'],no_retry=True))
 try:
  with Path(ARTIFACT).open('rb') as stream:raw=stream.read()
  counts['physical_file_byte_passes']+=1
  assert len(raw)==BYTES and hashlib.sha256(raw).hexdigest()==SHA
  counts['np_loads']+=1
  with np.load(io.BytesIO(raw),allow_pickle=False) as archive:
   data={}
   for name in SELECTED:
    data[name]=archive[name];counts['member_accesses'][name]+=1
  del raw
  assert data['raw_action6'].shape==(1000,6) and data['original_reward_motor_actions6'].shape==(1000,6)
  assert data['q30'].shape==(1000,30) and data['joint_names'].shape==(30,)
  assert data['authored_wheel_bottom_above_plane_m'].shape==(1000,2) and data['root13'].shape==(1000,13)
  assert data['commands'].shape==(1000,3) and data['original_reward_command4'].shape==(1000,4)
  assert data['control'].shape==(1000,) and np.array_equal(data['control'],np.arange(1,1001))
  assert len(set(str(x) for x in data['joint_names']))==30
  for name in ('raw_action6','original_reward_motor_actions6','q30','root13','commands','original_reward_command4'):assert np.isfinite(data[name]).all(),name
  report=dict(epoch=time.time(),purpose_id=PURPOSE,diagnostic_execution_passed=True,artifact=dict(path=ARTIFACT,bytes=BYTES,SHA=SHA),
   authority=authority,actual_read_counts=counts,analysis=analyze(data),
   preserved_input_case=dict(physical_result_passed=True,original_parent_passed_execution=False,
    parent_failure='APP220_CLOSED.json missing after app.close;originalwaitRC0/allownOUT/EXreleased retained by ROOT',
    reported_controls=1000,reported_physics=8000,reported_feedback=2000,reported_seconds=20.,
    reported_time_out_only=True,reported_both_wheel_force_norm_le1_rows=0,reported_flight_candidates=0,reported_confirmed_flight_runs=0,
    provenance='ROOT actual220 summary;no SDK/rollout rerun or old-result overwrite'),
   account_writes=0,learning=False,original220_case_replayed=False,artifact_or_model_transfers=0,GUI=False)
  put(out/'ACTUAL221_ACTION_CLAMP_Q_ROOT_NUMERIC.json',report)
  print(json.dumps(report,allow_nan=False))
 except BaseException:
  put(out/'ORIGINAL221_CPU_DIAGNOSTIC_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),actual_read_counts=counts,
   original220_parent_false_preserved=True,no_automatic_retry=True));raise


if __name__=='__main__':main()
