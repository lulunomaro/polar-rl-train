"""Actual PhysX parameter readback across resets, without PPO or production edits."""
import argparse
import json
import os
from pathlib import Path

for key,value in json.loads(Path(__file__).with_name('env.json').read_text()).items():os.environ[key]=str(value)
parser=argparse.ArgumentParser()
parser.add_argument('--output',required=True)
parser.add_argument('--num_envs',type=int,default=80)
from isaaclab.app import AppLauncher
AppLauncher.add_app_launcher_args(parser)
args=parser.parse_args()
app=AppLauncher(args).app
try:
    import torch
    import mod4_task as task
    from mod4_env import Mod4Env
    torch.manual_seed(20261001)
    cfg=task.Mod4EnvCfg();cfg.seed=20261001;cfg.scene.num_envs=args.num_envs
    env=Mod4Env(cfg=cfg)
    env.reset()
    dr=env._mild_dr
    before=dr.factor.clone()
    first=dr.audit()
    env.reset()
    second=dr.audit()
    changed=int((before-dr.factor).abs().gt(1e-6).sum())
    assert changed > args.num_envs*.5, 'reset did not resample mass factors'
    ids,_=env.scene['robot'].find_joints(task.LEG_ORDER,preserve_order=True)
    action=torch.zeros((env.num_envs,6),device=env.device)
    action[:,:4]=env._rescue_reset_q[:,ids]/task.LEG_ACTION_SCALE
    command=env.command_manager.get_term('twist')
    maxclosure=0.;maxmimic=0.;nonfinite=False
    for step in range(50):
        command.command[:]=0.;command.time_left[:]=1e9
        env.step(action)
        if step>=10:
            maxclosure=max(maxclosure,float(torch.stack(list(task.closure_errors(env).values())).max()))
            maxmimic=max(maxmimic,float(torch.stack(list(task.mimic_errors(env).values())).max()))
        nonfinite |= not bool(torch.isfinite(env.scene['robot'].data.joint_pos).all())
    third=dr.audit()
    report={'pass':not nonfinite and maxclosure<=.002 and maxmimic<=.01,
            'initial':first,'second_reset':second,'after_physics':third,
            'resampled_environments':changed,'max_closure_m':maxclosure,'max_mimic_rad':maxmimic,
            'nonfinite':nonfinite,'seconds':.5,'ppo_performed':False,
            'scope':'parameter and short physical probe, not fifteen-second skill graduation'}
    Path(args.output).write_text(json.dumps(report,indent=2))
    print(json.dumps(report),flush=True)
    assert report['pass'],report
    env.close()
finally:
    app.close()
