import json, os, sys, collections, re
man = json.load(open(sys.argv[1], encoding="utf8"))
S = man["solids"]
lvl = int(sys.argv[2]) if len(sys.argv) > 2 else 3
filt = sys.argv[3] if len(sys.argv) > 3 else ""
c = collections.Counter()
vol = collections.Counter()
for s in S:
    if filt and not re.search(filt, s["path"]):
        continue
    k = "/".join(s["path"].split("/")[:lvl])
    c[k] += 1
    vol[k] += s["volume_mm3"]
for k, n in sorted(c.items(), key=lambda kv: -kv[1]):
    print("%4d %9.1fcm3  %s" % (n, vol[k] / 1000, k))
