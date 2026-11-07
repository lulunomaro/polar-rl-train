import os, subprocess
from pathlib import Path
root=Path('/mnt/mod4_linux_durable_20261013/mod4v3_scut_target_native_20261107')
job=root/'scut_flat_v30_v28warm_1h_20261108_r1'
log=root/'scut_flat_v30_v28warm_1h_20261108_r1.log'
if job.exists(): raise SystemExit(f'job exists: {job}')
if log.exists(): raise SystemExit(f'log exists: {log}')
env=dict(os.environ)
env.update(WARP_CACHE_PATH=str(root/'cache/warp'),XDG_CACHE_HOME=str(root/'cache'),TMPDIR=str(root/'tmp'),TMP=str(root/'tmp'),TEMP=str(root/'tmp'),PYTHONUNBUFFERED='1',CUDA_VISIBLE_DEVICES='0',OMNI_KIT_ACCEPT_EULA='YES',ISAACSIM_ACCEPT_EULA='Y')
cmd=['/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python','-B','-u','-m','mod4v3_ppo.scut_flat_train','--plan',str(root/'PLAN_LOCAL.json'),'--mode','train','--job',str(job),'--num-envs','4096','--seconds','3600','--iterations','6528','--resume',str(root/'checkpoints/mod4v3_v28_flat_scut_order.pt')]
with open(log,'ab',buffering=0) as out:
    child=subprocess.Popen(cmd,cwd=str(root/'support'),env=env,stdin=subprocess.DEVNULL,stdout=out,stderr=subprocess.STDOUT,start_new_session=True)
(root/'scut_flat_v30_v28warm_1h_20261108_r1.pid').write_text(str(child.pid)+'\n')
print('PID',child.pid)
