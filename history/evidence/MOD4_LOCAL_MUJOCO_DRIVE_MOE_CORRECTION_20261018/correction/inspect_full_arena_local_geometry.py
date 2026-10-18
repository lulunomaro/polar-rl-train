from pathlib import Path
import numpy as np, trimesh, json
B=Path(__file__).resolve().parent
W=B.parent
out=[]
for i in (6,153,181,182,183,383):
    p=W/'rmuc2026_work/processed'/f'part_{i:03}.npz'
    d=np.load(p);m=trimesh.Trimesh(d['vertices'],d['faces'],process=True)
    parts=m.split(only_watertight=False)
    r=dict(part=i,faces=len(m.faces),components=len(parts),convex_components=sum(c.is_convex for c in parts),
        facets=len(m.facets),facet_faces=sum(map(len,m.facets)))
    out.append(r);print(json.dumps(r),flush=True)
(B/'reports/FULL_ARENA_COMPONENT_INSPECTION_ACTUAL.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
