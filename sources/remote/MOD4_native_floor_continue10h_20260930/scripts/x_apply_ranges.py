import io
F=r"D:\claude2\fangzhen\scripts\build_cc.py"
src=io.open(F,encoding="utf-8").read()
old = '''PASSIVE_RNG = {"shank":   (-2.20, 1.20),   # rear2  knee  (full workspace -1.934..+0.933)
               "link2":   (-1.30, 2.50),   # front2        (-0.971..+2.175)
               "link3":   (-2.20, 0.40),   # front3        (-1.850..+0.134)
               "link4":   (-1.30, 2.30),   # front4        (-0.933..+1.979)
               "spring1": (-0.40, 0.20)}   # gas-spring pivot (-0.247..+0.034)'''
new = '''# Solver-measured joint ranges (scripts/passive_range_solver.py): the base is welded,
# gravity off, the two hip-axis drives are held at the training PD gains and swept across
# the whole envelope the policy can command (thigh/crank +-0.80 rad, 441 poses, worst
# equality gap 0.027 mm) with the stops opened.  The previous numbers were taken in the
# ANALYTIC sign while an MJCF hinge stores the NEGATED value, so four of the five stops sat
# on the wrong side of the workspace and the closed chain jammed against its own limiter -
# front3 reached +1.072 rad against a +0.400 stop (38 deg of hard clamp).
# Each entry below brackets the measured motion with 0.15 rad of margin.
PASSIVE_RNG = {"shank":   (-0.84, 1.48),   # rear2  knee   achieved [-0.694, +1.328]
               "link2":   (-1.48, 0.84),   # front2        achieved [-1.328, +0.695]
               "link3":   (-0.28, 1.22),   # front3        achieved [-0.134, +1.072]
               "link4":   (-1.48, 0.84),   # front4        achieved [-1.328, +0.695]
               "spring1": (-0.18, 0.32)}   # gas-spring pivot achieved [-0.034, +0.169]'''
assert src.count(old)==1, "PASSIVE_RNG anchor missing"
io.open(F,"w",encoding="utf-8").write(src.replace(old,new))
print("PASSIVE_RNG replaced with solver-measured ranges")