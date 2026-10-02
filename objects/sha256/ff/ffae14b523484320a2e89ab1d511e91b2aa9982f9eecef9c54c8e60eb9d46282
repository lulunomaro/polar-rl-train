import io
p=r"D:/claude2/fangzhen/scripts/build_robot.py"
t=io.open(p,encoding="utf-8-sig").read()
reps=[
 ("sc.append('  <statistic mean=\"0 0 0.3\" extent=\"1.2\"/>')",
  "sc.append('  <statistic width=\"1600\" height=\"900\"/>')"),
 ('<texture type="gridname" name="grid"', '<texture type="2d" name="grid"'),
]
for a,b in reps:
    if a not in t: print("MISS:",a[:60]); continue
    t=t.replace(a,b); print("ok:",b[:60])
io.open(p,"w",encoding="utf-8").write(t)
