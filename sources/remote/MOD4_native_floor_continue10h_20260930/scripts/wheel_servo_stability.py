"""Is the deployed wheel velocity servo numerically stable?

mjlab drives the wheels through a MuJoCo joint actuator with an affine bias, and MuJoCo
integrates that damping term IMPLICITLY.  The deployment instead injects
    tau = kd * (v_cmd - omega)
as an explicit qfrc_applied once per physics step.  Explicit damping overshoots every step
while kd*dt > M, where M is the DOF inertia (body inertia about the hinge + joint armature).
Values are read straight out of the plant's mass matrix (1.616894e-03 for the wheel).
"""
import os, numpy as np, mujoco
ROOT = r"D:/claude2/fangzhen"
XML = os.path.join(ROOT, "robot/out_cc/scene_cc.xml")

m = mujoco.MjModel.from_xml_path(XML)
d = mujoco.MjData(m)
mujoco.mj_forward(m, d)
full = np.zeros((m.nv, m.nv))
mujoco.mj_fullM(m, d, full)   # sparse mass matrix -> dense (nv, nv)
M = {}
for jn in ("left_wheel_joint", "left_rear1_joint", "left_front1_joint"):
    dof = m.jnt_dofadr[mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, jn)]
    M[jn] = float(full[dof, dof])

print("effective DOF inertia from the plant mass matrix:")
for k, v in M.items():
    print("   %-18s M = %.6f kg*m^2" % (k, v))
print("\nexplicit-damping stability bound  kd*dt < M:")
KD_W = float(os.environ.get("RM_WHEEL_KD", "0.6"))
for jn, kd in (("left_wheel_joint", KD_W), ("left_rear1_joint", 2.0), ("left_front1_joint", 2.0)):
    for dt in (0.001, 0.002):
        r = kd * dt / M[jn]
        print("   %-18s kd=%.1f dt=%.4f  kd*dt/M = %6.3f  %s" %
              (jn, kd, dt, r, "stable" if r < 1.0 else "**UNSTABLE: overshoots every step**"))
print("""
Verdict (corrected 2026-09-05):
  * mjlab's motor actuator is biastype=NONE, so TRAINING integrates the same PD explicitly
    that the deployment does.  The earlier "MuJoCo does it implicitly, so training gets away
    with it" explanation was wrong -- both sides had the problem.
  * kd=1.5 at the 2 ms step (training physics dt AND the 500 Hz controller) is 1.855: every
    step overshoots, and the wheel torque rings at the integration limit.  That is why the
    deployment measured wheel forces far above the robot's weight and why the wheel loop needed
    a 1 ms hack.
  * kd=0.6 gives 0.742: monotone, settles in ~3 steps, and still holds 52 rad/s of wheel
    against a 0.2 N*m rolling load with only 0.3 rad/s of droop -- which is the whole point of
    the high-rate 小陀螺.  So the deployment can go back to its nominal 2 ms / 500 Hz loop.
  * The leg servos were never the binding case (0.074 / 0.226).
Set RM_WHEEL_KD to re-run this against a proposed gain; robot_cfg.WHEEL_KD is the authority and
scripts/check_contract_drift.py refuses a deployment YAML that disagrees with it.
""")
