"""New saved-state admission/rejection cases; no Isaac app or CUDA initialization."""
import torch,copy
from e1_terrain_state import validate
def main():
 n=3;s=dict(version=1,num_envs=n,profile='mod4_intro_gentle_v1',seed=20260928,layout=[40,40],command_vx_range=[-.3,.3],command_vy_yaw=[0.,0.],
 geometry_triangles_sha256='a'*64,ordered_partition_triangles_sha256='b'*64,triangles=100,partition_exact=True,no_ground_fallback=True,no_privileged_terrain_actor_input=True,
 reset_bank_sha256='78af9fa47686204ef370271a2da580d762aa9fda1c7a49844ced318b264e6b83',spawn_xy=torch.arange(n*2,dtype=torch.float32).reshape(n,2),reset_expected_q=torch.zeros(n,30),episode=torch.arange(n))
 assert validate(s,n);count=1
 for name,value in [('seed',7),('layout',[2,40]),('command_vy_yaw',[0.,1.]),('partition_exact',False),('no_ground_fallback',False),('spawn_xy',torch.zeros(n,3)),('reset_expected_q',torch.full((n,30),float('nan'))),('episode',torch.full((n,),-1))]:
  bad=copy.deepcopy(s);bad[name]=value
  try:validate(bad,n)
  except AssertionError:count+=1
  else:raise AssertionError('Invalid saved-state admission: '+name)
 assert not torch.cuda.is_initialized();return dict(passed=True,count=count,CUDA_initialized=False,actual_CUDA_restore_not_claimed=True)
if __name__=='__main__':print(main())
