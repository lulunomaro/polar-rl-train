import torch
torch.manual_seed(0)
N, w = 4096, 8.0
cmd = torch.empty(N).uniform_(-w, w)
act = cmd * torch.empty(N).uniform_(0.9, 1.1)          # holds BOTH directions
g_z = -torch.ones(N); rate = torch.zeros(N)
hard = (cmd.abs() >= 0.75 * w) & ((-g_z) > torch.cos(torch.tensor(0.35))) & (rate.abs() < 1.5)
c2 = cmd[hard].abs(); a2 = act[hard].abs()
ok2 = (torch.sign(cmd[hard]) == torch.sign(act[hard])) & (a2 > 0.75 * c2) & (a2 < 1.25 * c2)
g = torch.isfinite(a2); cg = cmd[hard][g]; og = ok2[g]
p = float(og[cg > 0].float().mean()); n = float(og[cg < 0].float().mean())
print("bidirectional policy: hold_pos=%.3f hold_neg=%.3f -> min=%.3f widens=%s"
      % (p, n, min(p, n), min(p, n) > 0.55))
assert min(p, n) > 0.55
# and the one-directional case again, explicitly
act1 = torch.where(cmd > 0, cmd * torch.empty(N).uniform_(0.9, 1.1), torch.full((N,), 1.5))
a1 = act1[hard].abs()
ok1 = (torch.sign(cmd[hard]) == torch.sign(act1[hard])) & (a1 > 0.75 * c2) & (a1 < 1.25 * c2)
g1 = torch.isfinite(a1); cg1 = cmd[hard][g1]; og1 = ok1[g1]
p1 = float(og1[cg1 > 0].float().mean()); n1 = float(og1[cg1 < 0].float().mean())
print("one-directional policy: hold_pos=%.3f hold_neg=%.3f -> min=%.3f widens=%s"
      % (p1, n1, min(p1, n1), min(p1, n1) > 0.55))
assert min(p1, n1) < 0.55 < p1
print("PASS: min-over-signs lets a genuine bidirectional hold through and blocks a one-sided one")
