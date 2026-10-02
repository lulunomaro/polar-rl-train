import io
F=r"D:\claude2\fangzhen\scripts\export_sim2sim_cc.py"
src=io.open(F,encoding="utf-8").read()
def rep(old,new,cnt=1):
    global src
    assert src.count(old)==cnt,("anchor count %d:"%src.count(old))+old[:70]
    src=src.replace(old,new)
rep("""xml = xml.replace('group="3"', 'group="2"').replace('group="4"', 'group="1"')""",
    """# The plant already uses the convention validated in MuJoCo: visual geoms in group 2 (shown),
# collision primitives in group 3 (hidden).  The old 3->2 / 4->1 remap was a leftover from when
# visuals lived in group 3; with the current plant it pushed every collision capsule and the
# chassis box into the visible set, so the deployed sim drew a translucent shell over the robot.
# (group="4" no longer exists, so that half of the remap was a silent no-op.)""")
rep(""" * visual geoms -> group 2, collision geoms -> group 1 (what the bridge renders)""",
    """ * visual geoms stay in group 2 (rendered), collision geoms stay in group 3 (hidden)""")
io.open(F,"w",encoding="utf-8").write(src)
print("patch8 OK")