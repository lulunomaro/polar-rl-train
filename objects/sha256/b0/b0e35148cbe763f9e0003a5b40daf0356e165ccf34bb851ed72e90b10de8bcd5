import io
F=r"D:\claude2\fangzhen\scripts\hop_control_law.py"
src=io.open(F,encoding="utf-8").read()
def rep(old,new,cnt=1):
    global src
    assert src.count(old)==cnt,("anchor count %d:"%src.count(old))+old[:70]
    src=src.replace(old,new)
rep("    hop = 0.0\n    cr = 0.0\n    air = 0.0\n",
    "    hop = 0.0\n    cr = 0.0\n    air = 0.0\n    tilt = 0.0\n    tilt_at_hop = 0.0\n")
rep('''        if z0 is not None:
            dz = float(d.qpos[2]) - z0
            hop = max(hop, dz)
            cr = min(cr, dz)
            if not wheels_down():
                air += DT''',
    '''        qu = d.qpos[3:7]
        uw = np.array([2 * (qu[1] * qu[3] - qu[0] * qu[2]),
                       2 * (qu[2] * qu[3] + qu[0] * qu[1]),
                       1 - 2 * (qu[1] * qu[1] + qu[2] * qu[2])])
        tl = float(np.degrees(np.arccos(np.clip(np.dot(uw, UP), -1.0, 1.0))))
        tilt = max(tilt, tl)
        if z0 is not None:
            dz = float(d.qpos[2]) - z0
            if dz > hop:
                hop, tilt_at_hop = dz, tl
            cr = min(cr, dz)
            if not wheels_down():
                air += DT''')
rep("    return hop * 100.0, cr * 100.0, air * 1000.0",
    "    return hop * 100.0, cr * 100.0, air * 1000.0, tilt, tilt_at_hop")
rep('print("%-16s %-12s %8s %10s %8s" % ("control law", "variant", "hop cm", "crouch cm", "air ms"))',
    'print("%-16s %-12s %8s %10s %8s %9s %10s" % ("control law", "variant", "hop cm",\n'
    '      "crouch cm", "air ms", "tilt max", "tilt@hop"))')
rep('        hop, cr, air = run(hz, mode)\n        print("%-16s %-12s %8.1f %10.1f %8.0f" % (lab, mode, hop, cr, air))',
    '        hop, cr, air, tl, tlh = run(hz, mode)\n'
    '        print("%-16s %-12s %8.1f %10.1f %8.0f %9.1f %10.1f %s"\n'
    '              % (lab, mode, hop, cr, air, tl, tlh,\n'
    '                 "UPRIGHT" if tl < 25 else "TOPPLED - not a hop"))')
io.open(F,"w",encoding="utf-8").write(src)
print("harness2 patched")