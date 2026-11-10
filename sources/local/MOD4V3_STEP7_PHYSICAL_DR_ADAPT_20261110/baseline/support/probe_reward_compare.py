from __future__ import annotations
import json, sys, torch
from pathlib import Path
HERE=Path(__file__).resolve().parent; sys.path.insert(0,str(HERE))
plan=json.loads((HERE.parent/'PLAN_LOCAL.json').read_bytes()); sys.path[:0]=[plan['runtime'],plan['shared_package'],plan['package'],plan['support']]
from launcher_mod4v1_e0 import IsolatedAppLauncher208
app=IsolatedAppLauncher208(dict(headless=True,device='cuda:0',enable_cameras=False)).app
from mod4v3_ppo_v1.scut_rough_v0_env import ScutRoughV0Env
from mod4v3_ppo_v1.scut_flat_env import configuration
from mod4v3_ppo_v1.model import metadata,reset_bank
from mod4v3_ppo_v1.sampling import Sampling
from tensordict import TensorDict
from rsl_rl.runners import OnPolicyRunner
from mod4v1_scut.config import runner_config
N=16; STEPS=50
meta=metadata(plan['package']); bank=reset_bank(plan['package'],plan['reset_bank'])
env=ScutRoughV0Env(configuration(meta,bank,N,66,terrain_selection='rough'),meta,bank)
env.render_enabled=False; env.enforce_closure_reset=False
class Vec:
 def __init__(self): self.num_envs=N; self.num_actions=6; self.device=env.device; self.max_episode_length=env.max_episode_length; self.cfg=env.cfg
 @property
 def episode_length_buf(self): return env.episode_length_buf
 def get_observations(self): return TensorDict(env._get_observations(),batch_size=[N])
cfg=runner_config();cfg['clip_actions']=None;cfg['algorithm']['value_loss_coef']=2.0;cfg['algorithm']['learning_rate']=1e-4
runner=OnPolicyRunner(Vec(),cfg,log_dir=None,device=env.device); alg=runner.alg
def evaluate(name,ckpt):
 data=torch.load(ckpt,map_location=env.device,weights_only=False); alg.actor.load_state_dict(data['actor_state_dict'],strict=True); alg.eval_mode(); policy=alg.get_policy()
 env.reset(); env.sample=Sampling(env); env.command[:,0]=2.0; env.command[:,1]=0.; env.command[:,2]=0.; env.height[:]=.28; env.command_timer[:]=1e9; env.standing_env.zero_(); env.heading_env.zero_(); env.reward.command.copy_(env.command); env.reward.height_cmd.copy_(env.height); env.reward._invalidate_step_caches()
 obs=TensorDict(env._get_observations(),batch_size=[N]); terms=[]
 with torch.no_grad():
  for i in range(STEPS):
   action=policy(obs,stochastic_output=False).clamp(-6,6); raw,reward,term,timeout,extra=env.step(action)
   if i>=20:
    vx=float(env.view.data.root_lin_vel_b[:,0].mean())
    vals=[]
    for k,v in getattr(env.reward,'raw_terms',{}).items():
     w=float(env.reward.cfg.rewards.get(k,0.0))
     if w!=0 and torch.is_tensor(v) and v.numel() and v.dtype.is_floating_point:
      vals.append((k,float((v*w).mean()),w,float(v.mean())))
    terms.append((vx,vals))
   obs=TensorDict(raw,batch_size=[N])
 # average term means
 names={k for _,vals in terms for k,_,_,_ in vals}; avg=[]
 for k in names:
  wm=sum(next((wm for kk,wm,w,rawm in vals if kk==k),0.0) for _,vals in terms)/len(terms)
  avg.append((abs(wm),k,wm))
 avg.sort(reverse=True)
 print(name,'vx_mean',round(sum(v[0] for v in terms)/len(terms),4),'top',[(k,round(wm,5)) for _,k,wm in avg[:15]],flush=True)
evaluate('parent_flat',HERE.parent/'parent_flatv2_best.pt')
evaluate('rough_final',HERE.parent/'job2h_r1'/'model_final.pt')
env.close(); app.close()
