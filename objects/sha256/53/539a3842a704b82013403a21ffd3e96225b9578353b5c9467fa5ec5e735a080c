"""Actual GPU sensor-path and parameter readback, no PPO or plant changes."""
import argparse, json, os, traceback
from pathlib import Path
for k,v in json.loads(Path(__file__).with_name('env.json').read_text()).items(): os.environ[k]=str(v)
p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--num_envs',type=int,default=80)
from isaaclab.app import AppLauncher
AppLauncher.add_app_launcher_args(p);args=p.parse_args();app=AppLauncher(args).app
try:
    import torch
    from mod4_env import Mod4Env
    import mod4_task as task
    from sim2real_sensor import audit
    from sensor_core import SensorCore
    torch.manual_seed(20261002)
    cfg=task.Mod4EnvCfg();cfg.seed=20261002;cfg.scene.num_envs=args.num_envs
    env=Mod4Env(cfg=cfg);env.reset();robot=env.scene['robot']
    q=robot.data.joint_pos.clone();root=robot.data.root_state_w.clone()
    a=env.observation_manager.compute();critic=a['critic'].clone();policy=a['policy'].clone()
    actual=audit(env);assert actual['profile']=='sensor_v1'
    assert actual['nominal_bias_zero'] and actual['nominal_lag_zero'] and actual['reset_count_min']>=1
    assert torch.equal(env._sim2real_sensor.core.nominal, env._mild_dr.nominal)
    env._sim2real_sensor.core.reset(torch.arange(env.num_envs,device=env.device),env._mild_dr.nominal)
    b=env.observation_manager.compute()
    assert torch.equal(critic,b['critic']), 'Sensor change corrupted critic'
    assert torch.equal(q,robot.data.joint_pos) and torch.equal(root,robot.data.root_state_w), 'Physical reset changed'
    assert b['policy'].shape[1]==35 and b['critic'].shape[1]==38
    assert bool((b['policy'][~env._mild_dr.nominal]-policy[~env._mild_dr.nominal]).abs().max()>0)
    assert torch.equal(b['policy'][env._mild_dr.nominal],policy[env._mild_dr.nominal])
    first=env._mild_dr.audit();assert first['actual_parameters_pass']
    env.reset();second=audit(env);assert second['reset_count_min']>=2
    assert env._mild_dr.audit()['actual_parameters_pass']
    # Read back real transform outputs while the actual environment advances.
    ids,_=robot.find_joints(task.LEG_ORDER,preserve_order=True)
    action=torch.zeros((env.num_envs,6),device=env.device)
    action[:,:4]=env._rescue_reset_q[:,ids]/task.LEG_ACTION_SCALE
    cmd=env.command_manager.get_term('twist');closure=mimic=0.;nonfinite=False
    for step in range(50):
        cmd.command[:]=0.;cmd.time_left[:]=1e9;env.step(action)
        if step>=10:
            closure=max(closure,float(torch.stack(list(task.closure_errors(env).values())).max()))
            mimic=max(mimic,float(torch.stack(list(task.mimic_errors(env).values())).max()))
        nonfinite |= not bool(torch.isfinite(robot.data.joint_pos).all())
    final=audit(env);assert all(x>0 for x in final['packet_count'].values())
    result=dict(pass_=not nonfinite and closure<=.002 and mimic<=.01,
        actual_sensor_initial=actual,actual_sensor_second_reset=second,actual_sensor_final=final,
        physical_parameters=env._mild_dr.audit(),critic_exact_unchanged=True,
        physical_root_q_exact_unchanged=True,nominal_actor_exact_unchanged=True,
        policy_dim=35,critic_dim=38,max_closure_m=closure,max_mimic_rad=mimic,
        nonfinite=nonfinite,seconds=.5,ppo_performed=False,
        scope='GPU sensor/parameter readback and short closed-chain smoke; not fifteen-second skill or real robot certification')
    result['pass']=result.pop('pass_');Path(args.output).write_text(json.dumps(result,indent=2))
    print('SENSOR_READBACK',json.dumps({k:v for k,v in result.items() if not k.startswith('actual') and k!='physical_parameters'}),flush=True)
    assert result['pass'];env.close()
except BaseException:
    error=traceback.format_exc();Path(args.output+'.error.txt').write_text(error);print(error,flush=True);raise
finally:app.close()
