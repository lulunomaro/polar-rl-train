from pathlib import Path
import hashlib,numpy as np
from curb20_geometry import make_mesh
from g4_worldmesh_query_contract import canonical_triangles,downward_triangle_heights
def expected_ground(actual_vertices,actual_faces,centers,actual_starts):
 tri=np.asarray(actual_vertices,dtype=np.float32)[actual_faces];centroid=tri.astype(np.float64).mean(1);out=[];receipts=[];evidence=[]
 for center,starts in zip(centers,actual_starts):
  selected=tri[np.all(abs(centroid[:,:2]-center)<4.5,axis=1)];lhs=canonical_triangles(selected);matches=[]
  for mirrored in (False,True):
   mesh,_=make_mesh((9.,9.),mirrored);v=mesh.vertices.copy();v[:,:2]-=4.5;v[:,:2]+=center;pred=v.astype(np.float32)[mesh.faces]
   if np.array_equal(lhs,canonical_triangles(pred)):matches.append((mirrored,pred))
  assert len(matches)==1,'Authored CURB mesh differs from both pinned procedural mirror variants'
  mirrored,pred=matches[0];u=pred[:,1]-pred[:,0];v=pred[:,2]-pred[:,0];det=u[:,0]*v[:,1]-u[:,1]*v[:,0];horizontal=abs(det)>1e-12
  assert len(pred)==8 and horizontal.sum()==6,'Vertical riser triangles kept for identity, excluded only from downward nonparallel intersection'
  out.append(downward_triangle_heights(pred[horizontal],starts));evidence.append(selected);receipts.append(dict(mirrored=mirrored,triangles=8,actual_SHA=hashlib.sha256(lhs.tobytes()).hexdigest(),expected_SHA=hashlib.sha256(canonical_triangles(pred).tobytes()).hexdigest(),byteexact=True,vertical_faces_preserved=2))
 return np.asarray(out),receipts,np.stack(evidence)
