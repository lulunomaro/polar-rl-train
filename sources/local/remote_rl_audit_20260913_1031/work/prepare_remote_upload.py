from pathlib import Path
root=Path('/home/egde/rl_repair_packages')
if root.resolve()!=root:
 raise RuntimeError('package root resolves elsewhere')
root.mkdir(exist_ok=True)
name='MOD4_RL_FIX_20260913_1500'
if (root/name).exists() or (root/(name+'.tar.gz')).exists():
 raise FileExistsError('package name already exists; do not overwrite')
print('UPLOAD_DIRECTORY='+str(root))
