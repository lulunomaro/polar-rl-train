"""Fixed-seed native evaluation of deterministic learned actions; no optimizer."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import random
import sys
import time
import traceback
from .jump_train import put


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--plan',required=True)
    parser.add_argument('--job',required=True)
    parser.add_argument('--checkpoint',required=True)
    parser.add_argument('--num-envs',type=int,default=256)
    parser.add_argument('--seed',type=int,default=10066)
    args = parser.parse_args()
    plan = json.loads(Path(args.plan).read_bytes())
    job = Path(args.job)
    job.mkdir(parents=True,exist_ok=False)
    storage = job/'kit_isolation'
    (storage/'data').mkdir(parents=True)
    (storage/'DerivedDataCache').mkdir()
    (storage/'data/user.config.json').write_text('{}')
    os.environ.update(MOD4V1_E0_JOB_ROOT=str(job),MOD4V1_E0_KIT_STORAGE_ROOT=str(storage),
        MOD4_SCUT_SOURCE_PATHS=plan['source_paths'],OMNI_KIT_ACCEPT_EULA='YES',ISAACSIM_ACCEPT_EULA='Y')
    sys.path[:0] = [plan['runtime'],plan['shared_package'],plan['package'],plan['support']]
    from launcher_mod4v1_e0 import IsolatedAppLauncher208
    app = IsolatedAppLauncher208(dict(headless=True,device='cuda:0',enable_cameras=False)).app
    env = None
    outcome = 'failed'
    try:
        import numpy as np
        import torch
        from torch import nn
        from .model import metadata,reset_bank
        from .moving_jump_env import MovingJumpEnv
        from .sampling import Sampling
        from .scut_flat_env import configuration,tensor
        for name,row in plan['asset_identity']['actual_training_assets'].items():
            assert hashlib.sha256((Path(plan['package'])/'assets'/name).read_bytes()).hexdigest() == row['sha256']
        seed = args.seed
        random.seed(seed)
        np.random.seed(seed)
        torch.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
        meta = metadata(plan['package'])
        bank = reset_bank(plan['package'],plan['reset_bank'])
        cfg = configuration(meta,bank,args.num_envs,seed,terrain_selection='flat')
        cfg.episode_length_s = 6.
        env = MovingJumpEnv(cfg,meta,bank)
        env.render_enabled = False
        checkpoint = Path(args.checkpoint)
        digest = hashlib.sha256(checkpoint.read_bytes()).hexdigest()
        data = torch.load(checkpoint,map_location=env.device,weights_only=False)
        assert data['action_order'] == env.order
        # Parent and all child checkpoints share this exact frozen RSL MLP schema.
        actor = nn.Sequential(nn.Linear(35,256),nn.ELU(),nn.Linear(256,128),nn.ELU(),
                              nn.Linear(128,64),nn.ELU(),nn.Linear(64,6)).to(env.device)
        actor.load_state_dict({k.removeprefix('mlp.'):v for k,v in data['actor_state_dict'].items() if k.startswith('mlp.')},strict=True)
        actor.eval().requires_grad_(False)
        random.seed(seed)
        np.random.seed(seed)
        torch.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
        env.reset_generator.manual_seed(seed+179)
        env.reset()
        env.sample = Sampling(env)
        parity = env.sample.parity()
        raw = env._get_observations()
        put(job/'STARTUP.json',dict(epoch=time.time(),checkpoint=str(checkpoint),sha256=digest,
            iteration=data['iter'],num_envs=args.num_envs,seed=seed,control='deterministic learned actor only',
            optimizer_created=False,teacher_execution=False,task=plan['jump'],sampling=parity,
            reset_distribution=env.reset_distribution_summary(),domain_randomization=env.full_dr.summary()))
        seen = torch.zeros(env.num_envs,device=env.device,dtype=torch.bool)
        rows = []
        traces = []
        peak_torque = torch.zeros(6,device=env.device)
        with torch.inference_mode():
            for step in range(305):
                policy_input=raw['policy'].clone()
                action = actor(raw['policy'])
                raw,reward,term,timeout,extra = env.step(action)
                assert all(bool(torch.isfinite(v).all()) for v in raw.values()) and bool(torch.isfinite(reward).all())
                peak_torque = torch.maximum(peak_torque,env.applied_motor_torque.abs().amax(0))
                snap = env.jump_snapshot
                values = dict(**snap,policy_input=policy_input,root_pos=env.snapshots['root_pos'],root_quat=env.snapshots['root_quat'],
                    native_q=tensor(env.robot.data.joint_pos),action=action,
                    closure=env.snapshots['closure'],done=term|timeout)
                traces.append({k:v.detach().cpu().numpy() for k,v in values.items()})
                for i in ((term|timeout)&~seen).nonzero().flatten().tolist():
                    row = {k:v[i].item() for k,v in snap.items()}
                    row.update(env=i,nominal=bool(env.full_dr.nominal_env_mask[i]),terminated=bool(term[i]),
                        timeout=bool(timeout[i]),closure_m=float(env.snapshots['closure'][i]),steps=step+1)
                    rows.append(row)
                seen |= term|timeout
                if bool(seen.all()):
                    break
        assert bool(seen.all())
        summary = {}
        for nominal,name in ((False,'fullDR'),(True,'nominal')):
            group = [row for row in rows if row['nominal'] == nominal]
            summary[name] = dict(requested=len(group),**{k:sum(bool(row[k]) for row in group) for k in ('crouched','extended','takeoff','retracted','landed','success')},
                air_balance_passed=sum(bool(row['takeoff'] and row['air_pitch'] <= .1745329252 and row['air_roll'] <= .0872664626) for row in group),
                max_air_s=max((row['air_s'] for row in group),default=0.),
                max_rim_m=max((row['rim_peak'] for row in group),default=0.))
        np.savez_compressed(job/'trajectory.npz',**{k:np.stack([v[k] for v in traces]) for k in traces[0]},
            env_origins=env.scene.env_origins.cpu().numpy(),joint_names=np.asarray(env.robot.joint_names))
        put(job/'RESULT.json',dict(epoch=time.time(),checkpoint=str(checkpoint),checkpoint_sha256=digest,
            iteration=data['iter'],seed=seed,num_envs=env.num_envs,steps=step+1,
            independent=True,control='actor',no_optimizer_update=True,optimizer_created=False,
            summary=summary,episodes=rows,peak_torque_Nm=peak_torque.tolist(),done_totals=dict(env.done_totals),
            note='Fixed seed and startup/reset distributions shared across checkpoint evaluations'))
        outcome = 'complete'
    except BaseException:
        put(job/'ERROR.json',dict(epoch=time.time(),traceback=traceback.format_exc()))
        raise
    finally:
        if env is not None:
            env.close()
        put(job/'SAFE_CLOSED.json',dict(epoch=time.time(),scene_closed=True,outcome=outcome))
        app.close()


if __name__ == '__main__':
    main()
