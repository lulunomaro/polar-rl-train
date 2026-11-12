from __future__ import annotations
import json, sys, torch, traceback
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
plan=json.loads((HERE.parent/'PLAN_LOCAL.json').read_bytes())
sys.path[:0]=[plan['runtime'],plan['shared_package'],plan['package'],plan['support']]
from launcher_mod4v1_e0 import IsolatedAppLauncher208

CKPT=HERE.parent/'job2h_r1'/'model_final.pt'
N=64
STEPS=220
SETTLE=120

app=IsolatedAppLauncher208(dict(headless=True,device='cuda:0',enable_cameras=False)).app
from mod4v3_ppo_v1.scut_rough_v0_env import ScutRoughV0Env
from mod4v3_ppo_v1.scut_flat_env import configuration
from mod4v3_ppo_v1.model import metadata, reset_bank
from mod4v3_ppo_v1.sampling import Sampling
from tensordict import TensorDict
from rsl_rl.runners import OnPolicyRunner
from mod4v1_scut.config import runner_config
env=None
try:
    meta=metadata(plan['package']); bank=reset_bank(plan['package'],plan['reset_bank'])
    env=ScutRoughV0Env(configuration(meta,bank,N,66,terrain_selection='rough'),meta,bank)
    env.render_enabled=False; env.enforce_closure_reset=False
    env.reset(); env.sample=Sampling(env)
    class Vec:
        def __init__(self):
            self.num_envs=N; self.num_actions=6; self.device=env.device
            self.max_episode_length=env.max_episode_length; self.cfg=env.cfg
        @property
        def episode_length_buf(self): return env.episode_length_buf
        def get_observations(self): return TensorDict(env._get_observations(),batch_size=[N])
    cfg=runner_config(); cfg['clip_actions']=None; cfg['algorithm']['value_loss_coef']=2.0; cfg['algorithm']['learning_rate']=1e-4
    runner=OnPolicyRunner(Vec(),cfg,log_dir=None,device=env.device)
    alg=runner.alg
    data=torch.load(CKPT,map_location=env.device,weights_only=False)
    alg.actor.load_state_dict(data['actor_state_dict'],strict=True)
    alg.eval_mode(); policy=alg.get_policy()

    def run(name,vx,wz,height):
        env.reset()
        env.command[:,0]=vx; env.command[:,1]=0.; env.command[:,2]=wz
        env.height[:]=height; env.command_timer[:]=1e9
        env.standing_env.zero_(); env.heading_env.zero_()
        env.reward.command.copy_(env.command); env.reward.height_cmd.copy_(env.height)
        env.reward._invalidate_step_caches()
        obs=TensorDict(env._get_observations(),batch_size=[N])
        vals={'vx':[],'wz':[],'height':[],'cos':[],'reward':[]}
        terms=falls=0; c0=env.done_totals.get('closure_catastrophic',0); f0=env.done_totals.get('fall',0)
        with torch.no_grad():
            for _ in range(STEPS):
                action=policy(obs,stochastic_output=False).clamp(-6.,6.)
                raw,reward,term,timeout,extra=env.step(action)
                vals['vx'].append(float(env.view.data.root_lin_vel_b[:,0].mean()))
                vals['wz'].append(float(env.view.data.root_ang_vel_b[:,2].mean()))
                vals['height'].append(float(env._height_observation().mean()))
                vals['cos'].append(float(env.view.data.projected_gravity_b[:,2].min()))
                vals['reward'].append(float(reward.mean()))
                terms+=int(term.sum()); obs=TensorDict(raw,batch_size=[N])
        sl=slice(SETTLE,None)
        out=dict(name=name,cmd_vx=vx,cmd_wz=wz,cmd_height=height,
            vx_mean=sum(vals['vx'][sl])/len(vals['vx'][sl]),
            wz_mean=sum(vals['wz'][sl])/len(vals['wz'][sl]),
            height_mean=sum(vals['height'][sl])/len(vals['height'][sl]),
            cos_min=min(vals['cos'][sl]),reward_mean=sum(vals['reward'][sl])/len(vals['reward'][sl]),
            term=terms,fall_reset=env.done_totals.get('fall',0)-f0,
            catastrophic_closure_reset=env.done_totals.get('closure_catastrophic',0)-c0)
        print(json.dumps(out,ensure_ascii=False),flush=True)
        return out

    results=[]
    try:
        for vx in (0.0,0.3,0.6,1.0,1.5,2.0,2.2):
            results.append(run(f'forward_{vx:.1f}',vx,0.,.28))
        results.append(run('backward_1.5',-1.5,0.,.28))
        for wz in (6.283185307179586,10.210176124166829,14.137166941154069):
            results.append(run(f'yaw_{wz:.2f}',0.,wz,.28))
        for h in (0.20,0.28,0.40):
            results.append(run(f'height_{h:.2f}',0.,0.,h))
        results.append(run('forward_2.2_h0.40',2.2,0.,.40))
        (HERE.parent/'EVAL_ROUGH_SKILLS.json').write_text(json.dumps(results,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    except BaseException:
        (HERE.parent/'EVAL_ROUGH_ERROR.txt').write_text(traceback.format_exc(),encoding='utf-8')
        raise
finally:
    if env is not None: env.close()
    app.close()

