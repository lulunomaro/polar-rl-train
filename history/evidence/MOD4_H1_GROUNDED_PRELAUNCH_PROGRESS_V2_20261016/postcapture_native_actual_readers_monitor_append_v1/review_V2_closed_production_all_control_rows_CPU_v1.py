"""Consume all existing H1 production prefixes on CPU without replaying physics.

Training sampled Gaussian actions, not deterministic means. No GPU-mean or saved
log-probability equality is claimed for quantities the trace did not record.
"""
from pathlib import Path
import os,json,time,hashlib,traceback
os.environ['CUDA_VISIBLE_DEVICES']=''
os.environ['OMP_NUM_THREADS']='4'
import numpy as np
import torch
B=Path(__file__).resolve().parent;ROOT=B.parent;OUT=ROOT/'job0/production';torch.set_num_threads(4)
def H(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for block in iter(lambda:f.read(4*1024*1024),b''):h.update(block)
 return h.hexdigest()
def put(p,x):
 tmp=p.with_suffix(p.suffix+'.partial');tmp.write_text(json.dumps(x,indent=2));tmp.replace(p)
def exact(a,b):
 if torch.is_tensor(a):return torch.is_tensor(b) and a.shape==b.shape and a.dtype==b.dtype and a.contiguous().reshape(-1).view(torch.uint8).numpy().tobytes()==b.contiguous().reshape(-1).view(torch.uint8).numpy().tobytes()
 if isinstance(a,dict):return isinstance(b,dict) and a.keys()==b.keys() and all(exact(a[k],b[k]) for k in a)
 if isinstance(a,(tuple,list)):return type(a)==type(b) and len(a)==len(b) and all(exact(x,y) for x,y in zip(a,b))
 return a==b
def finite(x,count):
 if torch.is_tensor(x):
  count[0]+=1
  if x.is_floating_point():count[1]+=1;assert torch.isfinite(x).all()
 elif isinstance(x,dict):
  for v in x.values():finite(v,count)
 elif isinstance(x,(tuple,list)):
  for v in x:finite(v,count)
def main():
 dest=B/'ALL_V2_PRODUCTION_CONTROL_ROWS_CPU_ACTUAL.json';assert not dest.exists();assert (ROOT/'NODE_EXIT_ACTUAL.json').exists();assert json.loads((ROOT/'NODE_TERMINAL_ALL_OWN_CHILDREN_EXIT_ACTUAL.json').read_bytes())['row']['production_complete'];rng=torch.get_rng_state().clone();index=json.loads((OUT/'control_prefix_raw/CONTROL_VALID_PREFIX_INDEX_ACTUAL.json').read_bytes());updates=index['controls']//24;assert updates>0 and index['controls']==updates*24 and len(index['index'])==updates and len(index['preupdate_full_sources'])==updates and not index['physical_callback_replay'];terms=index['reward_terms'];event_i=terms.index('h1_control_events');progress_i=terms.index('h1_prelaunch_progress');progress_err=progress_delta_err=progress_sum=0.;previous_paid=None;masked=[terms.index(k) for k in ('height','height_tight','height_both_wheels','height_square','height_deficit','height_error_l1','lin_vel_z')]
 source=ROOT/'job0/source/H1_final10_protected.pt';s=torch.load(source,map_location='cpu',weights_only=False);last=None;done=None;age=np.zeros(20000,np.int64);previous_counts=np.zeros((3,20000),np.int64);events=np.zeros((3,20000),np.int64);mode_counts=np.zeros(7,np.int64);resets=0;allrows=0;event_max=mask_max=reward_sum_error=closure_max=mimic_max=std_residual_max=0.;event_sum=0.;root_z=[];root_vz=[];both_unloaded=[];requested_root_z=[];requested_root_vz=[];modelrows=[];rawrows=[];begun=time.time();startz=None
 for block,row in enumerate(index['index']):
  p=Path(row['path']);assert p.stat().st_size==row['bytes'] and H(p)==row['SHA'];z=np.load(p,allow_pickle=False);d={k:z[k] for k in z.files};z.close()
  for k,v in d.items():
   if v.dtype.kind in 'fc':assert np.isfinite(v).all(),(p.name,k)
  model=index['preupdate_full_sources'][block];mp=Path(model['path']);assert mp.stat().st_size==model['bytes'] and H(mp)==model['SHA'];ck=torch.load(mp,map_location='cpu',weights_only=False);count=[0,0];finite(ck,count);assert {int(v['step']) for v in ck['optimizer_state_dict']['state'].values()}=={639760+block*20};assert len(ck['actor_state_dict'])==9 and len(ck['critic_state_dict'])==8
  if block==0:
   for k in ('actor_state_dict','critic_state_dict','optimizer_state_dict'):assert exact(ck[k],s[k]),k
  modelrows.append(dict(**model,tensors=count[0],float_tensors=count[1],all_finite=True,expected17Adam639760_plus20block=True));x=d['policy35'];assert x.shape==(24,20000,35) and d['critic38'].shape==(24,20000,38);request=d['public_request'].astype(bool);expected_mode=np.zeros_like(x[:,:,28:35]);expected_request=(age[None,:]>=100)&(age[None,:]<180)
  assert np.array_equal(d['executed6'],np.clip(d['raw_sampled6'],-6,6))
  for i in range(24):
   paid=d['progress_paid'][i];peak=d['progress_peak'][i];assert (paid>=0).all() and (paid<=1.000001).all() and np.array_equal(paid,peak)
   baseline=np.zeros_like(paid) if previous_paid is None else previous_paid.copy()
   if done is not None:baseline[done]=0
   delta=paid-baseline;assert (delta>=-1e-6).all();progress_delta_err=max(progress_delta_err,float(abs(.5*delta-d['progress_expected'][i]).max()));assert progress_delta_err<=1e-6;previous_paid=paid.copy()
   want=(age>=100)&(age<180);assert np.array_equal(want,request[i]);mode=np.zeros((20000,7),np.float32);mode[:,0]=~want;mode[:,4]=want;assert np.array_equal(mode,x[i,:,28:35]);mode_counts+=mode.sum(0).astype(np.int64)
   if last is not None:
    previous=last.copy();previous[done]=0;assert np.array_equal(previous,x[i,:,22:28])
   for k,name in enumerate(('takeoff_count','landing_count','recovery_count')):
    current=d[name][i];baseline=previous_counts[k].copy()
    if done is not None:baseline[done]=0
    delta=current-baseline;assert (delta>=0).all();events[k]+=delta;previous_counts[k]=current
   last=d['executed6'][i].copy();done=d['done'][i].astype(bool);resets+=int(done.sum());age+=1;age[done]=0
  applied=d['reward_term_contribution'];progress_err=max(progress_err,float(abs(applied[:,:,progress_i]-d['progress_expected']).max()));assert progress_err<=1e-6 and not d['progress_expected'][~request].any();progress_sum+=float(d['progress_expected'].sum(dtype=np.float64));event_max=max(event_max,float(abs(applied[:,:,event_i]-d['event_expected']).max()));assert event_max<=1e-6;event_sum+=float(d['event_expected'].sum(dtype=np.float64))
  for term_i in masked:
   if request.any():mask_max=max(mask_max,float(abs(applied[:,:,term_i][request]).max()))
  assert mask_max<=1e-6;reward_sum_error=max(reward_sum_error,float(abs(applied.sum(-1)-d['total_reward']).max()));closure_max=max(closure_max,float(d['closure'].max()));mimic_max=max(mimic_max,float(d['mimic'].max()));assert mimic_max<=.01
  sd=ck['actor_state_dict'];sigma=sd['distribution.std_param'].numpy();assert sigma.shape==(6,) and (sigma>0).all();maximum_z=0.;obs=x.reshape(-1,35);raw=d['raw_sampled6'].reshape(-1,6)
  with torch.inference_mode():
   for start in range(0,len(obs),20000):
    y=torch.from_numpy(obs[start:start+20000])
    for layer in (0,2,4,6):
     y=torch.nn.functional.linear(y,sd[f'mlp.{layer}.weight'],sd[f'mlp.{layer}.bias'])
     if layer<6:y=torch.nn.functional.elu(y)
    assert torch.isfinite(y).all();normalized=(raw[start:start+20000]-y.numpy())/sigma;assert np.isfinite(normalized).all();maximum_z=max(maximum_z,float(abs(normalized).max()))
  std_residual_max=max(std_residual_max,maximum_z);rz=d['root13'][:,:,2];vz=d['root13'][:,:,9];wheel=np.linalg.norm(d['history5ms'][:,:,0],axis=-1);unloaded=(wheel<=1.).all(-1);root_z.append(rz.copy());root_vz.append(vz.copy());both_unloaded.append(unloaded.copy());requested_root_z.append(rz[request].copy());requested_root_vz.append(vz[request].copy());allrows+=len(obs);rawrows.append(dict(**row,all_rows_finite=True,all_control_inputs_and_action_history_public_schedule_exact=True,CPU_manual_mean_and_standardized_sample_residual_finite=True,CPU_standardized_sample_residual_maxabs=maximum_z,not_GPU_mean_or_logprob_equality=True));put(B/'CURRENT_ACTUAL.json',dict(epoch=time.time(),blocks=block+1,controls=(block+1)*24,policy_rows=allrows,candidate_events=events.sum(1).tolist(),no_CUDA_or_optimizer=True));del d,ck
 rz=np.concatenate(root_z);vz=np.concatenate(root_vz);unloaded=np.concatenate(both_unloaded);requested_z=np.concatenate(requested_root_z);requested_vz=np.concatenate(requested_root_vz);finalrow=json.loads((OUT/'FINAL.json').read_bytes())['final'];final=Path(finalrow['path']);assert H(final)==finalrow['SHA'];f=torch.load(final,map_location='cpu',weights_only=False);count=[0,0];finite(f,count);assert f['owned_H1_completed_updates']==updates and f['owned_H1_phase']=='production' and not f['failed_partial_prefix'] and {int(v['step']) for v in f['optimizer_state_dict']['state'].values()}=={639760+updates*20};assert allrows==updates*480000 and torch.equal(torch.get_rng_state(),rng) and not torch.cuda.is_initialized()
 def stats(x):return dict(count=int(x.size),min=float(x.min()),mean=float(x.mean(dtype=np.float64)),p01=float(np.quantile(x,.01)),p99=float(np.quantile(x,.99)),max=float(x.max()))
 report=dict(epoch=time.time(),passed_integrity_CPU=True,controls=updates*24,all_policy_rows=allrows,formal_updates=updates,formal_envsteps=updates*480000,all_control_prefixes=rawrows,all_preupdate_complete_sources=modelrows,final_model=dict(**finalrow,tensors=count[0],float_tensors=count[1],all_finite=True,all17Adam639760_plus20updates=True),all35_38_inputs_history_actualclip_and_selectedreset_public_schedule_exact=True,mode_sample_counts=mode_counts.tolist(),reset_count_combined_ordinary_truncation_not_separately_recorded=resets,candidate_takeoff_landing_recovery_events=events.sum(1).tolist(),candidate_event_env_counts=[int((e>0).sum()) for e in events],candidate_event_reward_sum=event_sum,prelaunch_proxy_reward_sum=progress_sum,actual_live_prelaunch_progress_term_maxabs=progress_err,per_attempt_capped_peak_increment_reconstruction_maxabs=progress_delta_err,prelaunch_proxy_not_flight_or_COM_energy=True,actual_live_event_term_maxabs=event_max,seven_jump_request_height_vertical_mask_maxabs=mask_max,total_reward_terms_sum_float_maxabs=reward_sum_error,closure_control_sample_max_m=closure_max,mimic_control_sample_max_m=mimic_max,root_world_z_control_sample=stats(rz),root_vz_control_sample=stats(vz),jump_request_root_z_control_sample=stats(requested_z),jump_request_root_vz_control_sample=stats(requested_vz),both_wheels_5ms_mean_le1N_at10ms_control_samples=int(unloaded.sum()),CPU_standardized_sample_residual_maxabs=std_residual_max,not_saved_GPU_mean_or_logprob_bitexact=True,not_whole_physical_callback_replay_or_all34_shape_clearance_in_training=True,control_force_samples_not_strict40ms_flight_or_frozen_skill=True,no_ordinary_vs_truncation_relabel_from_combined_done=True,not_hardware_energy_integral_or_frozen_jump_qualification=True,no_GPU_optimizer_or_budget_write=True,elapsed_CPU_seconds=time.time()-begun)
 put(dest,report);print(json.dumps({k:report[k] for k in ('passed_integrity_CPU','controls','formal_updates','formal_envsteps','candidate_takeoff_landing_recovery_events','candidate_event_reward_sum','actual_live_event_term_maxabs','seven_jump_request_height_vertical_mask_maxabs','root_vz_control_sample','both_wheels_5ms_mean_le1N_at10ms_control_samples','elapsed_CPU_seconds')}),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:put(B/'ORIGINAL_ERROR_ACTUAL.json',dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_replay_or_reclassification=True));raise
