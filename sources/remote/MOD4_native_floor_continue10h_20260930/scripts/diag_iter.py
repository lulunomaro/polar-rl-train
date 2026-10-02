import io, re
d = io.open(r"D:/claude2/fangzhen/docs/_cc_v12.log", "rb").read().decode("utf-8", "replace")
its = re.findall(r"Learning iteration (\d+)/\d+", d)
times = re.findall(r"Iteration time: ([\d.]+)s", d)
coll = re.findall(r"Collection time: ([\d.]+)s", d)
learn = re.findall(r"Learning time: ([\d.]+)s", d)
sps = re.findall(r"Steps per second: (\d+)", d)
print("iterations logged:", len(its), "first", its[:3], "last", its[-3:])
for i in range(max(0, len(times) - 12), len(times)):
    print("  iter %s  total %7s s  collect %7s s  learn %6s s  sps %s" %
          (its[i], times[i], coll[i] if i < len(coll) else "?", learn[i] if i < len(learn) else "?",
           sps[i] if i < len(sps) else "?"))