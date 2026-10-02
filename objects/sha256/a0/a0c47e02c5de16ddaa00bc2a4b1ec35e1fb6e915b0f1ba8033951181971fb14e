import io
p=r"D:/claude2/fangzhen/robot/vehicle.spec.yaml"
t=io.open(p,encoding="utf-8").read()
t=t.replace("range: [-1.8, 1.2], effort: 17.0, class: leg","range: [-1.8, 1.2], effort: 30.0, class: leg")
t=t.replace("range: [-2.2, 0.4], effort: 17.0, class: leg","range: [-2.2, 0.4], effort: 30.0, class: leg")
io.open(p,"w",encoding="utf-8").write(t)
print("spec: leg effort 30 Nm")
