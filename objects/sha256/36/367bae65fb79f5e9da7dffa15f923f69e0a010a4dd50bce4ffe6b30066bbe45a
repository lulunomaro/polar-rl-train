import io
p=r"D:/claude2/fangzhen/scripts/build_robot.py"
t=io.open(p,encoding="utf-8").read()
a='''    nfaces = 0
    if args.no_mesh:
        import glob
        files = sorted(os.path.basename(f) for f in
                       glob.glob(os.path.join(args.outdir, "meshes", name + "*.stl")))
        assert files, "no cached mesh for %s" % name
    else:'''
b='''    nfaces = 0
    if args.no_mesh:
        files = mesh_index.get(name)
        assert files, "no cached mesh for %s (run without --no-mesh first)" % name
        nfaces = int(mesh_faces.get(name, 0))
    else:'''
assert a in t; t=t.replace(a,b)
a='''info = collections.OrderedDict()
print("== link physics ==")'''
b='''mesh_index, mesh_faces = {}, {}
idx_path = os.path.join(args.outdir, "mesh_index.json")
if os.path.exists(idx_path):
    jj = json.load(open(idx_path, encoding="utf-8"))
    mesh_index = {k: v["files"] for k, v in jj.items()}
    mesh_faces = {k: v["nfaces"] for k, v in jj.items()}

info = collections.OrderedDict()
print("== link physics ==")'''
assert a in t; t=t.replace(a,b)
a='''            files.append(fn)
            nfaces += len(mm.faces)'''
b='''            files.append(fn)
            nfaces += len(mm.faces)
        mesh_index[name] = list(files)
        mesh_faces[name] = nfaces'''
assert a in t; t=t.replace(a,b)
a='''raw_total = sum(v["mass"] for v in info.values())'''
b='''if not args.no_mesh:
    json.dump(mesh_index and {k: dict(files=v, nfaces=mesh_faces[k])
                              for k, v in mesh_index.items()},
              open(idx_path, "w"), indent=1)
    print("wrote", idx_path)

raw_total = sum(v["mass"] for v in info.values())'''
assert a in t; t=t.replace(a,b)
io.open(p,"w",encoding="utf-8").write(t)
import ast; ast.parse(io.open(p,encoding="utf-8").read()); print("patched + syntax ok")
