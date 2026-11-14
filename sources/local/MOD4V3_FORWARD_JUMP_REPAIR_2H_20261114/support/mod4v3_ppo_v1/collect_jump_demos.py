"""Capture native successful teacher episodes; no policy optimizer is created."""
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
    parser.add_argument('--num-envs',type=int,default=128)
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
        from .scut_flat_env import configuration
        seed = 20066
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
        path = Path(plan['teacher_parent'])
        assert hashlib.sha256(path.read_bytes()).hexdigest() == plan['teacher_sha256']
        parent = torch.load(path,map_location=env.device,weights_only=False)
        teacher = nn.Sequential(nn.Linear(35,256),nn.ELU(),nn.Linear(256,128),nn.ELU(),
                                nn.Linear(128,64),nn.ELU(),nn.Linear(64,6)).to(env.device)
        teacher.load_state_dict({k.removeprefix('mlp.'):v for k,v in parent['actor_state_dict'].items() if k.startswith('mlp.')},strict=True)
        env.teacher_net = teacher.eval().requires_grad_(False)
        env.reset()
        env.sample = Sampling(env)
        env.sample.parity()
        raw = env._get_observations()
        seen = torch.zeros(env.num_envs,device=env.device,dtype=torch.bool)
        successful = seen.clone()
        inputs = []
        targets = []
        phases = []
        eligible = []
        episodes = []
        with torch.inference_mode():
            for step in range(305):
                action = env.teacher_actions(raw['policy'])
                inputs.append(raw['policy'].detach().cpu())
                targets.append(action.detach().cpu())
                phases.append(env.phase.detach().cpu().clone())
                eligible.append((~seen).cpu().clone())
                raw,reward,term,timeout,extra = env.step(action)
                assert all(bool(torch.isfinite(v).all()) for v in raw.values())
                new = (term|timeout)&~seen
                for i in new.nonzero().flatten().tolist():
                    row = {k:v[i].item() for k,v in env.jump_snapshot.items()}
                    row.update(env=i,nominal=bool(env.full_dr.nominal_env_mask[i]),terminated=bool(term[i]),timeout=bool(timeout[i]))
                    episodes.append(row)
                successful[new] = env.jump_snapshot['success'][new]&~term[new]
                seen |= term|timeout
                if bool(seen.all()):
                    break
        assert bool(seen.all()) and bool(successful.any()), 'No complete successful demonstrations'
        mask = torch.stack(eligible)&successful.cpu()[None,:]
        policy = torch.stack(inputs)[mask].contiguous()
        actions = torch.stack(targets)[mask].contiguous()
        phase = torch.stack(phases)[mask].contiguous()
        metadata = dict(seed=seed,teacher_sha256=plan['teacher_sha256'],successful_episodes=int(successful.sum()),
            requested=env.num_envs,samples=len(policy),phase_counts=torch.bincount(phase,minlength=5).tolist(),
            native_success_only=True,optimizer_created=False,teacher_execution=True,
            note='Training demonstration collector; this is not a learned-policy evaluation')
        assert policy.shape[1] == 35 and actions.shape == (len(policy),6)
        torch.save(dict(policy=policy,actions=actions,phase=phase,metadata=metadata),job/'successful_demos.pt')
        put(job/'RESULT.json',dict(epoch=time.time(),metadata=metadata,episodes=episodes,
            dataset_sha256=hashlib.sha256((job/'successful_demos.pt').read_bytes()).hexdigest(),
            dataset_bytes=(job/'successful_demos.pt').stat().st_size,optimizer_updates=0))
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
