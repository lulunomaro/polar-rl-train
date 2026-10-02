import io, ast
p = r"D:/claude2/fangzhen/scripts/validate_cc.py"
t = io.open(p, encoding="utf-8").read()
t = t.replace('world("%s_link3" % side)', 'world("%s_front3" % side)').replace('world("%s_thigh" % side)', 'world("%s_rear1" % side)')
t = t.replace('world("%s_link4" % side)', 'world("%s_front4" % side)').replace('world("%s_spring2" % side)', 'world("%s_spring2" % side)')
t = t.replace('np.linalg.norm(world("%s_link4" % side) - world("%s_shank" % side))', 'np.linalg.norm(world("%s_front4" % side) - world("%s_rear2" % side))')
t = t.replace('np.linalg.norm(world("%s_spring2" % side) - world("%s_shank" % side))', 'np.linalg.norm(world("%s_spring2" % side) - world("%s_rear2" % side))')
t = t.replace('knee_name = "left_shank_joint" if "left_shank_joint" in names else None',
              'knee_name = "left_rear2_joint" if "left_rear2_joint" in names else None')
io.open(p, "w", encoding="utf-8", newline="\n").write(t); ast.parse(t); print("validator names fixed")
