import io
F = r"D:\claude2\fangzhen\scripts\build_cc.py"
s = io.open(F, encoding="utf-8").read()
i = s.index("# Hip mechanical stop.")
j = s.index("JOINT_PAR = {")
rest = s[j:]
old = ('    "rear1":  dict(rng=(-3.14, 1.0), armature=LEG_ARMATURE, damping=0.0,\n'
       '                   frictionloss=THIGH_FRICTION),')
new = '    "rear1":  dict(rng=None, armature=LEG_ARMATURE, damping=0.0, frictionloss=THIGH_FRICTION),'
assert rest.count(old) == 1, "rear1 rng anchor missing"
rest = rest.replace(old, new)
note = (
    "# Hip travel is intentionally UNLIMITED, as in V11 and as in the reference crank.\n"
    "# hip_workspace.py shows the similar-link four-bar closes for all 130321 (thigh, crank)\n"
    "# pairs over +-180 deg, so the linkage puts no boundary on the hip drives; a real stop has\n"
    "# to come from the CAD limiter (机械限位 / 限位安装销) swept volume.\n"
    "# Imposing the reference plant rear1 range=-3.14..1 was measured to BIND in normal\n"
    "# operation and cost the policy 13% of both top speed (2.89 -> 2.50 m/s) and gyro rate\n"
    "# (5.75 -> 5.01 rad/s), so it is reverted.  See docs/HOWTO.md section 18.\n"
)
io.open(F, "w", encoding="utf-8").write(s[:i] + note + rest)
print("hip stop reverted and documented")