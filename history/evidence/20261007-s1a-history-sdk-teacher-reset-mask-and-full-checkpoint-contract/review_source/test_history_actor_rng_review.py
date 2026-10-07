"""Target CPU tests of real RSL API, privileged isolation and complete candidate save/load."""
import json,sys,io,random
from pathlib import Path
import torch
from tensordict import TensorDict
from rsl_rl.models import MLPModel
from rsl_rl.storage import RolloutStorage
from history_actor_ppo import HistoryActor,HistoryPPO
from history_latent_component import expand_actor_state,FeedbackHistory
from history_checkpoint import attach_runtime_save,restore_rng
import numpy as np
torch.set_num_threads(1)
source=torch.load(sys.argv[1],map_location='cpu',weights_only=False)
torch.manual_seed(101)
obs=TensorDict(dict(policy=torch.randn(128,35),critic=torch.randn(128,38),feedback_history=torch.randn(128,175),body_velocity_label=torch.randn(128,3)),batch_size=[128])
groups=dict(actor=['policy','feedback_history'],critic=['critic'])
dist=lambda:dict(class_name='rsl_rl.modules.distribution:GaussianDistribution',init_std=1.,std_type='scalar')
old=MLPModel(obs,dict(actor=['policy'],critic=['critic']),'actor',6,[256,128,64],'elu',distribution_cfg=dist())
old.load_state_dict(source['actor_state_dict'])
tests=[]
for variant in ('A1','A2'):
 actor=HistoryActor(obs,groups,'actor',6,[256,128,64],'elu',distribution_cfg=dist(),variant=variant)
 state=actor.state_dict();state.update(expand_actor_state(source['actor_state_dict']));actor.load_state_dict(state)
 critic=MLPModel(obs,groups,'critic',1,[256,128,64],'elu');critic.load_state_dict(source['critic_state_dict'])
 assert torch.equal(actor.distribution.std_param,old.distribution.std_param)
 assert torch.equal(actor(obs),old(obs));tests.append(variant+'_zero_columns_real_source_output_std_exact')
 leaked=obs.clone();leaked['body_velocity_label'].add_(1000)
 assert torch.equal(actor(obs),actor(leaked));tests.append(variant+'_privileged_label_not_in_actor')
 export=torch.jit.script(actor.as_jit());assert torch.equal(export(obs['policy'],obs['feedback_history']),actor(obs));tests.append(variant+'_history_JIT_exact')
 with torch.no_grad():actor.mlp[0].weight[:,35:].fill_(.01)
 before=obs.clone();before['feedback_history'].add_(2)
 assert not torch.equal(actor(obs),actor(before));tests.append(variant+'_deployable_history_is_consumed')
 actor.zero_grad();actor(obs).sum().backward()
 grads=[p.grad for p in actor.encoder.parameters()]
 assert (all(g is None for g in grads) if variant=='A1' else any(g is not None and bool(g.abs().sum()>0) for g in grads));tests.append(variant+'_gradient_route')
 storage=RolloutStorage('rl',128,24,obs,[6],'cpu')
 alg=HistoryPPO(actor,critic,storage,learning_rate=1e-4,device='cpu')
 encids={id(p) for p in actor.encoder.parameters()};ppoids={id(p) for g in alg.optimizer.param_groups for p in g['params']}
 assert (not encids.intersection(ppoids) if variant=='A1' else encids.issubset(ppoids));tests.append(variant+'_optimizer_ownership')
 # Actual synthetic CPU optimizer steps, solely checkpoint fixtures, not task training.
 alg.optimizer.zero_grad();(actor(obs).square().mean()+critic(obs).square().mean()).backward();alg.optimizer.step()
 if alg.aux_optimizer:
  alg.aux_optimizer.zero_grad();(actor.encoder(obs['feedback_history'])-obs['body_velocity_label']).square().mean().backward();alg.aux_optimizer.step()
 for _ in range(24):
  alg.act(obs)
  alg.process_env_step(obs,torch.randn(128),torch.zeros(128,dtype=torch.long),{})
 alg.compute_returns(obs)
 before_encoder=[p.detach().clone() for p in actor.encoder.parameters()]
 losses=alg.update()
 assert alg.actual_updates==1 and bool(all(torch.isfinite(torch.tensor(v)) for v in losses.values()))
 assert any(not torch.equal(p,b) for p,b in zip(actor.encoder.parameters(),before_encoder))
 assert alg.aux_updates==(4 if variant=='A1' else 0)
 tests.append(variant+'_full_RSL_update_synthetic_CPU_fixture')
 alg.actual_updates=7;alg.aux_updates=28 if variant=='A1' else 0
 class Vec:
  env=type('Env',(),{'common_step_counter':18})()
  def history_state_dict(self):return history_state
 history=FeedbackHistory(128);history.observe(obs['policy'],18)
 history_state=dict(frames=history.frames.clone(),pending=history.pending.clone(),last_tick=18,advances=1)
 runner=type('Runner',(),{'alg':alg})();attach_runtime_save(runner,Vec())
 state=alg.save();buffer=io.BytesIO();torch.save(state,buffer);buffer.seek(0);loaded=torch.load(buffer,weights_only=False)
 target_actor=HistoryActor(obs,groups,'actor',6,[256,128,64],'elu',distribution_cfg=dist(),variant=variant)
 target_critic=MLPModel(obs,groups,'critic',1,[256,128,64],'elu')
 target=HistoryPPO(target_actor,target_critic,RolloutStorage('rl',128,24,obs,[6],'cpu'),learning_rate=1e-4,device='cpu')
 target.load(loaded,None,True)
 assert torch.equal(target.actor(obs),alg.actor(obs)) and torch.equal(target.critic(obs),alg.critic(obs))
 assert target.actual_updates==7 and target.aux_updates==alg.aux_updates
 for key in ('actor_state_dict','critic_state_dict','optimizer_state_dict','aux_optimizer_state_dict','feedback_history_state','rng_state'):assert key in loaded
 assert torch.equal(loaded['feedback_history_state']['frames'],history.frames)
 restore_rng(loaded['rng_state']);expected=(random.random(),np.random.random(),torch.rand(4));random.random();np.random.random();torch.rand(17);restore_rng(loaded['rng_state'])
 actual=(random.random(),np.random.random(),torch.rand(4));assert expected[0]==actual[0] and expected[1]==actual[1] and torch.equal(expected[2],actual[2])
 tests.append(variant+'_full_actor_encoder_critic_optimizers_RNG_history_roundtrip')
 try:
  HistoryActor(obs,dict(actor=['policy','body_velocity_label'],critic=['critic']),'actor',6,variant=variant)
  raise AssertionError('Privileged actor configuration admitted')
 except ValueError:tests.append(variant+'_privileged_actor_groups_rejected')
assert not torch.cuda.is_initialized()
print(json.dumps(dict(passed=True,tests=tests,test_count=len(tests),torch_version=torch.__version__,CUDA_initialized=False,
 actual_task_PPO=False,checkpoint_resume_semantics='New architecture weights migration keeps std/critic; new optimizers explicit. Simulator history cleared on new episodes.')))
