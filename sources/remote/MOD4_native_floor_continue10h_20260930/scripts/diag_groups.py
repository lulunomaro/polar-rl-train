import io, re, os, json
s = io.open(r"D:/claude2/fangzhen/scripts/build_cc.py", encoding="utf-8").read()
print("=== build_cc.py 里所有涉及 groups / 归类 的行 ===")
for i, l in enumerate(s.splitlines()):
    if re.search(r"groups|CLASS|classify|dropped|unassigned|LINK_OF|assign", l):
        print("%4d %s" % (i + 1, l.strip()[:150]))