import io
F=r"D:\claude2\fangzhen\scripts\hop_control_law.py"
src=io.open(F,encoding="utf-8").read()
def rep(old,new,cnt=1):
    global src
    assert src.count(old)==cnt,("anchor count %d:"%src.count(old))+old[:70]
    src=src.replace(old,new)
# The deployment's joint_action_scale is [0.5,0.5,0.5,0.5,10,10]: the policy vector is
# 4 LEG actions then 2 WHEEL actions, NOT the <actuator> block order.  Revert to that.
rep('''# ACTION ORDER.  The policy emits one number per *actuator*, in <actuator> block order:
#   left_front1, left_rear1, left_wheel, right_front1, right_rear1, right_wheel
# The harness used to feed a[0..3] to the four leg joints and a[4..5] to the wheels, which
# cross-wired the left wheel onto the right front leg.  That, not the robot, is why every
# earlier harness run toppled (tilt 180 deg) while mjlab and the ROS2 sim2sim balanced fine.
ACT_J = [nm for nm in
         (mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_ACTUATOR, i) for i in range(m.nu))]
ACT_J = [jn for jn in
         (mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_JOINT,
                            m.trngeom_trnid[m.actuator_trnid[i][0]])
          if False else
          mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_JOINT, m.actuator_trnid[i][0])
          for i in range(m.nu))]
assert len(ACT_J) == 6, ACT_J
LEGSET = set(LEG)
print("actuator order ->", ACT_J)''',
    '''# ACTION ORDER is [4 legs, 2 wheels]: the deployed controller's joint_action_scale is
# [0.5, 0.5, 0.5, 0.5, 10.0, 10.0], so a[0..3] are the leg position targets and a[4..5]
# the wheel velocity targets.  This is NOT the <actuator> block order of the MJCF.
ACT_J = LEG + WHL
assert m.nu == 6, m.nu
LEGSET = set(LEG)''')
# use the model's own gyro sensor (body frame) exactly like the deployment does
rep("site = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_SITE, \"imu\")",
    "site = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_SITE, \"imu\")\n"
    "GSAD = {n: m.sensor_adr[mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_SENSOR, n)]\n"
    "        for n in (\"gyro\", \"framequat\")}")
rep("        o[4:7] = d.qvel[3:6] * 0.5",
    "        # body-frame angular velocity straight from the model's gyro sensor, matching\n"
    "        # robot_state.body_state.ang_vel_b in state_rl.cpp\n"
    "        o[4:7] = d.sensordata[GSAD[\"gyro\"]:GSAD[\"gyro\"] + 3] * 0.5")
io.open(F,"w",encoding="utf-8").write(src)
print("harness4 patched")