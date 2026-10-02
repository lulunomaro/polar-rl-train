import io
p=r"D:/claude2/fangzhen/scripts/build_robot.py"
t=io.open(p,encoding="utf-8").read()
a='specular="0.2" castshadow="true"'
b='specular="0.2 0.2 0.2" castshadow="true"'
assert a in t, "MISS"
io.open(p,"w",encoding="utf-8").write(t.replace(a,b))
print("patched light specular")
