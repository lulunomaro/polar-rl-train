"""The same independent80 protocol, with a saved SuperMimic actor/history."""
from pathlib import Path
import argparse,sys
import torch

from . import newton_evaluate as protocol
from .supermimic_train import FORMAT,decode
from .config import runner_config
from .supermimic_newton import load_sources,FudanPPOResidualPolicy


class SavedPolicy:
    def __init__(self,teacher,payload,env):
        from supermimic_vendor_v2.networks import Policy
        cfg=payload['args']
        policy=Policy(35,3*cfg['goal_frames'],hist=cfg['hist'],z_dim=cfg['z_dim'],
            num_joints=6,hidden=tuple(cfg['policy_hidden']))
        self.actor=FudanPPOResidualPolicy(policy,teacher).to(env.device)
        self.actor.load_state_dict(payload['pi'],strict=True)
        self.actor.eval().requires_grad_(False)
        self.env=env;self.cfg=cfg;self.hist=torch.zeros(env.num_envs,cfg['hist'],35,device=env.device)

    def __call__(self,observation):
        obs=observation['policy']
        fresh=self.env.episode_length_buf==0
        shifted=torch.cat((self.hist[:,1:],obs[:,None]),1)
        self.hist=torch.where(fresh[:,None,None],obs[:,None].expand_as(self.hist),shifted)
        goal=obs[:,:3].repeat(1,self.cfg['goal_frames'])
        return self.actor(self.hist,goal)


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--binding',required=True)
    a,remaining=p.parse_known_args();load_sources(a.binding)
    def load(env,path,sha):
        from rsl_rl.runners import OnPolicyRunner
        payload=decode(path,sha)
        if payload['format']!=FORMAT:raise ValueError('Complete SuperMimic checkpoint required')
        runner=OnPolicyRunner(env,runner_config(),None,env.device)
        return SavedPolicy(runner.alg.actor,payload,env)
    argv=sys.argv
    try:
        sys.argv=[argv[0],*remaining]
        protocol.main(actor_loader=load)
    finally:
        sys.argv=argv


if __name__=='__main__':main()
