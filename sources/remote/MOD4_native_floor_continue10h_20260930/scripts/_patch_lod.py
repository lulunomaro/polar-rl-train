import io
p = r"D:/claude2/fangzhen/scripts/build_cc.py"
s = io.open(p, encoding="utf-8").read()

# legs: back to the coarse LOD (already low-poly, so nothing gets shredded), and never
# decimate below what the LOD already provides.
old = """        for d in ((FINE, COARSE) if BASE_FROM_FINE else (COARSE, FINE)):"""
new = """        for d in ((FINE, COARSE) if LEG_FROM_FINE else (COARSE, FINE)):"""
assert old in s
s = s.replace(old, new, 1)
s = s.replace('def write_mesh(body, side, budget=int(os.environ.get("CC_LEG_FACES", "9000"))):',
              'def write_mesh(body, side, budget=int(os.environ.get("CC_LEG_FACES", "10000000"))):', 1)
s = s.replace('def write_mesh(body, side, budget=int(os.environ.get("CC_LEG_FACES", "30000"))):',
              'def write_mesh(body, side, budget=int(os.environ.get("CC_LEG_FACES", "10000000"))):', 1)
# base: no decimation at all unless explicitly asked for
s = s.replace('BASE_FACE_BUDGET = int(os.environ.get("CC_BASE_FACES", "400000"))',
              'BASE_FACE_BUDGET = int(os.environ.get("CC_BASE_FACES", "10000000"))\n'
              '# legs keep their coarse LOD untouched: quadric decimation shreds thin wall\n'
              '# features and made the linkage look like scattered debris.\n'
              'LEG_FROM_FINE = os.environ.get("CC_LEG_FINE", "0") == "1"', 1)
io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("knobs: chassis=FINE untouched, legs=COARSE untouched (CC_LEG_FINE/CC_BASE_FACES to opt in)")