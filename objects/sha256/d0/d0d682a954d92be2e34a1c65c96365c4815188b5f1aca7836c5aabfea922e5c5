import io,re
F=r"D:\claude2\fangzhen\scripts\build_cc.py"
src=io.open(F,encoding="utf-8").read()
def rep(old,new,cnt=1):
    global src
    assert src.count(old)==cnt, ("anchor not unique/found (%d):"%src.count(old))+old[:70]
    src=src.replace(old,new)

# ---- 1. materials + buckets, inserted after the motor-profile block ----
rep('print("motor profile:", MOTOR_PROFILE, "armature", LEG_ARMATURE,\n'
    '      "leg torque", LEG_TORQUE, "wheel torque", WHEEL_TORQUE)\n',
    'print("motor profile:", MOTOR_PROFILE, "armature", LEG_ARMATURE,\n'
    '      "leg torque", LEG_TORQUE, "wheel torque", WHEEL_TORQUE)\n'
    '\n'
    '# ------------------------------------------------------------------ appearance\n'
    '# The STEP carries no colours, so every part used to be drawn in one flat grey:\n'
    '# 2.6 M triangles of 2-3 mm sheet all the same tone reads as "debris" even when the\n'
    '# model is complete.  Each functional group now gets its own material.\n'
    'MATERIALS = {\n'
    '    "m_frame":  ("0.36 0.38 0.42 1", 0.45, 0.40, 0.18),\n'
    '    "m_armor":  ("0.13 0.14 0.16 1", 0.60, 0.50, 0.12),\n'
    '    "m_motor":  ("0.07 0.07 0.08 1", 0.50, 0.45, 0.08),\n'
    '    "m_gimbal": ("0.58 0.60 0.64 1", 0.50, 0.50, 0.15),\n'
    '    "m_elec":   ("0.08 0.30 0.14 1", 0.30, 0.30, 0.08),\n'
    '    "m_leg":    ("0.17 0.18 0.21 1", 0.55, 0.50, 0.12),\n'
    '    "m_spring": ("0.66 0.10 0.09 1", 0.50, 0.50, 0.10),\n'
    '    "m_rubber": ("0.045 0.045 0.05 1", 0.15, 0.20, 0.03),\n'
    '}\n'
    'BASE_BUCKETS = [\n'
    '    ("motor",  r"DM_8116|DM80|电机铝件|电机涨块|电机座|滑环|中心轴|拨盘电机|步进|舵机|卡簧"),\n'
    '    ("armor",  r"装甲|防弹板|挡板|链轮保护"),\n'
    '    ("gimbal", r"^0120|云台|[Pp]itch|[Yy][Aa][Ww]|弹仓|鹅颈|大测速|斜板|复活赛|枪管|雷达"),\n'
    '    ("elec",   r"电池|超电|继电器|电管|电容|TOF|UWB|开发板|电脑|PCB|线束|30A|蚊香|转接|开关|模块"),\n'
    ']\n'
    'BASE_BUCKET_ORDER = ["frame", "armor", "motor", "gimbal", "elec"]\n'
    'BASE_MAT = {b: "m_" + b for b in BASE_BUCKET_ORDER}\n'
    'LEG_MAT = {"thigh": "m_leg", "shank": "m_leg", "crank": "m_leg", "link2": "m_leg",\n'
    '           "link3": "m_leg", "link4": "m_leg", "spring1": "m_spring",\n'
    '           "spring2": "m_spring", "wheel": "m_rubber"}\n'
    '\n'
    'def bucket_of(s):\n'
    '    txt = s["product"].strip() + "|" + s["path"]\n'
    '    for name, pat in BASE_BUCKETS:\n'
    '        if re.search(pat, txt):\n'
    '            return name\n'
    '    return "frame"\n')

# ---- 2. the base visual mesh: include the chassis-side leg hardware, bucket it ----
old_base = '''    if body == "base":
        ss = [s for s in groups["base"] if isinstance(s, dict)]'''
new_base = '''    if body == "base":
        # ALL chassis-fixed solids, including the 66 leg-side parts that are bolted to the
        # frame: the 4x DM-J8009 hip motors, DM80-V3, slip rings, central shafts, sprocket
        # guards and the 16 大装甲板 armour plates (2640 cm3 / 461k triangles).  Dropping
        # them is what made the body look gutted and left the rotating leg sprockets as the
        # only motor-like geometry on screen.
        ss = [s if isinstance(s, dict) else s[1] for s in groups["base"]]'''
rep(old_base,new_base)

rep('''            me.apply_transform(A4)
            parts.append(me)
            _names.append(s["product"].strip())
        mesh = trimesh.util.concatenate(parts)''',
    '''            me.apply_transform(A4)
            parts.append(me)
            _names.append((s["product"].strip(), bucket_of(s)))
        mesh = trimesh.util.concatenate(parts)''')

rep('''        _z = sorted(((float(mm.bounds[0][2]), float(mm.bounds[1][2]), nm)
                     for mm, nm in zip(parts, _names)), key=lambda t: -t[1])''',
    '''        _z = sorted(((float(mm.bounds[0][2]), float(mm.bounds[1][2]), nm)
                     for mm, (nm, _) in zip(parts, _names)), key=lambda t: -t[1])''')

rep('''        try:
            if len(mesh.faces) > BASE_FACE_BUDGET:
                mesh = mesh.simplify_quadric_decimation(face_count=BASE_FACE_BUDGET)
            print("  base decimated -> %d faces" % len(mesh.faces))
        except Exception as e:
            print("  base decimation skipped:", type(e).__name__, str(e)[:90])
        for i in range(0, len(mesh.faces), 150000):
            sub = mesh.submesh([np.arange(i, min(i + 150000, len(mesh.faces)))], append=True)
            fn = "base_%02d.stl" % (i // 150000)
            sub.export(os.path.join(OUT, "meshes", fn))
            MESH.setdefault("base", []).append(fn)
        print("  base -> %s faces" % len(mesh.faces))''',
    '''        try:
            if len(mesh.faces) > BASE_FACE_BUDGET:
                mesh = mesh.simplify_quadric_decimation(face_count=BASE_FACE_BUDGET)
            print("  base decimated -> %d faces" % len(mesh.faces))
        except Exception as e:
            print("  base decimation skipped:", type(e).__name__, str(e)[:90])
        # one merged + chunked mesh per visual bucket, so materials can differ
        for _stale in os.listdir(os.path.join(OUT, "meshes")):
            if _stale.startswith("base_") and _stale.endswith(".stl"):
                os.remove(os.path.join(OUT, "meshes", _stale))
        byb = collections.defaultdict(list)
        for mm, (nm, bk) in zip(parts, _names):
            byb[bk].append(mm)
        for bk in BASE_BUCKET_ORDER:
            if bk not in byb:
                continue
            bm = (byb[bk][0] if len(byb[bk]) == 1
                  else trimesh.util.concatenate(byb[bk]))
            bb = bm.bounds
            print("    bucket %-7s %3d solids  %8d faces  y[%6.1f %6.1f] z[%6.1f %6.1f]"
                  % (bk, len(byb[bk]), len(bm.faces), bb[0][1], bb[1][1], bb[0][2], bb[1][2]))
            for i in range(0, len(bm.faces), 150000):
                sub = bm.submesh([np.arange(i, min(i + 150000, len(bm.faces)))], append=True)
                fn = "base_%s_%02d.stl" % (bk, i // 150000)
                sub.export(os.path.join(OUT, "meshes", fn))
                MESH.setdefault("base", []).append((fn, bk))
        print("  base -> %s faces" % len(mesh.faces))''')

rep("       '  <asset>']",
    "       '  <asset>']\n"
    "for _mn, (_rgba, _sp, _sh, _rf) in MATERIALS.items():\n"
    "    out.append('    <material name=\"%s\" rgba=\"%s\" specular=\"%.3f\" '\n"
    "               'shininess=\"%.3f\" reflectance=\"%.3f\"/>' % (_mn, _rgba, _sp, _sh, _rf))")
rep("for f in MESH.get(\"base\", []):\n    out.append('    <mesh name=\"%s\" file=\"%s\" scale=\"0.001 0.001 0.001\"/>' % (f[:-4], f))",
    "for f, _bk in MESH.get(\"base\", []):\n    out.append('    <mesh name=\"%s\" file=\"%s\" scale=\"0.001 0.001 0.001\"/>' % (f[:-4], f))")
rep('''for f in MESH.get("base", []):
    out.append('      <geom type="mesh" contype="0" conaffinity="0" group="2" density="0" '
               'mesh="%s" rgba="0.72 0.72 0.75 1"/>' % f[:-4])''',
    '''for f, _bk in MESH.get("base", []):
    out.append('      <geom type="mesh" contype="0" conaffinity="0" group="2" density="0" '
               'mesh="%s" material="%s"/>' % (f[:-4], BASE_MAT[_bk]))''')
rep('''        out.append('%s  <geom type="mesh" contype="0" conaffinity="0" group="2" density="0" '
                   'mesh="%s_%s" rgba="0.72 0.72 0.75 1"/>' % (pad, BNAME[body], side.lower()))''',
    '''        out.append('%s  <geom type="mesh" contype="0" conaffinity="0" group="2" density="0" '
                   'mesh="%s_%s" material="%s"/>'
                   % (pad, BNAME[body], side.lower(), LEG_MAT[body]))''')
io.open(F,"w",encoding="utf-8").write(src)
print("patched OK")