import io
F=r"D:\claude2\fangzhen\scripts\export_sim2sim_cc.py"
s=io.open(F,encoding="utf-8").read()
old = '''# Physics rate.  Training uses timestep=0.002 with decimation=10, i.e. each policy torque is
# held across ten 2 ms substeps.  The bridge runs its control loop at 500 Hz, so a 2 ms plant
# step makes one control tick == one physics step and the new 50 Hz leg-torque ZOH reproduce
# the training regime exactly.  (1 ms here would decouple the two rates.)
xml = re.sub(r"(<option [^>]*?timestep=\\")[0-9.]+(\\")", r"\\g<1>0.002\\g<2>", xml, count=1)
print("deployment physics timestep -> 0.002 s (matches training dt x decimation)")'''
new = '''# Physics rate: KEEP the plant's own 1 ms step.  Matching training's 2 ms looks principled but
# is not, because the two sims apply actuator damping by different mechanisms.  mjlab drives the
# wheels through a MuJoCo joint actuator whose affine bias MuJoCo integrates IMPLICITLY; the
# deployment injects tau = kd*(v_cmd - omega) as an explicit qfrc_applied, which only stays
# stable while kd*dt < M.  With the wheel DOF inertia M = 1.6169e-3 kg*m^2 (measured from the
# plant mass matrix; body 6.169e-4 + armature 1.0e-3) and kd = 1.5:
#     dt = 0.001 -> kd*dt/M = 0.928   (stable)
#     dt = 0.002 -> kd*dt/M = 1.855   (UNSTABLE: overshoots every single step)
# Reproduce with scripts/wheel_servo_stability.py.
if os.environ.get("RM_DEPLOY_DT"):
    xml = re.sub(r"(<option [^>]*?timestep=\\")[0-9.]+(\\")",
                 r"\\g<1>%s\\g<2>" % os.environ["RM_DEPLOY_DT"], xml, count=1)
print("deployment physics timestep: keeping the plant's own 1 ms "
      "(2 ms makes the explicit wheel servo diverge; see wheel_servo_stability.py)")'''
assert s.count(old)==1, "dt anchor missing"
io.open(F,"w",encoding="utf-8").write(s.replace(old,new))
print("dt reverted to the plant default 1 ms")