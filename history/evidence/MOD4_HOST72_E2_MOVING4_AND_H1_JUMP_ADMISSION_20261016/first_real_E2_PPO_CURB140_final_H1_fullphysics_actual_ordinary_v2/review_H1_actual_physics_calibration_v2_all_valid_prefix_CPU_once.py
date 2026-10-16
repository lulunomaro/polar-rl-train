"""Actual full-physics data, all failed prefixes retained; scripted motion not an RL score."""
from pathlib import Path
import json,time,hashlib,numpy as np
from h1_flat_jump_evidence_reward_cpu_v1 import H1Evidence
D=Path(__file__).resolve().parent;R=D/'reports';H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 c=json.loads((R/'H1_FULLPHYSICS_CALIBRATION_V2_ACTUAL_BOUND_COLLECTION.json').read_bytes());assert not c['actual_processes'] and c['parent_exit'];reference=next(x['value'] for x in c['files'] if x['path'].endswith('/ACTUAL_AUTHORED_ALL_COLLIDER_REFERENCE.json'));shapes=reference['shapes'];assert len(shapes)==34 and len(reference['actual_contact_view_body_names'])==31;nonwheel=[i for i,n in enumerate(reference['actual_contact_view_body_names']) if n not in ('left_wheel','right_wheel')];fsm=H1Evidence(80);events={k:np.zeros(80,np.int64) for k in ('takeoff','landing','recovery')};reward=np.zeros(80);last_episode=None;count=0;maxclear=np.full(80,-np.inf);max_root_vz=np.full(80,-np.inf);mindistance=np.full(80,np.inf);reset_count=0;allfinite=True;raw=c.get('complete_local_raw',[]);physics=[r for r in raw if Path(r['path']).name.startswith('physics_')];controls=[r for r in raw if Path(r['path']).name.startswith('controls_')]
 for r in physics:
  p=Path(r['path']);assert H(p)==r['SHA'] and p.stat().st_size==r['bytes']
  with np.load(p,allow_pickle=False) as z:v={k:z[k] for k in z.files}
  for k,x in v.items():
   if x.dtype.kind in 'fc':assert np.isfinite(x).all(),k
  for i in range(len(v['tick'])):
   episode=v['episode'][i];done=np.zeros(80,bool) if last_episode is None else episode!=last_episode
   reset_count+=int(done.sum());last_episode=episode.copy();force=np.linalg.norm(v['wheel_5ms_mean_force'][i],axis=-1);non=np.linalg.norm(v['all_body_contact_force'][i][:,nonwheel],axis=-1);root=v['root13'][i];speed=np.linalg.norm(root[:,7:9],axis=-1);minimum=v['all_shape_clearance'][i].min(1);maxclear=np.maximum(maxclear,v['wheel_clearance'][i].min(1));mindistance=np.minimum(mindistance,minimum);max_root_vz=np.maximum(max_root_vz,root[:,9]);o=fsm.update(wheel_force_N=force,wheel_clearance_m=v['wheel_clearance'][i],all_collider_min_clearance_m=minimum,nonwheel_force_N=non,root_vz_m_s=root[:,9],roll_rad=v['roll'][i],pitch_rad=v['pitch'][i],yaw_error_rad=v['yaw'][i],speed_error_m_s=speed,done=done,operator_jump=np.ones(80,bool));reward+=o['control_event_reward']
   for k in events:events[k]+=o[k].astype(np.int64)
  count+=len(v['tick'])
 groups=[]
 for g in range(4):
  ids=np.arange(80)[np.arange(80)%4==g];groups.append(dict(diagnostic_group=g,env_ids=ids.tolist(),takeoff_envs=int((events['takeoff'][ids]>0).sum()),landing_envs=int((events['landing'][ids]>0).sum()),recovery_envs=int((events['recovery'][ids]>0).sum()),maximum_minimum_wheel_clearance_m=float(maxclear[ids].max()),perenv_maximum_wheel_clearance_m=maxclear[ids].tolist(),minimum_authored_collider_clearance_m=float(mindistance[ids].min()),perenv_candidate_event_reward=reward[ids].tolist()))
 complete=next((x['value'] for x in c['files'] if x['path'].endswith('/COMPLETE_ACTUAL.json')),None);passed=not c['errors'] and complete is not None
 if passed:assert count==1696 and complete['optimizer_updates']==0
 report=dict(epoch=time.time(),actual_data_integrity_passed=passed,original_errors=c['errors'],valid_physics_rows=count,expected_complete_physics_rows=1696,physical_dt=.0025,full_authored_collision_shapes=34,actual_contacts31=True,groups=groups,actual_episode_increments_in_prefix=reset_count,original_contact_hw_query_guard_not_relaxed=True,full_callback_prefix_finite=True,raw_twohost=raw,actual_state_event_facts_not_policy_learning=True,scripted_motor_calibration_only=True,actor_jump_skill_or_PPO_pass=False,new20k_H1_fullsource_and_executable_reward_termination_admission_still_required=True,authored_primitive_mesh_support_not_cooked_shapeLocal_bitexact=True,postreset_cannot_inherit_jump_credit=True)
 with (R/'H1_ACTUAL_FULLCOLLIDER_TAKEOFF_LANDING_CALIBRATION_V2_CPU_REVIEW.json').open('x',encoding='utf8') as f:json.dump(report,f,indent=2)
 print(json.dumps(dict(actual_data_integrity_passed=passed,valid_physics_rows=count,groups=groups,not_learned_jump=True)),flush=True)
if __name__=='__main__':main()
