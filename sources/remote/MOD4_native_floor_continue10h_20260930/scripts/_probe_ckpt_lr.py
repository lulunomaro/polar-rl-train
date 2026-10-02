import sys, hashlib
p = sys.argv[1]
ck = __import__('torch').load(p, map_location='cpu', weights_only=False)
print('FILE', p)
print('KEYS', sorted(ck.keys()))
print('iter', ck.get('iter'))
opt = ck.get('optimizer_state_dict')
if opt is None:
    print('no optimizer_state_dict')
else:
    pg = opt['param_groups']
    print('param_groups:', [{k: v for k, v in g.items() if k in ('lr','initial_lr','eps','weight_decay')} for g in pg])
for k in ('learning_rate','schedule','desired_kl','mean_kl','infos'):
    if k in ck:
        v = ck[k]
        print(k, '=', str(v)[:200])
