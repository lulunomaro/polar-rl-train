# -*- coding: utf-8 -*-
"""Patch scripts/build_cc.py so leg/wheel actuator numbers come from a selectable
MOTOR PROFILE.  Default = datasheet-faithful DM8009/M3508; CC_MOTOR=legacy54 restores
the plant v3..v10 were trained on."""
import io

P = r"D:/claude2/fangzhen/scripts/build_cc.py"
s = io.open(P, encoding="utf-8").read()
n0 = len(s)

anchor = 'OUT = os.path.join(ROOT, "robot/out_cc")'
block = anchor + """

# --- motor profile -------------------------------------------------------------
# The plant v3..v10 were trained on copied the *reference* MJCF numbers (armature
# 0.035, forcerange +-54/+-5).  The datasheet-faithful profile instead uses the real
# motors that are in the CAD - see docs/MOTOR_PARAMS.md:
#   DM-J8009-2EC, 9:1  peak 40 N*m / rated 20 N*m, rotor inertia 1.95e-4 kg*m^2
#                      -> armature   = 1.95e-4*9^2   = 0.0158 kg*m^2
#                      -> no-load    335 rpm @48 V => 167 rpm @24 V = 17.5 rad/s
#   M3508  + 15.8:1    output stall 5.5 N*m, no-load ~63 rad/s (SCUT's own numbers)
# Friction follows the reference file: 1.5 N*m Coulomb on the crank, 0 on the thigh.
MOTOR_PROFILE = os.environ.get("CC_MOTOR", "dm8009").lower()
if MOTOR_PROFILE == "legacy54":
  LEG_ARMATURE, CRANK_FRICTION, THIGH_FRICTION = 0.035, 1.5, 1.5
  LEG_TORQUE, WHEEL_TORQUE = 54.0, 5.0
elif MOTOR_PROFILE == "dm8009":
  LEG_ARMATURE, CRANK_FRICTION, THIGH_FRICTION = 0.0158, 1.5, 0.0
  LEG_TORQUE, WHEEL_TORQUE = 40.0, 5.5
else:
  raise SystemExit("unknown CC_MOTOR profile: " + MOTOR_PROFILE)
print("motor profile:", MOTOR_PROFILE, "armature", LEG_ARMATURE,
      "leg torque", LEG_TORQUE, "wheel torque", WHEEL_TORQUE)"""
assert anchor in s, "anchor OUT"
s = s.replace(anchor, block, 1)

old = """    "rear1":  dict(rng=None, armature=0.035, damping=0.0, frictionloss=1.5),
    "front1": dict(rng=None, armature=0.035, damping=0.0, frictionloss=1.5),"""
new = """    "rear1":  dict(rng=None, armature=LEG_ARMATURE, damping=0.0, frictionloss=THIGH_FRICTION),
    "front1": dict(rng=None, armature=LEG_ARMATURE, damping=0.0, frictionloss=CRANK_FRICTION),"""
assert old in s, "anchor jp"
s = s.replace(old, new, 1)

old = """       '    <default class="motor"><joint damping="0.0" frictionloss="1.5" '
       'armature="0.035"/></default></default>',"""
new = """       '    <default class="motor"><joint damping="0.0" frictionloss="%g" '
       'armature="%g"/></default></default>' % (CRANK_FRICTION, LEG_ARMATURE),"""
assert old in s, "anchor default"
s = s.replace(old, new, 1)

old = """        out.append('    <motor name="%s_%s_ctrl" joint="%s_%s_joint" gear="1" '
                   'forcerange="-54 54" ctrlrange="-54 54"/>' % (side, jn, side, jn))"""
new = """        out.append('    <motor name="%s_%s_ctrl" joint="%s_%s_joint" gear="1" '
                   'forcerange="-%g %g" ctrlrange="-%g %g"/>'
                   % (side, jn, side, jn, LEG_TORQUE, LEG_TORQUE, LEG_TORQUE, LEG_TORQUE))"""
assert old in s, "anchor leg act"
s = s.replace(old, new, 1)

old = """    out.append('    <motor name="%s_wheel_ctrl" joint="%s_wheel_joint" gear="1" '
               'forcerange="-5 5" ctrlrange="-5 5"/>' % (side, side))"""
new = """    out.append('    <motor name="%s_wheel_ctrl" joint="%s_wheel_joint" gear="1" '
               'forcerange="-%g %g" ctrlrange="-%g %g"/>'
               % (side, side, WHEEL_TORQUE, WHEEL_TORQUE, WHEEL_TORQUE, WHEEL_TORQUE))"""
assert old in s, "anchor wheel act"
s = s.replace(old, new, 1)

io.open(P, "w", encoding="utf-8", newline="\n").write(s)
print("patched build_cc.py: %d -> %d chars" % (n0, len(s)))
