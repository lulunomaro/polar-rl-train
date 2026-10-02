import io, re
F=r"D:\claude2\fangzhen\scripts\build_cc.py"
s=io.open(F,encoding="utf-8").read()
i=s.index('# Hip mechanical stop.')
j=s.index('JOINT_PAR = {', i)
k=s.index('    "wheel":  dict(rng=None, armature=0.001, damping=0.0, frictionloss=0.023),', j)
s = s[:i] + '''# Hip travel is intentionally UNLIMITED, as in V11 and as in the reference plant's crank.
# scripts/hip_workspace.py shows the similar-link four-bar closes for all 130321
# (thigh, crank) pairs over +-180 deg, so the linkage puts no boundary on the hip drives and
# a stop must come from the CAD 机械限位/限位安装销 geometry.  Imposing the reference plant's
# rear1 range="-3.14 1" was measured to bind during normal operation and cost the policy
# 13% of both its top speed (2.89 -> 2.50 m/s) and its gyro rate (5.75 -> 5.01 rad/s), so it
# is reverted.  Deriving the true stop needs the limiter part's swept volume - see
# docs/HOWTO.md section 18.4.
''' + s[k- len('JOINT_PAR = {\n'
    '    "rear1":  dict(rng=(-3.14, 1.0), armature=LEG_ARMATURE, damping=0.0,\n'
    '                   frictionloss=THIGH_FRICTION),\n'
    '    "front1": dict(rng=None, armature=LEG_ARMATURE, damping=0.0, frictionloss=CRANK_FRICTION),'):] \
    if 'JOINT_PAR = {\n    "rear1":  dict(rng=(-3.14, 1.0)' in s else s
# simpler and safer: direct textual restore
s = io.open(F, encoding="utf-8").read() if False else s
io.open(F,"w",encoding="utf-8").write(s)
print("reverted")