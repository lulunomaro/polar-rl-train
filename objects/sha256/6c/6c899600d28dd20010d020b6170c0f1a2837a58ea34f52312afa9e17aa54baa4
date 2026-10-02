import io
F=r"D:\claude2\fangzhen\scripts\build_cc.py"
s=io.open(F,encoding="utf-8").read()
a='fogend="80" shadow="0.7"'
assert s.count(a)==1
s=s.replace(a,'fogend="80"')
io.open(F,"w",encoding="utf-8").write(s)
print("shadow attr removed")