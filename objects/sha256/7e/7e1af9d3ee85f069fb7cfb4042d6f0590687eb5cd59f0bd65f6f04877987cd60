import io
p=r"D:/claude2/fangzhen/scripts/export_sim2sim.py"
t=io.open(p,encoding="utf-8").read()
t=t.replace('name="%s_wheel_collision"','name="%s_wheel_link_collision"')
io.open(p,"w",encoding="utf-8").write(t)
print("wheel geom renamed to <side>_wheel_link_collision")
