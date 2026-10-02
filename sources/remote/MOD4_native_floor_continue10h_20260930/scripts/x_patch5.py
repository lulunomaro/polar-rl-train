import io
F=r"D:\claude2\fangzhen\scripts\build_cc.py"
src=io.open(F,encoding="utf-8").read()
old = """      '  <visual><global offwidth="1600" offheight="900"/><map znear="0.02"/>',"""
new = """      # fogstart/fogend default to 0.7 m / 7 m, which veils a 1.5 m product shot in grey
      '  <visual><global offwidth="1600" offheight="900" fogstart="12" fogend="60" '
      'eyepose="0 0 1.2 0 1 0"/><map znear="0.02"/>',"""
assert src.count(old)==1
io.open(F,"w",encoding="utf-8").write(src.replace(old,new))
print("patch5 OK")