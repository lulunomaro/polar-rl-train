import io
F=r"D:\claude2\fangzhen\scripts\build_cc.py"
src=io.open(F,encoding="utf-8").read()
old='''_foreign = [v for v in VISLOG
            if os.path.dirname(v["_dir"]) == "vehicle" and v["used"] != v["solid_obj"]]'''
new='''_foreign = [v for v in VISLOG
            if v["_dir"] == "vehicle" and v["used"] != v["solid_obj"]]'''
assert src.count(old)==1
io.open(F,"w",encoding="utf-8").write(src.replace(old,new))
print("patch11 OK")