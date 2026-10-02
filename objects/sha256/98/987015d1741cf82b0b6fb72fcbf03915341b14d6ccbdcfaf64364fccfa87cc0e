# Unit test for sim2real/safety_monitor.py - the RC_WheelLeg-style four-level guard,
# re-tuned to this vehicle (docs/HOWTO.md sec.38.16).  Run: python scripts/test_safety_monitor.py
import sys
sys.path.insert(0, 'D:/claude2/fangzhen/sim2real')
import numpy as np
from safety_monitor import SafetyMonitor, SafetyLevel

FAIL = []


def expect(name, got, want):
    ok = (got == want)
    msg = ('OK   ' + name) if ok else ('FAIL ' + name + '  got ' + str(got) + ' want ' + str(want))
    print(msg)
    if not ok:
        FAIL.append(name)


m = SafetyMonitor()
g = (0.0, 0.0, -1.0)
expect('standing is NORMAL', m.check([0.2, 0.1, 0.2, 0.1], [1.0, 1.0], (0.1, 0.0, 0.2), g).level,
       SafetyLevel.NORMAL)
expect('20 deg tilt still NORMAL', m.check(projected_gravity=(0.34, 0, -0.94)).level, SafetyLevel.NORMAL)
expect('40 deg tilt raises CLIP (warn band)', m.check(projected_gravity=(0.64, 0, -0.77)).level,
       SafetyLevel.CLIP)
expect('70 deg tilt is BRAKE', m.check(projected_gravity=(0.94, 0, -0.34)).level, SafetyLevel.BRAKE)
expect('12 rad/s spin is BRAKE', m.check(gyro=(1, 1, 12), projected_gravity=g).level, SafetyLevel.BRAKE)
m.reset()
d = m.check([2.6, 0.1, 0.2, 0.1], None, (0, 0, 0), g)
expect('a 2.6 rad leg target is CLIP', d.level, SafetyLevel.CLIP)
expect('and it is clipped to the band', round(float(np.max(np.abs(d.clipped_target))), 2), 2.0)
m.reset()
for i in range(3):
    d = m.check([2.6, 0.1, 0.2, 0.1], None, (0, 0, 0), g)
expect('three consecutive clips escalate to BRAKE', d.level, SafetyLevel.BRAKE)
m.reset()
for i in range(19):
    d = m.check(None, [7.0, 7.0], (0, 0, 0), g)
expect('19 saturated wheel ticks are not yet BRAKE', d.level, SafetyLevel.CLIP)
d = m.check(None, [7.0, 7.0], (0, 0, 0), g)
expect('the 20th one is BRAKE', d.level, SafetyLevel.BRAKE)
m.reset()
for i in range(30):
    d = m.check(None, [1.0, 1.0], (0, 0, 0), g)
expect('a clean stretch resets the saturation counter', d.level, SafetyLevel.NORMAL)
expect('E-stop always wins',
       m.check([0.2, 0.2, 0.2, 0.2], None, (0, 0, 0), g, estop=True).level, SafetyLevel.ESTOP)
print()
print('RESULT: ' + ('ALL PASS' if not FAIL else str(len(FAIL)) + ' checks FAILED'))
sys.exit(1 if FAIL else 0)
