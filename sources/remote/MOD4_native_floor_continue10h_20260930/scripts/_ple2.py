import io, ast
p = r"D:/claude2/fangzhen/scripts/build_cc.py"
t = io.open(p, encoding="utf-8").read()
i = t.index("# ------------------------------------------------------------------ emit MJCF")
head = t[:i]
emitter = '''# ------------------------------------------------------------------ emit MJCF
SIDE_Y = {"L": 1.0, "R": -1.0}          # left leg sits at negative robot y in our frame
SIDE = {"L": "left", "R": "right"}
def f3(v):
    return " ".join("%.6g" % x for x in np.atleast_1d(v))

# per-body: parent, hinge (x,z), lateral y (left leg), collision primitive
BODY_DEF = {
    "thigh":   dict(parent="base",    pin=HIP,  y=Y_THIGH, col=("capsule", HIP, KNEE, 45.0)),
    "shank":   dict(parent="thigh",   pin=KNEE, y=Y_SHANK, col=("capsule", KNEE, AXLE, 32.0)),
    "wheel":   dict(parent="shank",   pin=AXLE, y=Y_WHEEL, col=("cylinder", AXLE, 73.0, 13.0)),
    "crank":   dict(parent="base",    pin=HIP,  y=Y_THIGH, col=("capsule", HIP, P2, 28.0)),
    "link2":   dict(parent="crank",   pin=P2,   y=Y_THIGH, col=("capsule", P2, APEX, 18.0)),
    "link3":   dict(parent="link2",   pin=APEX, y=Y_THIGH, col=("capsule", P1, P3, 18.0)),
    "link4":   dict(parent="link3",   pin=P3,   y=Y_THIGH, col=("capsule", P3, Q, 14.0)),
    "spring1": dict(parent="thigh",   pin=S1,   y=Y_THIGH, col=("capsule", S1, ((S1[0]+S2[0])/2, (S1[1]+S2[1])/2), 14.0)),
    "spring2": dict(parent="spring1", pin=S2,   y=Y_THIGH, col=("capsule", ((S1[0]+S2[0])/2, (S1[1]+S2[1])/2), S2, 17.0)),
}
ACT_OF = {"thigh": "rear1", "crank": "front1", "wheel": "wheel"}
JOINT_PAR = {
    "rear1":  dict(rng=(-3.14, 1.0), armature=0.035, damping=0.0, frictionloss=1.5),
    "front1": dict(rng=None, armature=0.035, damping=0.0, frictionloss=1.5),
    "wheel":  dict(rng=None, armature=0.001, damping=0.0, frictionloss=0.023),
}
PASSIVE_RNG = {"shank": (0.0, 1.2), "link2": (-1.0, 0.1), "link3": (-0.1, 1.0),
               "link4": (-2.0, 0.1), "spring1": (-0.5, 0.1)}

def anchor(body, side):
    d = BODY_DEF[body]
    return np.array([d["pin"][0], SIDE_Y[side] * d["y"], d["pin"][1]])
def anchor_parent(body, side):
    par = BODY_DEF[body]["parent"]
    return np.zeros(3) if par == "base" else anchor(par, side)
def to3(pt, y):
    return np.array([pt[0], y, pt[1]])

out = ['<mujoco model="rm_vehicle_cc">',
       '  <compiler angle="radian" autolimits="true" balanceinertia="true" '
       'inertiafromgeom="false"/>',
       '  <option timestep="0.002" iterations="50" ls_iterations="20" integrator="Euler" '
       'solver="Newton"/>',
       '  <default><geom condim="3" friction="1.2 0.01 0.001" margin="0"/>',
       '    <default class="motor"><joint damping="0.0" frictionloss="1.5" '
       'armature="0.035"/></default></default>',
       '  <asset>']
for f in MESH.get("base", []):
    out.append('    <mesh name="%s" file="%s" scale="0.001 0.001 0.001"/>' % (f[:-4], f))
for (body, side), fn in sorted(MESH.items(), key=lambda kv: str(kv[0])):
    if body == "base":
        continue
    out.append('    <mesh name="%s_%s" file="%s" scale="0.001 0.001 0.001"/>'
               % (body, side.lower(), fn))
out.append('  </asset>')
out.append('  <worldbody>')
out.append('    <body name="base_link" pos="0 0 0">')
out.append('      <freejoint name="floating_base"/>')
out.append('      <site name="imu" pos="0 0 0.3" size="0.01"/>')
b = BODIES["base"]; Ib = b["inertia"] / 1e6
out.append('      <inertial pos="%s" mass="%.4f" fullinertia="%s"/>'
           % (f3(b["com"] / 1000.0), b["mass"],
              f3([Ib[0, 0], Ib[1, 1], Ib[2, 2], Ib[0, 1], Ib[0, 2], Ib[1, 2]])))
for f in MESH.get("base", []):
    out.append('      <geom type="mesh" contype="0" conaffinity="0" group="3" density="0" '
               'mesh="%s" rgba="0.72 0.72 0.75 1"/>' % f[:-4])
out.append('      <geom name="base_col" type="box" size="0.357 0.196 0.1145" '
           'pos="0 0 0.1685" contype="0" conaffinity="1" group="4" density="0" '
           'rgba="0 0.5 0.1 0.12"/>')

def emit(body, side, depth):
    d = BODY_DEF[body]; bb = BODIES[body]
    pad = "  " * depth
    nm = "%s_%s" % (SIDE[side], body)
    rel = (anchor(body, side) - anchor_parent(body, side)) / 1000.0
    out.append('%s<body name="%s" pos="%s">' % (pad, nm, f3(rel)))
    jn = ACT_OF.get(body)
    if jn:
        jp = JOINT_PAR[jn]
        rng = ' range="%s"' % f3(jp["rng"]) if jp["rng"] else ""
        out.append('%s  <joint name="%s_joint" type="hinge" pos="0 0 0" axis="0 1 0"%s '
                   'class="motor" armature="%g" damping="%g" frictionloss="%g"/>'
                   % (pad, nm, rng, jp["armature"], jp["damping"], jp["frictionloss"]))
    elif body == "spring2":
        ax = np.array([S2[0] - S1[0], 0.0, S2[1] - S1[1]])
        ax = ax / np.linalg.norm(ax)
        out.append('%s  <joint name="%s_joint" type="slide" pos="0 0 0" axis="%s" '
                   'range="-0.02 0.06" damping="2.0" frictionloss="50" armature="0.001"/>'
                   % (pad, nm, f3(ax)))
    else:
        rng = PASSIVE_RNG.get(body, (-2.5, 2.5))
        out.append('%s  <joint name="%s_joint" type="hinge" pos="0 0 0" axis="0 1 0" '
                   'range="%s" damping="0.02" armature="0.001" frictionloss="0.1"/>'
                   % (pad, nm, f3(rng)))
    I = bb["inertia"] / 1e6
    out.append('%s  <inertial pos="%s" mass="%.4f" fullinertia="%s"/>'
               % (pad, f3(bb["com"] / 1000.0), bb["mass"],
                  f3([I[0, 0], I[1, 1], I[2, 2], I[0, 1], I[0, 2], I[1, 2]])))
    if (body, side) in MESH:
        out.append('%s  <geom type="mesh" contype="0" conaffinity="0" group="3" density="0" '
                   'mesh="%s_%s" rgba="0.72 0.72 0.75 1"/>' % (pad, body, side.lower()))
    y = anchor(body, side)[1]
    c = d["col"]
    if c[0] == "capsule":
        a0 = (to3(c[1], y) - anchor(body, side)) / 1000.0
        a1 = (to3(c[2], y) - anchor(body, side)) / 1000.0
        out.append('%s  <geom name="%s_col" type="capsule" size="%g" fromto="%s %s" '
                   'contype="0" conaffinity="1" group="4" density="0" '
                   'rgba="0 0.5 0.1 0.12"/>' % (pad, nm, c[3] / 1000.0, f3(a0), f3(a1)))
    else:
        a0 = (to3(c[1], y) - anchor(body, side)) / 1000.0
        out.append('%s  <geom name="%s_col" type="cylinder" size="%g %g" pos="%s" '
                   'quat="0.5 -0.5 0.5 0.5" condim="6" priority="1" contype="0" '
                   'conaffinity="1" group="4" density="0" rgba="0 0.5 0.1 0.12"/>'
                   % (pad, nm, c[2] / 1000.0, c[3] / 1000.0, f3(a0)))
    for child, cd in BODY_DEF.items():
        if cd["parent"] == body:
            emit(child, side, depth + 1)
    out.append(pad + "</body>")

for side in ("L", "R"):
    for top in ("thigh", "crank"):
        emit(top, side, 3)
out.append('    </body>')
out.append('  </worldbody>')

out.append('  <equality>')
for side in ("L", "R"):
    s = SIDE[side]
    def rel_pt(body, pt):
        y = anchor(body, side)[1]
        return (to3(pt, y) - anchor(body, side)) / 1000.0
    for b1, b2, pt in (("%s_link3" % s, "%s_thigh" % s, P1),
                       ("%s_link4" % s, "%s_shank" % s, Q),
                       ("%s_spring2" % s, "%s_shank" % s, S2)):
        who = "link3" if "link3" in b1 else ("link4" if "link4" in b1 else "spring2")
        out.append('    <connect body1="%s" body2="%s" anchor="%s" solref="0.002 1" '
                   'solimp="0.99 0.999 1e-05 0.5 2"/>' % (b1, b2, f3(rel_pt(who, pt))))
out.append('  </equality>')

out.append('  <actuator>')
for side in ("left", "right"):
    for jn in ("front1", "rear1"):
        out.append('    <motor name="%s_%s_ctrl" joint="%s_%s_joint" gear="1" '
                   'forcerange="-54 54" ctrlrange="-54 54"/>' % (side, jn, side, jn))
    out.append('    <motor name="%s_wheel_ctrl" joint="%s_wheel_joint" gear="1" '
               'forcerange="-5 5" ctrlrange="-5 5"/>' % (side, side))
    out.append('    <general name="%s_spring2_force" joint="%s_spring2_joint" '
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
print("\\nwrote rm_vehicle_cc.xml (%d lines)" % len(out))
sc = ['<?xml version="1.0"?>', '<mujoco model="rm_vehicle_cc scene">',
      '  <include file="rm_vehicle_cc.xml"/>',
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
      '  </worldbody>',
      '  <keyframe><key name="stand" qpos="0 0 0.075 1 0 0 0 ' +
      " ".join(["0"] * 18) + '"/></keyframe>', '</mujoco>']
open(os.path.join(OUT, "scene_cc.xml"), "w", encoding="utf-8").write("\\n".join(sc) + "\\n")
print("wrote scene_cc.xml")
'''
io.open(p, "w", encoding="utf-8", newline="\n").write(head + emitter)
ast.parse(head + emitter); print("emitter rewritten cleanly")
