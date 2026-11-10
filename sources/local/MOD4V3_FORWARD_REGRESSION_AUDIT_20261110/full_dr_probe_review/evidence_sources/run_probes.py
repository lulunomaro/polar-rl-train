import os, subprocess, json, sys
from pathlib import Path

root = Path('/mnt/mod4_linux_durable_20261013/mod4v3_scut_target_native_20261107')
probe = root / 'scut_rough_v0_22cap_1h_20261109_r2' / 'full_dr_probe_20261110_r1'
parent = root / 'scut_flat_v2_22cap_1h_20261108_r3' / 'job' / 'model_periodic.pt'
python = '/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python'

runs = [
    ('base_ext_on', 'base', 1),
    ('base_ext_off', 'base', 0),
    ('scut_ext_on', 'scut', 1),
    ('scut_ext_off', 'scut', 0),
]
summary = []
for name, plan_name, external in runs:
    support = probe / ('support_base' if plan_name == 'base' else 'support_scut_solver')
    job = probe / name
    log = probe / f'{name}.log'
    if job.exists() or log.exists():
        raise SystemExit(f'refusing to reuse {name}')
    env = dict(os.environ)
    env.update(
        WARP_CACHE_PATH=str(root/'cache/warp'), XDG_CACHE_HOME=str(root/'cache'),
        TMPDIR=str(root/'tmp'), TMP=str(root/'tmp'), TEMP=str(root/'tmp'),
        PYTHONUNBUFFERED='1', CUDA_VISIBLE_DEVICES='0',
        OMNI_KIT_ACCEPT_EULA='YES', ISAACSIM_ACCEPT_EULA='Y',
        FULL_DR_RAMP_STEPS='1', FULL_DR_MASS='1', FULL_DR_MATERIAL='1',
        FULL_DR_JOINT_FRICTION='1', FULL_DR_GAS='1', FULL_DR_ACTION_DELAY='1',
        FULL_DR_OBS_DELAY='1', FULL_DR_OBS_NOISE='1',
        FULL_DR_EXTERNAL=str(external), FULL_DR_PROBE_LOG='1',
    )
    cmd = [
        python, '-B', '-u', '-m', 'mod4v3_ppo_v1.scut_flat_train',
        '--plan', str(probe / f'PLAN_{plan_name}.json'),
        '--mode', 'evaluate', '--job', str(job),
        '--num-envs', '4096', '--seconds', '60', '--iterations', '100000',
        '--fixed-probe-steps', '300', '--resume', str(parent),
        '--profile', 'flat_robust_full',
    ]
    with log.open('xb', buffering=0) as out:
        proc = subprocess.run(cmd, cwd=str(support), env=env, stdin=subprocess.DEVNULL,
                              stdout=out, stderr=subprocess.STDOUT)
    result = {'name': name, 'plan': plan_name, 'external': external, 'returncode': proc.returncode,
              'job': str(job), 'log': str(log)}
    result_path = job / 'RESULT.json'
    if result_path.exists():
        r = json.loads(result_path.read_text())
        result.update(done_totals=r.get('done_totals'), episodes=r.get('episodes'),
                      requested=r.get('requested'), steps=r.get('steps'),
                      final_stable_count=r.get('final_stable_count'))
    summary.append(result)
    print(json.dumps(result, ensure_ascii=False), flush=True)

(probe / 'SUMMARY.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n')
print('SUMMARY_WRITTEN', flush=True)
