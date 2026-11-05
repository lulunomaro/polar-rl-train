"""ONE source-shape root-cause recovery. Preserve original failed6-vertex code.
Actual source has arbitrary convex polyhedra (6..420 vertices),not all tri-prisms.
Use installed SciPy ConvexHull ONLY for bbox-selected public-plan candidates.
No SDK/model/physics/scene edits/archivalhash/oldraw/controller input.
"""
from pathlib import Path
import ast
R=Path(__file__).resolve().parent

def main():
 old=R/'audit_public_route_macro_heights_once.py';text=old.read_text(encoding='utf-8')
 def one(a,b):
  nonlocal text
  if text.count(a)!=1:raise RuntimeError('Recovery anchor differs: '+a)
  text=text.replace(a,b,1)
 one("D=R/'PUBLIC_ROUTE_FOOTPRINT_SOURCE_V1'","D=R/'PUBLIC_ROUTE_FOOTPRINT_SOURCE_V1/RETRY001'")
 one("if len(v)!=6:raise ValueError('Not 6-vertex convex triangle prism')","if len(v)<4:raise ValueError('Source collider has fewer than4 vertices')")
 one("verts=np.array([v for _,v in records]);lo=verts[:,:,:2].min(axis=1);hi=verts[:,:,:2].max(axis=1)",
  "verts=[v for _,v in records];lo=np.array([v[:,:2].min(axis=0)for v in verts]);hi=np.array([v[:,:2].max(axis=0)for v in verts])")
 one("combinations=list(itertools.combinations(range(6),3));queries=0","hull_cache={};hull_errors={};queries=0")
 node=next(n for n in ast.walk(ast.parse(text))if isinstance(n,ast.FunctionDef)and n.name=='top')
 lines=text.splitlines(keepends=True);oldfunc=''.join(lines[node.lineno-1:node.end_lineno])
 newfunc=''' def top(x,y):
  nonlocal queries
  queries+=1;point=np.array([x,y]);ids=np.flatnonzero(np.all(lo<=point+1e-10,axis=1)&np.all(hi>=point-1e-10,axis=1));best=None;hit=None;unknown=[]
  for i0 in ids:
   i=int(i0)
   if i not in hull_cache and i not in hull_errors:
    try:hull_cache[i]=ConvexHull(verts[i]).equations
    except Exception as exc:hull_errors[i]=str(exc)
   if i in hull_errors:unknown.append(records[i][0]);continue
   E=hull_cache[i];rhs=-(E[:,0]*x+E[:,1]*y+E[:,3]);nz=E[:,2]
   flat=abs(nz)<1e-12;up=nz>=1e-12;down=nz<=-1e-12
   if np.any(rhs[flat]<-1e-9)or not np.any(up)or not np.any(down):continue
   upper=float(np.min(rhs[up]/nz[up]));lower=float(np.max(rhs[down]/nz[down]))
   if upper<lower-1e-9:continue
   if best is None or upper>best:best=upper;hit=records[i][0]
  return dict(x_m=x,y_m=y,top_z_m=best if not unknown else None,known_partial_top_z_m=best,
   top_source_geom=hit,candidate_convex_colliders=len(ids),unknown=best is None or bool(unknown),unknown_hull_candidates=unknown)
'''
 if text.count(oldfunc)!=1:raise RuntimeError('Unexpected original top function')
 text=text.replace(oldfunc,newfunc,1)
 text='from scipy.spatial import ConvexHull\n'+text
 one("actual_collision_prisms=len(records),actual_point_queries=queries,rows=rows,",
  "actual_collision_convex_colliders=len(records),actual_point_queries=queries,actual_selected_hull_builds=len(hull_cache),hull_errors=hull_errors,rows=rows,")
 text=text.replace('Each prism\'s upper convex envelope','Each source collider upper convex envelope')
 text=text.replace('Source convex-prism geometry heights','Source convex-hull geometry heights')
 if "RETRY001"not in text:raise RuntimeError('No fresh recovery prefix')
 compile(text,'public_route_macro_source_recovery','exec')
 exec(compile(text,'public_route_macro_source_recovery','exec'),{'__name__':'__main__','__file__':str(old)})
if __name__=='__main__':main()
