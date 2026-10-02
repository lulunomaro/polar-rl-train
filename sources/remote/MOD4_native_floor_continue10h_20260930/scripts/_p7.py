import io
p=r"D:/claude2/fangzhen/scripts/check_mjcf.py"
t=io.open(p,encoding="utf-8").read().split("\n")
# drop lines 6..9 (0-based 5..8) region that forms the broken print, rebuild it
i=[k for k,l in enumerate(t) if l.startswith("print(")][0]
j=[k for k,l in enumerate(t) if "m.nsensor" in l or "m.nkey" in l][0]
t=t[:i]+['print("nq=%d nv=%d nu=%d nbody=%d ngeom=%d nmesh=%d ntri=%d nsensor=%d nkey=%d"',
         '      % (m.nq, m.nv, m.nu, m.nbody, m.ngeom, m.nmesh,',
         '         int(m.mesh_face.sum()), m.nsensor, m.nkey))']+t[j+1:]
io.open(p,"w",encoding="utf-8").write("\n".join(t))
print("rebuilt header at line",i+1)
