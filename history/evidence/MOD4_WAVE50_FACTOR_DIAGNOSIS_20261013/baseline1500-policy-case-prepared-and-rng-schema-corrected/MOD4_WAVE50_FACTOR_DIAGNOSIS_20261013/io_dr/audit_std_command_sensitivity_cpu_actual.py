"""Actual checkpoint+observedactor-input CPU counterfactual. No physics/PPO/GPU."""
from pathlib import Path
import hashlib,json,time,traceback
import numpy as np
import torch
from scipy.special import ndtr
D=Path(__file__).resolve().parent;W=D.parents[1]
P=W/'MOD4_LOCAL_WAVE50_CONTINUE_20261013/attempts/same128_continue_second7200_v1/output/model_32396.pt'
B=W/'MOD4_WAVE50_FACTOR_DIAGNOSIS_20261013/geometry_pose/attempts/geometry_bodypos_worldpos_120_v1/output'
DIST=Path('C:/Users/lulu/miniconda3/envs/env_isaaclab/Lib/site-packages/rsl_rl/modules/distribution.py')
torch.set_num_threads(1)
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def meta(p):return dict(path=str(p),bytes=p.stat().st_size,sha256=H(p))
def stats(a):return dict(mean=float(a.mean()),std=float(a.std()),min=float(a.min()),max=float(a.max()))
def forward(x,a):
 for layer in (0,2,4,6):
  x=torch.nn.functional.linear(x,a['mlp.'+str(layer)+'.weight'],a['mlp.'+str(layer)+'.bias'])
  if layer!=6:x=torch.nn.functional.elu(x)
 return x
def main():
 assert H(P)=='91d428f02d27cdc6c876e30f355e1dcab6c7398042c2f240a1f177e5b3a898f4'
 complete=json.loads((B/'COMPLETE_ACTUAL.json').read_bytes());rp=Path(complete['raw']['path'])
 assert H(rp)==complete['raw']['sha256']
 c=torch.load(P,map_location='cpu',weights_only=False);a=c['actor_state_dict'];std=a['distribution.std_param'].numpy().astype(float)
 assert std.shape==(6,) and bool((std>0).all())
 assert 'log_std_param' not in a
 source_distribution=DIST.read_text(encoding='utf-8')
 assert 'std = self.std_param.expand_as(mean)' in source_distribution
 with np.load(rp) as raw:
  x=torch.from_numpy(raw['policy_obs'].copy()).reshape(-1,35);recorded=raw['action'].reshape(-1,6);processed=raw['processed_action'].reshape(-1,6)
  assert torch.isfinite(x).all()
  mu=forward(x,a).detach().numpy();err=np.abs(mu-recorded)
  # Forward counterfactual changes only command_vx; no interpretation as new physicalepisode.
  outputs={}
  for vx in (-.3,0.,.3):
   y=x.clone();y[:,0]=vx
   assert torch.equal(y[:,1:],x[:,1:])
   outputs[str(vx)]=forward(y,a).detach().numpy()
  per=[]
  for j in range(6):
   m=mu[:,j].astype(float);s=std[j]
   below=ndtr((-6-m)/s);above=ndtr((m-6)/s);inside=1-below-above
   per.append(dict(action=j,role=['left_crank','left_hip','right_crank','right_hip','left_wheel','right_wheel'][j],scalar_std=s,
    recorded_deterministic_mean=stats(m),raw_mean_clip6_fraction=float((np.abs(m)>=6).mean()),
    Gaussian_training_clip6_probability_mean=float((below+above).mean()),Gaussian_training_inside_clip_probability=stats(inside),
    Gaussian_training_below_negative_clip_probability_mean=float(below.mean()),Gaussian_training_above_positive_clip_probability_mean=float(above.mean()),
    CPU_vs_actual_GPU_recorded_mean_max_abs_error=float(err[:,j].max()),
    command_minus_to_plus_raw_difference=stats(outputs['0.3'][:,j]-outputs['-0.3'][:,j]),
    command_minus_to_plus_clip6_difference=stats(np.clip(outputs['0.3'][:,j],-6,6)-np.clip(outputs['-0.3'][:,j],-6,6)),
    counterfactual_raw_means={k:stats(v[:,j]) for k,v in outputs.items()},
    baseline_recorded_processed_targets=stats(processed[:,j])))
  cmd_jac=[]
  for col in range(3):
   lo=x.clone();hi=x.clone();lo[:,col]-=.001;hi[:,col]+=.001
   diff=((forward(hi,a)-forward(lo,a))/.002).detach().numpy()
   cmd_jac.append(dict(command_column=col,action_derivative_mean=diff.mean(0).tolist(),action_derivative_absmean=np.abs(diff).mean(0).tolist()))
  ancestors=[]
  for p in [W/'MOD4_E1_WAVE50_EPISODE_LIFETIME_REPAIR_20261012/shutdown_backup_1791808183793797400/training/learning_logs/2026-10-12_19-47-02_e1_WAVE50_episode_lifetime_observation_1791805426881441339/model_32264.pt',W/'MOD4_LOCAL_WAVE50_TEMP_TRAIN_20261013/attempts/temporary_train128_v10_sameidentity_saved_source/output/model_32305.pt']:
   src=torch.load(p,map_location='cpu',weights_only=False);ancestors.append(dict(checkpoint=meta(p),std_param=src['actor_state_dict']['distribution.std_param'].tolist()))
  o=dict(id='own32396_Gaussian_std_command_response_CPU_actual',epoch=time.time(),no_GPU_PPO_physics=True,
   source_checkpoint=meta(P),observed_baseline=meta(B/'COMPLETE_ACTUAL.json'),raw=meta(rp),installed_distribution_source=meta(DIST),
   std_is_direct_scalar_not_log=True,deterministic_GPU_action_is_MLP_mean_not_Gaussian_sample=True,
   actual_observed_rows=len(x),CPU_GPU_deterministic_mean_max_abs_error=float(err.max()),
   CPU_vs_GPU_float32_arithmetic_difference_reported_not_production_tolerance_changed=True,
   actions=per,command_local_finite_difference_001=cmd_jac,ancestor_std_actual=ancestors,
   counterfactual_only_commandvx_changed_on_actual_forward_observations=True,
   counterfactual_action_not_a_physical_reverse_route_result=True,
   conclusions=['Action0(leftcrank) mean is far beyond negativeclip6; its raw response to command may be nonzero while clip6 effective response is zero.','The large action0 scalar std was already present in original d05c; it is not newly introduced by Windowsadapter.','D3/D2 feedback ablations can measure residual tracking sensitivity but cannot restore gradient through a permanently saturated action dimension.','Prefer physical same-initial-state signbaseline and bounded-action/CADeffective-target diagnostic over treating DRlatency as proven rootcause.'],
   prior_exploratory_reader_error_preserved=dict(error="KeyError: 'name'",reason='COMPLETE_ACTUAL.raw schema is path not name',prewrite_no_GPU=True))
  p=D/'OWN32396_STD_COMMAND_CPU_ACTUAL_REVIEW.json';assert not p.exists();p.write_text(json.dumps(o,ensure_ascii=False,indent=2),encoding='utf-8')
  print(json.dumps(dict(report=str(p),max_actual_mean_error=float(err.max()),actions=[{k:r[k] for k in ['action','role','scalar_std','recorded_deterministic_mean','raw_mean_clip6_fraction','Gaussian_training_clip6_probability_mean','command_minus_to_plus_raw_difference','command_minus_to_plus_clip6_difference']} for r in per]),ensure_ascii=False,indent=2))
if __name__=='__main__':
 try:main()
 except BaseException:
  p=D/('STD_COMMAND_CPU_ERROR_'+str(time.time_ns())+'.json');p.write_text(json.dumps(dict(epoch=time.time(),error=traceback.format_exc(),source=meta(Path(__file__)),preGPU=True),indent=2),encoding='utf-8');raise
