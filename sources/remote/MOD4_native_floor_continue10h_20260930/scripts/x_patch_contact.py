import io
F=r"D:\claude2\fangzhen\scripts\export_sim2sim_cc.py"
s=io.open(F,encoding="utf-8").read()
anchor = "# ------------------------------------------------------------------ 2. MJCF edits"
assert s.count(anchor)==1
add = '''# ------------------------------------------------------------------ 2. MJCF edits
# Contact model.  Training builds the robot through mjlab CollisionCfg(
#     geom_names_expr=collide_geoms, contype=0, conaffinity=1,
#     condim={wheels: 6, ".*": 1}, priority={wheels: 1},
#     friction={wheels: (1.2, 0.02, 0.002)}, disable_other_geoms=True),
# which is NOT what the raw MJCF says.  Three concrete mismatches made the deployed
# plant a different physical object than the trained one:
#   * leg/spring capsules: MJCF default condim=3 (sticking friction) vs trained condim=1
#   * chassis box:         MJCF conaffinity=1 (can touch the floor) vs trained collision OFF
#   * wheels:              MJCF friction "1.2 0.01 0.001" vs trained "1.2 0.02 0.002"
# Reproduce the trained contact model so the policy is evaluated on the plant it learned.
_CAPS = re.compile(r"<geom name=\\"[^\\"]*_(?:rear1|rear2|front[1-4]|spring[12])_link_collision\\"")
def _condim1(mo):
    t = mo.group(0)
    return t if "condim=" in t else re.sub(r"<geom name=", '<geom condim="1" name=', t, count=1)
xml = _CAPS.sub(_condim1, xml)
xml = xml.replace('<geom name="base_link_collision" type="box"',
                  '<geom name="base_link_collision" contype="0" conaffinity="0" type="box"')
xml = xml.replace('name="left_wheel_link_collision"', 'friction="1.2 0.02 0.002" name="left_wheel_link_collision"')
xml = xml.replace('name="right_wheel_link_collision"', 'friction="1.2 0.02 0.002" name="right_wheel_link_collision"')
print("contact model -> trained: capsules condim=1, chassis box non-colliding, wheel friction 1.2/0.02/0.002")

'''
io.open(F,"w",encoding="utf-8").write(s.replace(anchor, add.rstrip("\n")))
print("contact patch OK")