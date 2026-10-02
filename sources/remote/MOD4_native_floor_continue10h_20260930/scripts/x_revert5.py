import io
F=r"D:\claude2\fangzhen\scripts\build_cc.py"
s=io.open(F,encoding="utf-8").read()
new = ('      # fogstart/fogend default to 0.7 m / 7 m, which veils a 1.5 m product shot in grey\n'
       '      \'  <visual><global offwidth="1600" offheight="900" fogstart="12" fogend="60" \'\n'
       '      \'eyepose="0 0 1.2 0 1 0"/><map znear="0.02"/>\',')
old = '      \'  <visual><global offwidth="1600" offheight="900"/><map znear="0.02"/>\','
assert s.count(new)==1, s.count(new)
io.open(F,"w",encoding="utf-8").write(s.replace(new, old))
print("reverted patch5")