import io
F=r"D:\claude2\fangzhen\scripts\hop_control_law.py"
src=io.open(F,encoding="utf-8").read()
def rep(old,new,cnt=1):
    global src
    assert src.count(old)==cnt,("anchor count %d:"%src.count(old))+old[:70]
    src=src.replace(old,new)
rep('''wb = {BD("left_wheel"), BD("right_wheel")}''',
    '''wb = {BD("left_wheel"), BD("right_wheel")}
# ACTION ORDER.  The policy emits one number per *actuator*, in <actuator> block order:
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
print("actuator order ->", ACT_J)''')
rep('''        for i, n in enumerate(LEG):
            tgt[n] = a[i] * S_LEG
        for i, n in enumerate(WHL):
            tgt[n] = a[4 + i] * S_WHL''',
    '''        for i, jn in enumerate(ACT_J):
            tgt[jn] = a[i] * (S_LEG if jn in LEGSET else S_WHL)''')
io.open(F,"w",encoding="utf-8").write(src)
print("harness3 patched")