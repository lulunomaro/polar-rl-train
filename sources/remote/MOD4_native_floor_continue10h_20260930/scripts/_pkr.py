import io,ast
p=r"D:/claude2/fangzhen/scripts/export_sim2sim.py"
t=io.open(p,encoding="utf-8").read()
a='''        out.append('%s    <joint name="%s_spring2_joint" type="slide" pos="0 0 0" '
                   'axis="0 0 1" range="0 0" limited="true" damping="50" frictionloss="0" '
                   'armature="0"/>' % (pad, side))'''
b='''        out.append('%s    <joint name="%s_spring2_joint" type="slide" pos="0 0 0" '
                   'axis="0 0 1" range="-0.001 0.001" stiffness="100000" damping="2000" '
                   'frictionloss="0" armature="0.001"/>' % (pad, side))'''
assert a in t
t=t.replace(a,b)
io.open(p,"w",encoding="utf-8").write(t); ast.parse(t); print("ok")
