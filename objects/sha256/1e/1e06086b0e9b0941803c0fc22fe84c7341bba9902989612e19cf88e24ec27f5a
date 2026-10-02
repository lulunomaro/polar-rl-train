def f3(v):
    return " ".join("%.6g" % x for x in np.atleast_1d(v))


# ------------------------------------------------------------------ kinematic tree
children = collections.defaultdict(list)
jinfo = {}
for j in spec["joints"]:
    children[j["parent"]].append(j["child"])
    jinfo[j["child"]] = j

order = [lk["name"] for lk in spec["links"] if lk["name"] in info]
roots = [n for n in order if n not in jinfo]
assert len(roots) == 1, roots
root = roots[0]
CT = {"base": 16, "thigh": 32, "shank": 64, "wheel": 128}


def emit_body(name, depth):
    v = info[name]
    lk = v["spec"]
    j = jinfo.get(name)
    pad = "  " * depth
    anchor = np.array(lk["anchor"], float) / 1000.0
    if j is None:
        out.append('%s<body name="%s" pos="%s">' % (pad, name, f3(anchor)))
        out.append('%s  <freejoint name="root"/>' % pad)
        out.append('%s  <site name="imu" size="0.01" group="5"/>' % pad)
    else:
        pa = np.array(info[j["parent"]]["spec"]["anchor"], float) / 1000.0
        out.append('%s<body name="%s" pos="%s">' % (pad, name, f3(anchor - pa)))
        rng = j.get("range")
        extra = ' range="%s"' % f3(rng) if rng else ""
        out.append('%s  <joint name="%s" type="%s" pos="0 0 0" axis="%s"%s '
                   'damping="%g" armature="%g" frictionloss="%g" actuatorfrcrange="%g %g"/>'
                   % (pad, j["name"], j.get("type", "hinge"), f3(j["axis"]), extra,
                      j.get("damping", 0.0), j.get("armature", 0.0),
                      j.get("frictionloss", 0.0), -j["effort"], j["effort"]))
    com = v["com"] / 1000.0 - anchor
    I = v["inertia"] / 1e6
    out.append('%s  <inertial pos="%s" mass="%.4f" fullinertia="%s"/>'
               % (pad, f3(com), v["mass"],
                  f3([I[0, 0], I[1, 1], I[2, 2], I[0, 1], I[0, 2], I[1, 2]])))
    rgba = " ".join("%.3f" % x for x in lk.get("rgba", [.7, .7, .75, 1]))
    for fn in v["mesh"]:
        out.append('%s  <geom type="mesh" contype="0" conaffinity="0" group="3" density="0" '
                   'rgba="%s" mesh="%s"/>' % (pad, rgba, fn[:-4]))
    bit = CT[name.split("_")[0]]
    common = 'group="4" contype="%d" conaffinity="0" density="0" rgba="0 0.55 0.15 0.15"' % bit
    for gi, g in enumerate(v["geoms"]):
        if g["type"] == "box":
            out.append('%s  <geom name="%s_col%d" type="box" size="%s" pos="%s" quat="%s" %s/>'
                       % (pad, name, gi, f3(g["size"]), f3(g["pos"]), f3(g["quat"]), common))
        elif g["type"] == "capsule":
            a, b = np.array(g["p0"], float) / 1000.0, np.array(g["p1"], float) / 1000.0
            out.append('%s  <geom name="%s_col%d" type="capsule" size="%g" fromto="%s %s" %s/>'
                       % (pad, name, gi, g["radius"] / 1000.0, f3(a), f3(b), common))
        else:
            out.append('%s  <geom name="%s_col%d" type="cylinder" size="%s" pos="%s" quat="%s" %s/>'
                       % (pad, name, gi, f3(g["size"]), f3(g["pos"]), f3(g["quat"]), common))
    for c in children.get(name, []):
        emit_body(c, depth + 1)
    out.append(pad + "</body>")


out = []
out.append('<mujoco model="%s">' % spec["name"])
out.append('  <compiler angle="radian" meshdir="meshes/" autolimits="true" '
           'balanceinertia="true" inertiafromgeom="false"/>')
out.append('  <option timestep="0.002" iterations="50" ls_iterations="20" '
           'integrator="implicitfast"/>')
out.append('  <default>')
out.append('    <geom condim="3" friction="1.2 0.01 0.001" solref="0.01 1" '
           'solimp="0.9 0.95 0.001"/>')
out.append('    <default class="leg"><joint damping="0.05" armature="0.0036" '
           'frictionloss="0.05"/></default>')
out.append('    <default class="wheel"><joint damping="0.0" armature="0.0021" '
           'frictionloss="0.02"/></default>')
out.append('  </default>')
out.append('  <asset>')
for name, v in info.items():
    for fn in v["mesh"]:
        out.append('    <mesh name="%s" file="%s" scale="0.001 0.001 0.001"/>'
                   % (fn[:-4], fn))
out.append('  </asset>')
out.append('  <worldbody>')
emit_body(root, 2)
out.append('  </worldbody>')
out.append('  <actuator>')
for j in spec["joints"]:
    e = j["effort"]
    out.append('    <motor name="%s" joint="%s" gear="1" forcerange="-%g %g" '
               'ctrlrange="-%g %g"/>' % (j["name"], j["name"], e, e, e, e))
out.append('  </actuator>')
out.append('  <sensor>')
out.append('    <framequat name="proj_grav" objtype="site" objname="imu"/>')
out.append('    <gyro name="gyro" site="imu"/>')
out.append('    <accelerometer name="acc" site="imu"/>')
for j in spec["joints"]:
    out.append('    <jointpos name="q_%s" joint="%s"/>' % (j["name"], j["name"]))
    out.append('    <jointvel name="dq_%s" joint="%s"/>' % (j["name"], j["name"]))
out.append('  </sensor>')
out.append('</mujoco>')

mjcf = os.path.join(args.outdir, spec["name"] + ".xml")
open(mjcf, "w", encoding="utf-8").write("\n".join(out) + "\n")
print("wrote", mjcf, len(out), "lines")

# ------------------------------------------------------------------ scene.xml
jnames = [j["name"] for j in spec["joints"]]
wheel_r = min(g["size"][0] for n, v in info.items() if n.startswith("wheel")
              for g in v["geoms"] if g["type"] == "cylinder")
key_qpos = [0.0, 0.0, wheel_r + 0.002, 1.0, 0.0, 0.0, 0.0] + [0.0] * len(jnames)
sc = []
sc.append('<mujoco model="%s_scene">' % spec["name"])
sc.append('  <include file="%s.xml"/>' % spec["name"])
sc.append('  <statistic mean="0 0 0.3" extent="1.2"/>')
sc.append('  <asset>')
sc.append('    <texture type="skybox" builtin="gradient" rgb1="0.55 0.6 0.68" '
           'rgb2="0.25 0.28 0.33" width="256" height="256"/>')
sc.append('    <texture type="gridname" name="grid" builtin="checker" rgb1="0.35 0.38 0.42" '
           'rgb2="0.5 0.53 0.57" width="200" height="200"/>')
sc.append('    <material name="floor" texture="grid" texrepeat="8 8" reflectance="0.05"/>')
sc.append('  </asset>')
sc.append('  <worldbody>')
sc.append('    <light name="t" pos="0.6 0.4 2.2" dir="0 0 -1" diffuse="0.9 0.9 0.9" '
           'specular="0.2" castshadow="true"/>')
sc.append('    <light name="s" pos="-0.8 0.6 1.6" dir="0.4 -0.3 -1" diffuse="0.4 0.4 0.4"/>')
sc.append('    <geom name="floor" type="plane" size="0 0 0.05" material="floor" '
           'contype="1" conaffinity="255" friction="1.6 0.01 0.001"/>')
sc.append('    <camera name="front" pos="2.0 -1.1 0.55" xyaxes="0.5 0.87 0 -0.35 0.2 0.91"/>')
sc.append('    <camera name="side" pos="0.0 -2.2 0.45" xyaxes="1 0 0 0 -0.2 0.98"/>')
sc.append('    <camera name="top" pos="0 0 2.4" xyaxes="1 0 0 0 -1 0"/>')
sc.append('    <body name="target" pos="0 0 0.15" mocap="true">')
sc.append('      <geom type="box" size="0.02 0.02 0.02" contype="0" conaffinity="0" '
           'rgba="1 0.2 0.2 0.6" group="5"/>')
sc.append('    </body>')
sc.append('  </worldbody>')
sc.append('  <keyframe>')
sc.append('    <key name="stand" qpos="%s"/>' % f3(key_qpos))
sc.append('  </keyframe>')
sc.append('</mujoco>')
scene = os.path.join(args.outdir, "scene.xml")
open(scene, "w", encoding="utf-8").write("\n".join(sc) + "\n")
print("wrote", scene, "wheel_r=%.4f" % wheel_r)
