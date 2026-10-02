import io, re
F=r"D:\claude2\fangzhen\scripts\export_sim2sim_cc.py"
s=io.open(F,encoding="utf-8").read()
# the *_link_collision names only exist AFTER line ~116; this block runs before that,
# so match the plant's own geom names instead.
old_caps = '_CAPS = re.compile(r"<geom name=\\"[^\\"]*_(?:rear1|rear2|front[1-4]|spring[12])_link_collision\\"")'
new_caps = '_CAPS = re.compile(r"<geom name=\\"[^\\"]*_(?:rear1|rear2|front[1-4]|spring[12])_col\\"")'
assert s.count(old_caps)==1
s=s.replace(old_caps,new_caps)
s=s.replace('''xml = xml.replace('<geom name="base_link_collision" type="box"',
                  '<geom name="base_link_collision" contype="0" conaffinity="0" type="box"')
xml = xml.replace('name="left_wheel_link_collision"', 'friction="1.2 0.02 0.002" name="left_wheel_link_collision"')
xml = xml.replace('name="right_wheel_link_collision"', 'friction="1.2 0.02 0.002" name="right_wheel_link_collision"')''',
'''xml = xml.replace('<geom name="base_col" type="box"',
                  '<geom name="base_col" contype="0" conaffinity="0" type="box"')
xml = xml.replace('name="left_wheel_col"', 'friction="1.2 0.02 0.002" name="left_wheel_col"')
xml = xml.replace('name="right_wheel_col"', 'friction="1.2 0.02 0.002" name="right_wheel_col"')''')
io.open(F,"w",encoding="utf-8").write(s)
print("contact patch now matches the plant's own geom names")