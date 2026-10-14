"""Single column mathematical response only; no model checkpoint is written."""
from pathlib import Path
import torch,numpy as np,json,inspect,hashlib,time,shutil,traceback
from tensordict import TensorDict
from rsl_rl.models import MLPModel
from rsl_rl.modules import MLP
from rsl_rl.utils import resolve_nn_activation
from rsl_rl.modules.distribution import GaussianDistribution
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports'
def read(p):return json.loads(p.read_bytes())
def ix(p):p=Path(p);return dict(path=str(p),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def main():
 out=R/'FIXED_2B_E3_ACTOR35_COMMAND_YAW_SINGLE_AXIS_ACTUAL_CPU_REVIEW.json';assert not out.exists()
 frozen=W/'MOD4_3060_LEFT_REPAIR_FULL80_20261014/payload/runtime/isaac/mod4/frozen_history_policy.py';text=frozen.read_text(encoding='utf8')
 assert "MLPModel(obs,dict(actor=['policy'],critic=['critic']),'actor',6,[256,128,64],'elu',distribution_cfg=cfg)" in text
 assert '"elu": torch.nn.ELU()' in inspect.getsource(resolve_nn_activation)
 assert isinstance(resolve_nn_activation('elu'),torch.nn.ELU)
 sources={}
 snap=D/'local_CPU_actor_source_snapshot';snap.mkdir(exist_ok=True)
 for obj in (MLPModel,MLP,resolve_nn_activation,GaussianDistribution):
  p=Path(inspect.getsourcefile(obj));q=snap/p.name;assert not q.exists();shutil.copyfile(p,q);sources[obj.__name__]=dict(actual_local_CPU_source=ix(p),retained_source=ix(q))
 sources['frozen_GPU_actor_constructor']=ix(frozen)
 # Local native source is recorded, not called remote SDK binary equivalent.
 review=read(R/'E3_POSITIVE_4PI_ALL_PREFIX_MOTOR_CONTACT_ACTUAL_CPU_REVIEW.json')
 checkpoints={
  'baseline':W/'MOD4_LINUX_FULLSTATE_REPAIR_RESUME_20261013/left_formal_final_actual/0_model_32635.pt',
  'candidate':W/'MOD4_LINUX_LEFT_SECOND_SAMEIDENTITY_CPU_PREPARE_20261014/left_second_ownsave_actual_1791963199228502100/0_model_32825.pt'}
 delivery=W/'MOD4_3060_LEFT_REPAIR_FULL80_20261014/payload/runtime/train/deploy/contract_rm2025_later.json';contract=read(delivery);assert contract['leg_action_scale']==.5 and contract['wheel_action_scale']==10
 models={};states={};rng_before=torch.get_rng_state().clone()
 for name,p in checkpoints.items():
  ck=torch.load(p,map_location='cpu',weights_only=False);state=ck['actor_state_dict'];assert len(state)==9 and ck.get('history_architecture',{}).get('variant','A0')=='A0'
  with torch.random.fork_rng(devices=[]):
   obs=TensorDict(dict(policy=torch.zeros(1,35),critic=torch.zeros(1,38),feedback_history=torch.zeros(1,175)),batch_size=[1])
   actor=MLPModel(obs,dict(actor=['policy'],critic=['critic']),'actor',6,[256,128,64],'elu',distribution_cfg=dict(class_name='rsl_rl.modules.distribution:GaussianDistribution',init_std=1.,std_type='scalar'))
   actor.load_state_dict(state,strict=True)
  actor.eval();actor.requires_grad_(False);assert all(torch.equal(v,state[k]) for k,v in actor.state_dict().items());assert not actor.obs_normalization
  models[name]=actor;states[name]={k:v.clone() for k,v in state.items()}
 assert torch.equal(rng_before,torch.get_rng_state())
 observations=[];source_indexes=[]
 for source in ('baseline','candidate'):
  p=Path(review[source]['raw']['path']);source_indexes.append(ix(p))
  with np.load(p,allow_pickle=False) as z:
   a={k:z[k].copy() for k in ('policy_obs','command','raw_actor_action','guarded_leg_targets','before_q')}
  assert np.array_equal(a['policy_obs'][...,:3],a['command'])
  for i in (51,73,84,62):
   stop=next(v['first_failure_control'] for v in review[source]['positive'] if v['env_id']==i)
   controls=sorted(set(t for t in (0,25,50,75,95,150,298,500,1000,1499) if t<stop))
   for t in controls:
    observations.append(dict(source=source,env_id=i,control=t,first_failure_control=stop,obs=a['policy_obs'][t,i],raw=a['raw_actor_action'][t,i],guard=a['guarded_leg_targets'][t,i],q30=a['before_q'][t,i]))
 tensor=torch.from_numpy(np.stack([x['obs'] for x in observations])).float();original=tensor.clone()
 outputs={}
 with torch.inference_mode():
  for name,actor in models.items():outputs[name]=actor(TensorDict(dict(policy=tensor),batch_size=[len(tensor)]))
 def guarded(clipped):
  leg=clipped[:4]*.5;leg=leg.clone()
  for j in (0,2):leg[j]=torch.minimum(torch.maximum(leg[j],leg[j+1]-1.0843),leg[j+1]+.85)
  return leg
 sameobs_error={};guard_error={}
 for name in models:
  ids=[i for i,x in enumerate(observations) if x['source']==name]
  old=torch.from_numpy(np.stack([observations[i]['raw'] for i in ids]));new=outputs[name][ids]
  sameobs_error[name]=float((new-old).abs().max());assert sameobs_error[name]<5e-4,'CPU float32 math differs materially from original GPU saved raw'
  guard_error[name]=max(float((guarded(torch.from_numpy(observations[i]['raw']).clamp(-6,6))-torch.from_numpy(observations[i]['guard'])).abs().max()) for i in ids)
  assert guard_error[name]<1e-6,'Direct CAD target reconstruction not validated on original saved samples'
 rows=[]
 for yaw in (-4*np.pi,-2.,-1.,1.,2.,4*np.pi):
  cf=original.clone();cf[:,2]=float(yaw);assert torch.equal(cf[:,:2],original[:,:2]) and torch.equal(cf[:,3:],original[:,3:]);assert torch.equal(tensor,original)
  with torch.inference_mode():result={name:actor(TensorDict(dict(policy=cf),batch_size=[len(cf)])) for name,actor in models.items()}
  for k,row in enumerate(observations):
   item={key:row[key] for key in ('source','env_id','control','first_failure_control')};item.update(original_yaw=float(row['obs'][2]),counterfactual_yaw=float(yaw),original_other34_fields_sha256=hashlib.sha256(np.delete(row['obs'],2).tobytes()).hexdigest(),original_q30_sha256=hashlib.sha256(row['q30'].tobytes()).hexdigest(),original_obs35_sha256=hashlib.sha256(row['obs'].tobytes()).hexdigest(),outputs={})
   for name,outp in result.items():
    raw=outp[k];clip=raw.clamp(-6,6);leg=guarded(clip)
    item['outputs'][name]=dict(fixed_head_mean6=raw.tolist(),clip6=clip.tolist(),wheel_requested_velocity_target_rad_s=(clip[4:]*10).tolist(),nominal_leg_scale_guard_math_rad=leg.tolist(),nominal_guard_crank_minus_hip_rad=[float(leg[j]-leg[j+1]) for j in (0,2)],left_wheel_actor_clip=bool(abs(raw[4])>=6),right_wheel_actor_clip=bool(abs(raw[5])>=6),left_crank_actor_clip=bool(abs(raw[0])>=6),left_CAD_lower_projected=bool(abs(float(leg[0]-leg[1])+1.0843)<1e-6),actual_physics_actuator_delay_contact_COM_response_NOT_simulated=True)
   rows.append(item)
 assert torch.equal(torch.get_rng_state(),rng_before)
 for name,actor in models.items():assert all(torch.equal(v,states[name][k]) for k,v in actor.state_dict().items())
 exposure=W/'MOD4_LINUX_LEFT_SECOND_SAMEIDENTITY_CPU_PREPARE_20261014/reports/LEFT_SECOND_COMPLETE_SAVED_COMMAND_EXPOSURE_CPU_ACTUAL.json'
 result=dict(epoch=time.time(),passed_fixed_actor_CPU_component=True,source_constructor_and_activation_verified=sources,checkpoints={k:ix(v) for k,v in checkpoints.items()},complete_command_exposure=ix(exposure),original_full_raw_indexes=source_indexes,delivery_action_scale_source=ix(delivery),selected_actual_validprefix_observations=len(observations),counterfactual_rows=len(rows),same_original_input_GPU_saved_raw_vs_CPU_maxabs=sameobs_error,same_input_CPU_vs_GPU_bitexact_NOT_claimed=True,CPU_float32_only_math_tolerance_not_physics_threshold=5e-4,CAD_guard_reconstruction_original_saved_raw_maxabs_rad=guard_error,original_other34_fields_exact=True,original_q30_not_changed=True,all_actorweights9_and_std_exact_after_review=True,global_CPU_RNG_unchanged=True,no_new_history_or_sensor_computation=True,no_SSH_GPU_PPO_budget_newcandidate=True,policy_input_counterfactual_not_new_physical_episode=True,no_contact_or_balance_causality_proven=True,rows=rows)
 out.write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(dict(output=str(out),selected_obs=len(observations),rows=len(rows),maxerrors=sameobs_error,guarderror=guard_error)))
if __name__=='__main__':
 try:main()
 except BaseException:
  p=R/('FIXED_ACTOR_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json');p.write_text(json.dumps(dict(error=traceback.format_exc(),no_SSH_GPU_PPO=True),indent=2),encoding='utf8');raise
