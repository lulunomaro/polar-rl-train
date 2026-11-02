"""Source planned initial state plus real-q queue hold and fresh derived IMU cache."""
from pathlib import Path
import json,types
import torch

def install_planned_reset389(env,path):
 from spring_nominal_sdk_readback import tensor
 from native_geometry272 import quat_to_mat
 data=json.loads(Path(path).read_bytes());initial=data['initial'];names=data['joint_names'];robot=env.scene['robot']
 aliases={f'guide_roller_{i:02d}':f'guide_roller_spin_{i}'for i in range(8)}
 order=[names.index(aliases.get(n,n))for n in robot.joint_names]
 legids=[robot.joint_names.index(n)for n in('left_crank','left_hip','right_crank','right_hip')]
 q0=torch.tensor(initial['qpos_initial'][7:],device=env.device)[order]
 v0=torch.tensor(initial['qvel_initial'][6:],device=env.device)[order]
 old=env._reset_idx;count=[0];selected=[0]
 def reset(this,ids):
  out=old(ids);ids=torch.as_tensor(ids,device=env.device,dtype=torch.long)
  if len(ids):
   q=q0.expand(len(ids),-1).clone();dq=v0.expand(len(ids),-1).clone()
   root=tensor(robot.data.default_root_state)[ids].clone()
   root[:,:3]=torch.tensor(initial['qpos_initial'][:3],device=env.device)+env.scene.env_origins[ids]+torch.tensor([.8,0.,0.],device=env.device)
   root[:,3:7]=torch.tensor(initial['qpos_initial'][3:7],device=env.device)[[1,2,3,0]]
   root[:,7:10]=torch.tensor(initial['qvel_initial'][:3],device=env.device)
   quat=torch.tensor(initial['qpos_initial'][3:7],device=env.device).expand(len(ids),-1)
   root[:,10:13]=torch.einsum('bij,j->bi',quat_to_mat(quat),torch.tensor(initial['qvel_initial'][3:6],device=env.device))
   robot.write_root_state_to_sim(root,env_ids=ids);robot.write_joint_state_to_sim(q,dq,env_ids=ids)
   g=env._physics_action_delay.queue.groups['legs'];g['applied'][ids]=q[:,legids];g['pending'][ids]=q[:,legids]
   for name in('_root_com_ang_vel_b','_root_link_ang_vel_b','_projected_gravity_b'):
    assert hasattr(robot.data,name);getattr(robot.data,name).timestamp=-float('inf')
   # Original reset already cleared selected episode D1/D3 samples. Derived data
   # may have been read during that reset, so invalidate selected caches again.
   for last,_ in env._sensor_mild.cache.values():last[ids]=-1
   for c in env._feedback_delay_mild.cache.values():c['last'][ids]=-1;c['sample_tick'][ids]=-1;c['ready'][ids]=False
   count[0]+=1;selected[0]+=len(ids)
  return out
 env._reset_idx=types.MethodType(reset,env)
 return types.SimpleNamespace(receipt=lambda:dict(kind='PLANNED347_Q_DQ_ROOT_RESET_RL389',calls=count[0],selected_rows=selected[0],q_nonzero=int((q0!=0).sum()),queue_only_applied_pending_actualq=True,original_D0_D7_resampled=True,original_clock_RNG_lag_untouched=True,derived_IMU_cache_fresh=True,physical_dt=.0025,policy_dt=.02,NN=False))
