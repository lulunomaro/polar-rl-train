"""Explicit closed-PPO-policy bootstrap with a NEW4096 physical episode.

No old20k environmental state is reshaped, restored or labeled exact continuation.
The original fullsave chain is installed separately on the actual new environment.
"""
from pathlib import Path
import hashlib,json,time
import torch

BOOTSTRAP_SHA='0c1edb9603c1cb84fbb894d242dae1b6a7c87fe3237d658dbc486ccbbad3d394'
BOOTSTRAP_ADAM=832460

def exact(a,b):
    if torch.is_tensor(a):return torch.is_tensor(b) and a.dtype==b.dtype and a.shape==b.shape and torch.equal(a.cpu(),b.cpu())
    if isinstance(a,dict):return isinstance(b,dict) and set(a)==set(b) and all(exact(a[k],b[k]) for k in a)
    if isinstance(a,(list,tuple)):return type(a)==type(b) and len(a)==len(b) and all(exact(x,y) for x,y in zip(a,b))
    return type(a)==type(b) and a==b

def verify_loaded_policy_only_fresh_environment(runner,env,checkpoint):
    if env.num_envs!=4096 or env.physics_dt!=.0025 or env.step_dt!=.01 or env.cfg.decimation!=4:
        raise ValueError('explicit4096/original2.5ms100Hz required')
    if float(env.cfg.episode_length_s)!=5.:
        raise ValueError('explicit five-second practice episodes required')
    if int(env._sim_step_counter)!=0 or bool(env.h1_phase.age_control.any()):
        raise ValueError('new physical episode must start at zero control clock')
    if bool(env.h1_phase.goal.success.any()) or bool(env.h1_phase.crossed.any()):
        raise ValueError('new episode cannot inherit success credits')
    pairs=[('actor_state_dict',runner.alg.actor.state_dict()),
           ('critic_state_dict',runner.alg.critic.state_dict()),
           ('optimizer_state_dict',runner.alg.optimizer.state_dict())]
    for name,current in pairs:
        if not exact(current,checkpoint[name]):raise ValueError('policy bootstrap differs: '+name)
    if len(checkpoint['actor_state_dict'])!=9 or len(checkpoint['critic_state_dict'])!=8:
        raise ValueError('whole qualified actor/critic groups required')
    if checkpoint['actor_state_dict']['distribution.std_param'].shape!=(6,):
        raise ValueError('all six STD required')
    if len(checkpoint['optimizer_state_dict']['state'])!=17 or {int(x['step']) for x in checkpoint['optimizer_state_dict']['state'].values()}!={BOOTSTRAP_ADAM}:
        raise ValueError('exact qualified17Adam832460 required')
    # Validate each new component's own complete state and target population;
    # do not compare it to saved20k environmental tensors.
    states={
        'sensor':env._sensor_mild.state_dict(),
        'physical_queue':env._physics_action_delay.state_dict(),
        'spring':env._spring_pressure.state_dict(),
        'gas':env._gas_damping.state_dict(),
        'COM':env._chassis_com.state_dict(),
        'PD':env._explicit_pd.state_dict(),
    }
    for name,value in states.items():
        count=value.get('n',value.get('num_envs'))
        if count!=4096:raise ValueError('new physical component population differs: '+name)
    return dict(policy_actor9_critic8_STD6_17Adam832460_exact=True,
        native_architecture_and_optimizers_fresh=True,physical_episode_fresh=True,
        old_environment_population=20000,new_environment_population=4096,
        old20k_environmental_state_restored=False,old_native86_optimizer_restored=False,
        PhysX_exact_resume=False,actual_clock_zero=True,actual_component_populations4096=True,
        source_role='closed_production_policy_only_bootstrap_for_new_native_method')

def resume_policy_only_fresh4096(runner,env,path,log_dir):
    path=Path(path)
    digest=hashlib.sha256(path.read_bytes()).hexdigest()
    if digest!=BOOTSTRAP_SHA:raise ValueError('latest closedH1 policy sourceSHA differs')
    checkpoint=torch.load(path,map_location='cpu',weights_only=False)
    row=verify_loaded_policy_only_fresh_environment(runner,env,checkpoint)
    row.update(epoch=time.time(),source_SHA=digest,source_Adam=BOOTSTRAP_ADAM)
    out=Path(log_dir)/'NATIVE87_POLICY_ONLY_FRESH4096_BOOTSTRAP_ACTUAL.json'
    if out.exists():raise FileExistsError(out)
    out.write_text(json.dumps(row,indent=2),'utf8')
    return row

