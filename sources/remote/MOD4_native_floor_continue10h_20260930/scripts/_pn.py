import io
p=r"D:/claude2/fangzhen/robot/vehicle.spec.yaml"
t=io.open(p,encoding="utf-8").read()
t=t.replace("range: [-2.2, 0.4], effort: 30.0","range: [-2.2, 2.1], effort: 30.0")
io.open(p,"w",encoding="utf-8").write(t)
print("knee range widened")
