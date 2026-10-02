import os, numpy as np, mujoco
ROOT=r"D:\claude2\fangzhen"
m=mujoco.MjModel.from_xml_path(os.path.join(ROOT,"robot/out_cc/_welded_leg_test.xml"))
d=mujoco.MjData(m)
m.opt.gravity[2]=0.0
for g in range(m.ngeom):
    if m.geom_group[g]==2: m.geom_group[g]=5
J=lambda n: mujoco.mj_name2id(m,mujoco.mjtObj.mjOBJ_JOINT,n)
print("nu=%d  nuser=%d" % (m.nu, m.nu))
for k in ("left_rear1","left_front1","left_rear2","left_wheel"):
    j=J(k+"_joint")
    print("  %-14s type=%d qposadr=%d dofadr=%d limited=%d axis=%s" %
          (k, m.jnt_type[j], m.jnt_qposadr[j], m.jnt_dofadr[j], m.jnt_limited[j], m.jnt_axis[j]))
print("\n-- open-loop torque test: hold nothing, apply constant effort to one joint --")
for k,tau in (("left_rear1_joint",20.0),("left_front1_joint",20.0),("left_wheel_joint",2.0)):
    mujoco.mj_resetData(m,d)
    v=m.jnt_dofadr[J(k)]
    for i in range(2000):
        d.qfrc_applied[:]=0.0
        d.qfrc_applied[v]=tau
        mujoco.mj_step(m,d)
    print("  %-18s tau=%5.1f N*m -> q=%+.4f rad  qvel=%+.3f   (moved %s)" %
          (k,tau,d.qpos[m.jnt_qposadr[J(k)]],d.qvel[v],
           "YES" if abs(d.qpos[m.jnt_qposadr[J(k)]])>0.05 else "NO"))
print("\n-- is the four-bar singular at qpos0?  crank torque vs resulting motion --")
# measure the transmission ratio d(knee)/d(crank) from the analytic model
import sys; sys.path.insert(0,os.path.join(ROOT,"scripts"))
from leg2d import Kite2D, CAD
L=Kite2D(CAD,"p")
for tc in (0.0,0.2,0.4):
    r=L.ratio(0.0,tc)
    print("  crank %+0.2f rad -> d(knee)/d(crank) = %+0.4f" % (tc, r))