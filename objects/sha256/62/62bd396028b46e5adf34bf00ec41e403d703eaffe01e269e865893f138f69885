import io, ast
p = r"D:/claude2/fangzhen/scripts/build_cc.py"
t = io.open(p, encoding="utf-8").read()
t = t.replace('''ACT_OF = {"thigh": "rear1", "crank": "front1", "wheel": "wheel"}''',
'''# contract names used by wheelbipe_ros2_sim2sim: the two leg actuators are both
# hip-axis cranks (front1 = knee drive, rear1 = thigh drive)
ACT_OF = {"thigh": "rear1", "crank": "front1", "wheel": "wheel"}
BNAME = {"thigh": "rear1", "shank": "rear2", "wheel": "wheel", "crank": "front1",
         "link2": "front2", "link3": "front3", "link4": "front4",
         "spring1": "spring1", "spring2": "spring2"}''')
t = t.replace('    nm = "%s_%s" % (SIDE[side], body)\n', '    nm = "%s_%s" % (SIDE[side], BNAME[body])\n')
t = t.replace('''    if (body, side) in MESH:
        out.append('%s  <geom type="mesh" contype="0" conaffinity="0" group="3" density="0" '
                   'mesh="%s_%s" rgba="0.72 0.72 0.75 1"/>' % (pad, body, side.lower()))''',
'''    if (body, side) in MESH:
        out.append('%s  <geom type="mesh" contype="0" conaffinity="0" group="3" density="0" '
                   'mesh="%s_%s" rgba="0.72 0.72 0.75 1"/>' % (pad, BNAME[body], side.lower()))''')
t = t.replace('''    out.append('    <mesh name="%s_%s" file="%s" scale="0.001 0.001 0.001"/>'
               % (body, side.lower(), fn))''',
'''    out.append('    <mesh name="%s_%s" file="%s" scale="0.001 0.001 0.001"/>'
               % (BNAME[body], side.lower(), fn))''')
t = t.replace('''    for b1, b2, pt in (("%s_link3" % s, "%s_thigh" % s, P1),
                       ("%s_link4" % s, "%s_shank" % s, Q),
                       ("%s_spring2" % s, "%s_shank" % s, S2)):
        who = "link3" if "link3" in b1 else ("link4" if "link4" in b1 else "spring2")''',
'''    for b1, b2, pt, who in ((s + "_front3", s + "_rear1", P1, "link3"),
                            (s + "_front4", s + "_rear2", Q, "link4"),
                            (s + "_spring2", s + "_rear2", S2, "spring2")):''')
t = t.replace('    knee_name = "left_shank_joint"', '    knee_name = "left_rear2_joint"')
io.open(p, "w", encoding="utf-8", newline="\n").write(t); ast.parse(t); print("contract naming applied")
