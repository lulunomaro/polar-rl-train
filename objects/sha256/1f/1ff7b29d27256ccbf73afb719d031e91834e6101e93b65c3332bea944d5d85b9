import io
R = r"D:\claude2\fangzhen"

# ---------- 1) wheel action scale: the real bottleneck for a fast gyro ----------
F = R + r"\train\rmvehicle\src\rmvehicle\robot_cfg.py"
s = io.open(F, encoding="utf-8").read()
old = "WHEEL_ACTION_SCALE = 10.0             # rad/s per unit action"
new = ('# A counter-rotating spin at yaw rate wz needs wheel speed wz*half_track/wheel_r.\n'
       '# With half_track 0.270 m and wheel_r 0.073 m that is 3.70 rad/s of wheel per rad/s of\n'
       '# yaw, so 14 rad/s of yaw needs 51.8 rad/s per wheel - the M3508 no-load limit is 63.4.\n'
       '# At the old scale of 10 the policy would have to output +-5.2, far outside its usable\n'
       '# range, so the commanded spin could never be reached.  20 puts 14 rad/s at action 2.6.\n'
       'import os as _os\n'
       'WHEEL_ACTION_SCALE = float(_os.environ.get("RM_WHEEL_SCALE", "20.0"))')
assert s.count(old) == 1, "wheel scale anchor"
io.open(F, "w", encoding="utf-8").write(s.replace(old, new))
print("robot_cfg: WHEEL_ACTION_SCALE env-gated, default 20")

# ---------- 2) command range, spin reward, and actuator-side DR ----------
F = R + r"\train\rmvehicle\src\rmvehicle\env_cfgs.py"
s = io.open(F, encoding="utf-8").read()
def rep(old, new, tag):
    global s
    assert s.count(old) == 1, "anchor missing: " + tag
    s = s.replace(old, new)

rep('''  vx = (-1.5, 2.8) if skills else (-1.0, 1.8)
  wz = (-6.0, 6.0) if skills else (-1.0, 1.0)''',
    '''  vx = (-1.5, 2.8) if skills else (-1.0, 1.8)
  # 小陀螺.  The kinematic ceiling is wheel_no_load*wheel_r/half_track =
  # 63.4*0.073/0.270 = 17.1 rad/s, and the SJTU design puts a 360-deg hip on the vehicle
  # precisely so the legs never interfere with a sustained spin.  +-6 under-used the
  # hardware by ~3x, so the command range now goes to +-14 rad/s (env-tunable).
  import os as _os
  _wzmax = float(_os.environ.get("RM_WZ_MAX", "14.0"))
  wz = (-_wzmax, _wzmax) if skills else (-1.0, 1.0)''', "wz range")

rep('''    "track_ang_vel": RewardTermCfg(func=velocity_mdp.track_angular_velocity, weight=1.6,
                                   params={"command_name": "twist", "std": math.sqrt(0.5)}),''',
    '''    # Wider std + higher weight: with std=sqrt(0.5) the Gaussian collapses once the yaw
    # error exceeds ~1 rad/s, so a +-14 rad/s command was actively unrewardable.  sqrt(2.0)
    # keeps a real gradient out to the rates the chassis can actually hold.
    "track_ang_vel": RewardTermCfg(func=velocity_mdp.track_angular_velocity, weight=2.5,
                                   params={"command_name": "twist", "std": math.sqrt(2.0)}),''',
    "track_ang_vel")

rep('''    "leg_damping": EventTermCfg(
      func=dr.joint_damping, mode="reset",
      params={"asset_cfg": leg, "operation": "scale", "ranges": (0.8, 1.25),
              "distribution": "uniform"}),
  }''',
    '''    "leg_damping": EventTermCfg(
      func=dr.joint_damping, mode="reset",
      params={"asset_cfg": leg, "operation": "scale", "ranges": (0.8, 1.25),
              "distribution": "uniform"}),
    # --- deployment-transfer randomization -------------------------------------------
    # The trained policy runs against mujoco-warp on the GPU at a 50 Hz torque ZOH, while
    # the wheelbipe deployment injects tau = kp*(q*-q) - kd*qdot as an EXPLICIT
    # qfrc_applied from a 500 Hz loop on the CPU solver.  Both sides are explicit (mjlab's
    # motor actuator is biastype=NONE), but the update instant, the rotor reflected
    # inertia and the hub frictionloss are not identical.  Randomizing them here is what
    # makes the policy tolerant of that mismatch instead of over-fitting to one timing.
    "leg_armature": EventTermCfg(
      func=dr.joint_armature, mode="reset",
      params={"asset_cfg": leg, "operation": "scale", "ranges": (0.7, 1.6),
              "distribution": "uniform"}),
    "leg_frictionloss": EventTermCfg(
      func=dr.joint_friction, mode="reset",
      params={"asset_cfg": leg, "operation": "scale", "ranges": (0.0, 2.5),
              "distribution": "uniform"}),
    "wheel_armature": EventTermCfg(
      func=dr.joint_armature, mode="reset",
      params={"asset_cfg": wheel, "operation": "scale", "ranges": (0.7, 1.6),
              "distribution": "uniform"}),
    "wheel_frictionloss": EventTermCfg(
      func=dr.joint_friction, mode="reset",
      params={"asset_cfg": wheel, "operation": "scale", "ranges": (0.0, 3.0),
              "distribution": "uniform"}),
  }''', "actuator DR")
io.open(F, "w", encoding="utf-8").write(s)
print("env_cfgs: wz +-14, spin reward widened, 4 actuator-side DR terms added")