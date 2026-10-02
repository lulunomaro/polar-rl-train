import io
p = r"D:/claude2/fangzhen/scripts/build_cc.py"
s = io.open(p, encoding="utf-8").read()
old = """print("  (leg parts kept chassis-side: %d distinct)" % len([u for u in un if u]))"""
new = old + '''

# ---- audit: what actually landed on the MOVING leg bodies? ----
MOTOR_WORDS = ("电机", "DM_8116", "DM80", "链轮", "链条", "齿轮", "起步齿轮", "轴承",
               "滑环", "中心轴", "涨块", "轴系", "卡簧", "键")
print("\\n== leg-body audit (motor / sprocket / chain / bearing parts on moving bodies) ==")
for body, cfg in TOPO.items():
    items = [i for i in groups.get(body, []) if isinstance(i, tuple)]
    if not items:
        continue
    names = sorted({i[1]["product"].strip() for i in items})
    bad = [n for n in names if any(w in n for w in MOTOR_WORDS)]
    print("  %-8s %3d solids, %3d distinct names, SUSPECT=%d" % (body, len(items), len(names), len(bad)))
    for n in bad[:14]:
        print("       ! ", n[:70])
    if not bad:
        for n in names[:6]:
            print("       . ", n[:70])
'''
assert old in s
s = s.replace(old, new, 1)
io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("audit added")