import io
p=r"D:/claude2/fangzhen/scripts/check_mjcf.py"
t=io.open(p,encoding="utf-8").read()
t=t.replace('ntri=%d nSensor=%d','ntri=%d nkey=%d')
t=t.replace('m.nmesh, m.ntri, m.nsensor, m.nkey))','m.nmesh, int(m.mesh_face.sum()), m.nsensor))')
t=t.replace('I = np.linalg.eigvalsh(m.inertia_full[b]) if m.nv else np.zeros(3)',
            'I = np.linalg.eigvalsh(np.diag(m.body_inertia[b]))')
io.open(p,"w",encoding="utf-8").write(t)
print("ok")
