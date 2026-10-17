"""CPU source admission; frozen evaluation does not restore training DR or BODY state."""
from pathlib import Path
import hashlib, torch
from bodyframe_owned_CPU_state_validation_v1 import KEY,validate
SOURCE_SHA="cfcefb1c46b33d6028bf6663921fac12a58a5abfdba782e1480a18ac84de541b"
def validate_path(path):
 p=Path(path);assert p.stat().st_size==19894311 and hashlib.sha256(p.read_bytes()).hexdigest()==SOURCE_SHA
 ck=torch.load(p,map_location='cpu',weights_only=False);validate(ck[KEY])
 assert ck['E1_WAVE50_BODYFRAME_OWN_GPU_SOURCE']['actual_GPU_fullrestore'] is True
 assert torch.equal(ck[KEY]['bound_episode'],ck['E1_terrain_state']['episode'])
 assert ck['E1_terrain_state']['num_envs']==20000 and len(ck['actor_state_dict'])==9
 assert ck['LINUX20K_LEFT_JOINT_EXPLORATION_INITIALIZATION']['profile']=='left_initial_joint_margin014_std1_v1'
 core={k:v for k,v in ck.items() if k not in (KEY,'E1_WAVE50_BODYFRAME_OWN_GPU_SOURCE')};values=[]
 def walk(x):
  if isinstance(x,torch.Tensor):values.append(x)
  elif isinstance(x,dict):
   for v in x.values():walk(v)
  elif isinstance(x,(list,tuple)):
   for v in x:walk(v)
 walk(core);assert len(values)==195 and sum(v.is_floating_point() for v in values)==107
 assert sum(v.ndim>0 and v.shape[0]==20000 for v in values)==99
 assert all(v.device.type=='cpu' and (not v.is_floating_point() or torch.isfinite(v).all().item()) for v in values)
 assert not torch.cuda.is_initialized()
 return dict(source_whole20k_195_107_99_CPU_verified=True,source_owned_body_state_independently_validated=True,legacy_counts_apply_to_core_only=True,source_SHA=SOURCE_SHA,source_bytes=p.stat().st_size,no_CUDA_or_trainingDR_resume=True)
