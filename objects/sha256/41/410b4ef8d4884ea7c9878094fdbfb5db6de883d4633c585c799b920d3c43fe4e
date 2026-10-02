import io
F=r"D:\claude2\fangzhen\scripts\export_sim2sim_cc.py"
s=io.open(F,encoding="utf-8").read()
old = """xml = xml.replace('<geom name="base_col" type="box"',
                  '<geom name="base_col" contype="0" conaffinity="0" type="box"')"""
new = """# rewrite in place - adding a second contype/conaffinity would be a duplicate attribute
def _box_off(mo):
    return re.sub(r'conaffinity="\\d+"', 'conaffinity="0"', mo.group(0))
xml = re.sub(r'<geom name="base_col"[^>]*>', _box_off, xml, count=1)"""
assert s.count(old)==1
io.open(F,"w",encoding="utf-8").write(s.replace(old,new))
print("dedup fix OK")