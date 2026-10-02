
import re, sys, collections
p = r"C:/Users/lulunomaro/Desktop/整车总装.STEP"
cnt = collections.Counter()
prod = []
units = []
line_re = re.compile(r'^#(\d+) = ([A-Z_0-9]+)\s*\(')
with open(p, 'r', encoding='utf8', errors='replace') as f:
    for i, line in enumerate(f):
        m = line_re.match(line)
        if m:
            k = m.group(2)
            cnt[k] += 1
            if k == 'PRODUCT':
                prod.append(line.strip())
        else:
            s = line.strip()
            if 'SI_UNIT' in s and len(units) < 40:
                units.append(s[:200])
print("TOTAL LINES", i+1)
print("--- top entity types ---")
for k,v in cnt.most_common(20): print("%-40s %d" % (k,v))
print("--- key counts ---")
for k in ['PRODUCT','PRODUCT_DEFINITION','PRODUCT_DEFINITION_SHAPE','MANIFOLD_SOLID_BREP','CLOSED_SHELL','ADVANCED_BREP_SHAPE_REPRESENTATION','SHAPE_REPRESENTATION','MECHANICAL_CONTEXT','PRODUCT_CONTEXT','ITEM_DEFINED_TRANSFORMATION','PRODUCT_RELATED_PRODUCT_CATEGORY','AXIS2_PLACEMENT_3D']:
    print("%-40s %d" % (k, cnt.get(k,0)))
print("--- units sample ---")
for u in units[:15]: print(u)
print("--- first 25 products ---")
for s in prod[:25]: print(s[:200])
