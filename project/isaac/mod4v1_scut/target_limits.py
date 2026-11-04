"""Bound SCUT processed positions using the actual MOD4 motor intervals."""
import torch

from .config import LEGS


def project_leg_targets(targets, joint_names, contract, diff_min, diff_max):
    """Keep the original crank/hip constraint inside the four motor limits."""
    if len(joint_names) != 4 or set(joint_names) != set(LEGS):
        raise ValueError('Expected the four named MOD4 leg motors')
    limits = targets.new_tensor([contract['joints'][name]['limits_si'] for name in joint_names])
    low, high = limits.unbind(-1)
    value = torch.maximum(torch.minimum(targets, high), low)
    if diff_min > -1.e8:
        for side in ('left', 'right'):
            crank, hip = (joint_names.index(side+'_'+part) for part in ('crank', 'hip'))
            lower = torch.maximum(low[crank], value[:, hip]+diff_min)
            upper = torch.minimum(high[crank], value[:, hip]+diff_max)
            if bool((lower > upper).any()):
                raise ValueError('Motor limits and existing CAD difference have no intersection')
            value[:, crank] = torch.maximum(torch.minimum(value[:, crank], upper), lower)
    return value


def limited_action_type(original, contract):
    """Install before env construction, so D4 captures the bounded processor."""
    class ContractLimitedLegAction(original):
        def __init__(self, cfg, env):
            super().__init__(cfg, env)
            ids = self._joint_ids
            if isinstance(ids, slice):
                ids = list(range(len(self._asset.joint_names)))[ids]
            self._mod4_target_names = tuple(self._asset.joint_names[int(i)] for i in ids)
            if self._mod4_target_names != LEGS:
                raise ValueError('MOD4 leg action order differs from its explicit policy interface')

        def process_actions(self, actions):
            super().process_actions(actions)
            # D4 submits this processed target after the original scale/default
            # offset. Reapply its same CAD constraint inside the motor limits.
            self._processed_actions.copy_(project_leg_targets(
                self.processed_actions, self._mod4_target_names, contract,
                self.diff_min, self.diff_max))

    return ContractLimitedLegAction
