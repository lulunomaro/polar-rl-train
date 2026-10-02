import io, ast
p = r"D:/claude2/fangzhen/scripts/build_cc.py"
t = io.open(p, encoding="utf-8").read()
# fix the tuple/dict filter and drop the dead export_mesh helper
t = t.replace('''    ss = [s for (sd, s) in groups.get(body, []) if not isinstance(s, dict) and sd == side]
    if isinstance(groups.get(body, [None])[0], dict):
        return None''', '''    ss = [i[1] for i in groups.get(body, []) if isinstance(i, tuple) and i[0] == side]''')
t = t.replace('''def export_mesh(body, side, budget):
    ss = [s for (sd, s) in groups.get(body, []) if not isinstance(s, dict) and sd == side]
    if isinstance(groups.get(body, [None])[0], dict):
        return None
    parts = []
    tot = sum(s["ntris"] for s in ss) or 1
    for s in ss:
        obj = CSUB.get((s["path"], round(s["volume_mm3"], 1)), s["obj"])
        try:
            m = trimesh.load(os.path.join(COARSE if obj in os.listdir(
                os.path.join(COARSE, "meshes")) else FINE, "meshes", obj), process=False)
        except Exception:
            continue
        m.apply_transform(A4)
        parts.append(m)
    if not parts:
        return None
    mesh = trimesh.util.concatenate(parts)
    pin, y = TOPO[name_of(body)][0] if False else (None, None)
    return mesh

name_of = lambda b: b
''', '')
t = t.replace('''    ss = [s for (sd, s) in groups.get(body, []) if not isinstance(s, dict) and sd == side]
    parts = []''', '''    ss = [i[1] for i in groups.get(body, []) if isinstance(i, tuple) and i[0] == side]
    parts = []''')
t = t.replace('''        ss = [s for s in groups["base"] if isinstance(s, dict)]''',
              '''        ss = [s for s in groups["base"] if isinstance(s, dict)]''')
t = t.replace('''    mesh.apply_translation(-ANCHOR[body] / 1000.0 * 1000.0 / 1000.0)
    mesh.apply_translation(-ANCHOR[body])''', '''    mesh.apply_translation(-ANCHOR[body])''')
t = t.replace('''    try:
        if len(mesh.faces) > 400:
            mesh = mesh.simplify_quadric_decimation(face_count=max(200, min(budget, len(mesh.faces) // 3)))
    except Exception:
        pass''', '''    try:
        if len(mesh.faces) > 400:
            mesh = mesh.simplify_quadric_decimation(
                face_count=max(120, min(budget, len(mesh.faces))))
    except Exception:
        pass''')
t += '''

# ------------------------------------------------------------------ emit MJCF
def f3(v):
    return " ".join("%.6g" % x for x in np.atleast_1d(v))

COLL = {
    "thigh":  dict(type="capsule", a=HIP, b=KNEE, r=45.0),
    "shank":  dict(type="capsule", a=KNEE, b=AXLE, r=32.0),
    "wheel":  dict(type="cylinder", a=AXLE, r=73.0, h=13.0),
    "crank":  dict(type="capsule", a=HIP, b=P2, r=28.0),
    "link2":  dict(type="capsule", a=P2, b=APEX, r=18.0),
    "link3":  dict(type="capsule", a=P1, b=P3, r=18.0),
    "link4":  dict(type="capsule", a=P3, b=Q, r=14.0),
    "spring1": dict(type="capsule", a=S1, b=(S1 + S2) / 2, r=14.0),
    "spring2": dict(type="capsule", a=(S1 + S2) / 2, b=S2, r=17.0),
}
ACT = {"thigh": "rear1", "crank": "front1", "wheel": "wheel"}
# SJTU reference numbers for the same mechanism
JOINT_PAR = {
    "rear1":  dict(range=(-3.14, 1.0), armature=0.035, damping=0.0, frictionloss=1.5, effort=54.0),
    "front1": dict(range=None, armature=0.035, damping=0.0, frictionloss=1.5, effort=54.0),
    "wheel":  dict(range=None, armature=0.001, damping=0.0, frictionloss=0.023, effort=5.0),
}
PASSIVE = {
    "shank":  (0.0, 1.2),     # knee
    "link2":  (-1.0, 0.1),
    "link3":  (-0.1, 1.0),
    "link4":  (-2.0, 0.1),
    "spring1": (-0.5, 0.1),
}
out = ['<mujoco model="rm_vehicle_cc">',
       '  <compiler angle="radian" autolimits="true" balanceinertia="true" '
       'inertiafromgeom="false"/>',
       '  <option timestep="0.002" iterations="30" ls_iterations="20" '
       'integrator="implicitfast"/>',
       '  <default>',
       '    <geom condim="3" friction="1.2 0.01 0.001" margin="0"/>',
       '    <default class="motor"><joint damping="0.0" frictionloss="1.5" '
       'armature="0.035"/></default>',
       '  </default>',
       '  <asset>']
for key, fn in sorted(MESH.items(), key=lambda kv: str(kv[0])):
    if key == "base":
        for f in MESH["base"]:
            out.append('    <mesh name="%s" file="%s" scale="0.001 0.001 0.001"/>'
                       % (f[:-4], f))
    else:
        out.append('    <mesh name="%s_%s" file="%s" scale="0.001 0.001 0.001"/>'
                   % (key[0], key[1], fn))
out.append('  </asset>')
out.append('  <worldbody>')
out.append('    <body name="base_link" pos="0 0 0">')
out.append('      <freejoint name="floating_base"/>')
out.append('      <site name="imu" pos="0 0 0.3" size="0.01"/>')
b = BODIES["base"]
out.append('      <inertial pos="%s" mass="%.4f" fullinertia="%s"/>'
           % (f3(b["com"] / 1000.0), b["mass"],
              f3(np.array([b["inertia"][0, 0], b["inertia"][1, 1], b["inertia"][2, 2],
                           b["inertia"][0, 1], b["inertia"][0, 2], b["inertia"][1, 2]]) / 1e6)))
for f in MESH.get("base", []):
    out.append('      <geom type="mesh" contype="0" conaffinity="0" group="3" density="0" '
               'mesh="%s" rgba="0.72 0.72 0.75 1"/>' % f[:-4])
out.append('      <geom name="base_col" type="box" size="0.357 0.196 0.1145" '
           'pos="0 0 0.1685" contype="0" conaffinity="1" group="4" density="0" '
           'rgba="0 0.5 0.1 0.1"/>')

def emit_leg(side):
    ys = {"L": -1.0, "R": 1.0}
    sy = ys[side]
    def Y(pt, y_ref):
        return np.array([pt[0], y_ref + sy * 0.0, pt[1]])
    def pos_of(body, pt):
        cfg = TOPO[body]
        y = cfg["y"] * (-sy)          # left leg uses negative y
        return np.array([pt[0], y, pt[1]]) / 1000.0
    def rec(body, parent_pin, depth):
        bb = BODIES[body]; cfg = TOPO[body]
        pin = cfg["pin"]; y = cfg["y"] * (-sy) if False else cfg["y"]
        # absolute anchor of this body in robot mm
        ab = np.array([pin[0], cfg["y"], pin[1]])
        par = ANCHOR[cfg["parent"]] if cfg["parent"] != "base" else np.zeros(3)
        if cfg["parent"] == "base":
            par = np.zeros(3)
        rel = (ab - par) / 1000.0
        pad = "  " * depth
        name = "%s_%s" % (body, side.lower())
        out.append('%s<body name="%s" pos="%s">' % (pad, name, f3(rel)))
        jn = ACT.get(body)
        if jn:
            jp = JOINT_PAR[jn]
            rng = (' range="%s"' % f3(jp["range"])) if jp["range"] else ""
            out.append('%s  <joint name="%s_%s_joint" type="hinge" pos="0 0 0" axis="0 1 0"%s '
                       'class="motor" armature="%g" damping="%g" frictionloss="%g"/>'
                       % (pad, {"L": "left", "R": "right"}[side], jn, rng,
                          jp["armature"], jp["damping"], jp["frictionloss"]))
        elif body == "spring2":
            d = (S2 - S1) / np.linalg.norm(S2 - S1)
            out.append('%s  <joint name="%s_spring2_joint" type="slide" pos="0 0 0" '
                       'axis="%s" range="-0.02 0.06" damping="1.0" frictionloss="20" '
                       'armature="0.001"/>'
                       % (pad, {"L": "left", "R": "right"}[side], f3(d)))
        else:
            rng = PASSIVE.get(body, (-2.5, 2.5))
            out.append('%s  <joint name="%s_%s_joint" type="hinge" pos="0 0 0" axis="0 1 0" '
                       'range="%s" damping="0.01" armature="0.001" frictionloss="0.1"/>'
                       % (pad, {"L": "left", "R": "right"}[side], body, f3(rng)))
        I = v_in = bb["inertia"] / 1e6
        out.append('%s  <inertial pos="%s" mass="%.4f" fullinertia="%s"/>'
                   % (pad, f3(bb["com"] / 1000.0), bb["mass"],
                      f3([I[0, 0], I[1, 1], I[2, 2], I[0, 1], I[0, 2], I[1, 2]])))
        fn = MESH.get((body, side))
        if fn:
            out.append('%s  <geom type="mesh" contype="0" conaffinity="0" group="3" '
                       'density="0" mesh="%s_%s" rgba="0.72 0.72 0.75 1"/>'
                       % (pad, body, side.lower()))
        c = COLL[body]
        if c["type"] == "capsule":
            a = (c["a"] - anchor_of(body)) / 1000.0
            bq = (c["b"] - anchor_of(body)) / 1000.0
            out.append('%s  <geom name="%s_col" type="capsule" size="%g" fromto="%s %s" '
                       'contype="0" conaffinity="1" group="4" density="0" rgba="0 0.5 0.1 0.1"/>'
                       % (pad, "%s_%s" % (body, side.lower()), c["r"] / 1000.0, f3(a), f3(bq)))
        else:
            a = (c["a"] - anchor_of(body)) / 1000.0
            out.append('%s  <geom name="%s_col" type="cylinder" size="%g %g" pos="%s" '
                       'quat="0.5 -0.5 0.5 0.5" contype="0" conaffinity="1" group="4" '
                       'density="0" condim="6" rgba="0 0.5 0.1 0.1"/>'
                       % (pad, "%s_%s" % (body, side.lower()), c["r"] / 1000.0,
                          c["h"] / 1000.0, f3(a)))
        for child in [k for k, v2 in TOPO.items() if v2["parent"] == body]:
            rec(child, ab, depth + 1)
        out.append(pad + "</body>")
    def anchor_of(body):
        if body == "base":
            return np.zeros(3)
        p = TOPO[body]["pin"]
        return np.array([p[0], TOPO[body]["y"], p[1]])
    for top in ("thigh", "crank"):
        rec(top, None, 3)

emit_leg("L")
emit_leg("R")
out.append('    </body>')
out.append('  </worldbody>')
out.append('  <equality>')
for side, sy in (("L", -1.0), ("R", 1.0)):
    s = {"L": "left", "R": "right"}[side]
    def rel(body, pt):
        return (pt - np.array([TOPO[body]["pin"][0], TOPO[body]["y"], TOPO[body]["pin"][1]])) / 1000.0
    out.append('    <connect body1="%s_link3" body2="%s_thigh" anchor="%s" '
               'solref="0.002 1" solimp="0.99 0.999 1e-05 0.5 2"/>'
               % (s, s, f3(np.append(rel("link3", P1), 0.0))))
    out.append('    <connect body1="%s_link4" body2="%s_shank" anchor="%s" '
               'solref="0.002 1" solimp="0.99 0.999 1e-05 0.5 2"/>'
               % (s, s, f3(np.append(rel("link4", Q), 0.0))))
    out.append('    <connect body1="%s_spring2" body2="%s_shank" anchor="%s" '
               'solref="0.002 1" solimp="0.99 0.999 1e-05 0.5 2"/>'
               % (s, s, f3(np.append(rel("spring2", S2), 0.0))))
out.append('  </equality>')
out.append('  <actuator>')
for side in ("left", "right"):
    for jn in ("front1", "rear1"):
        out.append('    <motor name="%s_%s_ctrl" joint="%s_%s_joint" gear="1" '
                   'forcerange="-54 54" ctrlrange="-54 54"/>' % (side, jn, side, jn))
    out.append('    <motor name="%s_wheel_ctrl" joint="%s_wheel_joint" gear="1" '
               'forcerange="-5 5" ctrlrange="-5 5"/>' % (side, side))
    out.append('    <general name="%s_spring2_ctrl" joint="%s_spring2_joint" '
               'gaintype="fixed" gainprm="1 0 0" biastype="affine" '
               'biasprm="450 0 -2500" ctrlrange="0 0"/>' % (side, side))
out.append('  </actuator>')
out.append('  <sensor>')
out.append('    <framequat name="imu" objtype="site" objname="imu"/>')
out.append('    <gyro name="gyro" site="imu"/>')
out.append('    <accelerometer name="accelerometer" site="imu"/>')
out.append('  </sensor>')
out.append('</mujoco>')
open(os.path.join(OUT, "rm_vehicle_cc.xml"), "w", encoding="utf-8").write("\\n".join(out) + "\\n")
print("\\nwrote", os.path.join(OUT, "rm_vehicle_cc.xml"), len(out), "lines")
sc = ['<?xml version="1.0"?>', '<mujoco model="rm_vehicle_cc scene">',
      '  <include file="rm_vehicle_cc.xml"/>',
      '  <statistic width="1600" height="900"/>',
      '  <visual><global offwidth="1280" offheight="720"/><map znear="0.02"/></visual>',
      '  <asset><texture type="skybox" builtin="gradient" rgb1="0.55 0.6 0.68" '
      'rgb2="0.25 0.28 0.33" width="256" height="256"/>',
      '    <texture type="2d" name="grid" builtin="checker" rgb1="0.42 0.45 0.5" '
      'rgb2="0.62 0.65 0.7" width="512" height="512"/>',
      '    <material name="floor" texture="grid" texrepeat="8 8" reflectance="0.0"/></asset>',
      '  <worldbody><light pos="0.6 0.4 2.2" dir="0 0 -1" diffuse="1 1 1" '
      'specular="0.2 0.2 0.2"/>',
      '    <geom name="floor" type="plane" size="0 0 0.05" material="floor" contype="1" '
      'conaffinity="255" friction="1.6 0.01 0.001"/>',
      '    <camera name="front" pos="1.9 -1.3 0.5" xyaxes="0.6 0.8 0 -0.3 0.25 0.95"/>',
      '  </worldbody>', '</mujoco>']
open(os.path.join(OUT, "scene_cc.xml"), "w", encoding="utf-8").write("\\n".join(sc) + "\\n")
print("wrote", os.path.join(OUT, "scene_cc.xml"))
'''
io.open(p, "w", encoding="utf-8", newline="\n").write(t)
try:
    ast.parse(t); print("MJCF emitter appended")
except SyntaxError as e:
    print("SYNTAX", e.lineno, e.msg)
