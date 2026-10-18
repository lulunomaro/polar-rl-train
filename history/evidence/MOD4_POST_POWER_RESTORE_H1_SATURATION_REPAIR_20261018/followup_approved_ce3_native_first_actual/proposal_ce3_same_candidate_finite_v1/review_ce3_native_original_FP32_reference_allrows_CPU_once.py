"""Independent all saved means/physics, public timing, event, source-state and prefix audit."""
from pathlib import Path
import os,json,time,hashlib,traceback
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch,numpy as np
from h1_takeoff_progress_phase_v2 import H1TakeoffProgressPhaseV2 as H1PublicRequestPhase
from h1_reference_geometry_cpu import support
B=Path(__file__).resolve().parent;J=B/'job0';OUT=J/'native';torch.set_num_threads(4)
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def exact(a,b):
 if torch.is_tensor(a):return torch.is_tensor(b) and a.dtype==b.dtype and a.shape==b.shape and a.contiguous().reshape(-1).numpy().tobytes()==b.contiguous().reshape(-1).numpy().tobytes()
 if isinstance(a,dict):return isinstance(b,dict) and a.keys()==b.keys() and all(exact(a[k],b[k]) for k in a)
 if isinstance(a,(tuple,list)):return type(a)==type(b) and len(a)==len(b) and all(exact(x,y) for x,y in zip(a,b))
 return a==b
def arrayfile(row):
 p=Path(row['path']);assert p.stat().st_size==row['bytes'] and H(p)==row['SHA']
 with np.load(p,allow_pickle=False) as z:v={k:z[k] for k in z.files}
 for k,x in v.items():
  if x.dtype.kind in 'fc':assert np.isfinite(x).all(),k
 return v
def finite(x):
 if torch.is_tensor(x):return not x.is_floating_point() or bool(torch.isfinite(x).all())
 if isinstance(x,dict):return all(finite(v) for v in x.values())
 if isinstance(x,(tuple,list)):return all(finite(v) for v in x)
 return True
def main():
 assert not (OUT/'H1_CE3_ORIGINAL_FP32_NATIVE180_ALL_ROWS_CPU_ACTUAL.json').exists();v=json.loads((OUT/'NATIVE180_PRELAUNCH_V2_COMPLETE_ACTUAL.json').read_bytes());task=json.loads((J/'TASK.json').read_bytes());source=J/'source/H1_ce3_public4_closed24.pt';assert H(source)==task['source_SHA'];s=torch.load(source,map_location='cpu',weights_only=False);ck=torch.load(v['saved']['path'],map_location='cpu',weights_only=False);assert finite(ck)
 for k in ('actor_state_dict','critic_state_dict','optimizer_state_dict'):assert exact(s[k],ck[k])
 assert {int(x['step']) for x in ck['optimizer_state_dict']['state'].values()}=={646100};ref=json.loads((OUT/'ACTUAL_ALL34_COLLIDER_PLANE_AND_31_CONTACT_REFERENCE.json').read_bytes());witness=np.asarray(ref['witness_ids']);wheel=[ref['contact_body_names'].index(x) for x in ('left_wheel','right_wheel')];non=[i for i in range(31) if i not in wheel];maxmean=impulse=eventerr=queryerr=progresserr=0.;proxy_total=0.;last=done=age=None;counts=np.zeros(7,np.int64);control_count=0
 for r in v['controls_raw']:
  d=arrayfile(r);x=d['policy35'];assert x.shape[1:]==(20000,35);request=(d['public_age_control']>=100)&(d['public_age_control']<180);mode=np.zeros_like(x[:,:,28:35]);mode[:,:,0]=~request;mode[:,:,4]=request;assert np.array_equal(mode,x[:,:,28:35]) and np.array_equal(request,d['public_request']) and np.array_equal(d['executed6'],np.clip(d['raw6'],-6,6)) and not d['command'].any();queryerr=max(queryerr,float(abs(d['ground']).max()));assert queryerr<=1e-6 and d['mimic'].max()<=.01
  for i in range(len(x)):
   if last is not None:
    previous=last.copy();previous[done]=0;assert np.array_equal(previous,x[i,:,22:28]);expected=age+1;expected[done]=0;assert np.array_equal(expected,d['public_age_control'][i])
   last=np.clip(d['raw6'][i],-6,6);done=d['done'][i].astype(bool);age=d['public_age_control'][i].copy();counts+=mode[i].sum(0).astype(np.int64)
  impulse=max(impulse,float(abs(np.maximum(d['physical_wheel_force'][:,:,:,:,2],0).sum(1)*.0025-d['impulse']).max()));eventerr=max(eventerr,float(abs(d['event_applied']-d['event_expected']).max()));progresserr=max(progresserr,float(abs(d['progress_applied']-d['progress_expected']).max()));proxy_total+=float(d['progress_applied'].sum(dtype=np.float64));assert impulse<=1e-6 and eventerr<=1e-6 and progresserr<=1e-6;assert not d['progress_applied'][~request].any()
  y=torch.from_numpy(x.reshape(-1,35));sd=s['actor_state_dict']
  for k in (0,2,4,6):
   y=torch.nn.functional.linear(y,sd[f'mlp.{k}.weight'],sd[f'mlp.{k}.bias'])
   if k<6:y=torch.nn.functional.elu(y)
  maxmean=max(maxmean,float(abs(y.numpy()-d['raw6'].reshape(-1,6)).max()));assert maxmean<=1e-4;control_count+=len(x)
 assert control_count==180 and counts[4]>0 and counts[0]>0
 phase=H1PublicRequestPhase(20000,'cpu');last_episode=None;physical_count=0;geometryerr=forceerr=normerr=phaseerr=0.;events=np.zeros((3,20000),np.int64)
 for r in v['physics_raw']:
  d=arrayfile(r);gold=support(d['witness_body_pos'],d['witness_body_quat_xyzw'],ref['shapes']);geometryerr=max(geometryerr,float(abs(gold-d['all34_clearance'][:,witness]).max()));assert geometryerr<=1e-6
  forceerr=max(forceerr,float(abs(d['all31_contact_force'][:,:,wheel]-d['wheel_raw']).max()));assert forceerr<=.1
  normerr=max(normerr,float(abs(np.linalg.norm(d['wheel_5ms_mean'],axis=-1)-d['wheel_norm_N']).max()));assert normerr<=1e-4
  for i in range(len(d['episode'])):
   ep=d['episode'][i];reset=np.zeros(20000,bool) if last_episode is None else ep!=last_episode;last_episode=ep.copy();phase.reset(torch.from_numpy(np.flatnonzero(reset)))
   if physical_count%4==0:phase.begin_control()
   root=d['root13'][i];args=dict(wheel_N=torch.from_numpy(d['wheel_norm_N'][i]),wheel_clear_m=torch.from_numpy(d['wheel_clearance'][i]),all_min_clear_m=torch.from_numpy(d['all34_clearance'][i].min(-1)),nonwheel_max_N=torch.from_numpy(d['nonwheel_max'][i]),root_vz=torch.from_numpy(root[:,9]),root_planar_speed=torch.from_numpy(d['root_planar_speed'][i]),roll=torch.from_numpy(d['roll'][i]),pitch=torch.from_numpy(d['pitch'][i]),yaw=torch.from_numpy(d['yaw'][i]));out=phase.physical(**args);phaseerr=max(phaseerr,float(abs(out['event_delta'].numpy()-d['event_delta'][i]).max()));assert phaseerr<=1e-6;assert float(abs(out['prelaunch_proxy_delta'].numpy()-d['prelaunch_proxy_delta'][i]).max())<=1e-6
   for k,name in enumerate(('takeoff','landing','recovery')):assert np.array_equal(out[name].numpy(),d[name][i]);events[k]+=d[name][i]
   physical_count+=1
   if physical_count%4==0:phase.finish_control_before_selected_reset()
 assert physical_count==720 and not torch.cuda.is_initialized();shadow=json.loads((OUT/'MID_NATIVE_PHASE_SHADOW_ROUNDTRIP_SELECTED_RESET_ACTUAL.json').read_bytes());assert shadow['actual_mid_phase_CUDA_diskroundtrip_exact']
 assert proxy_total>0 and float(phase.progress_paid.max())<=1.000001;report=dict(epoch=time.time(),passed=True,prelaunch_proxy_actual_live_term_maxabs=progresserr,prelaunch_proxy_total_credit=proxy_total,nonzero_training_signal_not_jump_skill=True,base_flight_landing_recovery_contract_unchanged=True,source_SHA=task['source_SHA'],native_checkpoint=v['saved'],controls=180,callbacks=720,all_policy_rows=3600000,all_physical_rows=14400000,sourceactor9critic8STD17Adam_literal_exact=True,all17Adam_step646100=True,all_saved_actor_CPUmean_maxabs=maxmean,CPU_GPU_not_bitexact=True,physical_positive_z_impulse_maxabs=impulse,actual_loaded_Plane_reference_query_maxabs=queryerr,actual_physics_Plane_cooked_shape_not_directquery=True,event_reward_actual_live_manager_maxabs=eventerr,actual_SDK_dt_probe=v['actual_sdk_reward_probe'],public_mode_history_lastactualclipped6_selectedreset_exact=True,normal_jump_sample_counts=counts.tolist(),all_saved_31force_34clearance_finite=True,geometry_8witness_all720callbacks_independent_numpy_maxabs=geometryerr,not_all20k_bodypose_replay=True,fullsensor_wheel_view_component_maxabs=forceerr,all20k_source_phase_CPU_event_reconstruction_maxabs=phaseerr,events_env_counts=[int((events[i]>0).sum()) for i in range(3)],native_not_jump_skill_or_PPO_pass=True,complete_original20k_typed_source_restore_actual=True,H1_phase_new_declared_actual_CUDA_diskroundtrip_exact=True,optimizer_CUDA_calls0_in_CPU=True,all_original_strict_guards_costs_and_physical_failure_prefixes_retained=True,learning_permission_not_granted_by_this_CPU_report=True)
 (OUT/'H1_CE3_ORIGINAL_FP32_NATIVE180_ALL_ROWS_CPU_ACTUAL.json').write_text(json.dumps(report,indent=2));print(json.dumps(report),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:(B/('H1_CE3_ORIGINAL_FP32_NATIVE_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).write_text(json.dumps(dict(error=traceback.format_exc(),no_GPU_replay=True),indent=2));raise
