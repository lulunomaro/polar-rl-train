import io
p=r"D:/claude2/fangzhen/scripts/verify_axes.py"
t=io.open(p,encoding="utf-8").read()
t=t.replace("from OCP.TDF import TDF_LabelSequence","from OCP.TDF import TDF_LabelSequence, TDF_Label")
t=t.replace('    shape.Location(__import__("OCP.TopLoc", fromlist=["TopLoc"]).TopLoc_Location())',
            "    shape.Location(TopLoc_Location())")
t=t.replace("from OCP.TopoDS import TopoDS","from OCP.TopoDS import TopoDS\nfrom OCP.TopLoc import TopLoc_Location")
io.open(p,"w",encoding="utf-8",newline="\n").write(t)
import ast; ast.parse(t); print("ok")
