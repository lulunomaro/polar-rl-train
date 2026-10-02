import io
F=r"D:\claude2\fangzhen\scripts\build_cc.py"
src=io.open(F,encoding="utf-8").read()
def rep(old,new,cnt=1):
    global src
    assert src.count(old)==cnt,("anchor count %d:"%src.count(old))+old[:70]
    src=src.replace(old,new)
# A MuJoCo plane with size.x=size.y=0 is drawn out to the scene bounding box and gets
# composited OVER the robot in an offscreen pass (the whole shot turns milky).  A finite
# quad renders correctly and is what the bucket test used.
rep("""      '    <geom name="floor" type="plane" size="0 0 0.05" material="floor" contype="1" '
      'conaffinity="255" friction="1.6 0.01 0.001"/>',""",
    """      '    <geom name="floor" type="plane" size="8 8 0.05" material="floor" contype="1" '
      'conaffinity="255" friction="1.6 0.01 0.001" rgba="0.55 0.55 0.58 1"/>',""")
io.open(F,"w",encoding="utf-8").write(src)
print("patch7 OK")