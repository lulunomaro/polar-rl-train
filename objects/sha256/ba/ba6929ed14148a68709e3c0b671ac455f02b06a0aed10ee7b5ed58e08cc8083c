import io,ast
p=r"D:/claude2/fangzhen/scripts/export_sim2sim.py"
t=io.open(p,encoding="utf-8").read()
a='''    if j is None:
        out.append('%s<body name="%s" pos="%s">' % (pad, body, f3(anchor)))'''
b='''    if j is None:
        # The deployment has no keyframe: the root must start with the wheels on
        # the ground, otherwise MuJoCo ejects the robot on the first step.
        start = anchor + np.array([0.0, 0.0, STAND_Z])
        out.append('%s<body name="%s" pos="%s">' % (pad, body, f3(start)))'''
assert a in t; t=t.replace(a,b)
t=t.replace('SPRING2 = ["left_spring2_joint", "right_spring2_joint"]',
            'SPRING2 = ["left_spring2_joint", "right_spring2_joint"]\nSTAND_Z = 0.075   # wheel radius + 2 mm')
t=t.replace('''u.append('  <joint name="fixed_base" type="fixed"><parent link="world"/>'
         '<child link="base_link"/><origin xyz="0 0 0.6"/></joint>')''',
            '''u.append('  <joint name="fixed_base" type="fixed"><parent link="world"/>'
         '<child link="base_link"/><origin xyz="0 0 %.3f"/></joint>' % (STAND_Z + 0.2121))''')
io.open(p,"w",encoding="utf-8").write(t); ast.parse(t); print("initial pose fixed")
