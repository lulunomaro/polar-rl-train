import io
p = r"D:/claude2/fangzhen/robot/vehicle.spec.yaml"
t = io.open(p, encoding="utf-8").read()
t = t.replace("range: null, effort: 24.0, class: leg", "range: [-6.2832, 6.2832], effort: 24.0, class: leg")
io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("hip range -> +-360 deg (finite, mjlab-friendly)")
