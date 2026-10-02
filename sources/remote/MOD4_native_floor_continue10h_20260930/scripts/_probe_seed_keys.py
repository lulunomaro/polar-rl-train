import sys, torch
p = sys.argv[1]
ck = torch.load(p, map_location='cpu', weights_only=False)
a = ck['actor_state_dict']
ks = sorted(a.keys())
print('n_keys', len(ks))
for k in ks:
    print('  ', k, tuple(a[k].shape))
print('NOTE:', str(ck.get('infos'))[:600])
