import os, sys, subprocess, glob, re, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
R = r'D:/claude2/fangzhen'
os.environ.update(dict(TMP=r'D:\tmp', TEMP=r'D:\tmp', TMPDIR=r'D:\tmp',
                       PYTHONIOENCODING='utf-8', PIP_CACHE_DIR=r'D:\pipcache',
                       RM_MOTOR='dm8009', CC_MOTOR='dm8009',
                       # v16 trained before the command-delay DR existed -> export/verify without it
                       RM_DELAY_MIN_LAG='0', RM_DELAY_MAX_LAG='0', RM_DELAY_HOLD_PROB='0.0',
                       # the v16 env knobs, copied from scripts/run_v16.ps1
                       RM_WZ_MAX='14.0', RM_WZ0='6.0', RM_WHEEL_SCALE='55.0',
                       RM_GYRO_WIDE_W='1.5', RM_GYRO_BAND='6.0',
                       RM_SKILL_SPLIT='1', RM_SKILL_GYRO_FRAC='0.25', RM_SKILL_WZ_LOCO='2.0',
                       RM_TERRAIN_CAP_H='0.20', RM_FLAT_PROP='0.45',
                       RM_RISE_MIN='0.06', RM_RISE_MAX='0.16', RM_JUMP_P='0.25'))
PY = os.path.join(R, '.venv-train', 'Scripts', 'python.exe')
TRAIN = os.path.join(R, 'train')
cands = sorted(glob.glob(os.path.join(TRAIN, 'logs/rsl_rl/rm_cc_v16/*/model_*.pt')),
               key=lambda p: int(re.search(r'model_(\d+)', p).group(1)))
CK = cands[-1]
print('### v16 checkpoint:', CK, time.strftime('%H:%M:%S'), flush=True)
KEEP = re.compile(r'wrote|metadata contract|action sample|OK:|cmd wz|rev/s|peak|SUMMARY|UPRIGHT|alive|cmd vx|\| |DRIFT|drift|EXIT|Traceback|Error|error', re.I)
def step(tag, args, cwd=TRAIN, tail=None):
    print('=== ' + tag + ' ===', flush=True)
    p = subprocess.run([PY] + args, cwd=cwd, capture_output=True, text=True, encoding='utf-8', errors='replace')
    out = (p.stdout or '') + (p.stderr or '')
    keep = [l for l in out.splitlines() if KEEP.search(l)]
    for l in (keep or out.splitlines())[-(tail or 26):]:
        print('   ' + l[:170], flush=True)
    print('   rc=%d' % p.returncode, flush=True)
    return p.returncode
step('1. export ONNX', ['export_onnx.py', '--task', 'RMVehicle-CC-Field-v0',
                        '--checkpoint', CK, '--out', 'deploy/rm_cc_v16_final.onnx'])
step('2. contract drift gate', [os.path.join(R, 'scripts', 'check_contract_drift.py')], cwd=R)
step('3. gyro ladder on flat (target 2 rev/s = 12.57 rad/s)',
     ['verify_skills.py', '--task', 'RMVehicle-CC-Skills-v0', '--checkpoint', CK,
      '--num-envs', '64', '--only', 'gyro', '--gyro-ladder', '6,10,12,14,-6,-10,-14',
      '--out', 'deploy/skills_v16_gyro.json'])
step('4a. run on the RMUC2026 map',
     ['verify_skills.py', '--task', 'RMVehicle-CC-Field-v0', '--checkpoint', CK,
      '--num-envs', '64', '--only', 'run', '--out', 'deploy/skills_v16_field_run.json'])
step('4b. jump on the RMUC2026 map',
     ['verify_skills.py', '--task', 'RMVehicle-CC-Field-v0', '--checkpoint', CK,
      '--num-envs', '64', '--only', 'jump', '--out', 'deploy/skills_v16_field_jump.json'])
step('5. GPU play video', ['-m', 'mjlab.scripts.play', 'RMVehicle-CC-Field-v0',
                           '--checkpoint-file', CK, '--video', 'True',
                           '--video-length', '600', '--video-width', '960',
                           '--video-height', '540'], tail=12)
print('FINISH_V16_DONE', time.strftime('%H:%M:%S'), flush=True)
