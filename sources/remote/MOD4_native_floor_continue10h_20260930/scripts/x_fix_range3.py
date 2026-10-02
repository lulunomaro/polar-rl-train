import io
F=r"D:\claude2\fangzhen\scripts\passive_range_solver.py"
lines=io.open(F,encoding="utf-8").read().split("\n")
hit=[n for n,l in enumerate(lines) if l.strip()=="c = cur.get(name[k])"]
assert len(hit)==1, hit
i=hit[0]
ind=len(lines[i])-len(lines[i].lstrip())
lines[i]=" "*ind+'c = cur.get(name.get(k, k)) if k != "spring2" else ("-0.030", "0.085")'
io.open(F,"w",encoding="utf-8").write("\n".join(lines))
print("guarded")