from pathlib import Path
import copy,hashlib,json,time,traceback
import numpy as np
import torch
from tensordict import TensorDict
from rsl_rl.models import MLPModel
from scipy.special import ndtr
import windows20k_fullstate_binding as binding
import left_head_offset_aware_migration_v3 as migration
D=Path(__file__).parent;W=D.parents[1]
SOURCE=W/'MOD4_E1_WAVE50_EPISODE_LIFETIME_REPAIR_20261012/shutdown_backup_1791808183793797400/training/learning_logs/2026-10-12_19-47-02_e1_WAVE50_episode_lifetime_observation_1791805426881441339/model_32264.pt'
BASE=W/'MOD4_WAVE50_FACTOR_DIAGNOSIS_20261013/geometry_pose/attempts/geometry_bodypos_worldpos_1500_v1/output/route_raw.npz'
FACTOR=W/'MOD4_WAVE50_FACTOR_DIAGNOSIS_20261013/geometry_pose/attempts/policy_leftrequested_factor_1500_v2_absolute_paths/output/route_raw.npz'
def index(p):return dict(path=str(p),bytes=p.stat().st_size,sha256=binding.H(p))
def write(name,value):
 q=D/'reports'/name;assert not q.exists();q.parent.mkdir(exist_ok=True);q.write_text(json.dumps(value,indent=2),encoding='utf8');return q
def actor(c,obs):
 with torch.random.fork_rng(devices=[]):
  a=MLPModel(obs,dict(actor=['policy'],critic=['critic']),'actor',6,[256,128,64],'elu',distribution_cfg=dict(class_name='rsl_rl.modules.distribution:GaussianDistribution',init_std=1.,std_type='scalar'));a.load_state_dict(c['actor_state_dict'],strict=True)
 return a
def main():
 torch.set_num_threads(1);rng=torch.get_rng_state().clone()
 assert binding.H(SOURCE)==binding.DONOR_SHA
 with np.load(BASE) as z:
  a=z['processed_action'].copy();t=z['guarded_leg_targets'].copy();feedback=z['policy_obs'][:,z['group_ids']!=2].reshape(-1,35).copy()
 hip=t[:,:,[1,3]]-.5*a[:,:,[1,3]];assert np.array_equal(hip,np.zeros_like(hip))
 diff=t[:,:,2]-t[:,:,3];inner=(diff>migration.LOWER+1e-5)&(diff<migration.UPPER-1e-5)
 right=(t[:,:,2]-.5*a[:,:,2])[inner];assert len(right)>0 and np.array_equal(right,np.zeros_like(right))
 with np.load(FACTOR) as z:
  raw=z['action'].copy();f=z['factor_action'].copy();pa=z['processed_action'].copy();targets=z['guarded_leg_targets'].copy()
 clipped=raw.clip(-6,6);mask=np.abs(f[:,:,0])<6-1e-5
 inferred=.5*clipped[:,:,1]+(.5*(clipped[:,:,2]-clipped[:,:,3])).clip(migration.LOWER,migration.UPPER)-.5*f[:,:,0]
 left=inferred[mask];assert len(left)>0 and np.max(np.abs(left))<=1e-6
 # Cross-check the complete actual guarded targets at process_actions phase.
 offset=torch.zeros((targets.shape[1],4),dtype=torch.float32)
 reproduced=migration.guarded_targets(torch.from_numpy(pa),offset).numpy()
 rawerror=float(np.max(np.abs(reproduced-targets)));assert rawerror<=1e-6
 old=torch.load(SOURCE,map_location='cpu',weights_only=False)
 new=migration.migrate_tree(old,source_sha=binding.DONOR_SHA,actual_offsets=torch.zeros(20000,4))
 obs=TensorDict(dict(policy=torch.from_numpy(feedback),critic=torch.zeros(len(feedback),38)),batch_size=[len(feedback)])
 with torch.inference_mode():mu=actor(old,obs)(obs);nu=actor(new,obs)(obs)
 assert torch.equal(mu[:,1:],nu[:,1:])
 zero=torch.zeros((len(feedback),4));oldtarget=migration.guarded_targets(mu,zero);newtarget=migration.guarded_targets(nu,zero)
 error=float((oldtarget-newtarget).abs().max());assert error<=1e-6
 std=old['actor_state_dict']['distribution.std_param'].double().numpy();ns=new['actor_state_dict']['distribution.std_param'].double().numpy()
 low=(mu[:,1].double().numpy()+migration.LOWER/.5).clip(-6,6);high=(mu[:,1].double().numpy()+migration.UPPER/.5).clip(-6,6)
 probability=lambda mean,s:ndtr((high-mean)/s)-ndtr((low-mean)/s)
 oldp=probability(mu[:,0].double().numpy(),std[0]);newp=probability(nu[:,0].double().numpy(),ns[0])
 path=D/'WINDOWS4090_D05C20K_OFFSET_AWARE_V3_CPU_CANDIDATE_FULLSTATE.pt';assert not path.exists();torch.save(new,path)
 assert binding.same(new,torch.load(path,map_location='cpu',weights_only=False)) and binding.floating_count(new)==107
 negatives=[]
 fixtures=[('wrong_expert',lambda c:c.__setitem__('independent_terrain_expert','E0')),('wrong_geometry',lambda c:c['E1_terrain_state'].__setitem__('geometry_triangles_sha256','0'*64)),('wrong_assignment',lambda c:c['E1_terrain_state'].__setitem__('entry_assignment_sha256','0'*64)),('wrong_initial_source',lambda c:c.__setitem__('E1_WAVE50_initial_source_sha256','0'*64)),('wrong_n',lambda c:c['E1_terrain_state'].__setitem__('num_envs',128)),('wrong_Adam_shape',lambda c:c['optimizer_state_dict']['state'][7].__setitem__('exp_avg',torch.zeros(5,64))),('bad_std',lambda c:c['actor_state_dict']['distribution.std_param'].__setitem__(2,0)),('local_projection_splice',lambda c:c.__setitem__('LOCAL_TEMPORARY_BRANCH',{}))]
 for name,fn in fixtures:
  bad=copy.deepcopy(old);fn(bad)
  try:migration.migrate_tree(bad,source_sha=binding.DONOR_SHA,actual_offsets=torch.zeros(20000,4))
  except (AssertionError,KeyError) as e:negatives.append(dict(name=name,rejected=True,error=str(e)))
  else:raise AssertionError('negative accepted '+name)
 bad_offset=torch.zeros(20000,4);bad_offset[17,0]=1.
 try:migration.migrate_tree(old,source_sha=binding.DONOR_SHA,actual_offsets=bad_offset)
 except AssertionError as e:negatives.append(dict(name='nonuniform_actual_API_offset',rejected=True,error=str(e)))
 else:raise AssertionError('nonuniform offsets accepted')
 assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
 report=dict(epoch=time.time(),passed_CPU_component=True,inputs=[index(SOURCE),index(BASE),index(FACTOR)],offset_evidence=dict(hip_offsets_exact=[0,0],right_crank_identifiable_samples=len(right),right_offset_exact=0.,left_factor_inverse_samples=len(left),left_inferred_min=float(left.min()),left_inferred_max=float(left.max()),left_inverse_float32_tolerance_rad=1e-6,leg_offsets_fixture=[0.,0.,0.,0.],guarded_target_reproduction_error_rad=rawerror,process_actions_phase='guarded_leg_targets are current processed targets restored after D4 physical apply; not delayed applied target',no_direct_API_offset_or_default_q_capture_claim=True,new20k_GPU_must_directly_verify_all_actual_offsets_and_default_q=True),candidate=index(path),source_original_unchanged=binding.H(SOURCE)==binding.DONOR_SHA,full107_and99perenv_tensors_exact_except_declared_actor_Adam_rows=True,conditional_probability_given_actual_mean_hip=dict(original_mean=float(oldp.mean()),candidate_mean=float(newp.mean()),not_full_stochastic_hip_joint_probability=True),actual_captured_domain_deterministic_guarded_target_max_error_rad=error,negative_fixtures=negatives,no_RNG_draw_or_GPU_or_PPO=True,old_v1_v2_offset_omitting_evidence_retained_and_not_deployed=True,formula='bias0=bias1+(diff_min+offsetHip-offsetCrank)/scale',actual_Windows4090_fullrestore_API_probe_PPO_pending=True,no_repair_success_or_unique_cause_or_qualification_claim=True)
 q=write('OFFSET_AWARE_V3_FULL20K_CPU_ACTUAL_REVIEW.json',report);print(json.dumps(dict(report=str(q),candidate=index(path),offset_evidence=report['offset_evidence'],prob=report['conditional_probability_given_actual_mean_hip'],negatives=len(negatives))))
if __name__=='__main__':
 try:main()
 except BaseException:
  write('OFFSET_AWARE_V3_ORIGINAL_CPU_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_GPU=True));raise
