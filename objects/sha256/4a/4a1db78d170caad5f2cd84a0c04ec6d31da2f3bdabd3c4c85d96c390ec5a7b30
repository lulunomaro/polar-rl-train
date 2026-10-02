import io, ast
p = r"D:/claude2/fangzhen/scripts/scan_workspace.py"
t = io.open(p, encoding="utf-8").read()
t = t.replace("""    idx = np.floor((P - LO) / VOX).astype(np.int64)
    ok = ((idx >= 0) & (idx < DIMS[:, None])).all(0)
    i = idx[:, ok]
    return (i[0] * DIMS[1] + i[1]) * DIMS[2] + i[2]""",
"""    i = np.floor((P - LO) / VOX).astype(np.int64)
    ok = ((i >= 0) & (i < DIMS[None, :])).all(1)
    i = i[ok]
    return (i[:, 0] * DIMS[1] + i[:, 1]) * DIMS[2] + i[:, 2]""")
t = t.replace("""def dilate(grid, r):
    \"\"\"cheap clearance test: also flag neighbours within r voxels along each axis\"\"\"
    k = int(round(r / VOX))
    out = grid.copy()
    f = grid.reshape(DIMS)
    for a in range(k):
        for ax in range(3):
            out |= np.roll(f, a + 1, axis=ax).ravel()
            out |= np.roll(f, -(a + 1), axis=ax).ravel()
    return out""",
"""def dilate(grid, r):
    \"\"\"grow the chassis occupancy by r metres so near-misses count as interference\"\"\"
    k = max(1, int(round(r / VOX)))
    f = grid.reshape(DIMS)
    for _ in range(k):
        f = (f | np.roll(f, 1, 0) | np.roll(f, -1, 0)
                | np.roll(f, 1, 1) | np.roll(f, -1, 1)
                | np.roll(f, 1, 2) | np.roll(f, -1, 2))
    return f.ravel()""")
t = t.replace("""        sk = rot_about(hip_c, (0, 1, 0), sk0 - hip_c + hip_c, q1)
        wh = rot_about(hip_c, (0, 1, 0), wh0, q1)""",
"""        sk = rot_about(hip_c, (0, 1, 0), sk0, q1)
        wh = rot_about(hip_c, (0, 1, 0), wh0, q1)""")
io.open(p, "w", encoding="utf-8", newline="\n").write(t); ast.parse(t)
print("broadcast + dilation + FK order fixed")
