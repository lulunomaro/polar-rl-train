import io
F=r"D:\claude2\fangzhen\train\verify_skills.py"
s=io.open(F,encoding="utf-8").read()
a='for kk, lb in enumerate(["L_front1", "L_rear1", "L_wheel",\n                                 "R_front1", "R_rear1", "R_wheel"]):'
b='for kk, lb in enumerate(["L_front1", "L_rear1", "R_front1",\n                                 "R_rear1", "L_wheel", "R_wheel"]):'
assert s.count(a)==1
io.open(F,"w",encoding="utf-8").write(s.replace(a,b))
print("labels fixed to the action-term order (4 legs then 2 wheels)")