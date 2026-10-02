import io
F=r"D:\claude2\fangzhen\scripts\build_cc.py"
s=io.open(F,encoding="utf-8").read()
old = '''JOINT_PAR = {
    "rear1":  dict(rng=None, armature=LEG_ARMATURE, damping=0.0, frictionloss=THIGH_FRICTION),
    "front1": dict(rng=None, armature=LEG_ARMATURE, damping=0.0, frictionloss=CRANK_FRICTION),'''
new = '''# Hip mechanical stop.  The similar-link four-bar itself closes for every (thigh, crank)
# pair - scripts/hip_workspace.py finds 130321/130321 poses assemblable over +-180 deg - so
# the linkage imposes NO hip boundary.  The bound has to come from the 机械限位 / 限位安装销
# hardware that the CAD classifies onto the thigh.  Rather than invent an angle, mirror the
# reference implementation's convention exactly: wheelbipeV14_2 puts the thigh drive on
# range="-3.14 1" and leaves the crank (front1) unlimited.  Our solver-measured thigh motion
# under the full commanded envelope is [-0.726, +0.500] rad, so this never binds in normal
# operation - it only stops the unbounded thigh runaway seen in the deployed sim.
JOINT_PAR = {
    "rear1":  dict(rng=(-3.14, 1.0), armature=LEG_ARMATURE, damping=0.0,
                   frictionloss=THIGH_FRICTION),
    "front1": dict(rng=None, armature=LEG_ARMATURE, damping=0.0, frictionloss=CRANK_FRICTION),'''
assert s.count(old)==1, "JOINT_PAR anchor missing"
io.open(F,"w",encoding="utf-8").write(s.replace(old,new))
print("hip stop applied to rear1 (thigh), crank left unlimited - mirrors the reference plant")