import io
F=r"D:\claude2\fangzhen\scripts\build_cc.py"
src=io.open(F,encoding="utf-8").read()
def rep(old,new,cnt=1):
    global src
    assert src.count(old)==cnt,("anchor count %d:"%src.count(old))+old[:70]
    src=src.replace(old,new)

# ---- regression guard: record exactly which CAD solid produced which rendered facet ----
rep("print(\"\\n== meshes ==\")\nMESH = {}",
    "print(\"\\n== meshes ==\")\nMESH = {}\nVISLOG = []   # one row per CAD solid that reached a mesh file")

rep('''        try:
            me = trimesh.load(f, process=False)
        except Exception:
            continue
        me.apply_transform(A4)
        parts.append(me)''',
    '''        try:
            me = trimesh.load(f, process=False)
        except Exception:
            continue
        VISLOG.append(dict(id=s["id"], solid_obj=s["obj"], used=os.path.basename(f),
                           faces=len(me.faces), body=body, side=side))
        me.apply_transform(A4)
        parts.append(me)''')

rep('''            if len(me.faces) == 0:
                _empty.append(s["product"].strip())
                continue
            me.apply_transform(A4)
            parts.append(me)
            _names.append((s["product"].strip(), bucket_of(s)))''',
    '''            if len(me.faces) == 0:
                _empty.append(s["product"].strip())
                continue
            VISLOG.append(dict(id=s["id"], solid_obj=s["obj"], used=os.path.basename(use),
                               faces=len(me.faces), body="base",
                               bucket=bucket_of(s)))
            me.apply_transform(A4)
            parts.append(me)
            _names.append((s["product"].strip(), bucket_of(s)))''')

rep('print("  leg meshes:", len(MESH) - 1, "files")',
    '''print("  leg meshes:", len(MESH) - 1, "files")

# --- visual completeness / identity guard -------------------------------------
# The chassis mesh is built from the FINE export, whose file names are per-solid ids.
# The COARSE export numbers its solids differently, so a COARSE name must never be
# resolved inside the FINE directory: that is how ~700 chassis parts once ended up
# being drawn as some other part (screws in place of armour plates), which is exactly
# the "parts flying around / gutted body" symptom.  Assert it cannot happen again.
_ids = [v["id"] for v in VISLOG]
assert len(_ids) == len(man["solids"]), \\
    ("visual mesh has %d solids but the CAD has %d" % (len(_ids), len(man["solids"])))
assert len(set(_ids)) == len(_ids), "a CAD solid was emitted twice"
_bad = [v for v in VISLOG if v["used"].startswith("solid_") and v["used"] != v["solid_obj"]
        and os.path.join(FINE, "meshes", v["used"]) == os.path.join(FINE, "meshes", v["solid_obj"])]
_bad = [v for v in VISLOG if v["used"] != v["solid_obj"]
        and os.path.exists(os.path.join(FINE, "meshes", v["used"]))
        and os.path.exists(os.path.join(COARSE, "meshes", v["used"]))
        and v["used"] == os.path.basename(v["used"]) and not v["used"].startswith("solid_")]
_foreign = [v for v in VISLOG if v["used"] != v["solid_obj"]
            and os.path.basename(v["used"]) == v["used"]
            and os.path.exists(os.path.join(FINE, "meshes", v["used"]))
            and not os.path.exists(os.path.join(COARSE, "meshes", v["used"]))]
assert not _foreign, "FINE mesh resolved through a COARSE id: %s" % _foreign[:3]
json.dump(VISLOG, open(os.path.join(OUT, "visual_manifest_cc.json"), "w"), indent=1)
print("  visual guard: %d/%d CAD solids accounted for, 0 foreign-id FINE loads"
      % (len(_ids), len(man["solids"])))''')
io.open(F,"w",encoding="utf-8").write(src)
print("patch9 OK")