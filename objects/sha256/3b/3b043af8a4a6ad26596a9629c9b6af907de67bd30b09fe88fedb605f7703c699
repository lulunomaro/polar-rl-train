import io
F=r"D:\claude2\fangzhen\scripts\build_cc.py"
src=io.open(F,encoding="utf-8").read()
def rep(old,new,cnt=1):
    global src
    assert src.count(old)==cnt,("anchor count %d:"%src.count(old))+old[:70]
    src=src.replace(old,new)
rep("""      '  <visual><global offwidth="1280" offheight="720"/><map znear="0.02"/></visual>',""",
    """      '  <visual><global offwidth="1600" offheight="900"/><map znear="0.02"/>',
      '    <headlight ambient="0.38 0.38 0.40" diffuse="0.45 0.45 0.45" specular="0.2 0.2 0.2"/></visual>',""")
rep("""      '  <worldbody><light pos="0.6 0.4 2.2" dir="0 0 -1" diffuse="1 1 1" '
      'specular="0.2 0.2 0.2"/>',""",
    """      # three-point rig: without it 2.6 M triangles of same-tone sheet metal reads as noise
      '  <worldbody><light name="key" pos="1.8 -2.0 2.6" dir="-0.45 0.5 -0.8" '
      'diffuse="1 0.98 0.95" specular="0.4 0.4 0.4" cutoff="55" exponent="15"/>',
      '    <light name="fill" pos="-2.2 1.6 1.4" dir="0.6 -0.45 -0.4" '
      'diffuse="0.42 0.47 0.56" specular="0.08 0.08 0.08" cutoff="70" exponent="20"/>',
      '    <light name="rim" pos="-0.5 -2.6 1.0" dir="0.12 0.62 -0.3" '
      'diffuse="0.5 0.55 0.66" cutoff="60" exponent="20"/>',""")
io.open(F,"w",encoding="utf-8").write(src)
print("patch3 OK")