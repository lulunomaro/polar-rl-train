import io,ast
p=r"D:/claude2/fangzhen/scripts/build_robot.py"
t=io.open(p,encoding="utf-8").read()
a="""sc.append('  <worldbody>')"""
b="""sc.append('  <visual>')
sc.append('    <global offwidth="1280" offheight="720"/>')
sc.append('    <map znear="0.02"/>')
sc.append('    <quality shadowtype="soft"/>')
sc.append('  </visual>')
sc.append('  <worldbody>')"""
assert a in t
t=t.replace(a,b,1)
ast.parse(t); io.open(p,"w",encoding="utf-8").write(t); print("added <visual> to scene")
