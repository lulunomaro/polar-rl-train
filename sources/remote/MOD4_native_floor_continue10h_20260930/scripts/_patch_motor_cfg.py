# -*- coding: utf-8 -*-
"""Give the training/deploy config a datasheet-faithful motor profile.

  RM_MOTOR=dm8009   (default)  DM-J8009-2EC 9:1 legs: 40 N*m stall, 17 rad/s no-load,
                               M3508+C620 wheels: 5.5 N*m, 63.4 rad/s,
                               actuators become mjlab DcMotorActuator (torque-speed curve)
  RM_MOTOR=legacy54            exactly the plant v3..v10 trained on (50.9 / 10 N*m,
                               builtin position/velocity actuators, no speed limit)

Joint armature/friction come from the MJCF (scripts/build_cc.py, CC_MOTOR).
"""
import io

NAMES = r"D:/claude2/fangzhen/train/rmvehicle/src/rmvehicle/names.py"
RCFG = r"D:/claude2/fangzhen/train/rmvehicle/src/rmvehicle/robot_cfg.py"

s = io.open(NAMES, encoding="utf-8").read()
n0 = len(s)
anchor = "from dataclasses import dataclass"
assert anchor in s, "names: import anchor"
block = '''import os

# --- motor profile (mirrors scripts/build_cc.py's CC_MOTOR) -------------------
# See docs/MOTOR_PARAMS.md for the source of every number below.
MOTOR_PROFILE = os.environ.get("RM_MOTOR", "dm8009").lower()
_MOTORS = {
  #                leg stall  leg vmax   wheel stall  wheel vmax  (N*m, rad/s)
  "dm8009":   dict(leg_effort=40.0, leg_velocity=17.0,
                   wheel_effort=5.5, wheel_velocity=63.4),
  "legacy54": dict(leg_effort=50.9, leg_velocity=100.0,
                   wheel_effort=10.0, wheel_velocity=25.0),
}
if MOTOR_PROFILE not in _MOTORS:
  raise SystemExit("unknown RM_MOTOR profile: " + MOTOR_PROFILE)
MOTORS = _MOTORS[MOTOR_PROFILE]
LEG_EFFORT = MOTORS["leg_effort"]
LEG_VELOCITY = MOTORS["leg_velocity"]
WHEEL_EFFORT_P = MOTORS["wheel_effort"]
WHEEL_VELOCITY = MOTORS["wheel_velocity"]

''' + anchor
s = s.replace(anchor, block, 1)
old = "  leg_effort=(50.9, 50.9, 50.9, 50.9),"
assert old in s, "names: leg_effort"
s = s.replace(old, "  leg_effort=(LEG_EFFORT,) * 4,", 1)
io.open(NAMES, "w", encoding="utf-8", newline="\n").write(s)
print("names.py %d -> %d" % (n0, len(s)))

r = io.open(RCFG, encoding="utf-8").read()
m0 = len(r)
old = "from mjlab.actuator import BuiltinPositionActuatorCfg, BuiltinVelocityActuatorCfg"
new = ("from mjlab.actuator import (\n"
       "  BuiltinPositionActuatorCfg,\n"
       "  BuiltinVelocityActuatorCfg,\n"
       "  DcMotorActuatorCfg,\n)")
assert old in r, "rcfg: import"
r = r.replace(old, new, 1)

old = "from .names import CC, OPEN, ModelNames"
new = ("from .names import (CC, LEG_EFFORT, LEG_VELOCITY, MOTOR_PROFILE, OPEN,\n"
       "                    WHEEL_EFFORT_P, WHEEL_VELOCITY, ModelNames)")
assert old in r, "rcfg: names import"
r = r.replace(old, new, 1)

old = "WHEEL_KD, WHEEL_EFFORT = 1.5, 10.0"
new = "WHEEL_KD = 1.5\nWHEEL_EFFORT = WHEEL_EFFORT_P"
assert old in r, "rcfg: wheel effort"
r = r.replace(old, new, 1)

old = """  legs = []
  for pat, eff in zip(names.leg_actuators, names.leg_effort):
    legs.append(BuiltinPositionActuatorCfg(
      target_names_expr=(pat,), stiffness=LEG_KP, damping=LEG_KD, effort_limit=eff))
  wheels = [BuiltinVelocityActuatorCfg(
    target_names_expr=names.wheel_actuators, damping=WHEEL_KD, effort_limit=WHEEL_EFFORT)]"""
new = """  legs = []
  if MOTOR_PROFILE == "dm8009":
    # DM-J8009-2EC 9:1: 40 N*m at stall falling linearly to 0 at 17 rad/s (24 V bus).
    # An explicit (ideal) PD is also what the onboard DM drive runs, at 1 kHz.
    for pat, eff in zip(names.leg_actuators, names.leg_effort):
      legs.append(DcMotorActuatorCfg(
        target_names_expr=(pat,), stiffness=LEG_KP, damping=LEG_KD,
        effort_limit=eff, saturation_effort=eff, velocity_limit=LEG_VELOCITY))
    wheels = [DcMotorActuatorCfg(
      target_names_expr=names.wheel_actuators, stiffness=0.0, damping=WHEEL_KD,
      effort_limit=WHEEL_EFFORT, saturation_effort=WHEEL_EFFORT,
      velocity_limit=WHEEL_VELOCITY)]
  else:
    for pat, eff in zip(names.leg_actuators, names.leg_effort):
      legs.append(BuiltinPositionActuatorCfg(
        target_names_expr=(pat,), stiffness=LEG_KP, damping=LEG_KD, effort_limit=eff))
    wheels = [BuiltinVelocityActuatorCfg(
      target_names_expr=names.wheel_actuators, damping=WHEEL_KD,
      effort_limit=WHEEL_EFFORT)]"""
assert old in r, "rcfg: actuators"
r = r.replace(old, new, 1)
io.open(RCFG, "w", encoding="utf-8", newline="\n").write(r)
print("robot_cfg.py %d -> %d" % (m0, len(r)))
print("ALL PATCHES APPLIED")
