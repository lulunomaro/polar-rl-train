import io
p=r"D:/claude2/fangzhen/scripts/check_mjcf.py"
t=io.open(p,encoding="utf-8").read()
old=t.split("\n")[6]
new=('print("nq=%d nv=%d nu=%d nbody=%d ngeom=%d nmesh=%d ntri=%d nsensor=%d nkey=%d"\n'
     '      % (m.nq, m.nv, m.nu, m.nbody, m.ngeom, m.nmesh, int(m.mesh_face.sum()),\n'
     '         m.nsensor, m.nkey))')
t=t.replace(old,new,1)
io.open(p,"w",encoding="utf-8").write(t)
print(repr(old))
