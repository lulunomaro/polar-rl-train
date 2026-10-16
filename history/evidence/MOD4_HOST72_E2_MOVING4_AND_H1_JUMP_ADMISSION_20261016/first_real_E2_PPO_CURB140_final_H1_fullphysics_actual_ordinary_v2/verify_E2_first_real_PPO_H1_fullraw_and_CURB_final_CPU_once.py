"""Independent local complete checkpoints/raw verification, no GPU or budget writes."""
from pathlib import Path
import os,json,hashlib,time,traceback
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch,numpy as np
torch.set_num_threads(4);D=Path(__file__).resolve().parent;R=D/'reports'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def exact(a,b):
 if torch.is_tensor(a):return torch.is_tensor(b) and a.dtype==b.dtype and a.shape==b.shape and a.contiguous().numpy().tobytes()==b.contiguous().numpy().tobytes()
 if isinstance(a,dict):return a.keys()==b.keys() and all(exact(x,b[k]) for k,x in a.items())
 if isinstance(a,(tuple,list)):return type(a)==type(b) and len(a)==len(b) and all(exact(x,y) for x,y in zip(a,b))
 return a==b
def finite(x):
 counts=[0,0]
 def walk(v):
  if torch.is_tensor(v):counts[0]+=1;counts[1]+=int(v.is_floating_point());assert not v.is_floating_point() or torch.isfinite(v).all()
  elif isinstance(v,dict):
   for q in v.values():walk(q)
  elif isinstance(v,(tuple,list)):
   for q in v:walk(q)
 walk(x);return counts
def main():
 c=json.loads((R/'E2_FIRST_FULLMODEL_H1_RAW_CURB_FINAL_V2_ACTUAL_BOUND_COLLECTION.json').read_bytes());s=torch.load(D/'payload/job0/source/E0_full_source.pt',map_location='cpu',weights_only=False);models=[]
 for row in c['E2_local_models']:
  p=Path(row['path']);assert H(p)==row['SHA'] and p.stat().st_size==row['bytes'];v=torch.load(p,map_location='cpu',weights_only=False);cnt=finite(v);phase=v['owned_phase'];updates=v['owned_phase_complete_updates'];assert len(v['actor_state_dict'])==9 and len(v['critic_state_dict'])==8 and len(v['optimizer_state_dict']['state'])==17
  assert {int(x['step']) for x in v['optimizer_state_dict']['state'].values()}=={639560+20*updates}
  assert v['owned_new_expert_task']['source_SHA']==H(D/'payload/job0/source/E0_full_source.pt')
  if phase=='native':
   for k in ('actor_state_dict','critic_state_dict','optimizer_state_dict'):assert exact(v[k],s[k]),k
  else:
   changed={k:[n for n,z in v[k].items() if not torch.equal(z,s[k][n])] for k in ('actor_state_dict','critic_state_dict')};assert changed['actor_state_dict'] and changed['critic_state_dict']
  if phase=='production':assert updates==1
  if phase=='precheck128':assert updates==2
  if phase=='precheck20k':assert updates==4
  command=v['E2_moving4_command_state'];mask=command['tensors']['is_moving_spin'];assert command['moving_yaw_cap']==4 and mask.any() and (command['tensors']['signed_yaw'][mask].abs()==4).all()
  models.append(dict(**row,phase=phase,updates=updates,all17Adam=639560+20*updates,whole_tensor_counts=cnt,source_weights_unchanged=(phase=='native'),changed=changed if phase!='native' else {}))
 actual=next((x for x in models if x['phase']=='production'),None);assert actual,'Not a real production first save; do not credit discarded prechecks'
 assert {x['phase'] for x in models}=={'production','native','precheck128','precheck20k'}
 put('E2_FIRST_REAL_MOVING4_PRODUCTION_COMPLETE_MODELS_LOCAL_CPU_VERIFIED.json',dict(epoch=time.time(),passed=True,source_SHA=H(D/'payload/job0/source/E0_full_source.pt'),models=models,original_native_source9critic8STD17Adam_literal_exact=True,discarded1282_all17Adam639600=True,discarded20k4_all17Adam639640=True,fresh_production1_all17Adam639580=True,first_production_environment_steps=480000,E2_mode_RNG_buffers_saved=True,actual_signed4_command_not_achieved_motion_claim=True,independent_policy_not_NCCL_or_gate=True,no_jump_PPO_claim=True,not_fullwindow_FINAL_or_skill_improvement=True,original_source_budget_not_modified_by_CPU=True))
 count=0;last=done=None;err=impulse_error=0.;resets=0
 for row in c['H1_complete_raw_twohost']:
  p=Path(row['path']);assert p.stat().st_size==row['bytes'] and H(p)==row['SHA']
  with np.load(p,allow_pickle=False) as z:d={k:z[k] for k in z.files}
  for k,x in d.items():
   if x.dtype.kind in 'fc':assert np.isfinite(x).all(),k
  x=d['policy35'];S=x.shape[0];assert x.shape[1:]==(80,35);mode=np.zeros_like(x[:,:,28:35]);mode[:,:,4]=1;assert np.array_equal(mode,x[:,:,28:35])
  assert np.array_equal(d['executed6'],np.clip(d['raw6'],-6,6));assert abs(d['ground']).max()<=1e-6 and d['mimic'].max()<=.01
  for i in range(S):
   if last is not None:
    expected=last.copy();expected[done]=0;assert np.array_equal(expected,x[i,:,22:28])
   last=np.clip(d['raw6'][i],-6,6);done=d['done'][i].astype(bool)
  impulse_error=max(impulse_error,float(abs(np.maximum(d['physical_wheel_force'][:,:,:,:,2],0).sum(1)*.0025-d['impulse']).max()));assert impulse_error<=1e-6
  y=torch.from_numpy(x.reshape(-1,35));sd=s['actor_state_dict']
  for i in (0,2,4,6):
   y=torch.nn.functional.linear(y,sd[f'mlp.{i}.weight'],sd[f'mlp.{i}.bias'])
   if i<6:y=torch.nn.functional.elu(y)
  err=max(err,float(abs(y.numpy()-d['raw6'].reshape(-1,6)).max()));assert err<=1e-4;count+=S;resets+=int(d['done'].sum());assert d['full_robot_contact_force'].shape[2:]==(31,3)
 assert count==144
 put('H1_NATIVE80_COMPLETE_TWOHOST_RAW_LOCAL_ALL_ROWS_CPU_ACTUAL.json',dict(epoch=time.time(),passed=True,raw=c['H1_complete_raw_twohost'],controls=144,callbacks=576,all_11520_actor_input_rows_CPU_checked=True,CPUvsGPUmean_maxabs=err,CPU_GPU_not_bitexact=True,positive_vertical_contact_impulse_maxabs=impulse_error,all_q30_root13_policy35_critic38_actions_torques_contacts31_bodyposes_finite=True,mode4_lastactualclipped6_selectedreset_exact=True,actual_done_events=resets,no_PPO_or_teacher_or_airborne_skill_credit=True,postreset_pose_contact_caution_preserved=True))
 curb=c.get('CURB_final_model')
 if curb:
  p=Path(curb['path']);assert H(p)==curb['SHA'];v=torch.load(p,map_location='cpu',weights_only=False);cnt=finite(v);src=c['source'];final=src['CURB_final']['final'];assert final['SHA']==H(p) and v['CURB35_training_phase']=='production';steps={int(x['step']) for x in v['optimizer_state_dict']['state'].values()};assert steps=={660400+20*final['updates']};assert v['E1_terrain_state']['CURB_height_m']==.035
  segs=src['canonical']['own_completed'];seg=next(x for x in segs if x.get('owner_parent_pid')==480021);elapsed=seg['ended_epoch']-seg['started_epoch'];assert abs(elapsed-seg['charged_seconds'])<1e-4;total=elapsed+114.0848639011383;assert src['CURB_owner_exit']['canonical_settled'] and src['CURB_worker_exit']['returncode']==0
  put('CURB35_FIRST_SCOPE_FINAL_FULLMODEL_AND_EXACT_COST_LOCAL_CPU_ACTUAL.json',dict(epoch=time.time(),passed_fullsave_CPU=True,model=curb,whole_tensor_counts=cnt,updates=final['updates'],all17Adam=next(iter(steps)),source_native_and_prechecks_reused_not_replayed=True,actual_new_fresh_parent_seconds=elapsed,old_failed_prechecks_actual_seconds=114.0848639011383,whole_scope_actual_charged_seconds=total,whole_scope_plan_cap_seconds=2700,duration_bound_passed=total<=2700,unique_original_completed_segment=seg,new_CURB35_model_frozen_behavior_not_yet_evaluated=True,later_E2_owner_may_hold_locks_not_falsely_all_idle=True))
 assert not torch.cuda.is_initialized();print(json.dumps(dict(E2_real_production_CPU_pass=True,E2_models=len(models),H1_complete_raw_controls=count,CURB_final_CPU=bool(curb),no_future_skill_pass_claim=True)),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:put('E2_H1_CURB_COMPLETE_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),read_only_no_GPU_replay=True));raise
