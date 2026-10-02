import io,ast
p=r"D:/claude2/fangzhen/scripts/build_robot.py"
t=io.open(p,encoding="utf-8").read()
a='''ap.add_argument("--no-mesh", action="store_true",
                help="reuse the STLs already in <outdir>/meshes (XML only)")'''
b='''ap.add_argument("--no-mesh", action="store_true",
                help="reuse the STLs already in <outdir>/meshes (XML only)")
ap.add_argument("--visual-manifest", default="",
                help="manifest whose (coarse) OBJs are used for the visual meshes")'''
assert a in t; t=t.replace(a,b)

a='''def link_mesh(ss, anchor, target):
    t0 = time.time()
    total = max(1, sum(s["ntris"] for s in ss))
    parts = []
    for s in ss:
        me = trimesh.load(os.path.join(mdir, "meshes", s["obj"]), process=False)'''
b='''VSUB = {}
if args.visual_manifest:
    cman = json.load(open(args.visual_manifest, encoding="utf-8"))
    cdir = os.path.dirname(os.path.abspath(args.visual_manifest))
    for s in cman["solids"]:
        VSUB[(s["path"], round(s["volume_mm3"], 1))] = s["obj"]
    print("visual override: %d coarse solids from %s" % (len(VSUB), cdir))


def link_mesh(ss, anchor, target):
    t0 = time.time()
    total = max(1, sum(s["ntris"] for s in ss))
    parts = []
    for s in ss:
        obj = VSUB.get((s["path"], round(s["volume_mm3"], 1)), s["obj"])
        me = trimesh.load(os.path.join(cdir if VSUB else mdir, "meshes", obj), process=False)'''
assert a in t; t=t.replace(a,b)

a='''S = man["solids"]
os.makedirs(os.path.join(args.outdir, "meshes"), exist_ok=True)'''
b='''S = man["solids"]
os.makedirs(os.path.join(args.outdir, "meshes"), exist_ok=True)'''
assert a in t
io.open(p,"w",encoding="utf-8").write(t)
ast.parse(io.open(p,encoding="utf-8").read()); print("ok")
