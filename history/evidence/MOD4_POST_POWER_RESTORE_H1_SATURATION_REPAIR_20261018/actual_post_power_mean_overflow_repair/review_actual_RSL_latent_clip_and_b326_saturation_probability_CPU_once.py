"""Actual installed source semantics plus conditional Gaussian calculation; no robot replay."""
from pathlib import Path
import os,json,time,ast,hashlib,traceback,math
os.environ['CUDA_VISIBLE_DEVICES']=''
import numpy as np,torch
B=Path(__file__).resolve().parent;R=B/'reports';W=B.parent;X=W/'MOD4_H1_FROZEN_FE1709_REVIEW_20261018';Z=W/'MOD4_POWER_RESTORED_THREE_HOST_READONLY_CHECK_20261018';H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 torch.set_num_threads(2);rng=torch.get_rng_state().clone();base=Z/'actual_installed_RSL72_sources';dist=base/'rsl_rl/modules/distribution.py';wrapper=base/'isaaclab_rl/rsl_rl/vecenv_wrapper.py';ppo=base/'rsl_rl/algorithms/ppo.py'
 td=ast.parse(dist.read_text('utf8'));g=next(n for n in td.body if isinstance(n,ast.ClassDef) and n.name=='GaussianDistribution');u=next(n for n in g.body if isinstance(n,ast.FunctionDef) and n.name=='update');assert 'self.std_param.expand_as(mean)' in ast.unparse(u) and 'Normal(mean, std)' in ast.unparse(u)
 tw=ast.parse(wrapper.read_text('utf8'));c=next(n for n in tw.body if isinstance(n,ast.ClassDef) and n.name=='RslRlVecEnvWrapper');step=next(n for n in c.body if isinstance(n,ast.FunctionDef) and n.name=='step');assert 'actions = torch.clamp(actions, -self.clip_actions, self.clip_actions)' in ast.unparse(step) and 'clamp_' not in ast.unparse(step)
 text=ppo.read_text('utf8');assert H(ppo)=='a2d35e7ad7b884c80b7434e7d2ce785a6da1e18d93c96f1179fbd3a208669f8c' and 'self.transition.actions = self.actor(obs, stochastic_output=True).detach()' in text and 'self.actor.get_output_log_prob(self.transition.actions)' in text
 ck=torch.load(B/'payload_h1_native/job0/source/H1_final10_protected.pt',map_location='cpu',weights_only=False);sigma=float(ck['actor_state_dict']['distribution.std_param'][0]);assert sigma>0
 collection=json.loads((X/'reports/LINUX_GPU1_B326_FULL1500_COMPLETE_OR_PENDING_BOUND_COLLECTION_ACTUAL.json').read_bytes());row=next(x for x in collection['files'] if x['relative'].endswith('/retention_full_control_substep_actual.npz'));assert row['twohost_complete_SHA']
 with np.load(row['local_path'],allow_pickle=False) as z:mu=torch.from_numpy(z['raw_actor_action'][...,0][z['H1_public_request']].copy()).double()
 assert len(mu)==6400 and bool((mu < -6).all());above=.5*torch.erfc((-6-mu)/(sigma*math.sqrt(2)));above6=.5*torch.erfc((6-mu)/(sigma*math.sqrt(2)));inside=above-above6
 def stats(x):return [float(x.min()),float(x.median()),float(x.max())]
 assert bool((above>0).all()) and bool((above<.01).all()) and torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
 out=dict(epoch=time.time(),actual_installed_readonly_source_SHA={str(p):H(p) for p in (dist,wrapper,ppo)},scalar_STD_parameter_direct_scale_in_current_source=True,wrapper_clip_is_out_of_place_PPO_raw_actions_and_logprob_retained=True,no_inplace_alias_or_incorrect_logprob_bug_claim=True,b326_original_STD0=sigma,saved_frozen_full_public4_control_rows=len(mu),saved_raw_mean0_min_median_max=stats(mu),conditional_probability_sample0_above_minus6_min_median_max=stats(above),conditional_probability_sample0_inside_minus6_plus6_min_median_max=stats(inside),not_actual_past20k_PPO_sampling_counts_or_RNG_or_counterfactual_physics=True,not_proof_of_zero_likelihood_ratio_PPO_gradient=True,auxiliary_loss_candidate_changes_optimization_objective_explicitly_not_environment_reward=True,no_STD_checkpoint_or_rng_optimizer_GPU_budget_change=True,raw_actual_path=row['path'],raw_prior_twohost_SHA=row['SHA'])
 with (R/'ACTUAL_RSL_GAUSSIAN_RAW_CLIP_SOURCE_AND_B326_CONDITIONAL_SATURATION_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(out,f,indent=2)
 print(json.dumps(dict(CPU_source_semantics=True,probability_above_negative6=out['conditional_probability_sample0_above_minus6_min_median_max'],STD0=sigma,no_clipping_logprob_bug_invented=True)),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('LATENT_CLIP_PROBABILITY_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_or_actual_model_change=True),f,indent=2)
  raise
