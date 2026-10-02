"""Fast text-level scan of a huge STEP file: product names + assembly edges, no geometry."""
import re, sys, collections
P = r"C:/Users/lulunomaro/Downloads/RMUC2026_V2.0.0.stp"
prod = {}          # id -> name
nauo = []          # (parent_prod_id, child_prod_id, name)
rx_p = re.compile(r"^#(\d+)\s*=\s*PRODUCT\s*\(\s*'[^']*'\s*,\s*'([^']*)'")
rx_a = re.compile(r"^#(\d+)\s*=\s*NEXT_ASSEMBLY_USAGE_OCCURRENCE\s*\(\s*'[^']*'\s*,\s*'([^']*)'\s*,\s*'[^']*'")
rx_ctx = re.compile(r"^#(\d+)\s*=\s*PRODUCT_DEFINITION_CONTEXT\s*\(")
n = 0
with open(P, "r", encoding="utf-8", errors="replace") as f:
    for line in f:
        n += 1
        if n % 2000000 == 0:
            sys.stderr.write("... %dM lines, %d products, %d edges\n" % (n // 1000000, len(prod), len(nauo)))
        if "#=" not in line[:14] and not line.startswith("#"):
            continue
        m = rx_p.match(line)
        if m:
            prod[m.group(1)] = m.group(2).strip()
            continue
        m = rx_a.match(line)
        if m:
            nauo.append((m.group(1), m.group(2).strip()))
print("lines:", n, "products:", len(prod), "assembly edges:", len(nauo))
import json
json.dump({"products": prod, "edges": nauo}, open(r"D:/claude2/fangzhen/cad/out_map/tree.json", "w", encoding="utf-8"), ensure_ascii=False)
print("\n== distinct product name stems (top 60) ==")
c = collections.Counter()
for name in prod.values():
    key = re.sub(r"[\d_\-]+$", "", name).strip()
    c[key] += 1
for k, v in c.most_common(60):
    print("   %5d  %s" % (v, k))
print("\n== top-level assembly edges (name contains map-ish words) ==")
KW = ("坡", "台", "阶", "障碍", "掩体", "基地", "补给", "竞技", "地形", "地面", "地板", "RAMP", "STEP", "BASE", "OBST", "TERRAIN", "FLOOR", "PLATFORM", "SLOPE", "岛", "资源", "哨", "塔", "桥", "栏", "墙")
hits = [(i, nm) for i, nm in prod.items() if any(k.lower() in nm.lower() for k in KW)]
for i, nm in hits[:80]:
    print("   #%s  %s" % (i, nm))
print("   ... total keyword hits:", len(hits))
