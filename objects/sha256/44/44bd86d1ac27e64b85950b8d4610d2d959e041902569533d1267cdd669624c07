
import re, sys, collections
p = r"C:/Users/lulunomaro/Desktop/整车总装.STEP"
cnt = collections.Counter()
prod = []
units = []
metrc = []
line_re = re.compile(r'^#(\d+) = ([A-Z_0-9]+)\s*\(')
prod_re = re.compile(r"PRODUCT \( *'([^']*)', *'([^']*)', *'([^']*)', *\(([^)]*)\)")
with open(p, 'r', encoding='utf8', errors='replace') as f:
    for i, line in enumerate(f):
        m = line_re.match(line)
        if m:
            cnt[m.group(2)] += 1
            if m.group(2) in ('PRODUCT','PRODUCT_DEFINITION','PRODUCT_DEFINITION_SHAPE','MANIFOLD_SOLID_BREP','ADVANCED_BREP_SHAPE_REPRESENTATION','SHAPE_REPRESENTATION','MECHANICAL_CONTEXT','PRODUCT_CONTEXT'):
                if len(prod) < 200000 and m.group(2)=='PRODUCT':
                    prod.append(line.strip())
            if m.group(2) in ('MANIFOLD_SOLID_BREP',):
                metrc.append(line.strip())
        else:
            s = line.strip()
            if s.startswith('( SI_UNIT') or 'LENGTH_UNIT' in s or 'PLANE_ANGLE_UNIT' in s or s.startswith('#') and 'SI_UNIT' in s:
                if len(units) < 40: units.append(s[:200])
print("TOTAL LINES", i+1)
print("--- top entity types ---")
for k,v in cnt.most_common(25): print(f"{k:40s} {v}")
print("--- key counts ---")
for k in ['PRODUCT','PRODUCT_DEFINITION','PRODUCT_DEFINITION_SHAPE','MANIFOLD_SOLID_BREP','CLOSED_SHELL','ADVANCED_BREP_SHAPE_REPRESENTATION','SHAPE_REPRESENTATION','MECHANICAL_CONTEXT','PRODUCT_CONTEXT','COUPLED_TRANSFORMATION','ITEM_DEFINED_TRANSFORMATION','PRODUCT_RELATED_PRODUCT_CATEGORY']:
    print(f"{k:40s} {cnt.get(k,0)}")
print("--- units sample ---")
for u in units[:20]: print(u)
print("--- first 30 products ---")
for s in prod[:30]: print(s[:220])
