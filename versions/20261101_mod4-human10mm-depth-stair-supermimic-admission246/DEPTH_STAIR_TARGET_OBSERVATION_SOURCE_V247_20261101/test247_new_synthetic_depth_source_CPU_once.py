"""New analytic synthetic-depth cases; zero SDK/model/remote/physics."""
from pathlib import Path
import ast,hashlib,json,time
import numpy as np
from depth_stair247 import target_from_depth,normalized_features,zero_expand_input_matrix,FEATURES
N=Path(__file__).resolve().parent;R=N/'reports';R.mkdir(exist_ok=True)
H,W=48,64;K=np.array([[50.,0.,31.5],[0.,50.,23.5],[0.,0.,1.]],dtype=np.float32)
T=np.array([[0.,0.,1.,0.],[-1.,0.,0.,0.],[0.,-1.,0.,.4],[0.,0.,0.,1.]],dtype=np.float32)
v,u=np.indices((H,W),dtype=np.float32);rays=np.stack((np.ones((H,W)),-(u-K[0,2])/K[0,0],-(v-K[1,2])/K[1,1]),axis=-1).astype(np.float32)
def image(step_height=None):
 depth=np.full((H,W),np.inf,dtype=np.float32);down=rays[...,2]<0
 with np.errstate(divide='ignore',invalid='ignore'):
  floor=-.4/rays[...,2];depth=np.where(down,floor,depth)
  if step_height is not None:
   front=np.ones((H,W),dtype=np.float32);z_at=.4+front*rays[...,2];y_at=front*rays[...,1];valid=(z_at>=0)&(z_at<=step_height)&(np.abs(y_at)<=.6);depth=np.where(valid,np.minimum(depth,front),depth)
   top=(step_height-.4)/rays[...,2];x=top;y=top*rays[...,1];valid=down&(x>=1.)&(x<=2.)&(np.abs(y)<=.6);depth=np.where(valid,np.minimum(depth,top),depth)
 return depth
flat=target_from_depth(image(),K,T,sensor_time=1.,control_time=1.05);step=target_from_depth(image(.27),K,T,sensor_time=1.,control_time=1.05);small=target_from_depth(image(.035),K,T,sensor_time=1.,control_time=1.05)
assert not flat['found']and step['found']and not small['found']
assert abs(step['step_height_m']-.27)<.015 and .85<step['edge_distance_m']<1.25
assert not target_from_depth(image(.27),K,T,sensor_time=1.,control_time=1.3)['found']
f=normalized_features(step);assert f.shape==(9,)and np.isfinite(f).all()
weights=np.arange(4*35,dtype=np.float32).reshape(4,35)/100.;expanded=zero_expand_input_matrix(weights);assert expanded.shape==(4,44)and np.array_equal(expanded[:,:35],weights)and not expanded[:,35:].any()
for p in N.glob('*.py'):ast.parse(p.read_text('utf8'),filename=str(p))
report=dict(passed=True,epoch=time.time(),cases=dict(synthetic_flat_detected=flat['found'],synthetic_270mm_target={k:v for k,v in step.items()if k!='features'},synthetic_35mm_not_a_jump_step=not small['found'],stale_depth_rejected=True),features=list(FEATURES),actor_input35_to44=True,critic_input38_to47=True,zero_column_expansion_preserves_old_input_weights=True,actual_model_or_optimizer_write=False,old_fixture_replays=0,Torch_SDK_GPU_remote_or_physics=0,synthetic_only_not_real_depth_or_step_skill=True)
with(R/'ROOT247_NEW_SYNTHETIC_DEPTH_AND_INPUT_INTERFACE_CPU_RETURNED.json').open('x',encoding='utf8')as f:json.dump(report,f,indent=2,allow_nan=False)
files=list(N.glob('*.py'))+[R/'ROOT247_NEW_SYNTHETIC_DEPTH_AND_INPUT_INTERFACE_CPU_RETURNED.json',N/'HANDOFF247_DEPTH_SOURCE_ONLY.md']
idx=N/'INDEX247_DEPTH_SOURCE_ONLY_FROZEN.json'
with idx.open('x',encoding='utf8')as f:json.dump(dict(epoch=time.time(),kind='FROZEN_DEPTH_STAIR_TARGET_LOCAL_SOURCE_ONLY',files=[dict(path=str(p),bytes=p.stat().st_size,SHA=hashlib.sha256(p.read_bytes()).hexdigest())for p in files],actual_camera_SDK_or_learning=False),f,indent=2)
print(json.dumps(dict(passed=True,index_SHA=hashlib.sha256(idx.read_bytes()).hexdigest(),synthetic_height_m=step['step_height_m'],synthetic_edge_m=step['edge_distance_m'],actual_SDK_or_models=0)))
