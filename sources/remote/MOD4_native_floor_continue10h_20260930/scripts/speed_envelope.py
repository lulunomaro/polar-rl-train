# Speed envelope of an exported policy, measured in plain native MuJoCo with the
# deployment control law.  Answers the practical question behind the map-running gap:
# what ground speed does each commanded vx actually produce, forward AND reverse?
import os, re, subprocess, sys
import numpy as np
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
R = r'D:/claude2/fangzhen'
PY = os.path.join(R, '.venv/Scripts/python.exe')
HARNESS = os.path.join(R, 'sim_mujoco/onnx_play.py')
ONNX = sys.argv[1] if len(sys.argv) > 1 else os.path.join(R, 'train/deploy/rm_cc_v16_final.onnx')
SCENE = sys.argv[2] if len(sys.argv) > 2 else os.path.join(R, 'robot/out_cc_linkfix/scene_cc.xml')
ROWS = re.compile(r'^\s+([0-9]+\.[0-9])\s+(-?[0-9.]+)\s+(-?[0-9.]+)\s+(-?[0-9.]+)\s+(-?[0-9.]+)\s+(-?[0-9.]+)')
print('scene  %s' % SCENE)
print('policy %s' % ONNX)
print('  cmd_vx  cmd_wz | steady vx (last 3 s) | wheels rad/s | travel m | max tilt | verdict')
for vx, wz in ((0.0, 0.0), (0.5, 0.0), (1.0, 0.0), (1.8, 0.0), (2.8, 0.0),
                (-0.5, 0.0), (-1.0, 0.0), (-1.8, 0.0), (1.0, 1.0), (1.0, -1.0)):
    p = subprocess.run([PY, HARNESS, '--model', SCENE, '--onnx', ONNX,
                        '--effort-mode', 'qfrc', '--train-contacts',
                        '--seconds', '12', '--settle', '0',
                        '--const=' + '%g,%g,0.22' % (vx, wz)],
                       capture_output=True, text=True, encoding='utf-8', errors='replace')
    out = (p.stdout or '') + (p.stderr or '')
    rows = []
    for l in out.splitlines():
        m = ROWS.match(l)
        if m:
            rows.append([float(x) for x in m.groups()])
    r = np.array(rows) if rows else np.zeros((0, 6))
    verdict = re.search(r'RESULT: (\w+)', out)
    if len(r) < 4:
        print('   %+5.2f %+5.2f | no trajectory rows (%s)' % (vx, wz, verdict.group(1) if verdict else '?'))
        continue
    tail = r[r[:, 0] > r[-1, 0] - 3.0]
    steady = float(np.mean(tail[:, 4]))
    wheels = float(np.mean(tail[:, 5]))
    travel = float(r[-1, 1] - r[0, 1])
    tilt = float(np.max(np.abs(r[:, 3])))
    print('   %+5.2f %+5.2f |  %+6.2f m/s (cmd %+5.2f, %3.0f%%) |  %+6.1f    | %+7.2f   | %5.1f    | %s' % (
          vx, wz, steady, vx, 100 * steady / vx if vx else 0, wheels, travel, tilt,
          verdict.group(1) if verdict else '?'))
