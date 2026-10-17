"""Describe saved original gates only; never redefine flight or mutate source/rewards."""
from pathlib import Path
import sys,json,time,hashlib,traceback,os
os.environ['CUDA_VISIBLE_DEVICES']=''
import numpy as np
B=Path(__file__).resolve().parent;R=B/'reports'
def main():
 label=sys.argv[1];assert label in ('FE1709','D723','B326','MEANFIRST','MEANFINAL','PUBLIC4N1','PUBLIC4FINAL');j=json.loads(Path(sys.argv[2]).read_bytes());p=Path(next(r['local_path'] for r in j['files'] if r['relative'].endswith('/retention_full_control_substep_actual.npz')))
 with np.load(p,allow_pickle=False) as z:
  done=z['terminated']|z['truncated'];S,N=done.shape;first=np.where(done.any(0),done.argmax(0),S);valid=np.arange(S)[:,None]<first[None,:];request=z['H1_public_request']&valid;physical_valid=np.repeat(valid,4,axis=0);physical_request=np.repeat(request,4,axis=0)
  phase={k:z['H1_phase_'+k] for k in ('ready','attempt','positive_vz','launched','landed','recovered','stable_ticks','air_ticks','land_ticks','recover_ticks','progress_peak','progress_paid')}
  counts={k:int((a&valid).any(0).sum()) for k,a in phase.items() if a.dtype.kind=='b'}
  maxima={k:[float(np.min(a[valid])),float(np.median(np.where(valid,a,0).max(0))),float(np.max(a[valid]))] for k,a in phase.items() if a.dtype.kind!='b'}
  wheelN=z['substep_H1_wheel_norm_N'];clear=z['substep_H1_wheel_clearance'];allmin=z['substep_H1_all34_clearance'].min(-1);nonwheel=z['substep_H1_nonwheel_max'];root=z['substep_H1_root13']
  factors={'both_wheel_force_at_most1N':(wheelN<=1).all(-1),'both_wheel_clearance_above5mm':(clear>.005).all(-1),'all_shapes_above_plane':allmin>0,'nonwheel_force_at_most1N':nonwheel<=1,'upward_root_vz_above05':root[...,9]>.05}
  summary={k:dict(request_valid_substep_count=int((a&physical_request).sum()),environments_ever_in_request=int((a&physical_request).any(0).sum())) for k,a in factors.items()}
  simultaneous=np.logical_and.reduce(list(factors.values()));runs=np.zeros(N,int);maxruns=np.zeros(N,int)
  for a,v in zip(simultaneous,physical_request):runs=np.where(a&v,runs+1,0);maxruns=np.maximum(maxruns,runs)
  summary['simultaneous_instantaneous_factors_without_phase_memory']=dict(max_consecutive_min_median_max=maxruns.tolist(),not_original_phase_air_ticks=True)
  events={k:int((z['substep_H1_'+k].reshape(S,4,N).any(1)&valid).any(0).sum()) for k in ('takeoff','landing','recovery')}
  initial_ready=int(phase['ready'][99].sum()) if S>99 and valid[99].all() else None
 out=dict(epoch=time.time(),source_label=label,collection=str(Path(sys.argv[2]).resolve()),raw_actual_path=str(p),raw_SHA=hashlib.sha256(p.read_bytes()).hexdigest(),steps=S,num_envs=N,valid_first_episode_controls=valid.sum(0).tolist(),request_valid_controls=request.sum(0).tolist(),original_phase_environments_ever=counts,phase_value_min_perenvmaxmedian_globalmax=maxima,ready_at_last_normal_control_before_first_mode4=initial_ready,original_source_event_before_first_failure_environment_counts=events,request_window_saved_physical_factors=summary,all_original_thresholds_and_failed_control_exclusion_unchanged=True,original_air_ticks_include_phase_memory_not_replaced_by_instantaneous_factor_diagnostic=True,not_causal_proof_reward_change_or_new_skill_PASS=True,no_GPU_optimizer_or_RNG=True)
 with (R/('H1_'+label+'_FULL1500_ORIGINAL_VALID_PREFIX_PHASE_FACTORS_CPU_ACTUAL.json')).open('x',encoding='utf8') as f:json.dump(out,f,indent=2)
 print(json.dumps(dict(source=label,phase_ever=counts,ready_before_first_mode4=initial_ready,events=events,phase_maxima=maxima)),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('H1_FROZEN_PHASE_FACTOR_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),no_GPU=True),f,indent=2)
  raise
