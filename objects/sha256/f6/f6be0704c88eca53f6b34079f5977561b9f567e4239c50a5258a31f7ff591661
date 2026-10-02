"""CPU test for joint permutation and genuine envelope clipping; no simulator."""
from types import SimpleNamespace
import torch
from actuator_clip_diagnostics import rating_clipped

requested = torch.tensor([[12., 18., 10., 16.]])  # hip/crank local order
gain = torch.tensor([[.95, 1.05, 1.04, .96]])
a = SimpleNamespace(computed_effort=requested, episode_scale=gain,
                    step_scale=torch.ones_like(gain), applied_effort=requested*gain)
assert not rating_clipped(a).any(), 'Unsaturated gain differences must not count as clipping'
policy_order = [1, 0, 3, 2]
old_unmapped = (requested[:, policy_order]*gain-a.applied_effort[:, policy_order]).abs() > .1
assert old_unmapped.all(), 'Fixture must catch mismatched per-joint gains'
a.applied_effort = a.applied_effort.clone()
a.applied_effort[:, 1] -= 2.
assert torch.equal(rating_clipped(a), torch.tensor([[False, True, False, False]]))
a.episode_scale[:] = 1.
a.applied_effort = requested.clone()
assert not rating_clipped(a).any()
a.step_scale[:, 0] = .98
a.applied_effort = requested*a.step_scale
assert not rating_clipped(a).any()
print('PASS: permutation, unsaturated gain, real clipping, nominal and step gains')
