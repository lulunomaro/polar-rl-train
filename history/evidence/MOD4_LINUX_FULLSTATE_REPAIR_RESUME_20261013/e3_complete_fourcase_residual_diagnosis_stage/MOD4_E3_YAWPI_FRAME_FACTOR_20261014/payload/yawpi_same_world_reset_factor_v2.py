"""One reset/frame factor: original full pose first, then legal rotated footprint.
Native3060 ABI is actual xyzw, pinned by the worker installed-backend guard.
No live correction, new RNG draws, q setters, simulation steps, or policy edits.
"""
import numpy as np, torch
from scipy.spatial.transform import Rotation
PROFILE='e3_yaw_pi_body_sign_same_world_fullfootprint_v1'
def tensor(x):
 if isinstance(x,torch.Tensor):return x
 if hasattr(x,'torch'):return x.torch
 import warp as wp
 return wp.to_torch(x)
def pi_xyzw(q):
 assert q.ndim==2 and q.shape[1]==4 and torch.isfinite(q).all()
 assert torch.allclose(q.square().sum(-1),torch.ones(len(q),device=q.device,dtype=q.dtype),atol=1e-6,rtol=0)
 out=torch.stack((-q[:,1],q[:,0],q[:,3],-q[:,2]),-1)
 assert torch.allclose(out.square().sum(-1),torch.ones(len(q),device=q.device,dtype=q.dtype),atol=1e-6,rtol=0)
 # Exact component permutation is the factor identity; floating reduction order
 # does not have to remain byteexact during pre-placement nonflat constructor reset.
 return out
def body_targets(groups):
 assert torch.equal(groups,torch.arange(80,device=groups.device)%3)
 v=torch.tensor([-.3,.3,0.],device=groups.device)[groups]
 assert torch.equal(v[groups==2],torch.zeros_like(v[groups==2]))
 return v
def full_reset_yawpi_same_world(env,env_ids):
 from e1_full_pose_reset import full_reset,query
 full_reset(env,env_ids)
 ids=torch.arange(env.num_envs,device=env.device) if env_ids is None else env_ids
 if not len(ids):return
 assert env.num_envs==80 and env.physics_dt==.0025 and env.step_dt==.01
 robot=env.scene['robot']; bank=env._rough_probe_bank; ray=query(env)
 before=tensor(robot.data.root_state_w)[ids].clone();q_before=tensor(robot.data.joint_pos)[ids].clone()
 assert q_before.shape==(len(ids),30) and bank['points'].shape==(25200,3)
 assert torch.equal(q_before,env._rough_probe_expected_q[ids])
 assert torch.equal(before[:,7:],torch.zeros_like(before[:,7:]))
 after=before.clone();after[:,3:7]=pi_xyzw(before[:,3:7]);xy=before[:,:2].clone()
 # Exact quaternion permutation; SciPy consumes the verified native xyzw ABI.
 frames=Rotation.from_quat(after[:,3:7].cpu().numpy()).as_matrix()
 rotations=torch.as_tensor(frames,device=env.device,dtype=torch.float32)
 z=torch.empty(len(ids),device=env.device,dtype=before.dtype)
 ceiling=float(ray.geometry.vertices[:,2].max())+2.;minimum=float('inf')
 for first in range(0,len(ids),64):
  last=min(first+64,len(ids)); offsets=torch.einsum('nij,pj->npi',rotations[first:last],bank['points'])
  starts=offsets.clone(); starts[:,:,:2]+=xy[first:last,None,:]; starts[:,:,2]=ceiling
  surface=ray.cast(starts.contiguous(),10.)
  assert surface['hit'].all() and torch.isfinite(surface['height']).all() and torch.isfinite(surface['normal']).all() and (surface['normal'][...,2]>0).all()
  placed=(surface['height']+.002-offsets[:,:,2]).amax(1)
  clear=placed[:,None]+offsets[:,:,2]-surface['height']
  assert torch.isfinite(clear).all() and float(clear.min())>=.002-1e-5
  z[first:last]=placed;minimum=min(minimum,float(clear.min()))
 after[:,2]=z
 assert torch.equal(after[:,:2],before[:,:2]) and torch.equal(after[:,7:],before[:,7:])
 robot.write_root_state_to_sim(after,env_ids=ids)
 assert torch.equal(tensor(robot.data.joint_pos)[ids],q_before)
 assert torch.equal(tensor(robot.data.root_state_w)[ids],after),'Root native setter readback mismatch'
 env._rough_query_tick=None
 receipt=dict(profile=PROFILE,ids=ids.cpu().tolist(),reset_index=getattr(env,'_yawpi_factor_reset_calls',0),original_full_reset_called_once=True,full_collision_points=25200,
  original_root_xyzw=before.cpu().tolist(),factor_root_xyzw=after.cpu().tolist(),root_Z_delta_m=(after[:,2]-before[:,2]).cpu().tolist(),
  full_q30_exact=True,XY_exact=True,zero_velocity_exact=True,quaternion_changed_NOT_root30_byteexact=True,minimum_sampled_clearance_m=minimum,
  original_clearance_m=.002,original_clearance_tolerance_m=1e-5,query_distance_m=10.,extra_physics_steps_forward_render_reset=0,no_rng_draw=True,
  legal_sampled_fullfootprint_not_continuous_collision_certificate=True)
 env._yawpi_factor_reset_calls=receipt['reset_index']+1
 env._yawpi_factor_birth_receipt=receipt
 if not hasattr(env,'_yawpi_factor_birth_receipts'):env._yawpi_factor_birth_receipts=[]
 env._yawpi_factor_birth_receipts.append(receipt)
