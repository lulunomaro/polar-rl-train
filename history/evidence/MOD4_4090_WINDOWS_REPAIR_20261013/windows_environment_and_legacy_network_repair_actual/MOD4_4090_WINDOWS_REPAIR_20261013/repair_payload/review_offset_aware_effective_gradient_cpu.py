"""Deterministic no-RNG synthetic derivative evidence, not realPPO efficacy."""
from pathlib import Path
import json,time,torch,numpy as np
from scipy.special import ndtri
import left_head_offset_aware_migration_v3 as repair
import windows20k_fullstate_binding as binding
D=Path(__file__).parent
q=(np.arange(3072)+.5)/3072.;normal=torch.tensor(ndtri(q),dtype=torch.float64)
hip=torch.full((3072,),1.7,dtype=torch.float64);zero=torch.zeros(3072,4,dtype=torch.float64)
results=[]
for name,mean,std in [('source_saturated',-109.2078,23.656826),('offset_aware_candidate',1.7+repair.LOWER/.5,.0544)]:
 mu=torch.tensor(mean,dtype=torch.float64,requires_grad=True);request=mu+normal*std
 action=torch.zeros(3072,6,dtype=torch.float64);action[:,0]=request;action[:,1]=hip
 target=repair.guarded_targets(action,zero)[:,0]-hip*.5
 pathwise=torch.autograd.grad(target.sum(),mu,retain_graph=True)[0]
 advantage=(target.detach()-repair.LOWER)
 logprob=torch.distributions.Normal(mu,std).log_prob(request.detach())
 score=torch.autograd.grad((logprob*advantage).mean(),mu)[0]
 results.append(dict(name=name,mean=mean,std=std,lower_target_fraction=float((target<=repair.LOWER+1e-12).double().mean()),effective_inner_target_samples=int(((target>repair.LOWER+1e-12)&(target<repair.UPPER-1e-12)).sum()),pathwise_target_mean_gradient_sum=float(pathwise),synthetic_detached_advantage_score_mean_gradient=float(score)))
assert results[0]['effective_inner_target_samples']==0 and results[0]['pathwise_target_mean_gradient_sum']==0 and results[0]['synthetic_detached_advantage_score_mean_gradient']==0
assert results[1]['effective_inner_target_samples']>0 and results[1]['pathwise_target_mean_gradient_sum']>0 and results[1]['synthetic_detached_advantage_score_mean_gradient']>0
assert not torch.cuda.is_initialized()
p=D/'reports/OFFSET_AWARE_V3_EFFECTIVE_GRADIENT_SYNTHETIC_CPU_ACTUAL.json';assert not p.exists();p.write_text(json.dumps(dict(epoch=time.time(),passed=True,results=results,actual_offset_fixture=[0,0,0,0],fixed_quantiles_no_RNG_draw=True,pathwise_diagnostic_not_Isaac_differentiability_or_PPO_backprop=True,score_estimator_uses_detached_samples_and_synthetic_target_advantage_not_real_reward=True,no_GPU_or_PPO_or_learning_success_claim=True),indent=2),encoding='utf8');print(json.dumps(dict(report=str(p),results=results)))
