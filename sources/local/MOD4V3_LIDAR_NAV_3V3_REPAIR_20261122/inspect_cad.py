from nav_common import HERE, put
import cadquery as cq
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.GeomAbs import GeomAbs_Plane
import numpy as np

shape = cq.importers.importStep(str(HERE / 'assets/cad/RMUL2027_3V3_V1.0.0.stp')).val()
rows = []
for i, face in enumerate(shape.Faces()):
    surf = BRepAdaptor_Surface(face.wrapped)
    bb = face.BoundingBox()
    center = face.Center()
    normal = face.normalAt()
    rows.append(dict(i=i, type=str(surf.GetType()), area=face.Area() * 1e-6,
                     center=[center.x*.001, center.z*.001, -center.y*.001],
                     normal=[normal.x, normal.z, -normal.y],
                     bbox_cad=[bb.xmin,bb.xmax,bb.ymin,bb.ymax,bb.zmin,bb.zmax],
                     vertices=[[v.X*.001,v.Z*.001,-v.Y*.001] for v in face.Vertices()]))
put(HERE / 'evidence/CAD_FACES.json', rows)
print('solids', len(shape.Solids()), 'faces', len(rows))
for row in rows:
    if row['normal'][2] > .15:
        print(row)
