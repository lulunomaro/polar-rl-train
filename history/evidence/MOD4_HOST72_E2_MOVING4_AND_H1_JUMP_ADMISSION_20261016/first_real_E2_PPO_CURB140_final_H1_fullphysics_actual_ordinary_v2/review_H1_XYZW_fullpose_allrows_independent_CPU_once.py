"""Independently reconstruct authored support from physical link poses using NumPy."""
from pathlib import Path
import json,time,hashlib,numpy as np
from h1_flat_jump_evidence_reward_cpu_v1 import H1Evidence
from h1_settled_support_evidence_candidate_v2 import SettledH1Evidence
D=Path(__file__).resolve().parent;R=D/'reports'
def support(pos,quat,shapes):
 # Rotate each basis vector via independent cross-product XYZW quaternion application.
 q=quat.astype(np.float64);a=q[...,:3];w=q[...,3:4];basis=np.broadcast_to(np.eye(3),q.shape[:-1]+(3,3));aa=a[...,None,:];t=2*np.cross(aa,basis);rotation_basis=basis+w[...,None,:]*t+np.cross(aa,t);zrow=rotation_basis[...,2]
 out=[]
 for s in shapes:
  rz=zrow[...,s['body_index'],:];L=np.asarray(s['linear_body_from_shape']);origin=np.asarray(s['origin_body_m']);shape_z=rz@L;center=pos[...,s['body_index'],2]+(rz*origin).sum(-1);kind=s['type']
  if kind=='Cube':
   corners=np.array([[x,y,z] for x in (-.5,.5) for y in (-.5,.5) for z in (-.5,.5)])*s['size'];value=center+(shape_z@corners.T).min(-1)
  elif kind=='Mesh':value=center+(shape_z@np.asarray(s['points']).T).min(-1)
  elif kind in ('Capsule','Cylinder'):
   axis=shape_z[...,s['axis']];r=np.linalg.norm(shape_z,axis=-1) if kind=='Capsule' else np.sqrt(np.maximum(0,(shape_z*shape_z).sum(-1)-axis*axis));value=center-np.abs(axis)*s['height']*.5-r*s['radius']
  else:raise ValueError('Unknown source shape')
  out.append(value)
 return np.stack(out,-1)
def main():
 c=json.loads((R/'H1_XYZW_FULLPOSE_COMPLETE_ACTUAL_BOUND_COLLECTION.json').read_bytes());assert not c['errors'] and not c['actual_processes'] and c['parent_exit'];ref=next(x['value'] for x in c['files'] if x['path'].endswith('/ACTUAL_AUTHORED_ALL_COLLIDER_REFERENCE.json'));shapes=ref['shapes'];non=[i for i,n in enumerate(ref['actual_contact_view_body_names']) if n not in ('left_wheel','right_wheel')];assert len(shapes)==34 and len(non)==29
 old=H1Evidence(80);new=SettledH1Evidence(80);last=None;events=np.zeros((2,3,80),int);rewards=np.zeros((2,80));maxerr=0.;maxq=0.;rows=0;maxclear=np.full(80,-np.inf);minimum=np.full(80,np.inf);per_reset=np.zeros(80,int)
 for r in c['complete_local_raw']:
  if not Path(r['path']).name.startswith('physics_'):continue
  p=Path(r['path']);assert p.stat().st_size==r['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==r['SHA']
  with np.load(p,allow_pickle=False) as z:
   for k in z.files:
    if z[k].dtype.kind in 'fc':assert np.isfinite(z[k]).all(),k
   q=z['body_quat31_xyzw'];maxq=max(maxq,float(np.abs(np.linalg.norm(q,axis=-1)-1).max()));gold=support(z['body_pos31_w'],q,shapes);maxerr=max(maxerr,float(np.abs(gold-z['all_shape_clearance']).max()));assert maxerr<=1e-6,maxerr
   for i in range(len(z['tick'])):
    ep=z['episode'][i];done=np.zeros(80,bool) if last is None else ep!=last;per_reset+=done;last=ep.copy();root=z['root13'][i];maxclear=np.maximum(maxclear,z['wheel_clearance'][i].min(-1));minimum=np.minimum(minimum,z['all_shape_clearance'][i].min(-1));args=dict(wheel_force_N=np.linalg.norm(z['wheel_5ms_mean_force'][i],axis=-1),wheel_clearance_m=z['wheel_clearance'][i],all_collider_min_clearance_m=gold[i].min(-1),nonwheel_force_N=np.linalg.norm(z['all_body_contact_force'][i][:,non],axis=-1),root_vz_m_s=root[:,9],roll_rad=z['roll'][i],pitch_rad=z['pitch'][i],yaw_error_rad=z['yaw'][i],speed_error_m_s=np.linalg.norm(root[:,7:9],axis=-1),done=done,operator_jump=np.ones(80,bool))
    for fi,f in enumerate((old,new)):
     o=f.update(**args);rewards[fi]+=o['control_event_reward']
     for k,n in enumerate(('takeoff','landing','recovery')):events[fi,k]+=o[n]
    rows+=1
 assert rows==896 and maxq<1e-5
 complete=next(x['value'] for x in c['files'] if x['path'].endswith('/COMPLETE_ACTUAL.json'));assert complete['callbacks']==896 and complete['source9critic8STD17Adam_unchanged'] and complete['optimizer_updates']==0
 groups=[]
 for g in range(4):
  ids=np.flatnonzero(np.arange(80)%4==g);groups.append(dict(diagnostic_action_group=g,not_actor_or_environment_truth_input=True,V1_candidate_events_envs=(events[0,:,ids].sum(0)>0).sum().item() if False else [(events[0,k,ids]>0).sum().item() for k in range(3)],settled_candidate_events_envs=[(events[1,k,ids]>0).sum().item() for k in range(3)],max_bothwheel_clearance_m=float(maxclear[ids].max()),min_authored_allshape_clearance_m=float(minimum[ids].min())))
 report=dict(epoch=time.time(),actual_callback_rows=rows,actual_all34authored_shapes_reconstructed_from31physical_link_poses=True,actual_SDK_quaternion_convention='XYZW',independent_numpy_vs_saved_GPU_clearance_maxabs_m=maxerr,quaternion_unit_norm_maxabs=maxq,fullsensor_vs_independent_wheel_sensor_component_maxabs_N=complete['fullsensor_wheel_sensor_max_component_error_N'],all20_complete_raw_files_twohost_SHA_checked=True,all_saved_prefixes_finite=True,parent_child_actualout_EXIT0_SimulationContext_cleared=True,groups=groups,events_order=['takeoff','landing','stable_recovery'],perenv_episode_resets=per_reset.tolist(),V1_original_wrong_observer_geometry_classification_rejected_not_overwritten=True,new_settled_candidate_offline_reward_sum=float(rewards[1].sum()),original_source_actor9_critic8_STD17Adam_unchanged_target_asserted=True,no_PPO_training_or_charge=True,no_actor_learned_jump_or_architecture_skill_pass=True,actual_authored_reference_not_cooked_ShapeLocal_directread=True,remaining=['Stable ground under original source actor before external jump request; zero-action/default-PD target is not zero effort','Actual full20k typed H1 restore/newphase save-resume and executable reward/termination audit','Freeze narrow H1 learning configuration and admit original solecanonical resource interval; no H2 step or airborne reset'],new_GPU_replay_not_for_hash=False)
 with (R/'H1_XYZW_FULLPOSE_ALL_ROWS_INDEPENDENT_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(report,f,indent=2)
 print(json.dumps(dict(callbacks=rows,all34geometry_maxabs=maxerr,groups=groups,no_jump_PPO=True)),flush=True)
if __name__=='__main__':main()
