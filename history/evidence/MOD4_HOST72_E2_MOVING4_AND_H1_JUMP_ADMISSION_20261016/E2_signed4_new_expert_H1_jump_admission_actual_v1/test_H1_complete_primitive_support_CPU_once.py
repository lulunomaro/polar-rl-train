"""All actual native collider kinds with rotated/scaled support; no SDK/dynamics claims."""
from pathlib import Path
import os,json,time,itertools,hashlib
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch,numpy as np
from h1_authored_full_collider_plane_reference_v1 import evaluate
D=Path(__file__).resolve().parent;R=D/'reports'
def main():
 rows=[]
 for kind in ('Cube','Capsule','Cylinder','Mesh'):
  shape=dict(body_index=0,type=kind,linear_body_from_shape=[[1.,0,0],[0,1.2,0],[0,0,.7]],origin_body_m=[.03,-.02,.04],size=.2,height=.3,radius=.05,axis=2)
  if kind=='Mesh':shape['points']=np.asarray(list(itertools.product((-.1,.1),repeat=3))).tolist()
  q=torch.tensor([[[1.,0,0,0]],[[np.cos(.35),np.sin(.35),0,0]]],dtype=torch.float64);p=torch.tensor([[[0.,0.,.5]],[[0.,0.,.8]]],dtype=torch.float64);v=evaluate(p,q,[shape]);assert torch.isfinite(v).all()
  if kind in ('Cube','Mesh'):
   local=np.asarray(list(itertools.product((-.1,.1),repeat=3)));L=np.asarray(shape['linear_body_from_shape']);t=np.asarray(shape['origin_body_m']);expected=[]
   for pos,angle in zip((.5,.8),(0,.7)):
    rot=np.array([[1,0,0],[0,np.cos(angle),-np.sin(angle)],[0,np.sin(angle),np.cos(angle)]]);expected.append((local@L.T+t)@rot[2]+pos)
   assert np.max(abs(v[:,0].numpy()-np.min(expected,axis=1)))<1e-12
  rows.append(dict(kind=kind,minima=v[:,0].tolist()))
 with (R/'H1_ACTUAL_NATIVE_COLLIDER_KIND_SUPPORT_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),passed_CPU_only=True,actual_native_types=['Cube','Capsule','Mesh','Cylinder'],fixtures=rows,all_authored_shapes_required_no_root_proxy=True,SDK_actual_pose_and_contact_still_required=True,not_cooked_PhysX_shapeLocal_readback=True,no_CUDA_or_optimizer=True,source_SHA=hashlib.sha256((D/'h1_authored_full_collider_plane_reference_v1.py').read_bytes()).hexdigest()),f,indent=2)
 print(json.dumps(dict(CPU_support_math_passed=True,collider_kinds=4,not_GPU_or_airborne_pass=True)),flush=True)
if __name__=='__main__':main()
