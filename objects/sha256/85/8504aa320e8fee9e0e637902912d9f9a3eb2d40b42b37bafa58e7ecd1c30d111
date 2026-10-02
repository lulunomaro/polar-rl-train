import io, re
p = r"D:/claude2/fangzhen/robot/vehicle.spec.yaml"
t = io.open(p, encoding="utf-8").read()

# 1) mass: SJTU 3.5 节 "全车减重，将质量从23kg降至20kg以下"
t = t.replace("mass_target_total: 25.0", "mass_target_total: 20.0")

# 2) wheel link: the M3508 rotor can / outer ring / planetary carrier turn WITH the wheel
t = t.replace(
  "    all: ['^整车总装/24\\s+髋腿/.*M3508P13\\.72轮组/24\\s+轮组(/|$)']",
  "    all: ['^整车总装/24\\s+髋腿/.*M3508P13\\.72轮组/']\n"
  "    any: ['24\\s+轮组(/|$)', '转子装配', '行星架端盖', '外圈铝件', '双联行星齿', '太阳齿加固',\n"
  "          '输入齿轮装配', '后轴承座', 'id2']")
t = t.replace(
  "    all: ['^整车总装/Mirror24\\s+髋腿/.*M3508P13\\.72轮组/Mirror24\\s+轮组(/|$)']",
  "    all: ['^整车总装/Mirror24\\s+髋腿/.*M3508P13\\.72轮组/']\n"
  "    any: ['Mirror24\\s+轮组(/|$)', '转子装配', '行星架端盖', '外圈铝件', '双联行星齿', '太阳齿加固',\n"
  "          '输入齿轮装配', '后轴承座', 'id2']")

# 3) hip: 上交文档 1.2.1/2.1.2 明确 "髋关节可以360°旋转" -> no position limit
t = t.replace('range: [-1.8, 1.2], effort: 30.0, class: leg', 'range: null, effort: 24.0, class: leg')
# 4) knee: the 相似连杆 (ratio 0.1134/0.21 = 0.54) de-rotates the crank, so the knee
#    output torque is ~0.54x the hip's for the same DM8009
t = t.replace('range: [-2.2, 2.1], effort: 30.0, class: leg', 'range: [-2.2, 2.2], effort: 13.0, class: leg')
t = t.replace("effort: 6.0, class: wheel", "effort: 6.0, class: wheel")

t = t.replace("# default joint angles", """# Joint limits follow the SJTU open-source note (RM2025 串联腿平衡步兵):
#   * hip is unlimited - the nested two-stage shaft with two hub-bearing sets is
#     explicitly designed for 360 deg leg rotation (doc 1.2.1 / 2.1.2)
#   * knee covers the full stroke from the folded CAD pose to a straight leg
#     (|thigh|+|shank| = 0.46 m), i.e. +-2.2 rad
#   * knee effort = 0.54 x hip effort, because the similar-linkage ratio
#     0.1134/0.21 = 0.54 multiplies crank speed and divides knee torque

# default joint angles""")
io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("spec updated")
for l in t.split("\n"):
    if "mass_target" in l or "hip_L_joint" in l or "knee_L_joint" in l or "转子装配" in l:
        print("   ", l.strip())
