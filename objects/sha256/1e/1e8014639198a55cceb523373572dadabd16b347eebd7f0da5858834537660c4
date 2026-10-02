import io
F=r"D:\claude2\fangzhen\scripts\passive_range_solver.py"
s=io.open(F,encoding="utf-8").read()
old = 'cur = dict(re.findall(r\'"(shank|link2|link3|link4|spring1)":\\s*\\((-?[\\d.]+),\\s*(-?[\\d.]+)\\)\', bc))'
new = ('_f = re.findall(r\'"(shank|link2|link3|link4|spring1)":\\s*\\((-?[\\d.]+),\\s*(-?[\\d.]+)\\)\', bc)\n'
       'cur = {k: (lo, hi) for k, lo, hi in _f}')
assert s.count(old)==1, "anchor missing"
io.open(F,"w",encoding="utf-8").write(s.replace(old,new))
print("reporting fixed")