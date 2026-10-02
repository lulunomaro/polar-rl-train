import io
p=r"D:/claude2/fangzhen/scripts/check_mjcf.py"
t=io.open(p,encoding="utf-8").read()
t=t.replace('m.jnt_armature[j], m.dof_damping[j], m.dof_frictionloss[j]))',
            'm.dof_armature[m.jnt_dofadr[j]], m.dof_damping[m.jnt_dofadr[j]],\n             m.dof_frictionloss[m.jnt_dofadr[j]]))')
t=t.replace('    if m.geom_group[g] >= 3:\n        continue','    if m.geom_group[g] != 4:\n        continue')
t=t.replace('int(m.mesh_ndata[i]/3)','int(m.mesh_face.size)')
t=t.replace('print("  %-2s %-14s tri=%-7d vert=%d" % (i, nm, int(m.mesh_face.size), m.mesh_vertnum[i]))',
            'print("  %-2s %-14s vert=%d" % (i, nm, m.mesh_vertnum[i]))')
t=t.replace('print("  %-2s %-14s type=%s size=%s pos=%s contype=%-4d conaff=%-4d mu=%s"\n          % (g, nm, m.geom_type[g], np.round(m.geom_size[g], 4), np.round(m.geom_pos[g], 4),\n             m.geom_contype[g], m.geom_conaffinity[g], np.round(m.geom_friction[g], 3)))',
            'print("  %-2s %-14s body=%-9s type=%s size=%s pos=%s fromto=%s ct=%-4d ca=%-4d mu=%s"\n          % (g, nm, mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_BODY, m.geom_bodyid[g]),\n             m.geom_type[g], np.round(m.geom_size[g], 4), np.round(m.geom_pos[g], 4),\n             np.round(m.geom_fromto[g], 4), m.geom_contype[g], m.geom_conaffinity[g],\n             np.round(m.geom_friction[g], 3)))')
io.open(p,"w",encoding="utf-8").write(t)
print("ok")
