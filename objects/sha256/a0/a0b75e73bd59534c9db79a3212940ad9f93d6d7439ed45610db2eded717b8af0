import io
F=r"D:\claude2\fangzhen\scripts\build_cc.py"
src=io.open(F,encoding="utf-8").read()
old = """      '  <visual><global offwidth="1600" offheight="900"/><map znear="0.02"/>',"""
new = """      # MuJoCo fog defaults to start=0.7 m / end=7 m, which veils a 1.5 m product shot
      # in flat grey and makes a solid machine look translucent.  Push it far out.
      '  <visual><global offwidth="1600" offheight="900"/>',
      '    <map znear="0.02" fogstart="25" fogend="80" shadow="0.7"/>',"""
assert src.count(old)==1, src.count(old)
io.open(F,"w",encoding="utf-8").write(src.replace(old,new))
print("patch6 OK")