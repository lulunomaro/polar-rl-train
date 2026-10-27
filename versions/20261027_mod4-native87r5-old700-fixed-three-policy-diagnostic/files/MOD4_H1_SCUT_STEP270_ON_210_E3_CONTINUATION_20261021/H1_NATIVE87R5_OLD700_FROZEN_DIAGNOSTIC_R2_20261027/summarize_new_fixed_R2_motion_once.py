"""Consume only this NEW fixed-three-seed recorded motion once; no model/SDK/actor."""
from pathlib import Path
import hashlib,importlib.util,json,sys,time,traceback
import numpy as np
S=Path(__file__).resolve().parent;T=S.parent;R=S/'reports'
P=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027/native87R5_frozen_step_acceptance_preparation_v2_own_pid_only'
def put(p,v):
 with Path(p).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
def main():
 put(R/'NEW_R2_MOTION_ANALYSIS_CONSUMED_BEFORE_RAW_READ_ACTUAL.json',dict(epoch=time.time(),new_purpose_only=True,no_old_raw_or_model_or_SDK_or_actor=True))
 q=json.loads((S/'BINDING.json').read_bytes());sys.path.insert(0,str(P))
 from aggregate_native87R5_frozen_three_seed_CPU_unused_once import summarize
 parent=json.loads((R/'FROZEN_OLD700_THREE_SEED_FINITE_RETURNED_ACTUAL.json').read_bytes())
 assert parent['all_own_children_actual_out'] and parent['parent_original_error'] is None and len(parent['cases'])==3
 cases={};metrics=[];arrays={}
 for seed in q['seeds']:
  f=S/'actual72'/('seed_'+str(seed));status=json.loads((f/'episode/FROZEN_SINGLE_CASE_STATUS_ACTUAL.json').read_bytes())
  cases[seed]=dict(status=status,authority=json.loads((f/'READONLY_AUTHORITY_CASE_EXIT.json').read_bytes()),function_return=json.loads((f/'FROZEN_SINGLE_CASE_FUNCTION_RETURNED_ACTUAL.json').read_bytes()) if (f/'FROZEN_SINGLE_CASE_FUNCTION_RETURNED_ACTUAL.json').exists() else json.loads((f/'FROZEN_SINGLE_CASE_FUNCTION_RETURNED_ACTUAL.json').read_bytes()),close_or_original_errors=[])
  geometry=json.loads((f/'ACTUAL_RENDER_GEOMETRY.json').read_bytes())
  # Each new source JSONL is consumed in this one reader; reusable compact arrays follow.
  ts=[];roots=[];bodyp=[];bodyq=[];wmin=[];wmax=[];contact=[];history=[];ages=[];requests=[];torques=[];executed=[]
  with (f/'episode/ACTUAL_400HZ_31BODY_FRAMES.jsonl').open('r',encoding='utf8') as stream:
   for line in stream:
    row=json.loads(line);st=row['state'];cache=st['actual_original_success_caches']
    ts.append(row['physics_callback']*.0025);roots.append(st['root13_sdk_xyzw']);bodyp.append(st['body_position31_world']);bodyq.append(st['body_quaternion31_sdk_xyzw'])
    wmin.append(cache.get('step_wheel_min',[[np.nan]*3]*2));wmax.append(cache.get('step_wheel_max',[[np.nan]*3]*2))
    contact.append(st['body_contact_force31']);history.append(st['contact_history18']);ages.append(st['public_age']);requests.append(st['public_request']);torques.append(st['applied_torque30']);executed.append(st['executed6'])
  rawmeans=[];rawactions=[];cages=[];packed=[]
  with (f/'episode/ACTUAL_100HZ_CONTROLS.jsonl').open('r',encoding='utf8') as stream:
   for line in stream:
    row=json.loads(line);rawmeans.append(row['mean6']);rawactions.append(row['raw_native_clamp20_6']);cages.append(row['age_for_action'][0]);packed.append(row['packed127_for_action'])
  arr={k:np.asarray(v,dtype=np.float32) for k,v in dict(t=ts,root=roots,body_position=bodyp,body_quaternion=bodyq,wheel_min=wmin,wheel_max=wmax,contact_force=contact,contact_history=history,age=ages,request=requests,torque=torques,executed=executed,mean=rawmeans,raw=rawactions,control_age=cages,packed127=packed).items()}
  assert len(arr['t'])==2001 and len(arr['mean'])==500
  for k,a in arr.items():arrays[str(seed)+'_'+k]=a
  root=arr['root'];bothbottom=np.min(arr['wheel_min'][:,:,2],axis=1);bothfront=np.min(arr['wheel_max'][:,:,0],axis=1);gap=.35-bothfront
  mask=(arr['control_age']>=100)&(arr['control_age']<180)
  physicalmask=(arr['age']>=100)&(arr['age']<=180)
  quat=root[:,3:7];x,y,z,w=quat.T
  roll=np.degrees(np.arctan2(2*(w*x+y*z),1-2*(x*x+y*y)));pitch=np.degrees(np.arcsin(np.clip(2*(w*y-z*x),-1,1)))
  row=dict(seed=seed,controls=500,physics_callbacks=2000,simulated_seconds=5.,original_done_terms=status['last_termination_terms']['values'],original_takeoff=status['last_original_state']['takeoff_count'],original_crossed=status['last_original_state']['crossed2'],original_landing=status['last_original_state']['landing_count'],original_recovery=status['last_original_state']['recovery_count'],original_success=status['last_original_state']['success'],initial_root_xz=[float(root[0,0]),float(root[0,2])],root_x_range_m=[float(root[:,0].min()),float(root[:,0].max())],root_z_range_m=[float(root[:,2].min()),float(root[:,2].max())],final_root_xz=[float(root[-1,0]),float(root[-1,2])],max_both_wheel_bottom_m=float(np.nanmax(bothbottom)),nearest_both_wheel_front_gap_to_edge_m=float(np.nanmin(gap)),peak_abs_roll_deg=float(np.max(np.abs(roll))),peak_abs_pitch_deg=float(np.max(np.abs(pitch))),request_action_rows=int(mask.sum()),request_max_both_bottom_m=float(np.nanmax(bothbottom[physicalmask])),request_nearest_both_front_gap_m=float(np.nanmin(gap[physicalmask])),request_root_vx_range_m_s=[float(root[physicalmask,7].min()),float(root[physicalmask,7].max())],request_root_vz_range_m_s=[float(root[physicalmask,9].min()),float(root[physicalmask,9].max())],mean6_minmax=[[float(arr['mean'][:,i].min()),float(arr['mean'][:,i].max())] for i in range(6)],raw_clip6_hit_fraction=float((np.abs(arr['raw'])>=6).mean()),not_hardware400_acceptance=True)
  metrics.append(row)
  # Geometry metadata is source-authored collider data, not another USD read.
  put(S/('DERIVED_GEOMETRY_'+str(seed)+'.json'),geometry)
 result=summarize(q,cases);result.update(hardware_scope=q['hardware_scope'],actual_no_learning_cost_write=True,original_parent_returned=True,original_old700_diagnostic_not400hardware_goal=True,motion_metrics=metrics)
 npz=S/'NEW_FIXED_R2_MOTION_DERIVED_ONLY.npz';assert not npz.exists();np.savez_compressed(npz,**arrays)
 result['new_derived_motion']=dict(path=str(npz),bytes=npz.stat().st_size,SHA=hashlib.sha256(npz.read_bytes()).hexdigest(),original_raw_paths_preserved=True)
 put(R/'FROZEN_FIXED_THREE_SEED_ORIGINAL_GOAL_AND_MOTION_ACTUAL.json',result)
 import matplotlib
 matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 fig,ax=plt.subplots(3,3,figsize=(14,9),sharex=True)
 for col,row in enumerate(metrics):
  seed=row['seed'];a={k:arrays[str(seed)+'_'+k] for k in ('t','root','wheel_min','wheel_max')}
  bottom=np.min(a['wheel_min'][:,:,2],axis=1);gap=.35-np.min(a['wheel_max'][:,:,0],axis=1)
  ax[0,col].plot(a['t'],bottom,label='both-wheel bottom');ax[0,col].axhline(.27,color='r',ls='--',label='270mm top')
  ax[1,col].plot(a['t'],gap);ax[1,col].axhline(0,color='r',ls='--')
  ax[2,col].plot(a['t'],a['root'][:,7],label='forward vx');ax[2,col].plot(a['t'],a['root'][:,9],label='vertical vz')
  for r in range(3):ax[r,col].axvspan(1.,1.8,color='orange',alpha=.15);ax[r,col].grid(alpha=.2)
  ax[0,col].set_title('Fixed seed '+str(seed));ax[2,col].set_xlabel('actual physics time (s)')
 ax[0,0].set_ylabel('wheel bottom height (m)');ax[1,0].set_ylabel('gap to edge, both fronts (m)');ax[2,0].set_ylabel('base velocity (m/s)')
 ax[0,0].legend();ax[2,0].legend();fig.suptitle('R5 frozen mean: OLD700 diagnostic, not 400N hardware acceptance');fig.tight_layout()
 image=S/'FIXED_THREE_CASES_HEIGHT_GAP_AND_VELOCITY.png';fig.savefig(image,dpi=150);plt.close(fig)
 put(R/'NEW_MOTION_PLOT_PRODUCER_ACTUAL.json',dict(path=str(image),bytes=image.stat().st_size,SHA=hashlib.sha256(image.read_bytes()).hexdigest(),source_derived_SHA=result['new_derived_motion']['SHA'],no_actor_or_physics_or_old_raw=True))
 print(json.dumps(dict(passed=True,successes=result['original_goal_success_count'],cases=metrics,plot=str(image))))
if __name__=='__main__':
 try:main()
 except BaseException:put(R/('NEW_MOTION_READER_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),dict(error=traceback.format_exc(),no_model_or_actor=True));raise
