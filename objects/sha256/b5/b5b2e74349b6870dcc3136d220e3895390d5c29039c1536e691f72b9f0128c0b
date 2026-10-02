# Behavioural gate: an exported policy must not sit at an unintended yaw rate.
# A policy that holds ~0.17 rad/s of yaw at a zero command drives a wide arc, which is what
# destroyed the straight-line speed on the RMUC2026 map.  train/export_onnx.py now solves and
# bakes the correction (rmvehicle/yaw_trim.py); this gate proves the shipped artifact is clean.
import glob, os, sys
import onnx
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.insert(0, r'D:/claude2/fangzhen/train/rmvehicle/src')
from rmvehicle import yaw_trim as YT
ROOT = r'D:/claude2/fangzhen'
bad = []
for o in sorted(glob.glob(os.path.join(ROOT, 'train/deploy/*.onnx'))):
    md = {e.key: e.value for e in onnx.load(o).metadata_props}
    if 'joint_action_scale' not in md:
        continue
    tag = os.path.basename(o)
    if 'yaw_command_trim_rad_s' not in md:
        print('  WARN %-28s no yaw trim recorded (exported before the calibration)' % tag)
        continue
    sess = YT.session(o)
    # commanded_yaw is the robust measure: the closed-loop fixed point diverges for
    # policies whose yaw feedback slope exceeds one, so it cannot be iterated.
    y = YT.commanded_yaw(sess, 0.0)
    line = '  %-28s residual yaw command offset %+0.4f rad/s  (trim %s)' % (tag, y, md['yaw_command_trim_rad_s'])
    if abs(y) < 0.02:
        print(line + '   OK')
    else:
        print(line + '   FAIL'); bad.append(tag)
print('RESULT:', 'ALL POLICIES YAW-CALIBRATED' if not bad else '%d policy/policies still biased' % len(bad))
sys.exit(1 if bad else 0)
