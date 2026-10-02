import io, sys
p = r"D:/claude2/fangzhen/scripts/build_robot.py"
c = io.open(p, encoding="utf-8-sig").read()
reps = []
reps.append((
"                    me = me.simplify_quadric_decimation(face_count=budget)",
"                    me = me.simplify_quadric_decimation(face_count=budget, aggression=4)"))
reps.append((
'''    mesh = trimesh.util.concatenate(parts)
    cap = min(int(decimate or 0), 190000) if decimate else 0
    for _ in range(4):
        if not cap or len(mesh.faces) <= cap:
            break
        try:
            mesh = mesh.simplify_quadric_decimation(face_count=cap)
        except Exception as e:
            print("   (decimation unavailable: %s)" % e)
            break
    return mesh''',
'''    mesh = trimesh.util.concatenate(parts)
    # MuJoCo's STL decoder caps a single mesh at 200k faces -> split into chunks.
    CAP = 150000
    if len(mesh.faces) > CAP:
        chunks = []
        cur = 0
        while cur < len(mesh.faces):
            sel_f = np.arange(cur, min(cur + CAP, len(mesh.faces)))
            chunks.append(mesh.submesh([sel_f], append=True))
            cur += CAP
    else:
        chunks = [mesh]
    return chunks'''))
reps.append((
'''    mesh = link_mesh(ss, anchor, args.decimate or lk.get("decimate", 0))
    stl = "%s.stl" % name
    mesh.export(os.path.join(args.outdir, "meshes", stl))''',
'''    meshes = link_mesh(ss, anchor, args.decimate or lk.get("decimate", 0))
    stl = []
    for i, mm in enumerate(meshes):
        fn = "%s.stl" % name if len(meshes) == 1 else "%s_%02d.stl" % (name, i)
        mm.export(os.path.join(args.outdir, "meshes", fn))
        stl.append(fn)
    mesh = trimesh.util.concatenate(meshes)'''))
reps.append(('                      nfaces=int(len(mesh.faces)), spec=lk)',
             '                      nfaces=int(sum(len(x.faces) for x in meshes)), spec=lk)'))
reps.append(('        name, len(ss), mass, np.round(com / 1000.0, 4), len(mesh.faces)))',
             '        name, len(ss), mass, np.round(com / 1000.0, 4), sum(len(x.faces) for x in meshes)))'))
reps.append((
'''for name, v in info.items():
    out.append('    <mesh name="%s" file="%s"/>' % (name, v["mesh"]))''',
'''for name, v in info.items():
    for i, fn in enumerate(v["mesh"]):
        out.append('    <mesh name="%s_%02d" file="%s"/>' % (name, i, fn))'''))
reps.append((
"""    out.append('%s  <geom class="visual" mesh="%s" rgba="%s"/>' % (pad, name, rgba))""",
"""    for i in range(len(v["mesh"])):
        out.append('%s  <geom class="visual" mesh="%s_%02d" rgba="%s"/>' % (pad, name, i, rgba))"""))
for a, b in reps:
    if a not in c:
        print("MISS:", a.splitlines()[0][:70])
    else:
        c = c.replace(a, b)
io.open(p, "w", encoding="utf8").write(c)
import ast
ast.parse(c)
print("patched + syntax ok")
