import io, ast
p = r"D:/claude2/fangzhen/sim_mujoco/onnx_play.py"
t = io.open(p, encoding="utf-8").read()
old = """LEG = ["hip_L_joint", "knee_L_joint", "hip_R_joint", "knee_R_joint"]
WHEEL = ["wheel_L_joint", "wheel_R_joint"]
ORDER = LEG + WHEEL
assert all(j in JN for j in ORDER), "model joints do not match the contract\""""
new = """ALIASES = {
    "LEG": {
        "ours": ["hip_L_joint", "knee_L_joint", "hip_R_joint", "knee_R_joint"],
        "contract": ["left_front1_joint", "left_rear1_joint",
                     "right_front1_joint", "right_rear1_joint"],
    },
    "WHEEL": {"ours": ["wheel_L_joint", "wheel_R_joint"],
              "contract": ["left_wheel_joint", "right_wheel_joint"]},
}
_layout = "ours" if "hip_L_joint" in JN else "contract"
LEG, WHEEL = ALIASES["LEG"][_layout], ALIASES["WHEEL"][_layout]
ORDER = LEG + WHEEL
print("joint layout:", _layout, LEG, WHEEL)"""
assert old in t
t = t.replace(old, new)
io.open(p, "w", encoding="utf-8").write(t)
ast.parse(t)
print("alias support added")
