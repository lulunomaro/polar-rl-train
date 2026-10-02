import io
F=r"D:\claude2\fangzhen\scripts\build_cc.py"
src=io.open(F,encoding="utf-8").read()
def rep(old,new,cnt=1):
    global src
    assert src.count(old)==cnt,("anchor count %d:"%src.count(old))+old[:70]
    src=src.replace(old,new)

# MATERIALS as <material> elements made the sheet metal blend with the floor reflection;
# plain opaque rgba per functional group reads far better and cannot go transparent.
rep('''MATERIALS = {
    "m_frame":  ("0.36 0.38 0.42 1", 0.45, 0.40, 0.18),
    "m_armor":  ("0.13 0.14 0.16 1", 0.60, 0.50, 0.12),
    "m_motor":  ("0.07 0.07 0.08 1", 0.50, 0.45, 0.08),
    "m_gimbal": ("0.58 0.60 0.64 1", 0.50, 0.50, 0.15),
    "m_elec":   ("0.08 0.30 0.14 1", 0.30, 0.30, 0.08),
    "m_leg":    ("0.17 0.18 0.21 1", 0.55, 0.50, 0.12),
    "m_spring": ("0.66 0.10 0.09 1", 0.50, 0.50, 0.10),
    "m_rubber": ("0.045 0.045 0.05 1", 0.15, 0.20, 0.03),
}''',
'''MATERIALS = {
    "m_frame":  "0.42 0.44 0.48 1",   # machined alu / carbon structure
    "m_armor":  "0.17 0.18 0.20 1",   # anodised armour plates
    "m_motor":  "0.09 0.09 0.11 1",   # DM-J8009 / M3508 housings, slip rings
    "m_gimbal": "0.63 0.65 0.69 1",   # gimbal + launcher
    "m_elec":   "0.11 0.34 0.17 1",   # batteries, PCBs
    "m_leg":    "0.24 0.25 0.29 1",   # leg links, cranks, sprockets
    "m_spring": "0.72 0.13 0.10 1",   # nitrogen gas spring
    "m_rubber": "0.06 0.06 0.07 1",   # tyre
}''')
rep("BASE_MAT = {b: \"m_\" + b for b in BASE_BUCKET_ORDER}",
    "BASE_MAT = {b: \"m_\" + b for b in BASE_BUCKET_ORDER}\n"
    "COL = lambda key: MATERIALS[key]")
# stop emitting <material>; keep colours on the geoms
rep('''for _mn, (_rgba, _sp, _sh, _rf) in MATERIALS.items():
    out.append('    <material name="%s" rgba="%s" specular="%.3f" '
               'shininess="%.3f" reflectance="%.3f"/>' % (_mn, _rgba, _sp, _sh, _rf))
''', "")
rep("""    out.append('      <geom type="mesh" contype="0" conaffinity="0" group="2" density="0" '
               'mesh="%s" material="%s"/>' % (f[:-4], BASE_MAT[_bk]))""",
    """    out.append('      <geom type="mesh" contype="0" conaffinity="0" group="2" density="0" '
               'mesh="%s" rgba="%s"/>' % (f[:-4], MATERIALS[BASE_MAT[_bk]]))""")
rep("""        out.append('%s  <geom type="mesh" contype="0" conaffinity="0" group="2" density="0" '
                   'mesh="%s_%s" material="%s"/>'
                   % (pad, BNAME[body], side.lower(), LEG_MAT[body]))""",
    """        out.append('%s  <geom type="mesh" contype="0" conaffinity="0" group="2" density="0" '
                   'mesh="%s_%s" rgba="%s"/>'
                   % (pad, BNAME[body], side.lower(), MATERIALS[LEG_MAT[body]]))""")
io.open(F,"w",encoding="utf-8").write(src)
print("patch4 OK")