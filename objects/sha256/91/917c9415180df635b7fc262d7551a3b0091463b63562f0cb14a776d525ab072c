import io, ast
p = r"D:/claude2/fangzhen/train/rmvehicle/src/rmvehicle/robot_cfg.py"
t = io.open(p, encoding="utf-8").read()
a = """LEG_KP, LEG_KD, LEG_EFFORT = 60.0, 2.0, 30.0
WHEEL_KD, WHEEL_EFFORT = 1.5, 8.0"""
b = """# Torque budget from the SJTU serial-leg note (RM2025 串联腿平衡步兵, 2.1.1):
# the hip sprocket is direct drive (~24 Nm from a DM8009P16) while the knee is driven
# through the similar-linkage whose ratio is 0.1134/0.21 = 0.54, i.e. the hip-mounted
# crank turns 1.85x the knee angle and therefore multiplies knee torque.  Holding the
# folded CAD pose costs m*g/2 * 0.20 m = 20 Nm per knee, so a naive "derate" to 13 Nm
# cannot even stand up.  Budget: hip 24, knee 30, wheel 10 Nm (deployment limit).
HIP_KP, HIP_KD, HIP_EFFORT = 60.0, 2.0, 24.0
KNEE_KP, KNEE_KD, KNEE_EFFORT = 60.0, 2.0, 30.0
LEG_KP, LEG_KD, LEG_EFFORT = HIP_KP, HIP_KD, KNEE_EFFORT      # back-compat alias
WHEEL_KD, WHEEL_EFFORT = 1.5, 10.0"""
assert a in t
t = t.replace(a, b)
io.open(p, "w", encoding="utf-8", newline="\n").write(t); ast.parse(t)
print("constants fixed")
