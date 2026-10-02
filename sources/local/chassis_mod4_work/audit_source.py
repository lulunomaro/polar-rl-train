"""Read-only B-Rep checks of MOD4 stops and wheel materials."""
from pathlib import Path
import sys,json,math
import numpy as np
from geometry import PARTS,ROT,O,PINS,configuration
from OCP.STEPCAFControl import STEPCAFControl_Reader
from OCP.TDocStd import TDocStd_Document
from OCP.TCollection import TCollection_ExtendedString
from OCP.XCAFDoc import XCAFDoc_DocumentTool
from OCP.TDF import TDF_Label
from OCP.collections import Sequence_TDF_Label
from OCP.TopLoc import TopLoc_Location
from OCP.gp import gp_Trsf
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_SOLID
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps
from OCP.BRepBndLib import BRepBndLib
from OCP.Bnd import Bnd_Box
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.BRepTools import BRepTools
from OCP.TopoDS import TopoDS_Shape
from OCP.BRep import BRep_Builder
sys.stdout.reconfigure(encoding='utf8')
ROOT=Path(__file__).parent;cache=ROOT/'reports/brep';cache.mkdir(exist_ok=True)
wanted={119,120,124,129,134,144,145,146,147,148,149,183}
shapes={}
if all((cache/f'{i}.brep').exists() for i in wanted):
    for i in wanted:
        s=TopoDS_Shape();BRepTools.Read_s(s,str(cache/f'{i}.brep'),BRep_Builder());shapes[i]=s
else:
    doc=TDocStd_Document(TCollection_ExtendedString('audit'));reader=STEPCAFControl_Reader()
    assert int(reader.ReadFile(r'C:\Users\lulu\Downloads\底盘_MOD4.STEP'))==1;assert reader.Transfer(doc)
    st=XCAFDoc_DocumentTool.ShapeTool_s(doc.Main());roots=Sequence_TDF_Label();st.GetFreeShapes(roots)
    counter=0
    def walk(label,parent):
        global counter
        loc=parent.Multiplied(st.GetLocation_s(label));definition=label
        if st.IsReference_s(label):definition=TDF_Label();st.GetReferredShape_s(label,definition)
        children=Sequence_TDF_Label();st.GetComponents_s(definition,children)
        if children.Length():
            for k in range(1,children.Length()+1):walk(children.Value(k),loc)
        else:
            s=st.GetShape_s(definition)
            if not s.IsNull():
                if counter in wanted:
                    shapes[counter]=s.Moved(loc);BRepTools.Write_s(shapes[counter],str(cache/f'{counter}.brep'))
                counter+=1
    for k in range(1,roots.Length()+1):walk(roots.Value(k),TopLoc_Location())
    assert counter==277

def transform(shape,R,t):
    tr=gp_Trsf();tr.SetValues(*np.column_stack((R,t)).ravel())
    return BRepBuilderAPI_Transform(shape,tr,True).Shape()

def ry(q):
    c,s=math.cos(q),math.sin(q);return np.array([[c,0,s],[0,1,0],[-s,0,c]])

si={i:transform(s,ROT*.001,-ROT@O*.001) for i,s in shapes.items()}
p=PINS['right'];pivot=lambda key:np.array([p[key][0],0.,p[key][1]])
def moved(i,diff):
    v,q=configuration(0.,diff)
    kind={134:('K',v['knee']),124:('P',v['rocker_pin']),119:('O',v['crank'])}
    if i not in kind:return si[i]
    key,ang=kind[i];R=ry(ang);return transform(si[i],R,pivot(key)-R@pivot(key))

def distance(a,b):
    op=BRepExtrema_DistShapeShape(a,b);op.Perform();assert op.IsDone();return float(op.Value())

def volume(a,b):
    op=BRepAlgoAPI_Common(a,b);op.Build();pr=GProp_GProps();BRepGProp.VolumeProperties_s(op.Shape(),pr);return float(pr.Mass())

def main():
    report={'source':'MOD4 exact B-Rep solids','stop_part':145,'samples':[],'wheel_solids':[]}
    for diff in np.arange(-.8,1.601,.1):
        try:v,q=configuration(0.,float(diff))
        except ValueError:continue
        gaps={str(i):distance(si[145],moved(i,float(diff))) for i in [119,124,134]}
        row={'difference_rad':float(diff),'knee_rad':v['knee'],'stop_gaps_m':gaps}
        report['samples'].append(row);print(row,flush=True)

    ex=TopExp_Explorer(shapes[183],TopAbs_SOLID)
    while ex.More():
        s=ex.Current();pr=GProp_GProps();BRepGProp.VolumeProperties_s(s,pr)
        bb=Bnd_Box();BRepBndLib.AddOptimal_s(s,bb);xyz=lambda p:[p.X(),p.Y(),p.Z()]
        I=pr.MatrixOfInertia()
        report['wheel_solids'].append({'volume_mm3':pr.Mass(),'com_mm':xyz(pr.CentreOfMass()),'bbox_mm':xyz(bb.CornerMin())+xyz(bb.CornerMax()),
          'inertia_mm5':[[I.Value(a,b) for b in range(1,4)] for a in range(1,4)]})
        ex.Next()
    (ROOT/'reports/source_audit.json').write_text(json.dumps(report,indent=2),encoding='utf8')
    print('DONE',len(report['wheel_solids']),'wheel solids',flush=True)


if __name__ == '__main__':
    main()
