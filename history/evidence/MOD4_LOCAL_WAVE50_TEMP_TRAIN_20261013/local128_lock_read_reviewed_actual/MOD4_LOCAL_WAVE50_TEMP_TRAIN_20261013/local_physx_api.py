"""Isolated-process PhysX2 SDK API bridge. No installed SDK files are edited."""
import torch,types

def tensor(v):
 if isinstance(v,torch.Tensor):return v
 import warp as wp
 return v.torch if hasattr(v,'torch') else wp.to_torch(v)

def install():
 # New modular SDK array views expose .torch; the installed2.x SDK alreadyreturns Torch.
 # This read-only identity property bridges representation without copying or changingvalues.
 if not hasattr(torch.Tensor,'torch'):torch.Tensor.torch=property(lambda v:v)
 from isaaclab.assets import Articulation
 from isaaclab.envs import ManagerBasedRLEnv
 from isaaclab.sensors import ContactSensor
 ManagerBasedRLEnv._physics_handles_decimation=False
 class View:
  def __init__(self,view):self.v=view
  def __getattr__(self,name):return getattr(self.v,name)
  def get_coms(self):
   v=self.v.get_coms().clone();v[...,3:]=v[..., [6,3,4,5]];return v
  def get_link_transforms(self):
   v=self.v.get_link_transforms().clone();v[...,3:]=v[..., [6,3,4,5]];return v
  def set_material_properties(self,values,indices):self.v.set_material_properties(tensor(values).cpu(),tensor(indices).to('cpu',dtype=torch.int32))
 Articulation.root_view=property(lambda r:View(r.root_physx_view))
 def set_mass(r,masses,env_ids):
  full=r.root_physx_view.get_masses().clone();full[env_ids.cpu().long()]=tensor(masses).cpu();r.root_physx_view.set_masses(full,env_ids.cpu().int())
 def set_inertia(r,inertias,env_ids):
  full=r.root_physx_view.get_inertias().clone();full[env_ids.cpu().long()]=tensor(inertias).cpu();r.root_physx_view.set_inertias(full,env_ids.cpu().int())
 def set_coms(r,coms,body_ids,env_ids,full_data=False):
  assert not full_data
  values=tensor(coms).clone();values[...,3:]=values[..., [4,5,6,3]]
  full=r.root_physx_view.get_coms().clone();full[env_ids.cpu().long()[:,None],torch.as_tensor(body_ids)[None,:]]=values.cpu()
  r.root_physx_view.set_coms(full,env_ids.cpu().int());r.data._body_com_pose_b.timestamp=-float('inf')
 def stiffness(r,stiffness,joint_ids,env_ids,full_data=False):
  assert not full_data;r.write_joint_stiffness_to_sim(tensor(stiffness),joint_ids=joint_ids,env_ids=env_ids)
 def damping(r,damping,joint_ids,env_ids,full_data=False):
  assert not full_data;r.write_joint_damping_to_sim(tensor(damping),joint_ids=joint_ids,env_ids=env_ids)
 Articulation.set_masses_index=set_mass;Articulation.set_inertias_index=set_inertia;Articulation.set_coms_index=set_coms
 Articulation.write_joint_stiffness_to_sim_index=stiffness;Articulation.write_joint_damping_to_sim_index=damping
 class ContactView:
  def __init__(self,v):self.v=v
  def get_net_contact_forces(self,dt):
   import warp as wp
   values=self.v.get_net_contact_forces(dt=dt)
   return wp.from_torch(values.reshape(-1,3).contiguous(),dtype=wp.vec3)
 ContactSensor.contact_view=property(lambda s:ContactView(s.contact_physx_view))

