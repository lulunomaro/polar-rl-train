import io
F=r"D:\claude2\fangzhen\scripts\x_patch_build.py"
s=io.open(F,encoding="utf-8").read()
old = '''rep("out.append('  <asset>')",
    "out.append('  <asset>')\\n"'''
new = '''rep("       '  <asset>']",
    "       '  <asset>']\\n"'''
assert s.count(old)==1, s.count(old)
s=s.replace(old,new)
io.open(F,"w",encoding="utf-8").write(s)
print("ok")