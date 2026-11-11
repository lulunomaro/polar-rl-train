import os, subprocess
from pathlib import Path
root=Path('/mnt/mod4_linux_durable_20261013/mod4v3_scut_target_native_20261107')
exp=root/'scut_rough_v0_22cap_1h_20261109_r2'
job=exp/'eval_flat_action_delay50_stage6b_60m_64env_20261110_r1'
log=exp/'eval_flat_action_delay50_stage6b_60m_64env_r1.log'
pid_file=exp/'eval_flat_action_delay50_stage6b_60m_64env_r1.pid'
resume=exp/'flat_action_delay50_stage6b_60m_20261110_r1'/'model_final.pt'
if job.exists(): raise SystemExit(f'job exists: {job}')
if log.exists(): raise SystemExit(f'log exists: {log}')
if pid_file.exists(): raise SystemExit(f'pid file exists: {pid_file}')
if not resume.is_file(): raise SystemExit(f'resume missing: {resume}')
env=dict(os.environ)
env.update(
    WARP_CACHE_PATH=str(root/'cache/warp'),
    XDG_CACHE_HOME=str(root/'cache'),
    TMPDIR=str(root/'tmp'),
    TMP=str(root/'tmp'),
    TEMP=str(root/'tmp'),
    PYTHONUNBUFFERED='1',
    CUDA_VISIBLE_DEVICES='0',
    OMNI_KIT_ACCEPT_EULA='YES',
    ISAACSIM_ACCEPT_EULA='Y',
    SPRING_DAMPING_FRACTION='0.25',
    EXTERNAL_DR_FRACTION='0.25',
    OBS_NOISE_FRACTION='0.25',
    OBS_DELAY_STEPS='1',
    ACTION_DELAY_STEPS='1',
    ACTION_DELAY_PROB='0.5',
)
cmd=[
    '/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python',
    '-B','-u','-m','mod4v3_ppo_v1.scut_flat_train',
    '--plan',str(exp/'PLAN_LOCAL.json'),
    '--mode','evaluate',
    '--job',str(job),
    '--num-envs','64',
    '--seconds','600',
    '--iterations','100000',
    '--resume',str(resume),
    '--profile','flat_action_delay',
]
with log.open('ab',buffering=0) as out:
    child=subprocess.Popen(
        cmd,
        cwd=str(exp/'support'),
        env=env,
        stdin=subprocess.DEVNULL,
        stdout=out,
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )
pid_file.write_text(str(child.pid)+'\n')
print('PID',child.pid)
print('JOB',job)
print('RESUME',resume)
