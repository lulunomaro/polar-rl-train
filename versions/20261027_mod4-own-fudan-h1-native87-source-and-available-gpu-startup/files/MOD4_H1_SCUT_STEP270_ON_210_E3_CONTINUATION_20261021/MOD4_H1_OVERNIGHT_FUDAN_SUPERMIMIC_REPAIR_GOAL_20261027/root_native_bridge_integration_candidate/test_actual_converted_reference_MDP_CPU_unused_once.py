"""New MDP goal/reward/history integration CPU test using frozen converted JSON."""
from pathlib import Path
from types import SimpleNamespace as S
import sys,json,traceback
HERE=Path(__file__).resolve().parent;L=HERE.parent
REPORT=L/'reports/CONVERTED_MOD4_REFERENCE_FUTURE_GOAL_ACTUAL_BPTT_CPU_ACTUAL.json'
assert not REPORT.exists()
for p in [HERE,L/'agent_static_dynamic_delay_contract_candidate',L/'root_compact_static_context_candidate',L/'root_augmented_world_model_candidate/v4']:
 sys.path.insert(0,str(p))
checks=[]
try:
 import torch
 from converted_MOD4_jump_mdp_v3 import ConvertedMOD4Reference,ConvertedMOD4JumpMdp
 from supermimic_wheel_leg_v3.learner import SuperMimicConfig,SuperMimicLearner
 from supermimic_wheel_leg_v3.geometry import unflatten_state,quat_to_mat
 from supermimic_wheel_leg_v3.contract import SUPERMIMIC_STATE_KEY as SK
 torch.set_num_threads(2)
 doc=json.loads((HERE/'MOD4_OWN_CONVERTED_FUDAN_JUMP_REFERENCE_V1_NOT_ADMITTED.json').read_bytes())
 provider=ConvertedMOD4Reference(doc).bind_named_order(doc['joint_names'],scope='source_CPU_fixture')
 mdp=ConvertedMOD4JumpMdp(provider)
 f=torch.tensor([0,130,145,165,300,301,450])
 values,mask=provider.query(f)
 assert values.shape==(7,73) and mask.shape==(7,73)
 assert torch.equal(values[-1,7:13],torch.zeros(6)) and torch.equal(values[-1,43:73],torch.zeros(30))
 checks.append('actual new table + explicit endpoint hold/zero velocities after age300')
 g=mdp.goal(torch.tensor([295,300]),10)
 assert g.shape==(2,1460) and torch.isfinite(g).all()
 checks.append('future10 state+mask goals explicit across endpoint, not silently truncated')
 packed=torch.cat((values,torch.zeros(7,54)),-1)
 state=unflatten_state(packed)
 # Neutral xi31 follows real random-parameter semantics.
 xi=torch.tensor([[1.,.9]+[1.]*6+[0.]*3+[1.]*10+[1.]*2+[1.]*2+[1.]*2+[0.]*4]).expand(7,-1).clone()
 obs=mdp.obs(state,torch.zeros(7,6),xi,f)
 assert obs.shape==(7,86)
 shifted=(state[0]+torch.tensor([.1,0.,0.]),*state[1:])
 assert not torch.equal(obs,mdp.obs(shifted,torch.zeros(7,6),xi,f))
 checks.append('real terrain/reference-relative position resolves previous XY alias')
 histories=tuple(x[:,None].expand(*x.shape[:1],3,*x.shape[1:]) for x in state)
 history_obs=mdp.obs(histories,torch.zeros(7,3,6),xi[:,None].expand(7,3,31),f[:,None].expand(7,3))
 assert history_obs.shape==(7,3,86)
 checks.append('BPTT/replay observation histories support arbitrary batch and history dimensions')
 biased=xi.clone();biased[:,27:31]=.0075
 biased_obs=mdp.obs(state,torch.zeros(7,6),biased,f)
 assert not torch.equal(obs,biased_obs)
 assert torch.equal(obs[:,:13],biased_obs[:,:13])
 checks.append('actual episode encoder-bias4 maps to named leg q slots, static xi not directly appended to actor')
 p=state[0].clone().requires_grad_()
 perturbed=(p+.05,*state[1:])
 r=mdp.reward(perturbed,f,torch.zeros(7,6),torch.zeros(7,6))
 grad=torch.autograd.grad(r.sum(),p)[0]
 assert torch.isfinite(r).all() and torch.isfinite(grad).all() and grad.abs().max()>0
 checks.append('same additive masked tracking head has finite nonzero position gradient')
 identical=mdp.reward(state,f,torch.zeros(7,6),torch.zeros(7,6))
 assert torch.allclose(identical,torch.full((7,),.06),atol=1e-6)
 checks.append('own reference query and reward head agree at reference states')
 n=4;start=torch.tensor([110,130,145,165])
 v,_=provider.query(start);s=torch.cat((v,torch.zeros(n,54)),-1)
 env=S(device='cpu',num_envs=n,supermimic_mdp=mdp,state=S(info={SK:dict(s=s,xi=xi[:n],f=start,a_prev=torch.zeros(n,6),ep_step=torch.zeros(n,dtype=torch.int32))}))
 cfg=SuperMimicConfig(iterations=1,buffer_steps=16,utd=.4,horizon=3,goal_frames=10,hist=3,
 wm_window=2,wm_batch=4,pi_batch=4,wm_batches=1,critic_epochs=1,critic_minibatches=1,
 wm_hidden=(16,16),policy_hidden=(16,16),critic_hidden=(16,16),test_hidden_dims=(16,16),
 amp='none',compile=False,log_backend='none')
 learner=SuperMimicLearner(env,cfg,HERE/'synthetic_actual_reference_mdp_CPU_only',device='cpu')
 with torch.no_grad():learner.wm.net[-1].weight.normal_(0,.001)
 for i in range(8):
  v,_=provider.query(start+i);v1,_=provider.query(start+i+1)
  learner.buffer.add(dict(s=torch.cat((v,torch.zeros(n,54)),-1),s1=torch.cat((v1,torch.zeros(n,54)),-1),
   a=torch.zeros(n,6),a_prev=torch.zeros(n,6),xi=xi[:n],r=torch.ones(n)*.06,
   f=start+i,ep_step=torch.full((n,),i,dtype=torch.int32),done=torch.zeros(n,dtype=torch.bool)))
 loss,err=learner.wm_update();pi=learner.policy_update()
 assert torch.isfinite(loss) and all(torch.isfinite(x).all() for x in pi)
 checks.append('actual candidate WM and full BPTT Pi/critic code step once using real converted-goal values and full future10 masks')
 assert not torch.cuda.is_initialized()
 checks.append('only synthetic CPU weights; no saved native policy, actual physics, SDK, GPU, SSH, GO or fee')
 result={'passed':True,'checks':checks,'count':len(checks),'provider_order_scope':provider.order_scope,
  'not_actual_SDK_or_dynamic_reference_admission':True,'reference_goal_not_robot_transition_groundtruth':True,
  'new_reference':str(HERE/'MOD4_OWN_CONVERTED_FUDAN_JUMP_REFERENCE_V1_NOT_ADMITTED.json'),
  'native_clean_proprioception_note':'Native observation includes own relative geometry and explicit leg encoder bias; original physical sensor wrapper remains, sensor-noise/history fidelity requires actual source contract and is not called identical PPO35.',
  'source_versions':'V1/V2 AST-only drafts retained; V3 fixes scalar terrain helper/batched history interface before this first MDP integration run.'}
except BaseException:
 result={'passed':False,'checks_before_failure':checks,'error':traceback.format_exc(),'all_new_partials_preserved':True}
 REPORT.write_text(json.dumps(result,indent=2),'utf8');raise
REPORT.write_text(json.dumps(result,indent=2),'utf8')
print(json.dumps({'passed':True,'count':len(checks)}))

