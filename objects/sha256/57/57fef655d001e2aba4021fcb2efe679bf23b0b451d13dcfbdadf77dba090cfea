import io
F=r"D:\claude2\fangzhen\scripts\build_cc.py"
src=io.open(F,encoding="utf-8").read()
old_start = '_bad = [v for v in VISLOG if v["used"].startswith("solid_")'
old_end   = 'assert not _foreign, "FINE mesh resolved through a COARSE id: %s" % _foreign[:3]'
i = src.index(old_start); j = src.index(old_end) + len(old_end)
new = '''_fine_dir = os.path.join(FINE, "meshes")
_foreign = [v for v in VISLOG
            if os.path.dirname(v["_dir"]) == "vehicle" and v["used"] != v["solid_obj"]]
assert not _foreign, "a FINE mesh was resolved through a COARSE id: %s" % _foreign[:3]'''
src = src[:i] + new + src[j:]
# record which directory each load came from so the guard can tell FINE from COARSE
src = src.replace('''            VISLOG.append(dict(id=s["id"], solid_obj=s["obj"], used=os.path.basename(use),
                               faces=len(me.faces), body="base",
                               bucket=bucket_of(s)))''',
'''            VISLOG.append(dict(id=s["id"], solid_obj=s["obj"], used=os.path.basename(use),
                               _dir=os.path.basename(os.path.dirname(os.path.dirname(use))),
                               faces=len(me.faces), body="base", bucket=bucket_of(s)))''')
src = src.replace('''        VISLOG.append(dict(id=s["id"], solid_obj=s["obj"], used=os.path.basename(f),
                           faces=len(me.faces), body=body, side=side))''',
'''        VISLOG.append(dict(id=s["id"], solid_obj=s["obj"], used=os.path.basename(f),
                           _dir=os.path.basename(os.path.dirname(os.path.dirname(f))),
                           faces=len(me.faces), body=body, side=side))''')
io.open(F,"w",encoding="utf-8").write(src)
print("patch10 OK")