"""G2 schema and same-geometry bookkeeping restoration, CPU fixtures only."""
import copy,json,tempfile,torch
from pathlib import Path
import g2_terrain_checkpoint as g
from g2_cad_wave_geometry import PROFILE as profile_path
import hashlib
def base(n):
 return dict(version=1,num_envs=n,profile='mod4_intro_gentle_v1',seed=20260928,layout=[40,40],command_vx_range=[-.3,.3],command_vy_yaw=[0.,0.],geometry_triangles_sha256='1'*64,ordered_partition_triangles_sha256='2'*64,triangles=4800,partition_exact=True,no_ground_fallback=True,no_privileged_terrain_actor_input=True,reset_bank_sha256='78af9fa47686204ef370271a2da580d762aa9fda1c7a49844ced318b264e6b83',spawn_xy=torch.zeros(n,2),reset_expected_q=torch.zeros(n,30),episode=torch.arange(n,dtype=torch.long))
class Env:
 device='cpu'
 def __init__(self,n):
  self.num_envs=n;self._rough_spawn_xy=torch.zeros(n,2);self._rough_probe_expected_q=torch.zeros(n,30);self._e1_episode=torch.zeros(n,dtype=torch.long)
def main():
 torch.set_num_threads(1);n=3;env=Env(n)
 original=g.old.current_state
 def state(e):
  b=base(n);b['spawn_xy']=e._rough_spawn_xy.clone();b['reset_expected_q']=e._rough_probe_expected_q.clone();b['episode']=e._e1_episode.clone();return b
 g.old.current_state=state
 try:
  s=g.current_state(env);assert g.validate(s,n)
  s['spawn_xy']+=2.;s['reset_expected_q']+=.1;s['episode']+=5
  g.restore(env,s);assert g.exact(g.current_state(env),s)
  with tempfile.TemporaryDirectory() as folder:
   p=Path(folder)/'fixture.pt';torch.save(s,p);r=torch.load(p,map_location='cpu',weights_only=False);g.restore(env,r);assert g.exact(g.current_state(env),s)
  for key,value in [('profile','mod4_intro_gentle_v1'),('G2_height_peak_to_trough_m',.01),('G2_profile_sha256','wrong'),('G2_is_derived_not_real_RM70mm',False),('seed',20261002),('partition_exact',False),('no_ground_fallback',False),('no_privileged_terrain_actor_input',False),('reset_expected_q',torch.zeros(n,6))]:
   bad=copy.deepcopy(s);bad[key]=value
   try:g.validate(bad,n)
   except (AssertionError,KeyError):pass
   else:raise AssertionError('Bad G2 schema accepted: '+key)
  bad=copy.deepcopy(s);bad['geometry_triangles_sha256']='3'*64
  try:g.restore(env,bad)
  except AssertionError:pass
  else:raise AssertionError('Mismatched geometry exactrestore accepted')
  assert not torch.cuda.is_initialized()
  print(json.dumps(dict(passed=True,tests=14,target_torch=torch.__version__,CPU_fixture_only=True,no_CUDA_initialized=True,actual_GPU_PPO_resume_still_required=True)))
 finally:g.old.current_state=original
if __name__=='__main__':main()
