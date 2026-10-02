import io
p=r"D:/claude2/fangzhen/scripts/check_mjcf.py"
t=io.open(p,encoding="utf-8").read()
t=t.replace('ntri = int(m.mesh_face.sum()) if m.nmesh else 0','ntri = int(m.mesh_face.size // 3) if m.nmesh else 0')
t=t.replace("eig = np.sort(np.linalg.eigvalsh(np.diag(m.body_inertia[b]))) / 1000.0","eig = np.sort(np.linalg.eigvalsh(np.diag(m.body_inertia[b])))")
t=t.replace("m.jnt_armature[j],","m.dof_armature[m.jnt_dofadr[j]],")
t=t.replace('"%-7d"% ','')
t=t.replace('print("  %-2s %-14s face=%-7d vert=%d" % (i, nm, m.mesh_face[i], m.mesh_vertnum[i]))',
            'print("  %-2s %-14s tri=%-7d vert=%d" % (i, nm, int(m.mesh_ndata[i]/3), m.mesh_vertnum[i]))')
io.open(p,"w",encoding="utf-8").write(t)
print("ok")
