import os
import subprocess
from pathlib import Path

root = Path('/mnt/mod4_linux_durable_20261013/mod4v3_scut_target_native_20261107')
exp = root / 'scut_rough_v0_22cap_1h_20261109_r2'
job = exp / 'flat_robust_full_v1_2h_20261109_r2'
log = exp / 'train_flat_robust_full_v1_2h_20261109_r2.log'
pid_file = exp / 'train_flat_robust_full_v1_2h_20261109_r2.pid'
if job.exists():
    raise SystemExit(f'job exists: {job}')
if log.exists():
    raise SystemExit(f'log exists: {log}')
env = dict(os.environ)
env.update(
    WARP_CACHE_PATH=str(root / 'cache/warp'),
    XDG_CACHE_HOME=str(root / 'cache'),
    TMPDIR=str(root / 'tmp'), TMP=str(root / 'tmp'), TEMP=str(root / 'tmp'),
    PYTHONUNBUFFERED='1', CUDA_VISIBLE_DEVICES='0',
    OMNI_KIT_ACCEPT_EULA='YES', ISAACSIM_ACCEPT_EULA='Y',
)
cmd = [
    '/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python',
    '-B', '-u', '-m', 'mod4v3_ppo_v1.scut_flat_train',
    '--plan', str(exp / 'PLAN_LOCAL.json'),
    '--mode', 'train', '--job', str(job),
    '--num-envs', '4096', '--seconds', '7200', '--iterations', '20000',
    '--resume', str(exp / 'flat_robust_v1_2h_20261109_r1/model_030m.pt'),
    '--profile', 'flat_robust_full',
]
with log.open('ab', buffering=0) as out:
    child = subprocess.Popen(cmd, cwd=str(exp / 'support'), env=env,
        stdin=subprocess.DEVNULL, stdout=out, stderr=subprocess.STDOUT,
        start_new_session=True)
pid_file.write_text(str(child.pid) + '\n')
print('PID', child.pid)
