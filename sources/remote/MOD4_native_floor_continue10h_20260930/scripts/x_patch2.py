import io
F=r"D:\claude2\fangzhen\scripts\build_cc.py"
src=io.open(F,encoding="utf-8").read()
def rep(old,new,cnt=1):
    global src
    assert src.count(old)==cnt,("anchor count %d:"%src.count(old))+old[:80]
    src=src.replace(old,new)

# CSUB is keyed by (path,volume) and yields the *coarse* manifest's file name.
# Loading that name out of the FINE directory therefore renders a DIFFERENT solid.
rep('''        obj = CSUB.get((s["path"], round(s["volume_mm3"], 1)), s["obj"])
        # same LOD policy as the chassis: FINE first, so sprockets/bearing seats survive
        for d in ((FINE, COARSE) if LEG_FROM_FINE else (COARSE, FINE)):
            f = os.path.join(d, "meshes", obj)
            if os.path.exists(f):
                break''',
    '''        # NOTE: CSUB maps (path, volume) -> the *coarse* manifest's file name, so it may
        # only ever be used to build a COARSE path.  The FINE mesh of a solid is its own
        # s["obj"]; mixing the two ids rendered ~700 chassis parts as the wrong part.
        obj = CSUB.get((s["path"], round(s["volume_mm3"], 1)), s["obj"])
        cand = [(os.path.join(COARSE, "meshes", obj)), os.path.join(FINE, "meshes", s["obj"])]
        if LEG_FROM_FINE:
            cand = cand[::-1]
        for f in cand:
            if os.path.exists(f):
                break''')

rep('''            obj = CSUB.get((s["path"], round(s["volume_mm3"], 1)), s["obj"])
            # the coarse LOD drops thin connectors (light bar, ammo-path plates, carbon
            # sheets) to zero facets, which is what made the chassis look "incomplete".
            # The visual mesh now comes from the FINE export, decimated once, gently.
            fine_f = os.path.join(FINE, "meshes", obj)
            coarse_f = os.path.join(COARSE, "meshes", obj)''',
    '''            # the coarse LOD drops thin connectors (light bar, ammo-path plates, carbon
            # sheets) to zero facets, which is what made the chassis look "incomplete".
            # The visual mesh now comes from the FINE export, decimated once, gently.
            # CSUB's value is a COARSE file name -> only valid under COARSE/.
            obj = CSUB.get((s["path"], round(s["volume_mm3"], 1)), s["obj"])
            fine_f = os.path.join(FINE, "meshes", s["obj"])
            coarse_f = os.path.join(COARSE, "meshes", obj)''')
io.open(F,"w",encoding="utf-8").write(src)
print("patch2 OK")