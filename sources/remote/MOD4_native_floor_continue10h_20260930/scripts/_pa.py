import io
p=r"D:/claude2/fangzhen/scripts/check_mjcf.py"
t=io.open(p,encoding="utf-8").read()
t=t.replace('np.round(m.geom_fromto[g], 4), ','')
t=t.replace('"  %-2s %-14s body=%-9s type=%s size=%s pos=%s fromto=%s ct=%-4d ca=%-4d mu=%s"','"  %-2s %-14s body=%-9s type=%s size=%s pos=%s quat=%s ct=%-4d ca=%-4d mu=%s"')
t=t.replace('np.round(m.geom_pos[g], 4),\n             m.geom_contype','np.round(m.geom_pos[g], 4), np.round(m.geom_quat[g], 3),\n             m.geom_contype')
io.open(p,"w",encoding="utf-8").write(t)
print("ok")
