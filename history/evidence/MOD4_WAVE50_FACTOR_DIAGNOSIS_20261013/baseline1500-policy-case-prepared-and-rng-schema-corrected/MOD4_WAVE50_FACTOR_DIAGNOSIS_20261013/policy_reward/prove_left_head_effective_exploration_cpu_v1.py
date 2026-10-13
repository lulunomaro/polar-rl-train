"""No-RNG deterministic CPU probability, policy-gradient and full-state proof."""
from pathlib import Path
import copy,hashlib,inspect,json,math,time,traceback
import numpy as np
import torch
from tensordict import TensorDict
from rsl_rl.models import MLPModel
from rsl_rl.algorithms import PPO
from rsl_rl.modules.distribution import GaussianDistribution
from scipy.special import ndtr
import left_head_exploration_migration_cpu_v1 as migration
D=Path(__file__).resolve().parent;W=D.parents[1]
SOURCE=W/'MOD4_LOCAL_WAVE50_CONTINUE_20261013/attempts/same128_continue_second7200_v1/output/model_32396.pt'
BASE=W/'MOD4_WAVE50_FACTOR_DIAGNOSIS_20261013/geometry_pose/attempts/geometry_bodypos_worldpos_120_v1/output'
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def index(p):return dict(path=str(p),bytes=Path(p).stat().st_size,sha256=H(p))
def write(name,v):
 p=D/name;assert not p.exists();p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8');return p
def model(ck,obs):
 # Constructor consumes only a forked CPU RNG whose complete original state restores.
 with torch.random.fork_rng(devices=[]):
  m=MLPModel(obs,dict(actor=['policy'],critic=['critic']),'actor',6,[256,128,64],'elu',
       distribution_cfg=dict(class_name='rsl_rl.modules.distribution:GaussianDistribution',init_std=1.,std_type='scalar'))
  m.load_state_dict(ck['actor_state_dict'],strict=True)
 return m
def target(mean,hip):
 return (mean.clamp(-6,6)*migration.SCALE-hip.clamp(-6,6)*migration.SCALE).clamp(migration.LOWER,migration.UPPER)
def main():
 torch.set_num_threads(1);rng=torch.get_rng_state().clone();new,old=migration.migrate(SOURCE)
 receipt=json.loads((BASE/'COMPLETE_ACTUAL.json').read_bytes());assert receipt['checkpoint_sha256']==migration.APPROVED_SOURCE_SHA
 assert H(receipt['raw']['path'])==receipt['raw']['sha256']
 with np.load(receipt['raw']['path'],allow_pickle=False) as z:
  moving=z['group_ids']!=2;feedback=z['policy_obs'][:,moving].reshape(-1,35).copy();recorded=z['action'][:,moving].reshape(-1,6).copy()
 ob=torch.tensor(feedback);obs=TensorDict(dict(policy=ob,critic=torch.zeros(len(ob),38)),batch_size=[len(ob)])
 base=model(old,obs);candidate=model(new,obs)
 with torch.inference_mode():mu=base(obs);nu=candidate(obs)
 assert torch.equal(mu[:,1:],nu[:,1:]),'Other five deterministic actions must be CPU byteexact'
 cpu_vs_saved_error=float((mu-torch.tensor(recorded)).abs().max())
 # CPU vs GPU ELU implementation is numerical replay, not a new physical tolerance.
 assert cpu_vs_saved_error<.001,'Incorrect mean replay or observation mapping'
 oldtarget=target(mu[:,0],mu[:,1]);newtarget=target(nu[:,0],nu[:,1])
 assert float((oldtarget-newtarget).abs().max())<1e-6
 std=old['actor_state_dict']['distribution.std_param'].numpy();nstd=new['actor_state_dict']['distribution.std_param'].numpy()
 lower=mu[:,1].numpy()+migration.LOWER/migration.SCALE
 upper=mu[:,1].numpy()+migration.UPPER/migration.SCALE
 probability_old=ndtr((upper-mu[:,0].numpy())/std[0])-ndtr((lower-mu[:,0].numpy())/std[0])
 probability_new=ndtr((upper-nu[:,0].numpy())/nstd[0])-ndtr((lower-nu[:,0].numpy())/nstd[0])
 assert float(probability_new.min())>.49
 # Fixed quantiles, not stochastic sampling or any CPU/CUDA random draw.
 zscore=torch.tensor([-2.326347874,-1.281551566,-.67448975,0.,.67448975,1.281551566,2.326347874])
 use=ob[::max(1,len(ob)//64)][:64];obs2=TensorDict(dict(policy=use,critic=torch.zeros(len(use),38)),batch_size=[len(use)])
 m0=base(obs2);m1=candidate(obs2)
 # Hold hip mean fixed so this specifically probes the left distribution channel.
 sampled0=m0[:,0,None]+base.distribution.std_param[0]*zscore[None]
 sampled1=m1[:,0,None]+candidate.distribution.std_param[0]*zscore[None]
 effect0=target(sampled0,m0[:,1,None].detach());effect1=target(sampled1,m1[:,1,None].detach())
 loss0=effect0.mean();loss1=effect1.mean();base.zero_grad();candidate.zero_grad();loss0.backward();loss1.backward()
 grad0=float(base.mlp[-1].weight.grad[0].abs().sum());grad1=float(candidate.mlp[-1].weight.grad[0].abs().sum())
 assert grad0==0 and grad1>0,'Fixed exploration target sensitivity must recover in candidate'
 negative=[]
 mutations=[('wrong_expert',lambda c:c.__setitem__('independent_terrain_expert','E0')),
   ('wrong_initial_source',lambda c:c.__setitem__('E1_WAVE50_initial_source_sha256','0'*64)),
   ('wrong_geometry',lambda c:c['E1_terrain_state'].__setitem__('geometry_triangles_sha256','0'*64)),
   ('wrong_assignment',lambda c:c['E1_terrain_state'].__setitem__('entry_assignment_sha256','0'*64)),
   ('wrong_environment_count',lambda c:c['LOCAL_TEMPORARY_BRANCH'].__setitem__('local_num_envs',64)),
   ('wrong_head_shape',lambda c:c['actor_state_dict'].__setitem__('mlp.6.weight',torch.zeros(5,64))),
   ('wrong_optimizer_binding',lambda c:c['optimizer_state_dict']['param_groups'][0].__setitem__('params',list(range(16)))),
   ('invalid_right_std',lambda c:c['actor_state_dict']['distribution.std_param'].__setitem__(2,0.))]
 for name,change in mutations:
  bad=copy.deepcopy(old);change(bad)
  try:migration.validate_source(bad)
  except AssertionError as e:negative.append(dict(fixture=name,rejected=True,original_error=str(e)))
  else:raise AssertionError('Missing negative rejection '+name)
 assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized(),'CPU proof must preserve global RNG and avoid CUDA'
 out=D/'LEFT_HEAD_RECENTER_CPU_PREPARED_FULLSTATE.pt';assert not out.exists();torch.save(new,out)
 roundtrip=torch.load(out,map_location='cpu',weights_only=False);assert migration.same(new,roundtrip)
 assert migration.floating_count(roundtrip)==107
 srcs=[SOURCE,BASE/'COMPLETE_ACTUAL.json',Path(receipt['raw']['path']),Path(migration.__file__),Path(inspect.getfile(MLPModel)),Path(inspect.getfile(GaussianDistribution)),Path(inspect.getfile(PPO))]
 report=dict(epoch=time.time(),passed=True,CPU_only_no_GPU_or_PPO=True,inputs=[index(x) for x in srcs],
   source_std_per_channel=std.tolist(),candidate_std_per_channel=nstd.tolist(),
   saved_current_actor_mean_replay_CPU_max_abs_difference=cpu_vs_saved_error,
   actual_saved_baseline_feedback_samples=len(ob),
   probability_conditioned_on_actual_hip_mean_and_independent_Gaussian_left_request=True,
   legal_inner_difference_request_interval_median=[float(np.median(lower)),float(np.median(upper))],
   source_effective_exploration_probability=dict(mean=float(probability_old.mean()),min=float(probability_old.min()),max=float(probability_old.max()),expected_samples_per3072_envstep_update=float(probability_old.mean()*3072)),
   candidate_effective_exploration_probability=dict(mean=float(probability_new.mean()),min=float(probability_new.min()),max=float(probability_new.max()),expected_samples_per3072_envstep_update=float(probability_new.mean()*3072)),
   source_vs_candidate_initial_deterministic_guarded_left_target_max_difference_rad=float((oldtarget-newtarget).abs().max()),
   other_five_action_means_and_std_byteexact=True,
   effective_target_fixed_quantile_changes=dict(source_max_span_rad=float((effect0.max(1).values-effect0.min(1).values).max()),candidate_min_span_rad=float((effect1.max(1).values-effect1.min(1).values).min()),source_head0_backprop_abs_gradient_sum=grad0,candidate_head0_backprop_abs_gradient_sum=grad1),
   full_state_tree_critic_DR_RNG_terrain_command_exact_except_declared_actor_row_and_Adam_rows=True,
   original_Adam_step_scalars_retained=True,original_actor_and_optimizer_unchanged_on_disk_SHA=H(SOURCE),
   negative_component_fixtures=negative,
   prepared_full_checkpoint=index(out),prepared_floating_schema_exact107=True,CPU_disk_roundtrip_exact=True,
   no_global_CPU_RNG_draw_or_change=True,no_CUDA_context=True,
   PPO_semantics=dict(raw_Gaussian_action_sample_stored_before_wrapper_clip=True,raw_action_log_prob_is_computed_on_raw_action=True,wrapper_clips_later_to6=True,many_to_one_clipped_environment_policy_is_valid_not_a_logprob_bug=True),
   risk='Initialization changes only left distribution and its Adam moments. New stochastic exploration intentionally changes behavior; deterministic target equality is limited to the actually captured prefix domain. CUDA/sourcefullstate admission and physical paired behavior test still required.',
   not_live_left_right_runtime_coupling_or_new_actor_input=True,not_training_deployed_or_qualification=True)
 path=write('LEFT_HEAD_EFFECTIVE_EXPLORATION_CPU_ACTUAL_PROOF.json',report)
 print(json.dumps(dict(report=str(path),candidate=index(out),source_probability=report['source_effective_exploration_probability'],candidate_probability=report['candidate_effective_exploration_probability'],target_difference=report['source_vs_candidate_initial_deterministic_guarded_left_target_max_difference_rad'],gradient=[grad0,grad1],negative=len(negative))))
if __name__=='__main__':
 try:main()
 except BaseException:
  write('LEFT_HEAD_CPU_PROOF_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),CPU_only=True));raise
