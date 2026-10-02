import io
F=r"D:\claude2\fangzhen\scripts\collision_debug_shots.py"
s=io.open(F,encoding="utf-8").read()
old = """ORIG = m.geom_rgba.copy()
ORIG_G = m.geom_group.copy()
"""
new = """ORIG = m.geom_rgba.copy()
ORIG_G = m.geom_group.copy()
# MuJoCo's offscreen renderer only draws geom groups 0-2 by default, so the collision
# primitives (group 3) have to be promoted into the visible set for these debug shots.
def show_collision():
    for g in COL:
        m.geom_group[g] = 2
"""
assert s.count(old)==1
s=s.replace(old,new)
s=s.replace("""    if mode == "visual":""","""    if mode == "visual":""")
s=s.replace("""        for g in COL:
            t = int(m.geom_type[g])
            if t == mujoco.mjtGeom.mjGEOM_MESH:""","""        show_collision()
        for g in COL:
            t = int(m.geom_type[g])
            if t == mujoco.mjtGeom.mjGEOM_MESH:""")
s=s.replace("""    else:
        for g in COL:
            t = int(m.geom_type[g])
            if "wheel" in""","""    else:
        show_collision()
        for g in COL:
            t = int(m.geom_type[g])
            if "wheel" in""")
io.open(F,"w",encoding="utf-8").write(s)
print("collision geoms now promoted to a visible group")