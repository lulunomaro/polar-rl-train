import io
p=r"D:/claude2/fangzhen/scripts/build_robot.py"
t=io.open(p,encoding="utf-8").read()
old='''        if target:
            budget = max(48, int(len(me.faces) * target / total))
            if len(me.faces) > budget:
                try:
                    me = me.simplify_quadric_decimation(face_count=budget)
                except Exception:
                    pass
'''
new='''        if target:
            budget = max(16, int(len(me.faces) * target / total))
            if len(me.faces) > budget:
                me = decimate_to(me, budget, passes=4)
'''
assert old in t, "MISS"
t=t.replace(old,new)
io.open(p,"w",encoding="utf-8").write(t)
print("patched per-solid multi-pass decimation")
