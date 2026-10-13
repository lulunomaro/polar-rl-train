"""Compare two complete donors without pretending local128 is a full20k resume."""
from pathlib import Path
import copy,hashlib,json,time,traceback
import numpy as np
import torch
from tensordict import TensorDict
from rsl_rl.models import MLPModel
from scipy.special import ndtr
import left_head_windows4090_migration_cpu_v2 as migration
D=Path(__file__).resolve().parent;W=D.parents[1]
FULL=W/'MOD4_E1_WAVE50_EPISODE_LIFETIME_REPAIR_20261012/shutdown_backup_1791808183793797400/training/learning_logs/2026-10-12_19-47-02_e1_WAVE50_episode_lifetime_observation_1791805426881441339/model_32264.pt'
LOCAL=W/'MOD4_LOCAL_WAVE50_CONTINUE_20261013/attempts/same128_continue_second7200_v1/output/model_32396.pt'
BASE=W/'MOD4_WAVE50_FACTOR_DIAGNOSIS_20261013/geometry_pose/attempts/geometry_bodypos_worldpos_1500_v1/output'
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def index(p):return dict(path=str(p),bytes=Path(p).stat().st_size,sha256=H(p))
def write(name,v):
 p=D/name;assert not p.exists();p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8');return p
def model(ck,obs):
 with torch.random.fork_rng(devices=[]):
  m=MLPModel(obs,dict(actor=['policy'],critic=['critic']),'actor',6,[256,128,64],'elu',distribution_cfg=dict(class_name='rsl_rl.modules.distribution:GaussianDistribution',init_std=1.,std_type='scalar'))
  m.load_state_dict(ck['actor_state_dict'],strict=True)
 return m
def target(x,h):return ((x.clamp(-6,6)-h.clamp(-6,6))*.5).clamp(migration.LOWER,migration.UPPER)
def main():
 torch.set_num_threads(1);rng=torch.get_rng_state().clone();bc=json.loads((BASE/'COMPLETE_ACTUAL.json').read_bytes());assert bc['passed_data_contract'];assert H(bc['raw']['path'])==bc['raw']['sha256']
 with np.load(bc['raw']['path'],allow_pickle=False) as z:
  # Both actor functions receive the same actually captured deployable35 feedback.
  # The full20k donor was not physically evaluated in this local baseline case.
  feedback=z['policy_obs'][:,z['group_ids']!=2].reshape(-1,35).copy()
 obs=TensorDict(dict(policy=torch.tensor(feedback),critic=torch.zeros(len(feedback),38)),batch_size=[len(feedback)])
 records=[];means=[];source_states=[]
 for label,path,n in [('original_d05c_full20k',FULL,20000),('latest_91d_local128',LOCAL,128)]:
  sha=H(path);new,old=migration.migrate_cpu(path,expected_source_sha=sha,expected_num_envs=n)
  baseline=model(old,obs);repaired=model(new,obs)
  with torch.inference_mode():mu=baseline(obs);nu=repaired(obs)
  assert torch.equal(mu[:,1:],nu[:,1:]);difference=float((target(mu[:,0],mu[:,1])-target(nu[:,0],nu[:,1])).abs().max());assert difference<1e-6
  std=old['actor_state_dict']['distribution.std_param'].double().numpy();ns=new['actor_state_dict']['distribution.std_param'].double().numpy()
  lo=mu[:,1].double().numpy()+migration.LOWER/.5;hi=mu[:,1].double().numpy()+migration.UPPER/.5
  probability=ndtr((hi-mu[:,0].double().numpy())/std[0])-ndtr((lo-mu[:,0].double().numpy())/std[0])
  newprob=ndtr((hi-nu[:,0].double().numpy())/ns[0])-ndtr((lo-nu[:,0].double().numpy())/ns[0])
  fname='WINDOWS4090_'+label+'_LEFT_HEAD_CPU_CANDIDATE_FULLSTATE.pt';dest=D/fname;assert not dest.exists();torch.save(new,dest)
  reopened=torch.load(dest,map_location='cpu',weights_only=False);assert migration.same(new,reopened) and migration.floating_count(reopened)==107
  negative=[]
  tests=[('wrong_expert',lambda c:c.__setitem__('independent_terrain_expert','E0')),
    ('wrong_geometry',lambda c:c['E1_terrain_state'].__setitem__('geometry_triangles_sha256','0'*64)),
    ('wrong_assignment',lambda c:c['E1_terrain_state'].__setitem__('entry_assignment_sha256','0'*64)),
    ('wrong_source35_ancestor',lambda c:c.__setitem__('E1_WAVE50_initial_source_sha256','0'*64)),
    ('wrong_fullstate_environment_count',lambda c:c['E1_terrain_state'].__setitem__('num_envs',17)),
    ('wrong_head_shape',lambda c:c['actor_state_dict'].__setitem__('mlp.6.weight',torch.zeros(5,64))),
    ('wrong_Adam_binding',lambda c:c['optimizer_state_dict']['param_groups'][0].__setitem__('params',list(range(16)))),
    ('invalid_right_std',lambda c:c['actor_state_dict']['distribution.std_param'].__setitem__(2,0.))]
  for name,change in tests:
   bad=copy.deepcopy(old);change(bad)
   try:migration.validate_source(bad,sha,n)
   except AssertionError as e:negative.append(dict(fixture=name,rejected=True,original_error=str(e)))
   else:raise AssertionError('Missing strict rejection '+name)
  try:migration.validate_source(old,sha,128 if n==20000 else 20000)
  except AssertionError as e:negative.append(dict(fixture='source_dimension_splice_rejected',rejected=True,original_error=str(e)))
  else:raise AssertionError('Silent environment enlargement/shrink accepted')
  record=dict(label=label,source=index(path),source_num_envs=n,source_iteration=int(old['iter']),
     source_std_per_action=std.tolist(),candidate_std_per_action=ns.tolist(),
     mean_left_actor_raw_action_unitless=float(mu[:,0].mean()),
     left_actor_request_range=[float(mu[:,0].min()),float(mu[:,0].max())],
     original_left_mean_outside_clip6_fraction=float((mu[:,0].abs()>6).float().mean()),
     source_effective_inner_request_probability=dict(mean=float(probability.mean()),min=float(probability.min()),max=float(probability.max()),expected_per3072=float(probability.mean()*3072)),
     candidate_effective_inner_request_probability=dict(mean=float(newprob.mean()),min=float(newprob.min()),max=float(newprob.max())),
     initial_deterministic_guarded_target_domain_max_difference_rad=difference,
     other_five_means_std_and_full_nonrepair_state_tree_exact=True,
     candidate=index(dest),candidate_floating_schema107=True,CPU_disk_roundtrip_exact=True,negative_component_fixtures=negative,
     restore_plan='Load the selected complete source exact including actor/critic/std/optimizer/allDR/globalnamed/dictprivateCPUCUDA/terraincommand/entrydirectionroutelifetime; only after12 actual startup markers and sourceepisode+1 apply the explicit one-channel initializer and save a separate runtime repair marker/CUDA disk roundtrip.',
     same_repaired_scope_resume_must_not_repeat_initialization_or_moment_reset=True,
     actual_Windows4090_probe_CUDA_restore_or_PPO_deployment=False)
  records.append(record);means.append(mu.cpu().numpy());source_states.append(old)
 assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
 a0,a1=source_states
 actor_changed=[k for k in a0['actor_state_dict'] if not torch.equal(a0['actor_state_dict'][k],a1['actor_state_dict'][k])]
 critic_changed=[k for k in a0['critic_state_dict'] if not torch.equal(a0['critic_state_dict'][k],a1['critic_state_dict'][k])]
 plan=dict(epoch=time.time(),passed=True,CPU_only_no_GPU=True,baseline_feedback=index(Path(bc['raw']['path'])),same_captured_deployable35_feedback_only_not_a_cross_engine_physical_comparison=True,
    inputs=[index(FULL),index(LOCAL),index(Path(migration.__file__))],sources=records,
    actual_actor_tensor_keys_different_between_sources=actor_changed,actual_critic_tensor_keys_different_between_sources=critic_changed,
    other5_inference_output_abs_difference_max=np.abs(means[0][:,1:]-means[1][:,1:]).max(0).tolist(),
    source_choice=dict(if_target20000='Prefer original full20k d05c as the coherent complete donor; CPUcandidate derived only from this donor. Explicitly disclose not using newer local128 learning weights.',
       if_target128='Latest91d is a coherent complete128 donor, preserving local learning. Full20k restoration cannot be claimed.',
       illegal_silent_splice='Never combine91d actor/optimizer with d05c20k DR/RNG without a separately approved and explicit multi-source/dimension migration axis.',
       other_experts='Both donors are only this unqualified E1_WAVE50 scope; never default donors for E0/CURB/SLOPE/otherexpert.'),
    proposed_single_axis='Restore effective exploration in independent actor column0 while preserving initial deterministic guarded target in actually captured domain; no live action coupling.',
    source_original_bytesSHA_unchanged=[H(FULL),H(LOCAL)],
    all_sources_candidate107_fulltree_identity_and_declared_Adam_row_step_preservation_checked=True,
    global_CPU_RNG_unchanged=True,
    actual_Windows4090_environment_version_API_resource_scope_admission_pending=True,
    own_CUDA_roundtrip12marker_SOURCEfreeze_PPO_checkpoint_PID_cost_and_physical_review_pending=True,
    no_source_overwrite_otherexpert_default_budgetwrite_or_installedSDKhotpatch=True,
    no_unique_forward_failure_cause_or_repair_success_or_50mm_graduation_claim=True,
    live_left_right_requested_coupling_actual2of7_to0of7_ordinary11_rejected=True)
 path=write('WINDOWS4090_SOURCE_CHOICE_AND_LEFT_HEAD_CPU_ACTUAL_REVIEW.json',plan)
 print(json.dumps(dict(report=str(path),sources=[dict(label=x['label'],n=x['source_num_envs'],std0=x['source_std_per_action'][0],mean0=x['mean_left_actor_raw_action_unitless'],prob=x['source_effective_inner_request_probability']['mean'],candidate=x['candidate'],deterministic_target_difference=x['initial_deterministic_guarded_target_domain_max_difference_rad']) for x in records],actor_changed=len(actor_changed),critic_changed=len(critic_changed))))
if __name__=='__main__':
 try:main()
 except BaseException:
  write('WINDOWS4090_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_GPU=True));raise
