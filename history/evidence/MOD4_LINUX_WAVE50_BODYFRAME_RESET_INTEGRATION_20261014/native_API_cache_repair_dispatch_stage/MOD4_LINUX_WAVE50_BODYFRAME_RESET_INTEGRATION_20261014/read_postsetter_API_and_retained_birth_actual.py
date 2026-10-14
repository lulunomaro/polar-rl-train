"""Read API timing and retained own birth data after v3 natural exit."""
import json
import transport_bodyframe_pipeline_v3 as t
CODE=r'''
from pathlib import Path
import json,hashlib,torch
files=[Path('/home/egde/anaconda3/envs/fangzhen-isaaclab/lib/python3.12/site-packages/isaacsim/extscache/omni.physics.tensors-110.1.13+110.1.2.lx64.r.cp312.u7f4/omni/physics/tensors/api.py'),Path('/home/egde/fangzhen_linux/third_party/IsaacLab-3.0.0-beta2.patch1/source/isaaclab_physx/isaaclab_physx/assets/articulation/articulation.py')]
out=[]
for p in files:
 lines=p.read_text().splitlines();hits=[]
 for i,line in enumerate(lines):
  if 'def set_root_transforms' in line or 'def write_root_pose_to_sim' in line or 'def write_root_state_to_sim' in line:
   hits.append(dict(line=i+1,text='\n'.join(lines[i:i+85])))
 out.append(dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),hits=hits))
root=Path(CONTEXT['root']);births=list((root/'native144/attempt/learning_logs').glob('*/BIRTH_BODYFRAME_ACTUAL_NATIVE_PLACEMENT_READBACK.pt'))
assert len(births)==1
b=torch.load(births[0],map_location='cpu',weights_only=False)
q=b['changed_root_xyzw'][:,3:7]
print(json.dumps(dict(installed_source=out,retained_birth=dict(path=str(births[0]),sha256=hashlib.sha256(births[0].read_bytes()).hexdigest(),pi_births=len(b['pi_ids']),quat_example=q[:5].tolist(),quat_norm_max_error=float((q.square().sum(-1)-1).abs().max()),Z_delta_max=float((b['changed_root_xyzw'][:,2]-b['original_root_xyzw'][:,2]).abs().max()),minimum_clearance=b['minimum_clearance_m']),read_only=True)))
'''
c=None
try:
 c=t.connect();v,p=t.run(c,CODE,dict(root=t.ROOT),'POSTSETTER_API_AND_RETAINED_BIRTH_ACTUAL')
 print(json.dumps(dict(report=str(p),actual=v)))
finally:t.close(c)
