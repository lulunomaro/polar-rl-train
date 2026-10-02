import io
p=r"D:/claude2/fangzhen/scripts/build_robot.py"
t=io.open(p,encoding="utf-8").read()
a='''ap.add_argument("--scale", type=float, default=1.0, help="extra visual decimation scale")'''
b='''ap.add_argument("--scale", type=float, default=1.0, help="extra visual decimation scale")
ap.add_argument("--no-mesh", action="store_true",
                help="reuse the STLs already in <outdir>/meshes (XML only)")'''
assert a in t; t=t.replace(a,b)
a='''    chunks = link_mesh(ss, anchor, int(lk.get("visual_faces", 0) * args.scale))
    files = []
    for i, mm in enumerate(chunks):
        fn = "%s.stl" % name if len(chunks) == 1 else "%s_%02d.stl" % (name, i)
        mm.export(os.path.join(args.outdir, "meshes", fn))
        files.append(fn)'''
b='''    nfaces = 0
    if args.no_mesh:
        import glob
        files = sorted(os.path.basename(f) for f in
                       glob.glob(os.path.join(args.outdir, "meshes", name + "*.stl")))
        assert files, "no cached mesh for %s" % name
    else:
        chunks = link_mesh(ss, anchor, int(lk.get("visual_faces", 0) * args.scale))
        files = []
        for i, mm in enumerate(chunks):
            fn = "%s.stl" % name if len(chunks) == 1 else "%s_%02d.stl" % (name, i)
            mm.export(os.path.join(args.outdir, "meshes", fn))
            files.append(fn)
            nfaces += len(mm.faces)'''
assert a in t; t=t.replace(a,b)
a='''    info[name] = dict(n=len(ss), mass=mass, com=com, inertia=I, eig=w, geoms=geoms,
                      mesh=files, nfaces=sum(len(c.faces) for c in chunks), spec=lk)'''
b='''    info[name] = dict(n=len(ss), mass=mass, com=com, inertia=I, eig=w, geoms=geoms,
                      mesh=files, nfaces=nfaces, spec=lk)'''
assert a in t; t=t.replace(a,b)
a='''          (name, len(ss), mass, np.round(com / 1000.0, 4), np.round(w / 1e6, 5), info[name]["nfaces"]))'''
b='''          (name, len(ss), mass, np.round(com / 1000.0, 4), np.round(w / 1e6, 5), nfaces))'''
assert a in t; t=t.replace(a,b)
io.open(p,"w",encoding="utf-8").write(t)
print("build_robot: --no-mesh added")
