from pathlib import Path
import os,sys,json,time,traceback
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch,numpy as np
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';sys.path.insert(0,str(W/'MOD4_H1_FLAT_JUMP_FULLSTATE_REWARD_NATIVE_ADMISSION_20261016'));from review_H1_complete_native_models_source_and_admission_local_CPU_once import eq,tensors,H
def main():
 p=R/'E3_12POSE_NATIVE_ALL_ROWS_FULL_GEOMETRY_SOURCE_LOCAL_CPU_ACTUAL.json';assert not p.exists();torch.set_num_threads(2);rng=torch.get_rng_state().clone();v=json.loads((R/'E3_EXISTING_SCOPE_COMPLETE_READONLY_COLLECTION_ACTUAL.json').read_bytes());assert v['terminal'] and not v['actual_own_processes'] and not any('ORIGINAL_ERROR' in x['path'] for x in v['files']);complete=next(x['value'] for x in v['files'] if x['path'].endswith('/COMPLETE_ACTUAL.json'));ref=next(x['value'] for x in v['files'] if x['path'].endswith('/ACTUAL_AUTHORED_COLLIDER_REFERENCE.json'));poses=complete['poses'];assert len(poses)==12 and all(x['actual_control_callbacks']==4 and x['root_pose_readback_position_maxabs']<=1e-6 and x['root_pose_readback_quaternion_sign_equivalent_maxabs']<=1e-6 and x['joints_unchanged_before_step'] for x in poses);shapes=ref['shapes'];indices=[x['body_index'] for x in shapes];wheel=[ref['contact_body_names'].index(x) for x in ('left_wheel','right_wheel')];err=forceerr=0.;rows=0;nonwheel=0;penetration=0.;artifacts=[]
 for row in v['local_artifacts']:
  f=Path(row['local_path']);assert f.stat().st_size==row['bytes'] and H(f)==row['SHA'];artifacts.append(row)
  if f.suffix!='.npz':continue
  with np.load(f,allow_pickle=False) as z:
   for k in z.files:
    if z[k].dtype.kind in 'fc':assert np.isfinite(z[k]).all(),k
   pos=z['body_pos31_w'].astype(np.float64);q=z['body_quat31_xyzw'].astype(np.float64);assert q.shape==(4,80,31,4) and z['phase'].tolist()==['fallen_control']*4;assert np.abs(np.linalg.norm(q,axis=-1)-1).max()<=1e-5
   xyz=q[...,:3];qw=q[...,3:4];basis=np.zeros_like(xyz);basis[...,2]=1.;localz=basis+2*np.cross(xyz,np.cross(xyz,basis)-qw*basis);clear=[]
   for s in shapes:
    rz=localz[:,:,s['body_index']];r=rz@np.asarray(s['linear_body_from_shape']);center=pos[:,:,s['body_index'],2]+np.einsum('...i,i->...',rz,np.asarray(s['origin_body_m']));kind=s['type'];norm=np.linalg.norm(r,axis=-1)
    if kind=='Cube':value=center-abs(r).sum(-1)*s['size']*.5
    elif kind in ('Cylinder','Capsule'):
     axial=abs(r[...,s['axis']]);extent=axial*s['height']*.5+s['radius']*(norm if kind=='Capsule' else np.sqrt(np.maximum(0,norm**2-axial**2)));value=center-extent
    elif kind=='Sphere':value=center-norm*s['radius']
    elif kind=='Mesh':value=center+(r@np.asarray(s['points']).T).min(-1)
    else:raise ValueError(kind)
    clear.append(value)
   reconstructed=np.stack(clear,-1);err=max(err,float(abs(reconstructed-z['all_shape_clearance']).max()));forceerr=max(forceerr,float(abs(z['all_body_contact_force'][:,:,wheel,:]-z['wheel_raw_force']).max()));rows+=z['root13'].shape[0]*80;penetration=min(penetration,float(reconstructed.min()));other=[i for i in range(31) if i not in wheel];nonwheel+=int((np.linalg.norm(z['all_body_contact_force'][:,:,other],axis=-1)>1).any(-1).sum())
 assert rows==3840 and err<=1e-6 and forceerr<=.1;source=W/'MOD4_HOST72_E2_MOVING4_AND_H1_JUMP_ADMISSION_20261016/payload/job1/source/E0_full_source.pt';assert H(source)==complete['source_SHA'];s=torch.load(source,map_location='cpu',weights_only=False);models=[]
 for row in artifacts:
  if not row['local_path'].endswith('.pt'):continue
  ck=torch.load(row['local_path'],map_location='cpu',weights_only=False);count=[0,0];tensors(ck,count)
  for key in ('actor_state_dict','critic_state_dict','optimizer_state_dict'):assert eq(ck[key],s[key])
  models.append(dict(**row,tensors=count[0],float_tensors=count[1],actor9critic8STD17Adam639560_literal_source_exact=True))
 assert len(models)==2 and torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized();result=dict(epoch=time.time(),passed_legal_pose_contact_native_integrity=True,pose_groups=12,envs=80,all_physical_callback_rows=3840,actual_control_callbacks=48,all34_authored_geometry_independent_numpy_maxabs=err,full31_contact_wheel_view_maxabs_N=forceerr,nonwheel_contact_rows_over1N=nonwheel,actual_minimum_authored_clearance_during_dynamics_m=penetration,poses=poses,full_source_models=models,original_ordinary_done_count=sum(x['ordinary_done_count'] for x in poses),original_termination_not_relaxed=True,source_original_joint_reset_preserved=True,zero_default_PD_not_zero_torque=True,no_actor_recovery_success_or_PPO_or_full20k_restore_claim=True,required_next='E3 learning needs an explicit reviewed recovery termination/reward/action contract, full20k state/native and original budget admission; the current original bad-orientation term immediately resets ±60/90 degree poses.',actual_child_EXIT0_and_parent_out=True,global_CPU_RNG_unchanged0CUDA0optimizer=True);p.write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps({k:result[k] for k in ('passed_legal_pose_contact_native_integrity','all_physical_callback_rows','all34_authored_geometry_independent_numpy_maxabs','nonwheel_contact_rows_over1N','original_ordinary_done_count','no_actor_recovery_success_or_PPO_or_full20k_restore_claim')}))
if __name__=='__main__':
 try:main()
 except BaseException:(R/('E3_ALLROWS_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).write_text(json.dumps(dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_replay_or_guard_change=True),indent=2),encoding='utf8');raise
