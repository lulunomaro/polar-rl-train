import io,ast
p=r"D:/claude2/fangzhen/scripts/export_sim2sim.py"
t=io.open(p,encoding="utf-8").read()
t=t.replace('''def arr(vals):
    return "[" + ", ".join("%g" % x for x in vals) + "]"''','''def arr(vals):
    # ROS parameter files require homogeneous sequences: always emit doubles.
    return "[" + ", ".join("%.6f" % float(x) for x in vals) + "]"''')
io.open(p,"w",encoding="utf-8").write(t); ast.parse(t); print("arr -> all doubles")
