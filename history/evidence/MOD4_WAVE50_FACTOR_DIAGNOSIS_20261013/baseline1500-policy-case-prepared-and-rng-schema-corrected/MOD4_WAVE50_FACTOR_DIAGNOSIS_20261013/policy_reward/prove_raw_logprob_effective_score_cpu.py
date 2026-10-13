"""Original Gaussian logprob and detached-advantage toy fixture, not real reward."""
from pathlib import Path
import hashlib,json,time
import numpy as np
import torch
from scipy.special import ndtr
from rsl_rl.modules.distribution import GaussianDistribution
import left_head_exploration_migration_cpu_v1 as migration
D=Path(__file__).resolve().parent;W=D.parents[1]
B=W/'MOD4_WAVE50_FACTOR_DIAGNOSIS_20261013/geometry_pose/attempts/geometry_bodypos_worldpos_120_v1/output'
source=W/'MOD4_LOCAL_WAVE50_CONTINUE_20261013/attempts/same128_continue_second7200_v1/output/model_32396.pt'
candidate=D/'LEFT_HEAD_RECENTER_CPU_PREPARED_FULLSTATE.pt'
old=torch.load(source,map_location='cpu',weights_only=False);new=torch.load(candidate,map_location='cpu',weights_only=False)
rng=torch.get_rng_state().clone();receipt=json.loads((B/'COMPLETE_ACTUAL.json').read_bytes())
with np.load(receipt['raw']['path'],allow_pickle=False) as z:
 mu=torch.tensor(z['action'][:,z['group_ids']!=2].reshape(-1,6).copy(),dtype=torch.float64)
nu=mu.clone();nu[:,0]=mu[:,1]+migration.LOWER/migration.SCALE
sig=old['actor_state_dict']['distribution.std_param'].double();nsig=new['actor_state_dict']['distribution.std_param'].double()
lo=mu[:,1].numpy()+migration.LOWER/migration.SCALE;hi=mu[:,1].numpy()+migration.UPPER/migration.SCALE
prob=ndtr((hi-mu[:,0].numpy())/float(sig[0]))-ndtr((lo-mu[:,0].numpy())/float(sig[0]))
quant=torch.tensor([-2.326347874,-1.281551566,-.67448975,0.,.67448975,1.281551566,2.326347874],dtype=torch.float64)
def one(m,s):
 # Mean and std are independent scalar distribution parameters in this toy.
 mean=m[::31].clone().requires_grad_();N=len(mean);K=len(quant)
 distribution=GaussianDistribution(6,std_type='scalar').double()
 with torch.no_grad():distribution.std_param.copy_(s)
 distribution.update(mean.repeat_interleave(K,0))
 raw=mean.detach()[:,None].repeat(1,K,1);raw[:,:,0]+=s[0]*quant[None]
 raw=raw.reshape(-1,6);processed=raw.clamp(-6,6)
 logp=distribution.log_prob(raw);clipped_logp=distribution.log_prob(processed)
 physical=((processed[:,0]-processed[:,1])*.5).clamp(migration.LOWER,migration.UPPER).reshape(N,K)
 # Stand-in advantage has only effective left-target variation. It is deliberately
 # detached like rollout rewards: no gradient through Isaac or physical target.
 centered=physical-physical.mean(1,keepdim=True)
 spread=centered.square().mean(1,keepdim=True).sqrt()
 adv=torch.where(spread>1e-12,centered/spread.clamp_min(1e-12),torch.zeros_like(centered)).detach()
 loss=-(logp.reshape(N,K)*adv).mean();loss.backward()
 return dict(raw_logprob_vs_clipped_max_difference=float((logp-clipped_logp).abs().max()),
    all_raw_logprobs_finite=bool(torch.isfinite(logp).all()),
    left_target_fixture_span_max_rad=float((physical.max(1).values-physical.min(1).values).max()),
    detached_target_based_toy_advantage_nonzero_fraction=float((adv.abs()>0).double().mean()),
    toy_score_gradient_mean0_abs_sum=float(mean.grad[:,0].abs().sum()),
    actual_environment_reward_or_PPO_update=False)
base=one(mu,sig);repair=one(nu,nsig)
assert base['toy_score_gradient_mean0_abs_sum']==0 and repair['toy_score_gradient_mean0_abs_sum']>0
assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
p=D/'RAW_LOGPROB_EFFECTIVE_SCORE_CPU_ACTUAL_PROOF.json';assert not p.exists()
report=dict(epoch=time.time(),passed=True,CPU_only=True,
 input_source_SHA=hashlib.sha256(source.read_bytes()).hexdigest(),candidate_SHA=hashlib.sha256(candidate.read_bytes()).hexdigest(),baseline_raw=receipt['raw'],
 original_GaussianDistribution_log_prob_method_executed=True,
 baseline_fixture=base,candidate_fixture=repair,
 source_effective_probability_double_precision=dict(mean=float(prob.mean()),min=float(prob.min()),max=float(prob.max()),expected_per3072=float(prob.mean()*3072)),
 interpretation='Raw logprob remains mathematically valid under downstream clipping. Saturation removes effective left-target variation in this fixed central-quantile fixture; restoring variation can produce a score gradient when a target-dependent advantage exists.',
 toy_advantage_is_not_saved_real_reward_or_success_evidence=True,
 earlier_0_to22_pathwise_gradient_not_actual_PPO_gradient=True,
 no_GPU_no_PPO_no_production_state_change=True,no_global_CPU_RNG_change=True)
p.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(dict(report=str(p),base=base,repair=repair,source_probability=report['source_effective_probability_double_precision'])))
