"""Functional value-equivalent shadow for a diagnostic derivative, no SDK edit."""
from pathlib import Path
import json,time,torch,numpy as np,traceback
from scipy.special import ndtri
import left_head_offset_aware_migration_v3 as repair
import windows20k_fullstate_binding as binding
D=Path(__file__).parent
def functional_guard(action,offsets):
 p=action[:,:4].clamp(-6,6)*repair.SCALE+offsets
 left=torch.minimum(torch.maximum(p[:,0],p[:,1]+repair.LOWER),p[:,1]+repair.UPPER)
 right=torch.minimum(torch.maximum(p[:,2],p[:,3]+repair.LOWER),p[:,3]+repair.UPPER)
 return torch.stack((left,p[:,1],right,p[:,3]),1)
def main():
 rng=torch.get_rng_state().clone();q=(np.arange(3072)+.5)/3072.;normal=torch.tensor(ndtri(q),dtype=torch.float64);hip=torch.full((3072,),1.7,dtype=torch.float64);zero=torch.zeros(3072,4,dtype=torch.float64);results=[]
 for name,mean,std in [('source_saturated',-109.2078,23.656826),('offset_aware_candidate',1.7+repair.LOWER/.5,.0544)]:
  mu=torch.tensor(mean,dtype=torch.float64,requires_grad=True);request=mu+normal*std
  action=torch.stack((request,hip,torch.zeros_like(hip),hip,torch.zeros_like(hip),torch.zeros_like(hip)),1)
  absolute=functional_guard(action,zero);assert torch.equal(absolute.detach(),repair.guarded_targets(action.detach(),zero))
  target=absolute[:,0]-hip*.5;pathwise=torch.autograd.grad(target.sum(),mu,retain_graph=True)[0]
  advantage=(target.detach()-repair.LOWER);logprob=torch.distributions.Normal(mu,std).log_prob(request.detach());score=torch.autograd.grad((logprob*advantage).mean(),mu)[0]
  results.append(dict(name=name,mean=mean,std=std,lower_target_fraction=float((target<=repair.LOWER+1e-12).double().mean()),effective_inner_target_samples=int(((target>repair.LOWER+1e-12)&(target<repair.UPPER-1e-12)).sum()),pathwise_target_mean_gradient_sum=float(pathwise),synthetic_detached_advantage_score_mean_gradient=float(score)))
 assert results[0]['effective_inner_target_samples']==0 and results[0]['pathwise_target_mean_gradient_sum']==0 and results[0]['synthetic_detached_advantage_score_mean_gradient']==0
 assert results[1]['effective_inner_target_samples']>0 and results[1]['pathwise_target_mean_gradient_sum']>0 and results[1]['synthetic_detached_advantage_score_mean_gradient']>0
 assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
 p=D/'reports/OFFSET_AWARE_V3_EFFECTIVE_GRADIENT_FUNCTIONAL_CPU_V2_ACTUAL.json';assert not p.exists();p.write_text(json.dumps(dict(epoch=time.time(),passed=True,results=results,actual_offset_fixture=[0,0,0,0],fixed_quantiles_no_RNG_draw=True,functional_shadow_guard_values_exact_to_original_inplace_guard=True,original_inplace_guard_autograd_failure_retained_not_production_failure=True,pathwise_diagnostic_not_Isaac_differentiability_or_PPO_backprop=True,score_estimator_uses_detached_samples_and_synthetic_target_advantage_not_real_reward=True,no_GPU_or_PPO_or_learning_success_claim=True),indent=2),encoding='utf8');print(json.dumps(dict(report=str(p),results=results)))
if __name__=='__main__':
 try:main()
 except BaseException:
  p=D/'reports'/('EFFECTIVE_GRADIENT_V2_ORIGINAL_CPU_ERROR_'+str(time.time_ns())+'.json');p.write_text(json.dumps(dict(epoch=time.time(),error=traceback.format_exc(),no_GPU=True),indent=2));raise
