"""Use SCUT equations; continuous motors have no independent angular stop cost."""
import torch
from .shared import load, export
_source=load('rewards')
export(_source,globals())


class ScutRewards(_source.ScutRewards):
    def motor_stop_terms(self,airborne=False):
        # Upstream evaluates these helper outputs even when their weights are0.
        # Released v2 motors are continuous; no finite motor-angle boundary exists.
        for name in ('left_crank','left_hip','right_crank','right_hip'):
            if self.contract['joints'][name]['limits_si'] != [None,None]:
                raise ValueError('Unexpected finite v2 motor boundary: '+name)
        zeros=torch.zeros(self.num_envs,device=self.device)
        return zeros,zeros.clone(),zeros.clone()
