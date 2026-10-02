import os, sys, subprocess, glob, re, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
R = r'D:/claude2/fangzhen'
os.environ.update(dict(TMP=r'D:\tmp', TEMP=r'D:\tmp', TMPDIR=r'D:\tmp',
                       PYTHONIOENCODING='utf-8', PIP_CACHE_DIR=r'D:\pipcache',
                       RM_MOTOR='dm8009', CC_MOTOR='dm8009',
                       # v17a trained before the command-delay DR existed -> export/verify without it
                       RM_DELAY_MIN_LAG='0', RM_DELAY_MAX_LAG='0', RM_DELAY_HOLD_PROB='0.0',
                       # the v17a env knobs, copied from scripts/run_v17a.ps1
                       RM_WZ_MAX='14.0', RM_WZ0='6.0', RM_WHEEL_SCALE='55.0',
                       RM_GYRO_WIDE_W='1.5', RM_GYRO_BAND='6.0',
                       RM_SKILL_SPLIT='1', RM_SKILL_GYRO_FRAC='0.25', RM_SKILL_WZ_LOCO='2.0',
                       RM_TERRAIN_CAP_H='0.20', RM_FLAT_PROP='0.45',
                       RM_RISE_MIN='0.06', RM_RISE_MAX='0.16', RM_JUMP_P='0.25'))
PY = os.path.join(R, '.venv-train', 'Scripts', 'python.exe')
TRAIN = os.path.join(R, 'train')
import io
# ---- wait for the v17a runner to write its exit line (the runner prints V17_EXIT ...)
A_LOG = os.path.join(R, 'docs/_cc_v17a.log')
print('waiting for v17a to finish ...', flush=True)
while True:
    try:
        tail = io.open(A_LOG, encoding='utf-8', errors='replace').read()[-3000:]
    except Exception:
        tail = ''
    if 'V17_EXIT' in tail:
        break
    time.sleep(60)
print('v17a done at ' + time.strftime('%H:%M:%S'), flush=True)
cands = sorted(glob.glob(os.path.join(TRAIN, 'logs/rsl_rl/rm_cc_v17a/*/model_*.pt')),
               key=lambda p: int(re.search(r'model_(\d+)', p).group(1)))
CK = cands[-1]
print('### v17a checkpoint:', CK, time.strftime('%H:%M:%S'), flush=True)
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
                        '--checkpoint', CK, '--out', 'deploy/rm_cc_v17a_final.onnx'])
step('2. contract drift gate', [os.path.join(R, 'scripts', 'check_contract_drift.py')], cwd=R)
step('3. gyro ladder on flat (target 2 rev/s = 12.57 rad/s)',
     ['verify_skills.py', '--task', 'RMVehicle-CC-Skills-v0', '--checkpoint', CK,
      '--num-envs', '64', '--only', 'gyro', '--gyro-ladder', '6,10,12,14,-6,-10,-14',
      '--out', 'deploy/skills_v17a_gyro.json'])
step('4a. run on the RMUC2026 map',
     ['verify_skills.py', '--task', 'RMVehicle-CC-Field-v0', '--checkpoint', CK,
      '--num-envs', '64', '--only', 'run', '--out', 'deploy/skills_v17a_field_run.json'])
step('4b. jump on the RMUC2026 map',
     ['verify_skills.py', '--task', 'RMVehicle-CC-Field-v0', '--checkpoint', CK,
      '--num-envs', '64', '--only', 'jump', '--out', 'deploy/skills_v17a_field_jump.json'])
step('5. GPU play video', ['-m', 'mjlab.scripts.play', 'RMVehicle-CC-Field-v0',
                           '--checkpoint-file', CK, '--video', 'True',
                           '--video-length', '600', '--video-width', '960',
                           '--video-height', '540'], tail=12)
step("10. consolidated verification report",
     [os.path.join(R, "scripts/verify_all.py"),
      os.path.join(TRAIN, "deploy/rm_cc_v17a_final.onnx")], cwd=R, tail=6)
print('FINISH_V16_DONE', time.strftime('%H:%M:%S'), flush=True)

# ---- gates added on 2026-09-06: the action-slot order and the staged plant
step("2b. action-order gate", [os.path.join(R, "scripts/check_action_order.py")], cwd=R, tail=10)
step("2c. plant sync gate",
     [os.path.join(R, "scripts/sync_plant_assets.py"), "--check",
      "--src", "robot/out_cc_linkfix/rm_vehicle_cc.xml"], cwd=R, tail=3)

# ---- the new deployment gate: the exported policy must BALANCE and spin >= 2 rev/s in
#      plain native MuJoCo with the deployment control law on the link-fixed plant.
for script in ("teleop", "spin", "jump"):
    step("8. native-MuJoCo gate /" + script,
         [os.path.join(R, "sim_mujoco/onnx_play.py"),
          "--model", os.path.join(R, "robot/out_cc_linkfix/scene_cc.xml"),
          "--onnx", os.path.join(TRAIN, "deploy/rm_cc_v17a_final.onnx"),
          "--effort-mode", "qfrc", "--train-contacts",
          "--seconds", "30" if script == "spin" else "20",
          "--settle", "0", "--script", script] +
         ([] if script != "jump" else ["--const=0,0,0.22"]),
         cwd=R, tail=12)

# The running skill measured properly: steady speed per command through the deployment
# control law.  This is the number that tracks the v18 reward-width experiment.
step("8b. speed envelope (flat, deployment control law)",
     [os.path.join(R, "scripts/speed_envelope.py"),
      os.path.join(TRAIN, "deploy/rm_cc_v17a_final.onnx"),
      os.path.join(R, "robot/out_cc_linkfix/scene_cc.xml")], cwd=R, tail=14)

# ---- seed and launch v17b = same plant + the 0-4 ms actuator delay DR (one new group)
os.environ.update(RM_DELAY_MIN_LAG="0", RM_DELAY_MAX_LAG="2",
                  RM_DELAY_HOLD_PROB="0.75")
step("9. seed v17b from v17a",
     [os.path.join(R, "scripts/seed_v15.py"), "--src", CK,
      "--dst-dir", "logs/rsl_rl/rm_cc_v17b/seed_from_v17a"], tail=6)
subprocess.Popen(["powershell", "-NoProfile", "-ExecutionPolicy",
                  "Bypass", "-File",
                  os.path.join(R, "scripts/run_v17b.ps1")],
                 stdout=open(os.path.join(R, "docs/_cc_v17b.log"), "w"),
                 stderr=open(os.path.join(R, "docs/_cc_v17b.log.err"), "w"))
print("v17b launched", time.strftime("%H:%M:%S"), flush=True)
