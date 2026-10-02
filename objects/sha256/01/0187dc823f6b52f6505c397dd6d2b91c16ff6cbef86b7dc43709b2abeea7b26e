import re, collections
P = r"C:/Users/lulunomaro/Downloads/RMUC2026_V2.0.0.stp"
rx = re.compile(r"^#(\d+)\s*=\s*([A-Z_0-9]+)\s*\(")
cnt = collections.Counter(); samples = {}
want = {"NEXT_ASSEMBLY_USAGE_OCCURRENCE", "PRODUCT", "PRODUCT_DEFINITION", "PRODUCT_DEFINITION_FORMATION",
        "PRODUCT_DEFINITION_FORMATION_WITH_SPECIFIED_SOURCE", "PRODUCT_DEFINITION_SHAPE",
        "SHAPE_DEFINITION_REPRESENTATION", "MANIFOLD_SOLID_BREP", "ADVANCED_BREP_SHAPE_REPRESENTATION",
        "ITEM_DEFINED_TRANSFORMATION", "CARTESIAN_POINT", "PRODUCT_RELATED_PRODUCT_CATEGORY", "MECHANICAL_CONTEXT"}
with open(P, encoding="utf-8", errors="replace") as f:
    for i, line in enumerate(f):
        if i > 4_000_000: break
        m = rx.match(line)
        if not m: continue
        t = m.group(2); cnt[t] += 1
        if t in want and t not in samples:
            samples[t] = line.strip()[:400]
print("entity counts (first 4M lines):")
for k, v in cnt.most_common(18):
    print("   %10d  %s" % (v, k))
print()
for k in ("NEXT_ASSEMBLY_USAGE_OCCURRENCE", "PRODUCT", "PRODUCT_DEFINITION", "PRODUCT_DEFINITION_SHAPE",
          "PRODUCT_RELATED_PRODUCT_CATEGORY", "MANIFOLD_SOLID_BREP", "ITEM_DEFINED_TRANSFORMATION"):
    if k in samples: print("%-34s %s\n" % (k, samples[k]))
