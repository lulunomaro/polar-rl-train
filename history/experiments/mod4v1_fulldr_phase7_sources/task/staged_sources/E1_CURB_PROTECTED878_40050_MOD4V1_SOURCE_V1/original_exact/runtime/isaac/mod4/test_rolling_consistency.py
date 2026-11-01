"""Meaningful math/gating checks; GPU/SDK lifecycle needs actual readback."""
import json
import torch
from rolling_consistency import consistency_cost

axle = torch.tensor([[[0., 1., 0.], [0., 1., 0.]]])
cmd = torch.tensor([[0., 0., 5.]])
force = torch.tensor([[70., 70.]])
vel = torch.tensor([[[.15, 0., 0.], [.15, 0., 0.]]])
cost = lambda v=vel, a=axle, f=force, c=cmd: consistency_cost(v, a, f, c)[0]
assert torch.allclose(cost(), torch.ones(1))
assert cost(vel * 0).item() == 0.
assert cost(vel * -1).item() == cost().item()
assert cost(c=cmd * -1).item() == cost().item()
assert cost(c=torch.tensor([[.3, 0., .5]])).item() == 0.
assert cost(c=torch.tensor([[0., 0., 2.]])).item() == 0.
assert cost(c=torch.tensor([[0., 0., 0.]])).item() == 0.
assert cost(f=force * 0).item() == .25
v = vel.clone(); v[:, 1, 0] = 100.
assert cost(v, f=torch.tensor([[70., 0.]])).item() == 1.125
assert cost(vel * 100).item() == 4.
assert cost(torch.tensor([[[0., 2., 0.], [0., 2., 0.]]])).item() == 0.
assert cost(vel, axle * -1).item() == cost().item()
assert torch.isfinite(cost(a=torch.tensor([[[0., 0., 1.], [0., 0., 1.]]]))).all()
# Rotate both point velocity and axle90deg around worldz: cost must be invariant.
rot = torch.tensor([[0., -1., 0.], [1., 0., 0.], [0., 0., 1.]])
assert torch.allclose(cost(vel @ rot.T, axle @ rot.T), cost())
# Reference consistency, using local arms avoids world-coordinate cancellation.
w = torch.tensor([[[0., 5., 5.], [0., -5., 5.]]])
arm = torch.tensor([[[0., 0., -.0637], [0., 0., -.0637]]])
com = torch.tensor([[[0., .001668, 0.], [0., -.001668, 0.]]])
link_v = vel.clone()
com_v = link_v + torch.cross(w, com, dim=-1)
assert torch.allclose(link_v + torch.cross(w, arm, dim=-1),
                      com_v + torch.cross(w, arm - com, dim=-1), atol=1e-7)
assert torch.equal(force, torch.tensor([[70., 70.]])) and torch.equal(vel[..., 0], torch.tensor([[.15, .15]]))
print(json.dumps(dict(passed=16, scope="CPU cost/reference/gating checks; no SDK or policy certification")))
